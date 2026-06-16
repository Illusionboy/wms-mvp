from dataclasses import dataclass
from datetime import date, datetime, timezone

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.customer import Customer
from app.models.inventory_record import InventoryRecord
from app.models.inventory_import_job import InventoryImportJob
from app.models.product import Product
from app.models.stock_transaction import StockTransaction, StockTransactionType
from app.models.warehouse import Warehouse
from app.schemas.inventory import InventoryImportCreate, StockAdjustCreate, StockInCreate, StockOutCreate, StockTransferCreate, WarehouseStatusRead


async def resolve_warehouse(session: AsyncSession, name: str) -> Warehouse | None:
    """Exact match first; falls back to case-insensitive substring match.

    Exact-first prevents "乐天" from silently resolving to "乐天仓库" when both exist.
    """
    exact = await session.scalar(select(Warehouse).where(Warehouse.name == name))
    if exact is not None:
        return exact
    return await session.scalar(
        select(Warehouse)
        .where(Warehouse.name.ilike(f"%{name}%"))
        .order_by(Warehouse.id.asc())
        .limit(1)
    )


async def resolve_customer(session: AsyncSession, name: str) -> Customer | None:
    """Exact match first; falls back to case-insensitive substring match."""
    exact = await session.scalar(select(Customer).where(Customer.name == name))
    if exact is not None:
        return exact
    return await session.scalar(
        select(Customer)
        .where(Customer.name.ilike(f"%{name}%"))
        .order_by(Customer.id.asc())
        .limit(1)
    )


class InventoryServiceError(Exception):
    pass


class InventoryTargetNotFoundError(InventoryServiceError):
    pass


class InventoryRecordNotFoundError(InventoryServiceError):
    pass


class AmbiguousInventoryRecordError(InventoryServiceError):
    pass


class InsufficientStockError(InventoryServiceError):
    pass


@dataclass(frozen=True)
class LowStockAlert:
    jan_code: str
    product_name: str
    total_quantity: int
    units_per_case: int
    threshold_quantity: int


@dataclass(frozen=True)
class StockMutationResult:
    record: InventoryRecord
    transaction: StockTransaction
    previous_quantity: int
    quantity_delta: int
    low_stock_alert: LowStockAlert | None = None


async def search_inventory_items(session: AsyncSession, keyword: str, limit: int = 20) -> list[Product]:
    statement = (
        _product_search_statement(keyword=keyword, limit=limit)
        .options(
            selectinload(Product.inventory_records).selectinload(InventoryRecord.warehouse),
            selectinload(Product.inventory_records).selectinload(InventoryRecord.customer),
        )
    )
    result = await session.scalars(statement)
    return list(result.all())


async def search_products(session: AsyncSession, keyword: str, limit: int = 20) -> list[Product]:
    result = await session.scalars(_product_search_statement(keyword=keyword, limit=limit))
    return list(result.all())


def is_outer_jan_match(keyword: str, product: Product) -> bool:
    """Return True when keyword matched via outer_jan but NOT the product's own jan_code."""
    if not product.outer_jan:
        return False
    kw = keyword.strip()
    if not kw.isdigit() or len(kw) != 5:
        return False
    like_5 = kw + "_"
    outer = product.outer_jan
    jan = product.jan_code
    # Check if outer_jan matches the 5-digit pattern
    outer_hit = outer[:-1].endswith(kw) or outer.endswith(kw)
    # Check if jan_code itself would also match (then it's not an outer-jan-only hit)
    jan_hit = jan[:-1].endswith(kw) or jan.endswith(kw)
    return outer_hit and not jan_hit


