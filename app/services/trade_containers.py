"""贸易集装箱模块服务（P1：托盘 CRUD、加货、库位绑定、候选/客户查询）。

设计基准（详见 贸易集装箱模块_实施指南.md）：
- 托盘 `customer_name`/`planned_outbound_date` 与 `CustomerAllocation` 同值同格式，用于对账。
- 加货候选 = 该 (客户, 日期) 的 reserved + waiting 并集（WMS 滞后实物，两者都可装）。
- 本模块**只改托盘自身数据，绝不改动库存或预留状态**（出库/快照属 P2）。
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.pallet import Pallet, PalletItem
from app.models.product import Product
from app.schemas.trade_container import (
    DailyCustomerRead,
    NextSerialRead,
    PalletCandidateRead,
    PalletItemRead,
    PalletPlaceResult,
    PalletRead,
)
from app.services.customer_allocations import (
    get_allocation_status,
    get_daily_allocation_overview,
)
from app.services.product_alias import resolve_canonical_jan

_LOADABLE_STATUSES = ("reserved", "waiting")


# ── 读 ──────────────────────────────────────────────────────────────────────
async def _product_names(session: AsyncSession, jans: list[str]) -> dict[str, str]:
    if not jans:
        return {}
    rows = (await session.scalars(select(Product).where(Product.jan_code.in_(jans)))).all()
    return {p.jan_code: p.name_jp for p in rows}


async def _to_read(session: AsyncSession, pallet: Pallet) -> PalletRead:
    names = await _product_names(session, [it.jan_code for it in pallet.items])
    items = [
        PalletItemRead(jan_code=it.jan_code, quantity=it.quantity, product_name=names.get(it.jan_code))
        for it in sorted(pallet.items, key=lambda i: i.jan_code)
    ]
    return PalletRead(
        id=pallet.id,
        code=pallet.code,
        shelf_location=pallet.shelf_location,
        customer_name=pallet.customer_name,
        planned_outbound_date=pallet.planned_outbound_date,
        status=pallet.status,
        note=pallet.note,
        items=items,
        created_at=pallet.created_at,
        updated_at=pallet.updated_at,
    )


async def _load_pallet(session: AsyncSession, pallet_id: int, *, for_update: bool = False) -> Pallet | None:
    stmt = select(Pallet).where(Pallet.id == pallet_id)
    if for_update:
        # 行锁不能带 selectinload 的 outer join，单独锁行后再取 items
        pallet = await session.scalar(stmt.with_for_update())
        if pallet is not None:
            await session.refresh(pallet, attribute_names=["items"])
        return pallet
    return await session.scalar(stmt.options(selectinload(Pallet.items)))


async def get_pallet(session: AsyncSession, pallet_id: int) -> PalletRead | None:
    pallet = await _load_pallet(session, pallet_id)
    return await _to_read(session, pallet) if pallet else None


async def get_pallet_by_code(session: AsyncSession, code: str) -> PalletRead | None:
    pallet = await session.scalar(
        select(Pallet).where(Pallet.code == code.strip()).options(selectinload(Pallet.items))
    )
    return await _to_read(session, pallet) if pallet else None


async def list_pallets(
    session: AsyncSession,
    *,
    customer_name: str | None = None,
    planned_outbound_date: date | None = None,
    status: str | None = None,
    code: str | None = None,
    shelf_location: str | None = None,
    unlocated: bool = False,
) -> list[PalletRead]:
    stmt = select(Pallet).options(selectinload(Pallet.items))
    if customer_name:
        stmt = stmt.where(Pallet.customer_name == customer_name)
    if planned_outbound_date:
        stmt = stmt.where(Pallet.planned_outbound_date == planned_outbound_date)
    if status:
        stmt = stmt.where(Pallet.status == status)
    if code:
        stmt = stmt.where(Pallet.code.ilike(f"%{code.strip()}%"))
    if shelf_location:  # 扫库位查内容：1:1 下正常返回该库位上的那一个托盘
        stmt = stmt.where(Pallet.shelf_location == shelf_location.strip())
    if unlocated:  # 无库位（临时放地面区）的托盘
        stmt = stmt.where(Pallet.shelf_location.is_(None))
    stmt = stmt.order_by(Pallet.updated_at.desc())
    pallets = (await session.scalars(stmt)).all()
    return [await _to_read(session, p) for p in pallets]


async def next_pallet_serial(session: AsyncSession, prefix: str = "PLT", width: int = 4) -> NextSerialRead:
    """托盘标签生成：返回下一个可用序号（现有 prefix-#### 最大序号 +1），防重号。"""
    prefix = prefix.strip() or "PLT"
    like = f"{prefix}-%"
    codes = (await session.scalars(select(Pallet.code).where(Pallet.code.like(like)))).all()
    plen = len(prefix) + 1
    mx = 0
    for c in codes:
        suf = c[plen:]
        if suf.isdigit():
            mx = max(mx, int(suf))
    nxt = mx + 1
    return NextSerialRead(prefix=prefix, width=width, next_serial=nxt, next_code=f"{prefix}-{nxt:0{width}d}")


