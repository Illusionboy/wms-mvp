"""
供应链历史查询端点（无需认证，只读）

- GET /analytics/counterparties        — 所有出现过的供应商和客户名列表
- GET /analytics/supplier-history      — 按供应商 + 日期范围查询入库事务
- GET /analytics/customer-history      — 按客户 + 日期范围查询出库事务
- GET /analytics/product-history       — 按 JAN 码 + 日期范围查询所有事务
- GET /analytics/safety-stock-recommendations — 动态安全库存/再订货点预警
- GET /analytics/system-logs            — 系统异常日志（负库存、预留冲突等）
"""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import require_admin
from app.db.session import get_db_session
from app.models.dormant_ignore import DormantIgnore
from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.models.stock_transaction import StockTransaction, StockTransactionType
from app.schemas.inventory import SafetyStockRecommendation, SystemLogRead
from app.services.inventory_planning import list_safety_stock_recommendations
from app.services.system_log import get_system_logs

router = APIRouter()


# ── helpers ──────────────────────────────────────────────────────────────────

def _effective_date():
    """业务日期表达式：transaction_date 为空时回退到 created_at 的日期部分。

    用于排序与日期过滤——乐天 CSV / 微信报库 / 贸易出库 的 transaction_date 目前为 NULL，
    若按 transaction_date 直接排序会被排到最后（nullslast），按 `OR IS NULL` 过滤又会让它们
    无视日期范围全部漏放（"选了时间还是全出来"）。统一用 COALESCE 回退到 created_at 即可修正两者。
    """
    return func.coalesce(StockTransaction.transaction_date, cast(StockTransaction.created_at, Date))


def _txn_to_dict(txn: StockTransaction) -> dict:
    ir = txn.inventory_record
    return {
        "id": txn.id,
        "transaction_type": txn.transaction_type,
        "quantity_change": txn.quantity_change,
        "source": txn.source,
        "supplier": txn.supplier,
        "customer": txn.customer,
        "note": txn.note,
        "reference_id": txn.reference_id,
        "transaction_date": txn.transaction_date.isoformat() if txn.transaction_date else None,
        "created_at": txn.created_at.isoformat(),
        "jan_code": ir.product_jan if ir else None,
        "product_name": ir.product.name_jp if (ir and ir.product) else None,
        "product_name_zh": ir.product.name_zh if (ir and ir.product) else None,
        "warehouse_name": ir.warehouse.name if (ir and ir.warehouse) else None,
        "warehouse_id": ir.warehouse_id if ir else None,
    }


# ── endpoints ────────────────────────────────────────────────────────────────

