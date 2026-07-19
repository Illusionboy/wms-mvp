"""批量点数模块（数据通信功能）端点。

会话 CRUD + Excel 导入需认证（mutation）；库存模拟 / 托盘对账为只读、免认证
（与 analytics 一致）。全程只读 WMS 库存，不写 StockTransaction。
"""
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_db_session
from app.schemas.count_session import (
    CountSessionRead,
    CountSessionUpsert,
    ImportResult,
    PalletCheckRequest,
    PalletCheckResult,
    SimulateRequest,
    SimulateResult,
)
from app.services import count_session as svc
from app.services.auth import CurrentUser

router = APIRouter()

_MAX_BYTES = 20 * 1024 * 1024


# ── 会话 CRUD（需认证）──────────────────────────────────────────────────────
@router.post("/sessions", response_model=CountSessionRead)
async def create_session(
    payload: CountSessionUpsert,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> CountSessionRead:
    return await svc.create_session(
        session,
        name=payload.name,
        note=payload.note,
        items=payload.items,
        created_by=current_user.id,
    )


@router.get("/sessions", response_model=list[CountSessionRead])
async def list_sessions(
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(require_admin),
) -> list[CountSessionRead]:
    return await svc.list_open_sessions(session)


@router.get("/sessions/{session_id}", response_model=CountSessionRead)
async def get_session(
    session_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(require_admin),
) -> CountSessionRead:
    obj = await svc.get_session(session, session_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="点数会话不存在")
    return obj


@router.patch("/sessions/{session_id}", response_model=CountSessionRead)
async def update_session(
    session_id: int,
    payload: CountSessionUpsert,
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(require_admin),
) -> CountSessionRead:
    obj = await svc.update_session(
        session, session_id,
        name=payload.name, note=payload.note, items=payload.items,
    )
    if obj is None:
        raise HTTPException(status_code=404, detail="点数会话不存在")
    return obj


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(require_admin),
) -> dict[str, bool]:
    ok = await svc.delete_session(session, session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="点数会话不存在")
    return {"deleted": True}


@router.post("/import-excel", response_model=ImportResult)
async def import_excel(
    file: UploadFile = File(..., description="报库 Excel（sheet=客户/供应商，含 JAN+数量）"),
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(require_admin),
) -> ImportResult:
    content = await file.read(_MAX_BYTES + 1)
    if len(content) > _MAX_BYTES:
        raise HTTPException(status_code=413, detail="文件过大")
    try:
        return await svc.import_excel(session, content)
    except Exception as exc:  # openpyxl 解析错误 → 422
        raise HTTPException(status_code=422, detail=f"Excel 解析失败：{exc}") from exc


# ── 只读（免认证）───────────────────────────────────────────────────────────
@router.post("/simulate", response_model=SimulateResult)
async def simulate(
    payload: SimulateRequest,
    session: AsyncSession = Depends(get_db_session),
) -> SimulateResult:
    return await svc.simulate_stock(
        session,
        items=[(it.jan_code, it.quantity) for it in payload.items],
        warehouse_id=payload.warehouse_id,
        exclude_reserved=payload.exclude_reserved,
    )


@router.post("/pallet-check", response_model=PalletCheckResult)
async def pallet_check(
    payload: PalletCheckRequest,
    session: AsyncSession = Depends(get_db_session),
) -> PalletCheckResult:
    return await svc.check_against_pallets(
        session,
        items=[(it.jan_code, it.quantity) for it in payload.items],
        pallet_codes=payload.pallet_codes,
    )
