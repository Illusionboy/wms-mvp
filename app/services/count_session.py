"""批量点数模块（数据通信功能）服务。

一个独立的"点数工作台"：扫码/手输/Excel 收集 (JAN, 数量)，产出通用结构供各模块复用，
并支持库存模拟、与托盘 QR 对账。**全程只读 WMS 库存，绝不写 StockTransaction / 改 InventoryRecord。**
"""
from __future__ import annotations

from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.count_session import CountSession
from app.models.customer_allocation import CustomerAllocation
from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.schemas.count_session import (
    CountItem,
    CountSessionRead,
    ImportedItem,
    ImportResult,
    PalletCheckResult,
    PalletCheckRow,
    SimulateResult,
    SimulateRow,
)
from app.services.customer_allocations import _parse_allocation_excel
from app.services.trade_containers import get_pallet_by_code


# ── 商品补全 ────────────────────────────────────────────────────────────────
async def _product_map(session: AsyncSession, jans: list[str]) -> dict[str, Product]:
    if not jans:
        return {}
    rows = (await session.scalars(select(Product).where(Product.jan_code.in_(jans)))).all()
    return {p.jan_code: p for p in rows}


# ── 会话 CRUD ───────────────────────────────────────────────────────────────
def _to_read(obj: CountSession) -> CountSessionRead:
    raw_items = (obj.document or {}).get("items", [])
    items = [CountItem.model_validate(it) for it in raw_items]
    return CountSessionRead(
        id=obj.id,
        name=obj.name,
        note=obj.note,
        status=obj.status,
        items=items,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


async def create_session(
    session: AsyncSession,
    *,
    name: str | None,
    note: str | None,
    items: list[CountItem],
    created_by: int | None,
) -> CountSessionRead:
    obj = CountSession(
        name=name,
        note=note,
        status="open",
        created_by=created_by,
        document={"items": [it.model_dump() for it in items]},
    )
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return _to_read(obj)


async def get_session(session: AsyncSession, session_id: int) -> CountSessionRead | None:
    obj = await session.get(CountSession, session_id)
    return _to_read(obj) if obj else None


async def list_open_sessions(session: AsyncSession, limit: int = 50) -> list[CountSessionRead]:
    rows = (await session.scalars(
        select(CountSession)
        .where(CountSession.status == "open")
        .order_by(CountSession.updated_at.desc())
        .limit(limit)
    )).all()
    return [_to_read(o) for o in rows]


async def update_session(
    session: AsyncSession,
    session_id: int,
    *,
    name: str | None,
    note: str | None,
    items: list[CountItem],
) -> CountSessionRead | None:
    obj = await session.scalar(
        select(CountSession).where(CountSession.id == session_id).with_for_update()
    )
    if obj is None:
        return None
    if name is not None:
        obj.name = name
    if note is not None:
        obj.note = note
    obj.document = {"items": [it.model_dump() for it in items]}
    await session.commit()
    await session.refresh(obj)
    return _to_read(obj)


async def delete_session(session: AsyncSession, session_id: int) -> bool:
    obj = await session.get(CountSession, session_id)
    if obj is None:
        return False
    await session.delete(obj)
    await session.commit()
    return True


# ── Excel 导入（sheet=客户/供应商，JAN+数量；逻辑与预留模块一致）───────────────
async def import_excel(session: AsyncSession, content: bytes) -> ImportResult:
    parsed = _parse_allocation_excel(content)  # [(customer, jan, qty), ...]
    # 同 JAN 跨 sheet 合并数量；客户名取首次出现（仅展示）
    merged: dict[str, int] = defaultdict(int)
    first_customer: dict[str, str] = {}
    for customer, jan, qty in parsed:
        merged[jan] += qty
        first_customer.setdefault(jan, customer)

    products = await _product_map(session, list(merged.keys()))
    items: list[ImportedItem] = []
    new_count = 0
    for jan, qty in merged.items():
        p = products.get(jan)
        is_new = p is None
        if is_new:
            new_count += 1
        items.append(ImportedItem(
            jan_code=jan,
            quantity=qty,
            name_zh=p.name_zh if p else None,
            units_per_case=p.units_per_case if p else None,
            is_new=is_new,
            customer_name=first_customer.get(jan),
        ))
    return ImportResult(items=items, new_count=new_count)


# ── 库存模拟（是否够货；可选除去已预留）──────────────────────────────────────
async def simulate_stock(
    session: AsyncSession,
    *,
    items: list[tuple[str, int]],
    warehouse_id: int,
    exclude_reserved: bool,
) -> SimulateResult:
    jans = [jan for jan, _ in items]
    products = await _product_map(session, jans)

    # 按 (jan) 聚合仓库内所有库存桶（历史多桶数据未合并时，避免只取到其中一桶）
    inv_rows = (await session.execute(
        select(InventoryRecord.product_jan, func.sum(InventoryRecord.quantity)).where(
            InventoryRecord.product_jan.in_(jans),
            InventoryRecord.warehouse_id == warehouse_id,
        ).group_by(InventoryRecord.product_jan)
    )).all()
    stock_map = {jan: int(qty or 0) for jan, qty in inv_rows}

    reserved_rows = (await session.execute(
        select(CustomerAllocation.jan_code, func.sum(CustomerAllocation.quantity))
        .where(
            CustomerAllocation.jan_code.in_(jans),
            CustomerAllocation.status == "reserved",
        )
        .group_by(CustomerAllocation.jan_code)
    )).all()
    reserved_map = {jan: int(total or 0) for jan, total in reserved_rows}

    rows: list[SimulateRow] = []
    for jan, need in items:
        p = products.get(jan)
        reserved = reserved_map.get(jan, 0)
        if p is None:
            rows.append(SimulateRow(
                jan_code=jan, name_zh=None, need=need,
                current_stock=None, reserved=reserved, available=None, status="unknown",
            ))
            continue
        if jan not in stock_map:
            rows.append(SimulateRow(
                jan_code=jan, name_zh=p.name_zh, need=need,
                current_stock=None, reserved=reserved, available=None, status="no_record",
            ))
            continue
        current = stock_map[jan]
        available = current - (reserved if exclude_reserved else 0)
        status = "ok" if available >= need else "insufficient"
        rows.append(SimulateRow(
            jan_code=jan, name_zh=p.name_zh, need=need,
            current_stock=current, reserved=reserved, available=available, status=status,
        ))
    return SimulateResult(rows=rows)


# ── 贸易检查：点数 vs 扫到的托盘 QR 内容 ────────────────────────────────────
async def check_against_pallets(
    session: AsyncSession,
    *,
    items: list[tuple[str, int]],
    pallet_codes: list[str],
) -> PalletCheckResult:
    counted: dict[str, int] = defaultdict(int)
    for jan, qty in items:
        counted[jan] += qty

    expected: dict[str, int] = defaultdict(int)
    unknown_codes: list[str] = []
    seen: set[str] = set()
    for raw in pallet_codes:
        code = raw.strip()
        if not code or code in seen:
            continue
        seen.add(code)
        pallet = await get_pallet_by_code(session, code)
        if pallet is None:
            unknown_codes.append(code)
            continue
        for it in pallet.items:
            expected[it.jan_code] += it.quantity

    all_jans = sorted(set(counted) | set(expected))
    products = await _product_map(session, all_jans)
    rows: list[PalletCheckRow] = []
    for jan in all_jans:
        c = counted.get(jan, 0)
        e = expected.get(jan, 0)
        p = products.get(jan)
        rows.append(PalletCheckRow(
            jan_code=jan,
            name_zh=p.name_zh if p else None,
            counted=c,
            expected=e,
            diff=c - e,
            match=(c == e),
        ))
    return PalletCheckResult(rows=rows, unknown_pallet_codes=unknown_codes)