def _product_search_statement(keyword: str, limit: int):
    normalized_keyword = keyword.strip()
    name_pattern = f"%{normalized_keyword}%"

    conditions = []
    rank_conditions = []
    if normalized_keyword.isdigit():
        conditions.append(Product.jan_code == normalized_keyword)
        rank_conditions.append((Product.jan_code == normalized_keyword, 0))
        # 假设 normalized_keyword 是用户输入的 JAN 码片段
        keyword_len = len(normalized_keyword)
        
        if keyword_len == 6:
            # 如果输入了 6 位：说明是扫的/输入的单品后六位，直接精确匹配结尾
            conditions.append(Product.jan_code.endswith(normalized_keyword))
            rank_conditions.append((Product.jan_code.endswith(normalized_keyword), 1))
            
        elif keyword_len == 5:
            # 如果输入了 5 位：说明是为了规避外箱最后一位校验码不同的情况
            # 目标：匹配倒数第 6 位到倒数第 2 位
            # 拼接 LIKE 模式：前面任意字符 + 用户的5位数字 + 最后刚好1个字符
            like_pattern = f"%{normalized_keyword}_"
            suffix_condition = or_(
                Product.jan_code.like(like_pattern),             # 命中情况 1
                Product.jan_code.endswith(normalized_keyword)    # 命中情况 2：同事直接输入了最后 5 位
            )
            conditions.append(suffix_condition)
            rank_conditions.append((suffix_condition, 1))
            # 同款逻辑应用于 outer_jan（外箱JAN末6位前5位 或 末5位）
            outer_condition = and_(
                Product.outer_jan.isnot(None),
                or_(
                    Product.outer_jan.like(like_pattern),
                    Product.outer_jan.endswith(normalized_keyword),
                ),
            )
            conditions.append(outer_condition)
            rank_conditions.append((outer_condition, 2))  # rank 低于直接 JAN 命中
    else:
        conditions.extend(
            [
                Product.name_jp.ilike(name_pattern),
                Product.name_zh.ilike(name_pattern),
            ]
        )

    statement = (
        select(Product)
        .where(or_(*conditions))
        .limit(limit)
    )
    if rank_conditions:
        statement = statement.order_by(case(*rank_conditions, else_=9), Product.jan_code.asc())
    else:
        statement = statement.order_by(Product.jan_code.asc())
    return statement


async def stock_in_item(
    session: AsyncSession,
    payload: StockInCreate,
    *,
    commit: bool = True,
    user_id: int | None = None,
) -> StockMutationResult:
    product = await session.scalar(select(Product).where(Product.jan_code == payload.sku))
    warehouse = await session.scalar(select(Warehouse).where(Warehouse.id == payload.warehouse_id))
    if product is None or warehouse is None:
        raise InventoryTargetNotFoundError

    # One bucket per (product, warehouse) — lock to prevent concurrent duplicate creation
    statement = select(InventoryRecord).where(
        InventoryRecord.product_jan == payload.sku,
        InventoryRecord.warehouse_id == payload.warehouse_id,
    ).with_for_update()
    record = await session.scalar(statement)
    if record is None:
        record = InventoryRecord(
            product_jan=payload.sku,
            warehouse_id=payload.warehouse_id,
            location_code="A-00-00",
            quantity=payload.quantity,
        )
        session.add(record)
        previous_quantity = 0
    else:
        previous_quantity = record.quantity
        record.quantity += payload.quantity

    await session.flush()
    await _refresh_low_stock_state(session=session, jan_code=payload.sku)
    transaction = _create_stock_transaction(
        record=record,
        transaction_type=StockTransactionType.in_,
        quantity_change=payload.quantity,
        source=payload.source,
        reference_id=payload.reference_id,
        note=payload.note,
        user_id=user_id,
        transaction_date=payload.transaction_date,
        supplier=payload.supplier,
    )
    session.add(transaction)
    await session.flush()
    # Auto-reserve: promote waiting CustomerAllocation rows for this JAN if stock now sufficient
    from app.services.customer_allocations import try_auto_reserve  # lazy to avoid circular import
    await try_auto_reserve(session, payload.sku, payload.warehouse_id)
    if commit:
        await session.commit()
    refreshed_record = await _get_inventory_record_for_response(session, record.id)
    refreshed_transaction = await session.get(StockTransaction, transaction.id)
    if refreshed_record is None or refreshed_transaction is None:
        raise InventoryServiceError
    return StockMutationResult(
        record=refreshed_record,
        transaction=refreshed_transaction,
        previous_quantity=previous_quantity,
        quantity_delta=payload.quantity,
    )