@router.get("/counterparties")
async def list_counterparties(
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Return all distinct supplier and customer names seen in stock_transactions."""
    supplier_rows = await session.scalars(
        select(StockTransaction.supplier)
        .where(StockTransaction.supplier.isnot(None))
        .group_by(StockTransaction.supplier)
        .order_by(StockTransaction.supplier.asc())
    )
    customer_rows = await session.scalars(
        select(StockTransaction.customer)
        .where(StockTransaction.customer.isnot(None))
        .group_by(StockTransaction.customer)
        .order_by(StockTransaction.customer.asc())
    )
    return {
        "suppliers": list(supplier_rows.all()),
        "customers": list(customer_rows.all()),
    }


@router.get("/supplier-history")
async def supplier_history(
    supplier: str = Query(..., min_length=1),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
    limit: int = Query(default=200, le=1000),
    session: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    """IN transactions filtered by supplier name (partial match) + date range."""
    stmt = (
        select(StockTransaction)
        .options(
            selectinload(StockTransaction.inventory_record)
            .selectinload(InventoryRecord.product),
            selectinload(StockTransaction.inventory_record)
            .selectinload(InventoryRecord.warehouse),
        )
        .where(
            StockTransaction.transaction_type == StockTransactionType.in_,
            StockTransaction.supplier.ilike(f"%{supplier}%"),
        )
        .order_by(
            _effective_date().desc(),
            StockTransaction.created_at.desc(),
        )
        .limit(limit)
    )
    if from_date:
        stmt = stmt.where(_effective_date() >= from_date)
    if to_date:
        stmt = stmt.where(_effective_date() <= to_date)
    if warehouse_id:
        stmt = stmt.join(
            InventoryRecord, InventoryRecord.id == StockTransaction.inventory_record_id
        ).where(InventoryRecord.warehouse_id == warehouse_id)

    rows = await session.scalars(stmt)
    return [_txn_to_dict(t) for t in rows.all()]


@router.get("/customer-history")
async def customer_history(
    customer: str = Query(..., min_length=1),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
    limit: int = Query(default=200, le=1000),
    session: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    """OUT transactions filtered by customer name (partial match) + date range."""
    stmt = (
        select(StockTransaction)
        .options(
            selectinload(StockTransaction.inventory_record)
            .selectinload(InventoryRecord.product),
            selectinload(StockTransaction.inventory_record)
            .selectinload(InventoryRecord.warehouse),
        )
        .where(
            StockTransaction.transaction_type == StockTransactionType.out,
            StockTransaction.customer.ilike(f"%{customer}%"),
        )
        .order_by(
            _effective_date().desc(),
            StockTransaction.created_at.desc(),
        )
        .limit(limit)
    )
    if from_date:
        stmt = stmt.where(_effective_date() >= from_date)
    if to_date:
        stmt = stmt.where(_effective_date() <= to_date)
    if warehouse_id:
        stmt = stmt.join(
            InventoryRecord, InventoryRecord.id == StockTransaction.inventory_record_id
        ).where(InventoryRecord.warehouse_id == warehouse_id)

    rows = await session.scalars(stmt)
    return [_txn_to_dict(t) for t in rows.all()]


@router.get("/product-history")
async def product_history(
    jan_code: str = Query(..., min_length=5),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    warehouse_id: int | None = Query(default=None),
    transaction_type: str | None = Query(default=None, description="IN / OUT / ADJUST"),
    limit: int = Query(default=200, le=1000),
    session: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    """All stock transactions for a specific JAN code, optionally filtered by date and type."""
    stmt = (
        select(StockTransaction)
        .join(InventoryRecord, InventoryRecord.id == StockTransaction.inventory_record_id)
        .options(
            selectinload(StockTransaction.inventory_record)
            .selectinload(InventoryRecord.product),
            selectinload(StockTransaction.inventory_record)
            .selectinload(InventoryRecord.warehouse),
        )
        .where(InventoryRecord.product_jan == jan_code)
        .order_by(
            _effective_date().desc(),
            StockTransaction.created_at.desc(),
        )
        .limit(limit)
    )
    if transaction_type:
        stmt = stmt.where(StockTransaction.transaction_type == transaction_type.upper())
    if from_date:
        stmt = stmt.where(_effective_date() >= from_date)
    if to_date:
        stmt = stmt.where(_effective_date() <= to_date)
    if warehouse_id:
        stmt = stmt.where(InventoryRecord.warehouse_id == warehouse_id)

    rows = await session.scalars(stmt)
    return [_txn_to_dict(t) for t in rows.all()]


@router.get("/product-summary")
async def product_summary(
    jan_code: str = Query(..., min_length=5),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Aggregate IN/OUT/ADJUST totals for a product, optionally within a date range."""
    base = (
        select(
            StockTransaction.transaction_type,
            func.sum(StockTransaction.quantity_change).label("total"),
            func.count().label("count"),
        )
        .join(InventoryRecord, InventoryRecord.id == StockTransaction.inventory_record_id)
        .where(InventoryRecord.product_jan == jan_code)
        .group_by(StockTransaction.transaction_type)
    )
    if from_date:
        base = base.where(_effective_date() >= from_date)
    if to_date:
        base = base.where(_effective_date() <= to_date)

    rows = await session.execute(base)
    summary: dict[str, dict] = {}
    for row in rows.all():
        summary[row.transaction_type] = {"total": int(row.total or 0), "count": int(row.count)}

    # Also fetch product name
    product = await session.scalar(
        select(Product).where(Product.jan_code == jan_code)
    )
    return {
        "jan_code": jan_code,
        "name_jp": product.name_jp if product else None,
        "name_zh": product.name_zh if product else None,
        "summary": summary,
    }


@router.get("/dormant-products")
async def dormant_products(
    days: int = Query(30, ge=1, le=3650),
    warehouse_id: int | None = Query(default=None),
    include_ignored: bool = Query(default=False),
    session: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    """最近 N 天内【没有任何出库(OUT)】的在库商品——呆滞/滞销库存报表。
    只算 OUT 事务（不算 ADJUST 调整、不算入库）；只统计当前库存 > 0 的商品；可选按仓库。
    被标记「忽略」的 JAN 默认不返回（include_ignored=true 则全部返回并带 ignored 标记）。
    返回 JAN、名称、当前库存、最后出库日期、距今天数（从未出库者 last_out_date 为空、排最前）。"""
    cutoff = date.today() - timedelta(days=days)
    ignored_set = set((await session.execute(select(DormantIgnore.jan_code))).scalars().all())

    # 1) 当前有库存(>0)的商品，可选按仓库
    stock_stmt = (
        select(InventoryRecord.product_jan, func.sum(InventoryRecord.quantity).label("stock"))
        .group_by(InventoryRecord.product_jan)
        .having(func.sum(InventoryRecord.quantity) > 0)
    )
    if warehouse_id is not None:
        stock_stmt = stock_stmt.where(InventoryRecord.warehouse_id == warehouse_id)
    stock_map = {jan: int(s) for jan, s in (await session.execute(stock_stmt)).all()}
    if not stock_map:
        return []

    # 2) 每个商品最后一次 OUT 的业务日期（可选按仓库）
    out_stmt = (
        select(InventoryRecord.product_jan, func.max(_effective_date()).label("last_out"))
        .select_from(StockTransaction)
        .join(InventoryRecord, InventoryRecord.id == StockTransaction.inventory_record_id)
        .where(StockTransaction.transaction_type == StockTransactionType.out)
        .group_by(InventoryRecord.product_jan)
    )
    if warehouse_id is not None:
        out_stmt = out_stmt.where(InventoryRecord.warehouse_id == warehouse_id)
    last_out_map = {jan: d for jan, d in (await session.execute(out_stmt)).all()}

    # 3) 每个商品最早一次入库/建档的业务日期（任意事务的最早日）——用于判断是不是"新上架"
    first_stmt = (
        select(InventoryRecord.product_jan, func.min(_effective_date()).label("first_seen"))
        .select_from(StockTransaction)
        .join(InventoryRecord, InventoryRecord.id == StockTransaction.inventory_record_id)
        .group_by(InventoryRecord.product_jan)
    )
    if warehouse_id is not None:
        first_stmt = first_stmt.where(InventoryRecord.warehouse_id == warehouse_id)
    first_seen_map = {jan: d for jan, d in (await session.execute(first_stmt)).all()}

    # 4) 商品名
    name_map = {
        p.jan_code: p
        for p in (await session.execute(
            select(Product).where(Product.jan_code.in_(list(stock_map.keys())))
        )).scalars().all()
    }

    today = date.today()
    result: list[dict] = []
    for jan, stock in stock_map.items():
        last_out = last_out_map.get(jan)
        if last_out is not None and last_out >= cutoff:
            continue  # 近 N 天内出过库 → 不算滞销
        first_seen = first_seen_map.get(jan)
        if first_seen is not None and first_seen > cutoff:
            continue  # 首次入库不足 N 天 → 新上架，还没到该卖的时候，不算滞销
        is_ignored = jan in ignored_set
        if is_ignored and not include_ignored:
            continue  # 默认隐藏被标记忽略的
        p = name_map.get(jan)
        result.append({
            "jan_code": jan,
            "product_name": p.name_jp if p else None,
            "product_name_zh": p.name_zh if p else None,
            "current_stock": stock,
            "last_out_date": last_out.isoformat() if last_out else None,
            "days_since_out": (today - last_out).days if last_out else None,
            "first_in_date": first_seen.isoformat() if first_seen else None,
            "days_in_stock": (today - first_seen).days if first_seen else None,
            "ignored": is_ignored,
        })
    # 从未出库者最前，其余按距今天数降序（最久没动的在上）
    result.sort(key=lambda r: (r["last_out_date"] is None, r["days_since_out"] or 0), reverse=True)
    return result


class DormantIgnoreRequest(BaseModel):
    jan_code: str
    ignored: bool


@router.post("/dormant-products/ignore")
async def set_dormant_ignore(
    payload: DormantIgnoreRequest,
    session: AsyncSession = Depends(get_db_session),
    _=Depends(require_admin),
) -> dict:
    """标记/取消标记某 JAN 为「忽略」——被忽略的商品默认不出现在滞销品统计里。"""
    jan = (payload.jan_code or "").strip()
    if not jan:
        return {"jan_code": jan, "ignored": False}
    existing = await session.get(DormantIgnore, jan)
    if payload.ignored and existing is None:
        session.add(DormantIgnore(jan_code=jan))
        await session.commit()
    elif not payload.ignored and existing is not None:
        await session.delete(existing)
        await session.commit()
    return {"jan_code": jan, "ignored": payload.ignored}


@router.get("/safety-stock-recommendations", response_model=list[SafetyStockRecommendation])
async def safety_stock_recommendations(
    warehouse_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> list[SafetyStockRecommendation]:
    """基于 SS = Z * sigma_D * sqrt(L) 计算各 SKU 的安全库存与再订货点，

    返回当前库存量低于建议再订货点（ROP）的商品列表。详见 docs/safety_stock_manage.md。
    """
    return await list_safety_stock_recommendations(session, warehouse_id=warehouse_id)


@router.get("/system-logs", response_model=list[SystemLogRead])
async def system_logs(
    category: str | None = Query(default=None, description="negative_stock / allocation_conflict 等"),
    level: str | None = Query(default=None, description="warning / error / info"),
    limit: int = Query(default=200, le=1000),
    session: AsyncSession = Depends(get_db_session),
) -> list[SystemLogRead]:
    """系统异常事件统一日志：出库/调整后出现负库存、预留冲突等，按时间倒序。"""
    return await get_system_logs(session, category=category, level=level, limit=limit)