async def list_daily_customers(session: AsyncSession, planned_outbound_date: date) -> list[DailyCustomerRead]:
    """某计划出库日期下有预留的客户（建空托盘时只能从这里选，不能手输）。"""
    overview = await get_daily_allocation_overview(session, planned_outbound_date)
    return [
        DailyCustomerRead(
            customer_name=c.customer_name,
            reserved_count=c.ready_count,
            waiting_count=c.waiting_count,
        )
        for c in overview
        if (c.ready_count + c.waiting_count) > 0
    ]


async def get_pallet_candidates(session: AsyncSession, pallet_id: int) -> list[PalletCandidateRead]:
    """加货候选 = 托盘绑定 (客户,日期) 的 reserved + waiting 并集，附已在此托盘上的数量。"""
    pallet = await _load_pallet(session, pallet_id)
    if pallet is None:
        raise ValueError("托盘不存在")
    if not pallet.customer_name or not pallet.planned_outbound_date:
        return []
    allocs = await get_allocation_status(
        session,
        customer_name=pallet.customer_name,
        planned_outbound_date=pallet.planned_outbound_date,
    )
    on_pallet = {it.jan_code: it.quantity for it in pallet.items}
    out: list[PalletCandidateRead] = []
    for a in allocs:
        # 精确客户过滤（get_allocation_status 用模糊匹配，可能带回近似客户）
        if a.customer_name != pallet.customer_name or a.status not in _LOADABLE_STATUSES:
            continue
        out.append(PalletCandidateRead(
            jan_code=a.jan_code,
            product_name=a.product_name,
            reserved_quantity=a.quantity,
            status=a.status,
            current_stock=a.current_stock,
            on_pallet_quantity=on_pallet.get(a.jan_code, 0),
        ))
    return out


# ── 写 ──────────────────────────────────────────────────────────────────────
async def create_empty_pallet(
    session: AsyncSession,
    *,
    code: str,
    planned_outbound_date: date,
    customer_name: str,
) -> PalletRead:
    """建空托盘：绑定客户+日期。客户必须来自当天预留客户列表（只能选，不能手输）。

    - 托盘码不存在 → 新建
    - 已存在且为空 → 复用并重新绑定客户/日期
    - 已存在且有货 → 拒绝（避免覆盖在用托盘）
    """
    code = code.strip()
    daily = await list_daily_customers(session, planned_outbound_date)
    if customer_name not in {c.customer_name for c in daily}:
        raise ValueError(f"{planned_outbound_date} 的预留中没有客户「{customer_name}」，只能从预留客户中选择")

    pallet = await session.scalar(select(Pallet).where(Pallet.code == code).with_for_update())
    if pallet is None:
        pallet = Pallet(
            code=code,
            customer_name=customer_name,
            planned_outbound_date=planned_outbound_date,
            status="staging",
        )
        session.add(pallet)
    else:
        await session.refresh(pallet, attribute_names=["items"])
        if pallet.items:
            raise ValueError(f"托盘「{code}」非空（已有 {len(pallet.items)} 种货），请先清空或换一个托盘")
        pallet.customer_name = customer_name
        pallet.planned_outbound_date = planned_outbound_date
        pallet.status = "staging"

    await session.commit()
    reloaded = await get_pallet_by_code(session, code)
    assert reloaded is not None
    return reloaded