async def stock_out_item(
    session: AsyncSession,
    payload: StockOutCreate,
    *,
    commit: bool = True,
    user_id: int | None = None,
    force_negative: bool = False,
) -> StockMutationResult:
    try:
        # with_for_update() inside _find_single_inventory_record prevents concurrent deduction
        record = await _find_single_inventory_record(
            session=session,
            sku=payload.sku,
            warehouse_id=payload.warehouse_id,
        )
    except InventoryRecordNotFoundError:
        # No existing record — allowed when warehouse has negative stock enabled OR caller forces it
        warehouse = await session.get(Warehouse, payload.warehouse_id)
        if not force_negative and (warehouse is None or not warehouse.allow_negative_stock):
            raise
        product = await session.scalar(select(Product).where(Product.jan_code == payload.sku))
        if product is None:
            raise InventoryTargetNotFoundError
        record = InventoryRecord(
            product_jan=payload.sku,
            warehouse_id=payload.warehouse_id,
            customer_id=payload.customer_id,
            location_code=payload.location_code or "A-00-00",
            quantity=0,
            expiration_date=payload.expiration_date,
        )
        session.add(record)
        await session.flush()

    previous_quantity = record.quantity
    if record.quantity < payload.quantity:
        warehouse = await session.get(Warehouse, payload.warehouse_id)
        if not force_negative and (warehouse is None or not warehouse.allow_negative_stock):
            raise InsufficientStockError

    record.quantity -= payload.quantity
    await session.flush()
    low_stock_alert = None
    if not payload.suppress_low_stock_alert:
        low_stock_alert = await _maybe_create_low_stock_alert(session=session, jan_code=payload.sku)
    transaction = _create_stock_transaction(
        record=record,
        transaction_type=StockTransactionType.out,
        quantity_change=-payload.quantity,
        source=payload.source,
        reference_id=payload.reference_id,
        note=payload.note,
        user_id=user_id,
        transaction_date=payload.transaction_date,
        customer=payload.customer,
    )
    session.add(transaction)
    await session.flush()
    if commit:
        await session.commit()
    refreshed_record = await _get_inventory_record_for_response(session, record.id)
    refreshed_transaction = await session.get(StockTransaction, transaction.id)
    if refreshed_record is None or refreshed_transaction is None:
        raise InventoryServiceError
    return StockMutationResult(
        record=refreshed_record,
        transaction=refreshed_transaction,
        previous_quantity=previous_quantity,
        quantity_delta=-payload.quantity,
        low_stock_alert=low_stock_alert,
    )


async def adjust_stock_item(
    session: AsyncSession,
    payload: StockAdjustCreate,
    *,
    commit: bool = True,
    user_id: int | None = None,
) -> StockMutationResult:
    record = await _find_single_inventory_record(
        session=session,
        sku=payload.sku,
        warehouse_id=payload.warehouse_id,
    )
    previous_quantity = record.quantity
    quantity_delta = payload.actual_quantity - previous_quantity
    record.quantity = payload.actual_quantity
    await session.flush()
    low_stock_alert = await _maybe_create_low_stock_alert(session=session, jan_code=payload.sku)
    transaction = _create_stock_transaction(
        record=record,
        transaction_type=StockTransactionType.adjust,
        quantity_change=quantity_delta,
        source=payload.source,
        reference_id=payload.reference_id,
        note=payload.note,
        user_id=user_id,
        transaction_date=payload.transaction_date,
    )
    session.add(transaction)
    await session.flush()
    if commit:
        await session.commit()
    refreshed_record = await _get_inventory_record_for_response(session, record.id)
    refreshed_transaction = await session.get(StockTransaction, transaction.id)
    if refreshed_record is None or refreshed_transaction is None:
        raise InventoryServiceError
    return StockMutationResult(
        record=refreshed_record,
        transaction=refreshed_transaction,
        previous_quantity=previous_quantity,
        quantity_delta=quantity_delta,
        low_stock_alert=low_stock_alert,
    )


