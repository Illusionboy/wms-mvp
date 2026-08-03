"""装柜出库：装柜前/后对账 + 上柜扫描（托盘/散货）+ 装柜完成出库。

对账口径：需求=客户预留(waiting/reserved) 按 JAN 汇总；
  装柜前 = 绑定到(客户,日期)的托盘内容汇总；装柜后 = 本次实际扫上柜的托盘 + 散货。
装柜完成 = 按【实际上柜量】写 OUT 出库到 WMS 库存 + 预留标记 shipped + 上柜托盘清零&标签重置。
散货无托盘，不涉及标签。多装只在对账里预警，不封顶。
"""
from __future__ import annotations

import json
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.container_load_draft import ContainerLoadDraft
from app.models.customer_allocation import CustomerAllocation
from app.models.pallet import Pallet
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.schemas.inventory import StockOutCreate
from app.services.customer_allocations import ALLOCATION_WAREHOUSE_NAME
from app.services.inventory import stock_out_item

LOAD_SOURCE = "container_load"


async def list_pending_customers(session: AsyncSession) -> list[dict]:
    """所有当前还有未出预留(waiting/reserved)的 (客户,计划出库日期)，按日期升序。

    实际装柜常常提前一天(甚至更早)开始，操作员未必记得准确的「计划出库日期」——
    装柜出库页不再要求先猜日期，而是从这里选客户，日期自动带出。
    完成装柜后该客户预留变 shipped，会自动从本列表消失。
    """
    rows = (await session.execute(
        select(
            CustomerAllocation.customer_name,
            CustomerAllocation.planned_outbound_date,
            func.sum(CustomerAllocation.quantity),
            func.count(func.distinct(CustomerAllocation.jan_code)),
        )
        .where(CustomerAllocation.status.in_(("waiting", "reserved")))
        .group_by(CustomerAllocation.customer_name, CustomerAllocation.planned_outbound_date)
        .order_by(CustomerAllocation.planned_outbound_date, CustomerAllocation.customer_name)
    )).all()
    return [
        {
            "customer": c,
            "planned_date": d.isoformat(),
            "need_total": int(q or 0),
            "sku_count": int(n or 0),
        }
        for c, d, q, n in rows
    ]


async def _get_or_create_draft(
    session: AsyncSession, customer: str, planned_date: date, *, create: bool = True
) -> ContainerLoadDraft | None:
    d = await session.scalar(
        select(ContainerLoadDraft).where(
            ContainerLoadDraft.customer_name == customer,
            ContainerLoadDraft.planned_date == planned_date,
            ContainerLoadDraft.status == "loading",
        )
    )
    if d is None and create:
        d = ContainerLoadDraft(customer_name=customer, planned_date=planned_date,
                               status="loading", pallet_codes="[]", loose_items="[]")
        session.add(d)
        await session.flush()
    return d


async def _needs(session: AsyncSession, customer: str, planned_date: date) -> dict[str, int]:
    rows = await session.execute(
        select(CustomerAllocation.jan_code, func.sum(CustomerAllocation.quantity))
        .where(
            CustomerAllocation.customer_name == customer,
            CustomerAllocation.planned_outbound_date == planned_date,
            CustomerAllocation.status.in_(("waiting", "reserved")),
        )
        .group_by(CustomerAllocation.jan_code)
    )
    return {j: int(q or 0) for j, q in rows.all()}


async def _bound_pallet_items(session: AsyncSession, customer: str, planned_date: date) -> dict[str, int]:
    pallets = (await session.execute(
        select(Pallet).where(
            Pallet.customer_name == customer,
            Pallet.planned_outbound_date == planned_date,
        ).options(selectinload(Pallet.items))
    )).scalars().all()
    agg: dict[str, int] = {}
    for p in pallets:
        for it in p.items:
            agg[it.jan_code] = agg.get(it.jan_code, 0) + it.quantity
    return agg


async def _pallets_by_codes(session: AsyncSession, codes: list[str]) -> list[Pallet]:
    if not codes:
        return []
    return list((await session.execute(
        select(Pallet).where(Pallet.code.in_(codes)).options(selectinload(Pallet.items))
    )).scalars().all())


async def _loaded(session: AsyncSession, draft: ContainerLoadDraft):
    codes = json.loads(draft.pallet_codes or "[]")
    loose = json.loads(draft.loose_items or "[]")
    pallets = await _pallets_by_codes(session, codes)
    by_code = {p.code: p for p in pallets}
    agg: dict[str, int] = {}
    pallet_detail = []
    for code in codes:  # 保留扫描顺序，缺失的托盘也列出来
        p = by_code.get(code)
        if p is None:
            pallet_detail.append({"code": code, "missing": True, "items": []})
            continue
        items = [{"jan": it.jan_code, "qty": it.quantity} for it in p.items]
        for it in p.items:
            agg[it.jan_code] = agg.get(it.jan_code, 0) + it.quantity
        pallet_detail.append({"code": code, "missing": False, "items": items})
    for l in loose:
        agg[l["jan"]] = agg.get(l["jan"], 0) + int(l["qty"])
    return agg, pallet_detail, loose


async def _name_map(session: AsyncSession, jans) -> dict[str, str | None]:
    jans = list(jans)
    if not jans:
        return {}
    rows = (await session.execute(select(Product).where(Product.jan_code.in_(jans)))).scalars().all()
    return {p.jan_code: (p.name_zh or p.name_jp) for p in rows}


def _compare(needs: dict[str, int], have: dict[str, int], names: dict) -> list[dict]:
    out = []
    for j in set(needs) | set(have):
        n, h = needs.get(j, 0), have.get(j, 0)
        st = "ok" if h == n else ("over" if h > n else "short")
        out.append({"jan": j, "name": names.get(j), "need": n, "have": h, "diff": h - n, "status": st})
    # 有问题的(多装/少装)排前，其次按JAN
    out.sort(key=lambda r: (r["status"] == "ok", r["jan"]))
    return out


