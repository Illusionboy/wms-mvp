"""秦丝调拨单（调库）同步到 WMS。

秦丝的调拨单 = WMS 的调库：一出一入。单号 DB 开头，与出库 XS / 入库 CG 完全不重叠，
所以接入同步不会和既有的出入库同步重复计数。

**防重复**：仓库两边都可能操作（WMS 手工调库 + 秦丝调库），同一笔调库若两边各做一次，
同步进来就会重复扣减。因此 preview 时逐单做「疑似重复」检测，命中的单在前端默认不勾选。
"""
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import Date, and_, cast, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_record import InventoryRecord
from app.models.stock_transaction import StockTransaction, StockTransactionType
from app.models.warehouse import Warehouse
from app.schemas.inventory import StockTransferCreate
from app.services.inventory import InventoryServiceError, transfer_stock_item

TRANSFER_SOURCE = "qinsi_transfer"
# 疑似重复的判定窗口：WMS 既有调库与秦丝单据日期相差几天内算同一笔
_DUP_WINDOW_DAYS = 3


def _ref(order_sn: str, jan: str) -> str:
    return f"qinsi_transfer:{order_sn}:{jan}"


def _effective_date():
    """业务日期优先，缺失回退到写入日期（与项目其它分析口径一致）。"""
    return func.coalesce(StockTransaction.transaction_date, cast(StockTransaction.created_at, Date))


async def _warehouse_ids(session: AsyncSession) -> dict[str, int]:
    rows = (await session.scalars(select(Warehouse))).all()
    return {w.name: w.id for w in rows}


async def _already_synced(session: AsyncSession, order_sn: str, jans: list[str]) -> set[str]:
    """该单里哪些 JAN 已经同步过（幂等）。"""
    if not jans:
        return set()
    refs = {_ref(order_sn, j): j for j in jans}
    found = (await session.scalars(
        select(StockTransaction.reference_id).where(
            StockTransaction.source == TRANSFER_SOURCE,
            StockTransaction.reference_id.in_(list(refs)),
        )
    )).all()
    return {refs[r] for r in set(found) if r in refs}


async def _looks_duplicated(
    session: AsyncSession, *, jan: str, qty: int, from_id: int, to_id: int, day: date
) -> bool:
    """WMS 里是否已有一笔「看起来就是这一笔」的调库（非本同步写入的）。

    判据：同 JAN、同数量、同调出仓的 OUT，且业务日期在 ±N 天内，
    并且同一个 reference_id 下有调入仓的 IN（即确实是一次调库而不是普通出库）。
    """
    lo, hi = day - timedelta(days=_DUP_WINDOW_DAYS), day + timedelta(days=_DUP_WINDOW_DAYS)
    eff = _effective_date()

    out_refs = (await session.scalars(
        select(StockTransaction.reference_id)
        .join(InventoryRecord, InventoryRecord.id == StockTransaction.inventory_record_id)
        .where(
            InventoryRecord.product_jan == jan,
            InventoryRecord.warehouse_id == from_id,
            StockTransaction.transaction_type == StockTransactionType.out,
            StockTransaction.quantity_change == -qty,
            StockTransaction.source != TRANSFER_SOURCE,   # 本同步写的不算"别处已记"
            StockTransaction.reference_id.isnot(None),
            and_(eff >= lo, eff <= hi),
        )
    )).all()
    if not out_refs:
        return False

    # 同一 reference_id 下要有调入仓的 IN，才能确认是一次调库
    hit = await session.scalar(
        select(StockTransaction.id)
        .join(InventoryRecord, InventoryRecord.id == StockTransaction.inventory_record_id)
        .where(
            InventoryRecord.product_jan == jan,
            InventoryRecord.warehouse_id == to_id,
            StockTransaction.transaction_type == StockTransactionType.in_,
            StockTransaction.quantity_change == qty,
            StockTransaction.reference_id.in_(list(set(out_refs))),
        )
        .limit(1)
    )
    return hit is not None


