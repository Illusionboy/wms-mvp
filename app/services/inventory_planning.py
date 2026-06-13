"""动态安全库存（Safety Stock）计算服务。

公式: SS = Z * sigma_D * sqrt(L)
      ROP = D_avg * L + SS

- Z: 服务水平系数，来自 settings.safety_stock_z（默认 1.65，对应 95% 不缺货概率）
- L: 补货前置时间（天），按该商品最近一次 IN 事务的 supplier 映射得到，
     未匹配到供应商或 supplier 为空时使用 DEFAULT_LEAD_TIME_DAYS
- sigma_D / D_avg: 过去 lookback_days 天每日 OUT 总量的标准差 / 均值
  （按 COALESCE(transaction_date, created_at::date) 聚合，缺失的日期记为 0）
"""
from __future__ import annotations

import math
import statistics
from datetime import date, timedelta

from sqlalchemy import Date, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.models.stock_transaction import StockTransaction, StockTransactionType
from app.models.warehouse import Warehouse
from app.schemas.inventory import SafetyStockRecommendation

# 供应商 -> 补货前置时间（天）。未来可移入配置或 DB；目前仅作为示例映射。
SUPPLIER_LEAD_TIME_DAYS: dict[str, int] = {}

DEFAULT_LEAD_TIME_DAYS = 5
DEFAULT_LOOKBACK_DAYS = 30


async def _get_primary_supplier(session: AsyncSession, jan_code: str) -> str | None:
    """该商品最近一次 IN 事务的 supplier（主力供应商）。"""
    stmt = (
        select(StockTransaction.supplier)
        .join(InventoryRecord, InventoryRecord.id == StockTransaction.inventory_record_id)
        .where(
            InventoryRecord.product_jan == jan_code,
            StockTransaction.transaction_type == StockTransactionType.in_,
            StockTransaction.supplier.isnot(None),
        )
        .order_by(
            StockTransaction.transaction_date.desc().nullslast(),
            StockTransaction.created_at.desc(),
        )
        .limit(1)
    )
    return await session.scalar(stmt)


async def _get_daily_out_quantities(
    session: AsyncSession,
    jan_code: str,
    warehouse_id: int,
    start_date: date,
) -> dict[date, int]:
    day_expr = func.coalesce(StockTransaction.transaction_date, cast(StockTransaction.created_at, Date))
    stmt = (
        select(day_expr.label("day"), func.sum(func.abs(StockTransaction.quantity_change)).label("qty"))
        .join(InventoryRecord, InventoryRecord.id == StockTransaction.inventory_record_id)
        .where(
            InventoryRecord.product_jan == jan_code,
            InventoryRecord.warehouse_id == warehouse_id,
            StockTransaction.transaction_type == StockTransactionType.out,
            day_expr >= start_date,
        )
        .group_by(day_expr)
    )
    rows = await session.execute(stmt)
    return {row.day: int(row.qty) for row in rows}


async def calculate_safety_stock(
    session: AsyncSession,
    jan_code: str,
    warehouse_id: int,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> SafetyStockRecommendation | None:
    """计算单个 (jan_code, warehouse_id) 的安全库存与再订货点建议。"""
    record = await session.scalar(
        select(InventoryRecord)
        .where(
            InventoryRecord.product_jan == jan_code,
            InventoryRecord.warehouse_id == warehouse_id,
        )
    )
    if record is None:
        return None

    product = await session.get(Product, jan_code)
    warehouse = await session.get(Warehouse, warehouse_id)
    if product is None or warehouse is None:
        return None

    supplier = await _get_primary_supplier(session, jan_code)
    lead_time_days = SUPPLIER_LEAD_TIME_DAYS.get(supplier, DEFAULT_LEAD_TIME_DAYS) if supplier else DEFAULT_LEAD_TIME_DAYS

    today = date.today()
    start_date = today - timedelta(days=lookback_days)
    daily_qty = await _get_daily_out_quantities(session, jan_code, warehouse_id, start_date)

    # 过去 lookback_days 天（不含今天），缺失的日期记为 0
    series = [daily_qty.get(today - timedelta(days=i), 0) for i in range(1, lookback_days + 1)]
    sufficient_data = any(qty > 0 for qty in series)

    daily_avg = statistics.fmean(series)
    std_dev = statistics.pstdev(series)

    safety_stock = settings.safety_stock_z * std_dev * math.sqrt(lead_time_days)
    reorder_point = daily_avg * lead_time_days + safety_stock

    return SafetyStockRecommendation(
        jan_code=jan_code,
        name_jp=product.name_jp,
        name_zh=product.name_zh,
        warehouse_id=warehouse_id,
        warehouse_name=warehouse.name,
        supplier=supplier,
        lead_time_days=lead_time_days,
        daily_avg=round(daily_avg, 2),
        std_dev=round(std_dev, 2),
        safety_stock=round(safety_stock, 2),
        reorder_point=round(reorder_point, 2),
        current_quantity=record.quantity,
        sufficient_data=sufficient_data,
    )


async def list_safety_stock_recommendations(
    session: AsyncSession,
    warehouse_id: int | None = None,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> list[SafetyStockRecommendation]:
    """返回当前库存低于建议再订货点的商品列表（可选按仓库过滤）。

    MVP 阶段逐个 SKU 计算（数据量小时足够；后续若 SKU 数量增大可考虑
    在 DB 层一次性聚合所有商品的日出库量）。
    """
    stmt = select(InventoryRecord.product_jan, InventoryRecord.warehouse_id)
    if warehouse_id is not None:
        stmt = stmt.where(InventoryRecord.warehouse_id == warehouse_id)
    buckets = (await session.execute(stmt)).all()

    recommendations: list[SafetyStockRecommendation] = []
    for product_jan, bucket_warehouse_id in buckets:
        rec = await calculate_safety_stock(
            session, product_jan, bucket_warehouse_id, lookback_days=lookback_days
        )
        if rec is None:
            continue
        if rec.current_quantity < rec.reorder_point:
            recommendations.append(rec)

    return recommendations
