"""
供应链历史查询端点（无需认证，只读）

- GET /analytics/counterparties        — 所有出现过的供应商和客户名列表
- GET /analytics/supplier-history      — 按供应商 + 日期范围查询入库事务
- GET /analytics/customer-history      — 按客户 + 日期范围查询出库事务
- GET /analytics/product-history       — 按 JAN 码 + 日期范围查询所有事务
- GET /analytics/safety-stock-recommendations — 动态安全库存/再订货点预警
- GET /analytics/system-logs            — 系统异常日志（负库存、预留冲突等）
"""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db_session
from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.models.stock_transaction import StockTransaction, StockTransactionType
from app.schemas.inventory import SafetyStockRecommendation, SystemLogRead
from app.services.inventory_planning import list_safety_stock_recommendations
from app.services.system_log import get_system_logs

router = APIRouter()


# ── helpers ──────────────────────────────────────────────────────────────────

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
            StockTransaction.transaction_date.desc().nullslast(),
            StockTransaction.created_at.desc(),
        )
        .limit(limit)
    )
    if from_date:
        stmt = stmt.where(
            or_(
                StockTransaction.transaction_date >= from_date,
                StockTransaction.transaction_date.is_(None),
            )
        )
    if to_date:
        stmt = stmt.where(
            or_(
                StockTransaction.transaction_date <= to_date,
                StockTransaction.transaction_date.is_(None),
            )
        )
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
            StockTransaction.transaction_date.desc().nullslast(),
            StockTransaction.created_at.desc(),
        )
        .limit(limit)
    )
    if from_date:
        stmt = stmt.where(
            or_(
                StockTransaction.transaction_date >= from_date,
                StockTransaction.transaction_date.is_(None),
            )
        )
    if to_date:
        stmt = stmt.where(
            or_(
                StockTransaction.transaction_date <= to_date,
                StockTransaction.transaction_date.is_(None),
            )
        )
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
            StockTransaction.transaction_date.desc().nullslast(),
            StockTransaction.created_at.desc(),
        )
        .limit(limit)
    )
    if transaction_type:
        stmt = stmt.where(StockTransaction.transaction_type == transaction_type.upper())
    if from_date:
        stmt = stmt.where(
            or_(
                StockTransaction.transaction_date >= from_date,
                StockTransaction.transaction_date.is_(None),
            )
        )
    if to_date:
        stmt = stmt.where(
            or_(
                StockTransaction.transaction_date <= to_date,
                StockTransaction.transaction_date.is_(None),
            )
        )
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
        base = base.where(StockTransaction.transaction_date >= from_date)
    if to_date:
        base = base.where(StockTransaction.transaction_date <= to_date)

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
