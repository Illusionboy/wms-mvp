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


# ── 快照同步（ERP → WMS 镜像）───────────────────────────────────────────────
SNAPSHOT_SOURCE = "erp_mirror_sync"


async def sync_snapshot(
    session: AsyncSession, warehouse_id: int, *, dry_run: bool = True, user_id: int | None = None
) -> dict:
    """把秦丝某仓库的当前库存快照覆盖写进 WMS（仅限 ERP_MIRROR 仓库）。

    为什么用「快照覆盖」而不是「流水累加」：
    流水里已知存在重复风险（同一笔调库可能既手工录了 WMS、又同步了秦丝调拨单），
    累加会把这些误差永久滚进库存。快照每次都把数字拉回 ERP 口径，误差不累积。
    差额写一笔 ADJUST 留痕——不静默改数，事后能查出每次校正了多少。

    流水同步照常继续（安全库存/需求预测依赖它）：快照回答"现在有多少"，
    流水回答"卖得多快"，两者各司其职。
    """
    from app.models.warehouse import InventorySourceMode
    from app.scrapers.qinsi_scraper import fetch_stock_snapshot

    wh = await session.get(Warehouse, warehouse_id)
    if wh is None:
        return {"success": False, "error": "仓库不存在"}
    if wh.inventory_source_mode != InventorySourceMode.erp_mirror:
        return {"success": False,
                "error": f"仓库「{wh.name}」不是 ERP_MIRROR 模式，快照同步只对镜像仓库开放"}
    if not wh.qinsi_depot_id:
        return {"success": False, "error": f"仓库「{wh.name}」未关联秦丝仓库(qinsi_depot_id)"}

    snap = await fetch_stock_snapshot(int(wh.qinsi_depot_id))
    if not snap["success"]:
        return {"success": False, "error": snap["error"], "needs_relogin": snap.get("needs_relogin")}

    # 快照只含"有库存"的 SKU；WMS 有记录但快照里没有的，说明 ERP 侧已归零 → 目标即 0
    erp_qty = {it["jan_code"]: it["quantity"] for it in snap["items"]}

    # WMS 侧该仓库现有库存
    rows = (await session.execute(
        select(InventoryRecord.product_jan, func.sum(InventoryRecord.quantity))
        .where(InventoryRecord.warehouse_id == warehouse_id)
        .group_by(InventoryRecord.product_jan)
    )).all()
    wms_qty = {j: int(q or 0) for j, q in rows}

    # 只处理「ERP 有量」或「WMS 有记录」的 JAN——
    # 整个商品目录有 7000+ 个，两边都为 0 的没必要建记录
    jans = {j for j, q in erp_qty.items() if q != 0} | set(wms_qty)
    known = set((await session.scalars(
        select(Product.jan_code).where(Product.jan_code.in_(list(jans)))
    )).all()) if jans else set()

    changes, unknown = [], []
    for jan in sorted(jans):
        target = erp_qty.get(jan, 0)
        current = wms_qty.get(jan, 0)
        if target == current:
            continue
        if jan not in known:
            unknown.append({"jan_code": jan, "erp_qty": target,
                            "reason": "商品不在 WMS 目录，跳过（需先登记商品）"})
            continue
        changes.append({"jan_code": jan, "wms_qty": current,
                        "erp_qty": target, "delta": target - current})

    result = {
        "success": True, "dry_run": dry_run,
        "warehouse_id": warehouse_id, "warehouse_name": wh.name,
        "qinsi_depot_id": int(wh.qinsi_depot_id),
        "erp_sku_total": len(snap["items"]),
        "erp_sku_with_stock": sum(1 for q in erp_qty.values() if q != 0),
        "changes": changes, "change_count": len(changes),
        "delta_abs_total": sum(abs(c["delta"]) for c in changes),
        "unknown_products": unknown,
        "applied": 0,
    }
    if dry_run or not changes:
        return result

    # 实际写入：走 adjust_stock_item 保证每笔都有 StockTransaction
    from app.schemas.inventory import StockAdjustCreate
    from app.services.inventory import adjust_stock_item, stock_in_item
    from app.schemas.inventory import StockInCreate

    applied, errors = 0, []
    for ch in changes:
        try:
            if ch["wms_qty"] == 0 and not await session.scalar(
                select(InventoryRecord.id).where(
                    InventoryRecord.product_jan == ch["jan_code"],
                    InventoryRecord.warehouse_id == warehouse_id,
                ).limit(1)
            ):
                # 该仓库还没有这个 SKU 的桶 → 用入库建桶
                await stock_in_item(session, StockInCreate(
                    sku=ch["jan_code"], warehouse_id=warehouse_id, quantity=ch["erp_qty"],
                    location_code="A-00-00", source=SNAPSHOT_SOURCE,
                    note=f"ERP镜像快照建桶：秦丝 {ch['erp_qty']}",
                ), commit=False, user_id=user_id)
            else:
                await adjust_stock_item(session, StockAdjustCreate(
                    sku=ch["jan_code"], warehouse_id=warehouse_id,
                    actual_quantity=max(ch["erp_qty"], 0),
                    source=SNAPSHOT_SOURCE,
                    note=(f"ERP镜像快照校正：WMS {ch['wms_qty']} → 秦丝 {ch['erp_qty']}"
                          f"（{ch['delta']:+d}）"),
                ), commit=False, user_id=user_id)
            applied += 1
        except Exception as exc:  # noqa: BLE001
            errors.append({"jan_code": ch["jan_code"], "error": f"{type(exc).__name__}: {exc}"})

    await session.commit()
    result["applied"] = applied
    result["errors"] = errors
    return result
