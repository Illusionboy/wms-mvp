from dataclasses import dataclass
from datetime import date

from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.customer import Customer
from app.models.inventory_record import InventoryRecord
from app.models.inventory_import_job import InventoryImportJob
from app.models.product import Product
from app.models.stock_transaction import StockTransaction, StockTransactionType
from app.models.warehouse import Warehouse
from app.schemas.inventory import InventoryImportCreate, StockAdjustCreate, StockInCreate, StockOutCreate


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


async def stock_in_item(session: AsyncSession, payload: StockInCreate) -> StockMutationResult:
    product = await session.scalar(select(Product).where(Product.jan_code == payload.sku))
    warehouse = await session.scalar(select(Warehouse).where(Warehouse.id == payload.warehouse_id))
    customer = None
    if payload.customer_id is not None:
        customer = await session.scalar(select(Customer).where(Customer.id == payload.customer_id))
    if product is None or warehouse is None or (payload.customer_id is not None and customer is None):
        raise InventoryTargetNotFoundError

    statement = select(InventoryRecord).where(
        InventoryRecord.product_jan == payload.sku,
        InventoryRecord.warehouse_id == payload.warehouse_id,
        InventoryRecord.customer_id == payload.customer_id,
        InventoryRecord.location_code == payload.location_code,
        InventoryRecord.expiration_date == payload.expiration_date,
    )
    record = await session.scalar(statement)
    if record is None:
        record = InventoryRecord(
            product_jan=payload.sku,
            warehouse_id=payload.warehouse_id,
            customer_id=payload.customer_id,
            location_code=payload.location_code,
            quantity=payload.quantity,
            expiration_date=payload.expiration_date,
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
    )
    session.add(transaction)
    await session.flush()
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


async def stock_out_item(session: AsyncSession, payload: StockOutCreate) -> StockMutationResult:
    record = await _find_single_inventory_record(
        session=session,
        sku=payload.sku,
        warehouse_id=payload.warehouse_id,
        customer_id=payload.customer_id,
        location_code=payload.location_code,
        expiration_date=payload.expiration_date,
    )
    previous_quantity = record.quantity
    if record.quantity < payload.quantity:
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
    )
    session.add(transaction)
    await session.flush()
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


async def adjust_stock_item(session: AsyncSession, payload: StockAdjustCreate) -> StockMutationResult:
    record = await _find_single_inventory_record(
        session=session,
        sku=payload.sku,
        warehouse_id=payload.warehouse_id,
        customer_id=payload.customer_id,
        location_code=payload.location_code,
        expiration_date=payload.expiration_date,
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
    )
    session.add(transaction)
    await session.flush()
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


async def _refresh_low_stock_state(session: AsyncSession, jan_code: str) -> None:
    product = await session.get(Product, jan_code)
    if product is None or product.units_per_case is None:
        return
    total_quantity = await _get_product_total_quantity(session=session, jan_code=jan_code)
    if total_quantity >= product.units_per_case * 2:
        product.low_stock_alert_sent = False


async def _maybe_create_low_stock_alert(session: AsyncSession, jan_code: str) -> LowStockAlert | None:
    product = await session.get(Product, jan_code)
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
    customer_id: int | None,
    location_code: str | None,
    expiration_date: date | None,
) -> InventoryRecord:
    statement = select(InventoryRecord).where(
        InventoryRecord.product_jan == sku,
        InventoryRecord.warehouse_id == warehouse_id,
    )
    if customer_id is not None:
        statement = statement.where(InventoryRecord.customer_id == customer_id)
    if location_code is not None:
        statement = statement.where(InventoryRecord.location_code == location_code)
    if expiration_date is not None:
        statement = statement.where(InventoryRecord.expiration_date == expiration_date)

    result = await session.scalars(statement.limit(2))
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
) -> StockTransaction:
    return StockTransaction(
        inventory_record_id=record.id,
        transaction_type=transaction_type,
        quantity_change=quantity_change,
        source=source,
        reference_id=reference_id,
        note=note,
    )


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