async def add_items_to_pallet(
    session: AsyncSession,
    pallet_id: int,
    items: list[tuple[str, int]],
) -> PalletRead:
    """加货：往托盘累加货物（同 JAN 累加）。别名 JAN 归并到主 JAN。只改托盘，不动库存/预留。"""
    pallet = await _load_pallet(session, pallet_id, for_update=True)
    if pallet is None:
        raise ValueError("托盘不存在")
    if pallet.status == "loaded":
        raise ValueError("托盘已装柜，不能再加货")

    existing = {it.jan_code: it for it in pallet.items}
    for raw_jan, qty in items:
        if qty <= 0:
            continue
        jan = await resolve_canonical_jan(session, raw_jan.strip())
        if jan in existing:
            existing[jan].quantity += qty
        else:
            row = PalletItem(jan_code=jan, quantity=qty)
            pallet.items.append(row)  # 走关系集合，提交后内存集合与库一致（响应不漏货）
            existing[jan] = row
    if pallet.status == "empty":
        pallet.status = "staging"

    await session.commit()
    return await _to_read(session, pallet)


async def set_pallet_item_quantity(
    session: AsyncSession,
    pallet_id: int,
    jan_code: str,
    quantity: int,
) -> PalletRead:
    """设定某 JAN 在托盘上的绝对数量（纠错用）；quantity=0 则从托盘移除该 JAN。"""
    pallet = await _load_pallet(session, pallet_id, for_update=True)
    if pallet is None:
        raise ValueError("托盘不存在")
    if pallet.status == "loaded":
        raise ValueError("托盘已装柜，不能修改内容")
    jan = await resolve_canonical_jan(session, jan_code.strip())
    row = next((it for it in pallet.items if it.jan_code == jan), None)
    if quantity <= 0:
        if row is not None:
            pallet.items.remove(row)  # delete-orphan 级联删除该行
    elif row is not None:
        row.quantity = quantity
    else:
        pallet.items.append(PalletItem(jan_code=jan, quantity=quantity))

    await session.commit()
    return await _to_read(session, pallet)


async def place_pallet_at_location(
    session: AsyncSession,
    *,
    pallet_code: str,
    location_code: str,
) -> PalletPlaceResult:
    """库位绑定（库位↔托盘 1:1）：把托盘放到该库位；原占用该库位的其它托盘自动解绑。"""
    code = pallet_code.strip()
    loc = location_code.strip()
    pallet = await session.scalar(select(Pallet).where(Pallet.code == code).with_for_update())
    if pallet is None:
        raise ValueError(f"托盘「{code}」不存在，请先建托盘")
    # 1:1 —— 清掉原来占用该库位的其它托盘（新映射建立、旧映射自动断开）
    displaced_code: str | None = None
    others = (await session.scalars(
        select(Pallet).where(Pallet.shelf_location == loc, Pallet.code != code).with_for_update()
    )).all()
    for other in others:
        displaced_code = other.code  # 1:1 正常只有一个
        other.shelf_location = None
    pallet.shelf_location = loc
    await session.commit()
    placed = await get_pallet_by_code(session, code)
    assert placed is not None
    return PalletPlaceResult(pallet=placed, displaced_pallet_code=displaced_code)