async def transfer_stock_item(
    session: AsyncSession,
    payload: StockTransferCreate,
    *,
    user_id: int | None = None,
) -> tuple[StockMutationResult, StockMutationResult]:
    from uuid import uuid4

    if payload.from_warehouse_id == payload.to_warehouse_id:
        raise InventoryServiceError("调出仓库和调入仓库不能相同")

    ref = f"transfer:{uuid4().hex}"
    note = payload.note or ""

    out_payload = StockOutCreate(
        sku=payload.sku,
        warehouse_id=payload.from_warehouse_id,
        quantity=payload.quantity,
        source="web_ui",
        reference_id=ref,
        note=note,
        transaction_date=payload.transaction_date,
    )
    out_result = await stock_out_item(session, out_payload, commit=False, user_id=user_id)

    in_payload = StockInCreate(
        sku=payload.sku,
        warehouse_id=payload.to_warehouse_id,
        quantity=payload.quantity,
        location_code="A-00-00",
        source="web_ui",
        reference_id=ref,
        note=note,
        transaction_date=payload.transaction_date,
    )
    in_result = await stock_in_item(session, in_payload, commit=False, user_id=user_id)

    await session.commit()
    return out_result, in_result


async def _refresh_low_stock_state(session: AsyncSession, jan_code: str) -> None:
    product = await session.scalar(
        select(Product).where(Product.jan_code == jan_code).with_for_update()
    )
    if product is None or product.units_per_case is None:
        return
    total_quantity = await _get_product_total_quantity(session=session, jan_code=jan_code)
    if total_quantity >= product.units_per_case * 2:
        product.low_stock_alert_sent = False


async def _maybe_create_low_stock_alert(session: AsyncSession, jan_code: str) -> LowStockAlert | None:
    product = await session.scalar(
        select(Product).where(Product.jan_code == jan_code).with_for_update()
    )
    if product is None or product.units_per_case is None:
        return None
    total_quantity = await _get_product_total_quantity(session=session, jan_code=jan_code)
    threshold_quantity = product.units_per_case * 2
    if total_quantity >= threshold_quantity:
        product.low_stock_alert_sent = False
        return None
    if product.low_stock_alert_sent:
        return None

    product.low_stock_alert_sent = True
    return LowStockAlert(
        jan_code=product.jan_code,
        product_name=product.name_jp,
        total_quantity=total_quantity,
        units_per_case=product.units_per_case,
        threshold_quantity=threshold_quantity,
    )


async def _get_product_total_quantity(session: AsyncSession, jan_code: str) -> int:
    total_quantity = await session.scalar(
        select(func.coalesce(func.sum(InventoryRecord.quantity), 0)).where(
            InventoryRecord.product_jan == jan_code
        )
    )
    return int(total_quantity or 0)


async def _find_single_inventory_record(
    session: AsyncSession,
    sku: str,
    warehouse_id: int,
) -> InventoryRecord:
    # One bucket per (product, warehouse) — lock to prevent concurrent quantity races
    result = await session.scalars(
        select(InventoryRecord).where(
            InventoryRecord.product_jan == sku,
            InventoryRecord.warehouse_id == warehouse_id,
        ).with_for_update().limit(2)
    )
    records = list(result.all())
    if not records:
        raise InventoryRecordNotFoundError
    if len(records) > 1:
        raise AmbiguousInventoryRecordError
    return records[0]


async def _get_inventory_record_for_response(session: AsyncSession, record_id: int) -> InventoryRecord | None:
    return await session.scalar(
        select(InventoryRecord)
        .options(
            selectinload(InventoryRecord.warehouse),
            selectinload(InventoryRecord.customer),
        )
        .where(InventoryRecord.id == record_id)
    )


def _create_stock_transaction(
    record: InventoryRecord,
    transaction_type: StockTransactionType,
    quantity_change: int,
    source: str,
    reference_id: str | None = None,
    note: str | None = None,
    user_id: int | None = None,
    transaction_date: date | None = None,
    supplier: str | None = None,
    customer: str | None = None,
) -> StockTransaction:
    return StockTransaction(
        inventory_record_id=record.id,
        transaction_type=transaction_type,
        quantity_change=quantity_change,
        source=source,
        reference_id=reference_id,
        note=note,
        user_id=user_id,
        transaction_date=transaction_date,
        supplier=supplier,
        customer=customer,
    )


