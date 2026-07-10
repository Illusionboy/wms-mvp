"""贸易集装箱模块端点（P1）。查询只读免认证；变动加 require_auth。"""
from datetime import date
from typing import NoReturn

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_auth
from app.db.session import get_db_session
from app.schemas.trade_container import (
    DailyCustomerRead,
    NextSerialRead,
    PalletAddItems,
    PalletCandidateRead,
    PalletCreate,
    PalletItemSetQuantity,
    PalletPlaceLocation,
    PalletPlaceResult,
    PalletRead,
)
from app.services import trade_containers as svc

router = APIRouter()


def _raise(exc: ValueError) -> NoReturn:
    msg = str(exc)
    code = 404 if "不存在" in msg else 409 if "非空" in msg else 422
    raise HTTPException(status_code=code, detail=msg)


# ── 只读查询 ────────────────────────────────────────────────────────────────
@router.get("/customers", response_model=list[DailyCustomerRead])
async def daily_customers(
    planned_outbound_date: date,
    session: AsyncSession = Depends(get_db_session),
) -> list[DailyCustomerRead]:
    """某计划出库日期下有预留的客户（建空托盘时只能从此列表选）。"""
    return await svc.list_daily_customers(session, planned_outbound_date)


@router.get("/pallets", response_model=list[PalletRead])
async def list_pallets(
    customer_name: str | None = None,
    planned_outbound_date: date | None = None,
    status: str | None = None,
    code: str | None = None,
    shelf_location: str | None = None,
    unlocated: bool = False,
    session: AsyncSession = Depends(get_db_session),
) -> list[PalletRead]:
    return await svc.list_pallets(
        session,
        customer_name=customer_name,
        planned_outbound_date=planned_outbound_date,
        status=status,
        code=code,
        shelf_location=shelf_location,
        unlocated=unlocated,
    )


@router.get("/pallets/next-serial", response_model=NextSerialRead)
async def next_serial(
    prefix: str = "PLT",
    width: int = 4,
    session: AsyncSession = Depends(get_db_session),
) -> NextSerialRead:
    """托盘标签生成：下一个可用序号（防重号）。"""
    return await svc.next_pallet_serial(session, prefix=prefix, width=width)


@router.get("/pallets/by-code/{code}", response_model=PalletRead)
async def get_pallet_by_code(
    code: str,
    session: AsyncSession = Depends(get_db_session),
) -> PalletRead:
    pallet = await svc.get_pallet_by_code(session, code)
    if pallet is None:
        raise HTTPException(status_code=404, detail=f"托盘「{code}」不存在")
    return pallet


@router.get("/pallets/{pallet_id}", response_model=PalletRead)
async def get_pallet(
    pallet_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> PalletRead:
    pallet = await svc.get_pallet(session, pallet_id)
    if pallet is None:
        raise HTTPException(status_code=404, detail="托盘不存在")
    return pallet


@router.get("/pallets/{pallet_id}/candidates", response_model=list[PalletCandidateRead])
async def pallet_candidates(
    pallet_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> list[PalletCandidateRead]:
    """加货候选 = 托盘绑定 (客户,日期) 的 reserved + waiting 并集。"""
    try:
        return await svc.get_pallet_candidates(session, pallet_id)
    except ValueError as exc:
        _raise(exc)


# ── 变动（需认证）───────────────────────────────────────────────────────────
@router.post("/pallets", response_model=PalletRead, dependencies=[Depends(require_auth)])
async def create_pallet(
    payload: PalletCreate,
    session: AsyncSession = Depends(get_db_session),
) -> PalletRead:
    try:
        return await svc.create_empty_pallet(
            session,
            code=payload.code,
            planned_outbound_date=payload.planned_outbound_date,
            customer_name=payload.customer_name,
        )
    except ValueError as exc:
        _raise(exc)


@router.post("/pallets/place", response_model=PalletPlaceResult, dependencies=[Depends(require_auth)])
async def place_pallet(
    payload: PalletPlaceLocation,
    session: AsyncSession = Depends(get_db_session),
) -> PalletPlaceResult:
    """库位绑定：扫托盘码 + 扫库位码 → 放置到该库位（1:1，原占用者自动解绑）。"""
    try:
        return await svc.place_pallet_at_location(
            session, pallet_code=payload.pallet_code, location_code=payload.location_code
        )
    except ValueError as exc:
        _raise(exc)


@router.post("/pallets/{pallet_id}/items", response_model=PalletRead, dependencies=[Depends(require_auth)])
async def add_items(
    pallet_id: int,
    payload: PalletAddItems,
    session: AsyncSession = Depends(get_db_session),
) -> PalletRead:
    try:
        return await svc.add_items_to_pallet(
            session, pallet_id, [(it.jan_code, it.quantity) for it in payload.items]
        )
    except ValueError as exc:
        _raise(exc)


@router.patch(
    "/pallets/{pallet_id}/items/{jan_code}",
    response_model=PalletRead,
    dependencies=[Depends(require_auth)],
)
async def set_item_quantity(
    pallet_id: int,
    jan_code: str,
    payload: PalletItemSetQuantity,
    session: AsyncSession = Depends(get_db_session),
) -> PalletRead:
    """设定某 JAN 在托盘上的绝对数量；quantity=0 移除该行。"""
    try:
        return await svc.set_pallet_item_quantity(session, pallet_id, jan_code, payload.quantity)
    except ValueError as exc:
        _raise(exc)
