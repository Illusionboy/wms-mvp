"""装柜出库端点：装柜前/后对账、上柜扫描(托盘/散货)、装柜完成出库。

- GET  /containers/loading?customer=&date=   当前装柜状态(两次对账 + 已上柜快照)
- POST /containers/loading/scan-pallet        扫托盘上柜
- POST /containers/loading/loose              加散货
- POST /containers/loading/remove-pallet      移除已上柜托盘
- POST /containers/loading/remove-loose       移除散货
- POST /containers/loading/complete           装柜完成→出库+预留标记+托盘清零&标签重置
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_db_session
from app.services import container_loading as cl
from app.services.auth import CurrentUser

router = APIRouter()


class ScanPalletReq(BaseModel):
    customer: str
    date: date
    code: str


class LooseReq(BaseModel):
    customer: str
    date: date
    jan: str
    qty: int = 1


class RemovePalletReq(BaseModel):
    customer: str
    date: date
    code: str


class RemoveLooseReq(BaseModel):
    customer: str
    date: date
    jan: str


class CompleteReq(BaseModel):
    customer: str
    date: date


@router.get("/loading")
async def loading_state(
    customer: str = Query(...),
    date: date = Query(...),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    return await cl.build_state(session, customer, date)


@router.get("/loading/pending-customers")
async def pending_customers(session: AsyncSession = Depends(get_db_session)) -> list[dict]:
    """当前所有还有未出预留的 (客户,计划出库日期)——装柜出库页用来按客户选，免猜日期。"""
    return await cl.list_pending_customers(session)


@router.post("/loading/scan-pallet")
async def scan_pallet(
    payload: ScanPalletReq,
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(require_admin),
) -> dict:
    return await cl.scan_pallet(session, payload.customer, payload.date, payload.code)


@router.post("/loading/loose")
async def add_loose(
    payload: LooseReq,
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(require_admin),
) -> dict:
    if payload.qty <= 0:
        raise HTTPException(status_code=400, detail="数量需大于 0")
    return await cl.add_loose(session, payload.customer, payload.date, payload.jan, payload.qty)


@router.post("/loading/remove-pallet")
async def remove_pallet(
    payload: RemovePalletReq,
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(require_admin),
) -> dict:
    return await cl.remove_pallet(session, payload.customer, payload.date, payload.code)


@router.post("/loading/remove-loose")
async def remove_loose(
    payload: RemoveLooseReq,
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(require_admin),
) -> dict:
    return await cl.remove_loose(session, payload.customer, payload.date, payload.jan)


@router.post("/loading/complete")
async def complete(
    payload: CompleteReq,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> dict:
    try:
        return await cl.complete_loading(session, payload.customer, payload.date, current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