async def get_system_status(session: AsyncSession) -> list[WarehouseStatusRead]:
    stmt = (
        select(
            Warehouse.id.label("warehouse_id"),
            Warehouse.name.label("warehouse_name"),
            Warehouse.allow_negative_stock,
            func.max(
                case((StockTransaction.transaction_type == StockTransactionType.in_, StockTransaction.created_at), else_=None)
            ).label("last_stock_in_at"),
            func.max(
                case((StockTransaction.transaction_type == StockTransactionType.out, StockTransaction.created_at), else_=None)
            ).label("last_stock_out_at"),
            func.max(
                case((StockTransaction.source == "rakuten_csv", StockTransaction.created_at), else_=None)
            ).label("last_csv_apply_at"),
            func.max(
                case((StockTransaction.source == "physical_count", StockTransaction.created_at), else_=None)
            ).label("last_physical_count_at"),
            (
                select(func.count())
                .where(
                    InventoryRecord.warehouse_id == Warehouse.id,
                    InventoryRecord.quantity < 0,
                )
                .correlate(Warehouse)
                .scalar_subquery()
            ).label("negative_stock_count"),
        )
        .select_from(Warehouse)
        .outerjoin(InventoryRecord, InventoryRecord.warehouse_id == Warehouse.id)
        .outerjoin(StockTransaction, StockTransaction.inventory_record_id == InventoryRecord.id)
        .group_by(Warehouse.id, Warehouse.name, Warehouse.allow_negative_stock)
        .order_by(Warehouse.id.asc())
    )
    rows = await session.execute(stmt)
    now = datetime.now(tz=timezone.utc)
    result: list[WarehouseStatusRead] = []
    for row in rows.all():
        last_activity = max(
            (t for t in (row.last_stock_in_at, row.last_stock_out_at, row.last_physical_count_at) if t is not None),
            default=None,
        )
        data_gap_days: int | None = None
        if last_activity is not None:
            last_dt = last_activity if last_activity.tzinfo else last_activity.replace(tzinfo=timezone.utc)
            data_gap_days = (now - last_dt).days
        result.append(
            WarehouseStatusRead(
                warehouse_id=row.warehouse_id,
                warehouse_name=row.warehouse_name,
                allow_negative_stock=row.allow_negative_stock,
                last_stock_in_at=row.last_stock_in_at,
                last_stock_out_at=row.last_stock_out_at,
                last_csv_apply_at=row.last_csv_apply_at,
                last_physical_count_at=row.last_physical_count_at,
                data_gap_days=data_gap_days,
                negative_stock_count=row.negative_stock_count,
            )
        )
    return result


async def export_warehouse_inventory(
    session: AsyncSession,
    warehouse_id: int,
) -> tuple[str, list[dict]]:
    """Return (warehouse_name, rows) for all inventory records in the warehouse.

    Each row is a flat dict ready for serialisation to Excel or CSV.
    Only products with inventory records are included; zero-quantity rows are included.
    """
    wh = await session.get(Warehouse, warehouse_id)
    if wh is None:
        raise ValueError(f"Warehouse {warehouse_id} not found")

    stmt = (
        select(InventoryRecord, Product)
        .join(Product, InventoryRecord.product_jan == Product.jan_code)
        .where(InventoryRecord.warehouse_id == warehouse_id)
        .order_by(Product.jan_code.asc())
    )
    rows_db = (await session.execute(stmt)).all()

    rows = [
        {
            "JAN码": rec.product_jan,
            "商品名(日语)": prod.name_jp,
            "商品名(中文)": prod.name_zh or "",
            "库存数量": rec.quantity,
            "箱规(个/箱)": prod.units_per_case or "",
            "库位": rec.location_code or "",
            "最后更新": rec.updated_at.strftime("%Y-%m-%d %H:%M") if rec.updated_at else "",
        }
        for rec, prod in rows_db
    ]
    return wh.name, rows


async def create_inventory_import_job(
    session: AsyncSession,
    payload: InventoryImportCreate,
) -> InventoryImportJob:
    job = InventoryImportJob(
        original_filename=payload.original_filename,
        content_type=payload.content_type,
        file_size=payload.file_size,
        status="pending",
        message="File received. Parsing/import workflow is not enabled yet.",
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)
    return job
