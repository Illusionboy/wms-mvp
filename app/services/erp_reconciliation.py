"""ERP 镜像仓库的库存对账（reconciliation）。

镜像仓库（`inventory_source_mode = ERP_MIRROR`）里，同一个 SKU 有两个独立来源的数字：

1. **ERP 快照** —— 秦丝侧当前库存，直接覆盖写进 `inventory_records.quantity`
2. **WMS 流水推导** —— 把 `stock_transactions.quantity_change` 按 SKU 累加

两者理论上应当一致。不一致只有两种可能，而且都值得立刻知道：

- 有流水没同步进来（秦丝发生了出入库，WMS 这边漏了）→ 分析层的消耗速度会算错
- 有流水重复进来（例如同一笔调库既手工录了 WMS、又同步了秦丝调拨单）→ 库存与销量都会虚高

**为什么这件事值得单独建一层**：库存数字本身可以靠快照覆盖"治标"，但流水的完整性治不了——
而安全库存、需求预测全部依赖流水（快照只能回答"现在有多少"，回答不了"卖得多快"）。
差异监控让系统自己监控自己的数据质量，把上面两类问题从"悄悄烂在数据里"变成"看得见的指标"。

这也是物流/供应链分析岗位的核心日常能力：inventory reconciliation。
"""
from __future__ import annotations

from sqlalchemy import Date, Integer, cast, func, literal, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.models.stock_transaction import StockTransaction
from app.models.warehouse import InventorySourceMode, Warehouse

# 调库是仓库之间的内部搬运，不是对外消耗。算"卖得多快"时必须排除，
# 否则一次大额调库会被当成一次大额销售，把安全库存和预测整体抬高。
INTERNAL_MOVE_SOURCES = ("qinsi_transfer",)
# 快照覆盖写的那笔校正本身也不是业务流水
SNAPSHOT_SOURCES = ("erp_mirror_sync",)


async def list_mirror_warehouses(session: AsyncSession) -> list[Warehouse]:
    return list((await session.scalars(
        select(Warehouse).where(Warehouse.inventory_source_mode == InventorySourceMode.erp_mirror)
    )).all())


async def reconcile(
    session: AsyncSession,
    warehouse_id: int | None = None,
    *,
    only_diff: bool = True,
    limit: int = 500,
) -> list[dict]:
    """逐 SKU 比对「ERP 快照库存」与「WMS 流水累计」。

    `inventory_records.quantity` 是被快照覆盖过的值（= ERP 口径）；
    `SUM(stock_transactions.quantity_change)` 是流水累计（= WMS 口径）。
    两者相减即为差异。
    """
    derived = (
        select(
            StockTransaction.inventory_record_id.label("rec_id"),
            func.coalesce(func.sum(StockTransaction.quantity_change), 0).label("derived_qty"),
            func.max(func.coalesce(StockTransaction.transaction_date,
                                   cast(StockTransaction.created_at, Date))).label("last_txn_date"),
        )
        .group_by(StockTransaction.inventory_record_id)
        .subquery()
    )

    diff_expr = (InventoryRecord.quantity - func.coalesce(derived.c.derived_qty, 0))
    stmt = (
        select(
            Warehouse.id.label("warehouse_id"),
            Warehouse.name.label("warehouse_name"),
            InventoryRecord.product_jan,
            Product.name_jp,
            InventoryRecord.quantity.label("erp_snapshot_qty"),
            func.coalesce(derived.c.derived_qty, 0).label("wms_derived_qty"),
            diff_expr.label("diff"),
            derived.c.last_txn_date,
        )
        .select_from(InventoryRecord)
        .join(Warehouse, Warehouse.id == InventoryRecord.warehouse_id)
        .outerjoin(Product, Product.jan_code == InventoryRecord.product_jan)
        .outerjoin(derived, derived.c.rec_id == InventoryRecord.id)
        .where(Warehouse.inventory_source_mode == InventorySourceMode.erp_mirror)
        .order_by(func.abs(cast(diff_expr, Integer)).desc())
        .limit(limit)
    )
    if warehouse_id is not None:
        stmt = stmt.where(Warehouse.id == warehouse_id)
    if only_diff:
        stmt = stmt.where(diff_expr != 0)

    rows = (await session.execute(stmt)).all()
    return [
        {
            "warehouse_id": r.warehouse_id,
            "warehouse_name": r.warehouse_name,
            "product_jan": r.product_jan,
            "product_name_jp": r.name_jp,
            "erp_snapshot_qty": int(r.erp_snapshot_qty or 0),
            "wms_derived_qty": int(r.wms_derived_qty or 0),
            "diff": int(r.diff or 0),
            "last_txn_date": r.last_txn_date.isoformat() if r.last_txn_date else None,
        }
        for r in rows
    ]


async def diff_summary(session: AsyncSession) -> dict:
    """仪表盘用的汇总：有多少个 SKU 对不上、差多少件。"""
    rows = await reconcile(session, only_diff=True, limit=100000)
    mirrors = await list_mirror_warehouses(session)
    return {
        "mirror_warehouses": [{"id": w.id, "name": w.name} for w in mirrors],
        "diff_sku_count": len(rows),
        "diff_total_abs": sum(abs(r["diff"]) for r in rows),
        "worst": rows[:5],
    }