async def annotate_orders(session: AsyncSession, orders: list[dict]) -> list[dict]:
    """给 preview 的每张调拨单补上：仓库是否可映射、是否已同步、是否疑似重复。"""
    wh = await _warehouse_ids(session)
    result = []
    for o in orders:
        from_id, to_id = wh.get(o["out_warehouse"]), wh.get(o["in_warehouse"])
        jans = [i["jan_code"] for i in o["items"]]
        synced = await _already_synced(session, o["order_sn"], jans) if (from_id and to_id) else set()

        dup_jans: list[str] = []
        if from_id and to_id:
            day = date.fromisoformat(o["date"]) if o.get("date") else date.today()
            for it in o["items"]:
                if it["jan_code"] in synced:
                    continue
                if await _looks_duplicated(session, jan=it["jan_code"], qty=it["quantity"],
                                           from_id=from_id, to_id=to_id, day=day):
                    dup_jans.append(it["jan_code"])

        blocked = None
        if from_id is None:
            blocked = f"WMS 里没有仓库「{o['out_warehouse']}」（调出仓未映射）"
        elif to_id is None:
            blocked = f"WMS 里没有仓库「{o['in_warehouse']}」（调入仓未映射）"
        elif from_id == to_id:
            blocked = "调出仓与调入仓映射到了同一个 WMS 仓库"

        result.append({
            **o,
            "from_warehouse_id": from_id,
            "to_warehouse_id": to_id,
            "blocked": blocked,
            "already_synced": sorted(synced),
            "duplicate_jans": dup_jans,
            "suspected_duplicate": bool(dup_jans),
            "pending_lines": len([i for i in o["items"] if i["jan_code"] not in synced]),
        })
    return result


async def apply_transfers(
    session: AsyncSession, orders: list[dict], user_id: int | None = None
) -> dict:
    """把选中的调拨单写成 WMS 调库。幂等：reference_id = qinsi_transfer:{单号}:{JAN}。"""
    wh = await _warehouse_ids(session)
    applied, skipped, errors = [], [], []

    for o in orders:
        sn = o["order_sn"]
        from_id, to_id = wh.get(o["out_warehouse"]), wh.get(o["in_warehouse"])
        if not from_id or not to_id or from_id == to_id:
            errors.append({"order_sn": sn, "error": "仓库映射无效，已跳过整单"})
            continue

        jans = [i["jan_code"] for i in o["items"]]
        synced = await _already_synced(session, sn, jans)
        day = date.fromisoformat(o["date"]) if o.get("date") else None
        n_ok = 0
        for it in o["items"]:
            jan, qty = it["jan_code"], int(it["quantity"])
            if jan in synced:
                skipped.append({"order_sn": sn, "jan_code": jan, "reason": "已同步过"})
                continue
            try:
                await transfer_stock_item(
                    session,
                    StockTransferCreate(
                        sku=jan, from_warehouse_id=from_id, to_warehouse_id=to_id,
                        quantity=qty, transaction_date=day,
                        note=f"秦丝调拨单 {sn}：{o['out_warehouse']} → {o['in_warehouse']}",
                    ),
                    user_id=user_id,
                    source=TRANSFER_SOURCE,
                    reference_id=_ref(sn, jan),
                    commit=False,
                )
                n_ok += 1
            except InventoryServiceError as exc:
                errors.append({"order_sn": sn, "jan_code": jan, "error": str(exc)})
            except Exception as exc:  # noqa: BLE001
                errors.append({"order_sn": sn, "jan_code": jan, "error": f"{type(exc).__name__}: {exc}"})
        if n_ok:
            applied.append({"order_sn": sn, "lines": n_ok,
                            "route": f"{o['out_warehouse']} → {o['in_warehouse']}"})

    await session.commit()
    return {"applied": applied, "skipped": skipped, "errors": errors,
            "applied_orders": len(applied),
            "applied_lines": sum(a["lines"] for a in applied)}