async def build_state(session: AsyncSession, customer: str, planned_date: date) -> dict:
    draft = await _get_or_create_draft(session, customer, planned_date)
    needs = await _needs(session, customer, planned_date)
    bound = await _bound_pallet_items(session, customer, planned_date)
    loaded, pallet_detail, loose = await _loaded(session, draft)
    names = await _name_map(session, set(needs) | set(bound) | set(loaded))
    after = _compare(needs, loaded, names)
    return {
        "customer": customer,
        "planned_date": planned_date.isoformat(),
        "pre_check": _compare(needs, bound, names),
        "loaded_pallets": pallet_detail,
        "loose_items": [{"jan": l["jan"], "qty": int(l["qty"]), "name": names.get(l["jan"])} for l in loose],
        "after_check": after,
        "over": [r for r in after if r["status"] == "over"],
        "short": [r for r in after if r["status"] == "short"],
        "loaded_total": sum(loaded.values()),
    }


async def scan_pallet(session: AsyncSession, customer: str, planned_date: date, code: str) -> dict:
    code = (code or "").strip()
    draft = await _get_or_create_draft(session, customer, planned_date)
    pallet = await session.scalar(select(Pallet).where(Pallet.code == code).options(selectinload(Pallet.items)))
    warn = None
    if pallet is None:
        warn = f"托盘 {code} 不存在"
    else:
        if pallet.customer_name and pallet.customer_name != customer:
            warn = f"注意：托盘 {code} 绑定的是客户「{pallet.customer_name}」，不是当前客户"
        codes = json.loads(draft.pallet_codes or "[]")
        if code not in codes:
            codes.append(code)
            draft.pallet_codes = json.dumps(codes, ensure_ascii=False)
            await session.commit()
        else:
            warn = f"托盘 {code} 已在上柜列表里（未重复添加）"
    state = await build_state(session, customer, planned_date)
    state["warn"] = warn
    return state


async def add_loose(session: AsyncSession, customer: str, planned_date: date, jan: str, qty: int) -> dict:
    jan = "".join(c for c in str(jan) if c.isdigit())
    draft = await _get_or_create_draft(session, customer, planned_date)
    loose = json.loads(draft.loose_items or "[]")
    for l in loose:
        if l["jan"] == jan:
            l["qty"] = int(l["qty"]) + int(qty)
            break
    else:
        loose.append({"jan": jan, "qty": int(qty)})
    draft.loose_items = json.dumps(loose, ensure_ascii=False)
    await session.commit()
    return await build_state(session, customer, planned_date)


async def remove_pallet(session: AsyncSession, customer: str, planned_date: date, code: str) -> dict:
    draft = await _get_or_create_draft(session, customer, planned_date)
    codes = [c for c in json.loads(draft.pallet_codes or "[]") if c != code]
    draft.pallet_codes = json.dumps(codes, ensure_ascii=False)
    await session.commit()
    return await build_state(session, customer, planned_date)


async def remove_loose(session: AsyncSession, customer: str, planned_date: date, jan: str) -> dict:
    draft = await _get_or_create_draft(session, customer, planned_date)
    loose = [l for l in json.loads(draft.loose_items or "[]") if l["jan"] != jan]
    draft.loose_items = json.dumps(loose, ensure_ascii=False)
    await session.commit()
    return await build_state(session, customer, planned_date)


async def complete_loading(session: AsyncSession, customer: str, planned_date: date, user_id: int | None) -> dict:
    """装柜完成：按实际上柜量出库 + 预留标记 shipped + 上柜托盘清零&标签重置。"""
    draft = await _get_or_create_draft(session, customer, planned_date, create=False)
    if draft is None:
        raise ValueError("没有进行中的装柜")
    loaded, pallet_detail, loose = await _loaded(session, draft)
    if not loaded:
        raise ValueError("还没有扫任何货上柜")
    wh = await session.scalar(select(Warehouse).where(Warehouse.name == ALLOCATION_WAREHOUSE_NAME))
    if wh is None:
        raise ValueError(f"找不到仓库「{ALLOCATION_WAREHOUSE_NAME}」")

    applied = []
    for jan, qty in loaded.items():
        await stock_out_item(
            session=session,
            payload=StockOutCreate(
                sku=jan, warehouse_id=wh.id, quantity=qty, source=LOAD_SOURCE,
                customer=customer, transaction_date=planned_date,
                reference_id=f"container:{draft.id}:{jan}",
                note=f"装柜出库 {customer} {planned_date.isoformat()}",
            ),
            commit=False, user_id=user_id, force_negative=True,
        )
        applied.append({"jan": jan, "qty": qty})

    allocs = (await session.execute(select(CustomerAllocation).where(
        CustomerAllocation.customer_name == customer,
        CustomerAllocation.planned_outbound_date == planned_date,
        CustomerAllocation.status.in_(("waiting", "reserved")),
    ))).scalars().all()
    for a in allocs:
        a.status = "shipped"

    codes = json.loads(draft.pallet_codes or "[]")
    pallets = await _pallets_by_codes(session, codes)
    for p in pallets:
        for it in list(p.items):
            await session.delete(it)
        p.status = "empty"
        p.customer_name = None
        p.planned_outbound_date = None
        p.shelf_location = None

    draft.status = "applied"
    await session.commit()
    return {
        "applied": applied,
        "out_lines": len(applied),
        "allocations_shipped": len(allocs),
        "pallets_reset": [p.code for p in pallets],
    }
