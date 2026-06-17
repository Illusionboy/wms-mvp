from datetime import date

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_auth
from app.db.session import get_db_session
from app.schemas.inventory import (
    BulkCancelAllocationResult,
    CustomerAllocationRead,
    CustomerAllocationStatusResult,
    CustomerAllocationUploadResult,
)
from app.services.auth import CurrentUser
from app.services.customer_allocations import (
    bulk_cancel_allocations,
    cancel_allocation,
    get_allocation_status,
    get_allocation_summary,
    mark_as_shipped,
    revert_to_waiting,
    try_reserve_one,
    update_allocation_quantity,
    upsert_allocations_from_excel,
)

router = APIRouter()

MAX_BYTES = 20 * 1024 * 1024


@router.post(
    "/allocations/upload",
    response_model=CustomerAllocationUploadResult,
    dependencies=[Depends(require_auth)],
)
async def upload_allocation_excel(
    file: UploadFile = File(..., description="客户需求 Excel（每 sheet 为一个客户代码）"),
    planned_outbound_date: date | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> CustomerAllocationUploadResult:
    """上传客户需求 Excel，自动预留普通仓库库存。

    - 库存足够 → status=reserved；不足 → status=waiting（不报错，整行等待）
    - 重复上传同文件：幂等（quantity 未变则跳过；quantity 变大则更新并重新评估）
    - 文件名须含日期（YYYYMMDD 或 YYYY-MM-DD），或通过 `planned_outbound_date` 参数手动指定
    """
    content = await file.read(MAX_BYTES + 1)
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="文件超过 20MB 限制")
    try:
        return await upsert_allocations_from_excel(
            session=session,
            content=content,
            filename=file.filename or "upload.xlsx",
            planned_outbound_date=planned_outbound_date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/allocations", response_model=list[CustomerAllocationRead])
async def list_allocations(
    customer_name: str | None = None,
    planned_outbound_date: date | None = None,
    status: str | None = None,
    jan_code: str | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> list[CustomerAllocationRead]:
    """查询客户预留列表。可按客户名、计划出库日期、状态、JAN 筛选。"""
    return await get_allocation_status(
        session,
        customer_name=customer_name,
        planned_outbound_date=planned_outbound_date,
        status_filter=status,
        jan_code=jan_code,
    )


@router.get("/allocations/summary", response_model=CustomerAllocationStatusResult)
async def allocation_summary(
    customer_name: str,
    planned_outbound_date: date,
    session: AsyncSession = Depends(get_db_session),
) -> CustomerAllocationStatusResult:
    """查看某客户某日期的货齐了状态汇总。"""
    return await get_allocation_summary(session, customer_name, planned_outbound_date)


@router.patch(
    "/allocations/{allocation_id}/reserve",
    response_model=CustomerAllocationRead,
    dependencies=[Depends(require_auth)],
)
async def manual_reserve(
    allocation_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_auth),
) -> CustomerAllocationRead:
    """手动将 waiting 行调转为 reserved（库存不足时返回 409）。"""
    try:
        alloc = await try_reserve_one(session, allocation_id)
    except ValueError as exc:
        status_code = 409 if "库存不足" in str(exc) else 404 if "不存在" in str(exc) else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    r = CustomerAllocationRead.model_validate(alloc)
    return r


@router.patch(
    "/allocations/{allocation_id}/quantity",
    response_model=CustomerAllocationRead,
    dependencies=[Depends(require_auth)],
)
async def adjust_allocation_quantity(
    allocation_id: int,
    quantity: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_auth),
) -> CustomerAllocationRead:
    """手动修正预留数量（纠正重复上传/录入错误导致的多算或少算）。"""
    try:
        alloc = await update_allocation_quantity(session, allocation_id, quantity)
    except ValueError as exc:
        status_code = 404 if "不存在" in str(exc) else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return CustomerAllocationRead.model_validate(alloc)


@router.patch(
    "/allocations/{allocation_id}/revert",
    response_model=CustomerAllocationRead,
    dependencies=[Depends(require_auth)],
)
async def revert_reservation(
    allocation_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_auth),
) -> CustomerAllocationRead:
    """撤销 reserved → waiting，释放的库存量会重新评估其他 waiting 行。"""
    try:
        alloc = await revert_to_waiting(session, allocation_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return CustomerAllocationRead.model_validate(alloc)


@router.patch(
    "/allocations/{allocation_id}/cancel",
    response_model=CustomerAllocationRead,
    dependencies=[Depends(require_auth)],
)
async def cancel_reservation(
    allocation_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_auth),
) -> CustomerAllocationRead:
    """取消预留（reserved/waiting → cancelled）。"""
    try:
        alloc = await cancel_allocation(session, allocation_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return CustomerAllocationRead.model_validate(alloc)


@router.patch(
    "/allocations/{allocation_id}/ship",
    response_model=CustomerAllocationRead,
    dependencies=[Depends(require_auth)],
)
async def mark_allocation_shipped(
    allocation_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_auth),
) -> CustomerAllocationRead:
    """手动标记该预留对应的货已实际出库（reserved/waiting → shipped）。

    系统不会自动按客户名匹配秦丝同步/贸易出库等渠道的实际出库记录——
    各渠道客户名格式不统一，自动匹配错了比不匹配更危险。
    由操作员在确认实际出库已发生后手动标记，避免误标到错误客户的预留行。
    """
    try:
        alloc = await mark_as_shipped(session, allocation_id)
    except ValueError as exc:
        status_code = 404 if "不存在" in str(exc) else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return CustomerAllocationRead.model_validate(alloc)


@router.post(
    "/allocations/bulk-cancel",
    response_model=BulkCancelAllocationResult,
    dependencies=[Depends(require_auth)],
)
async def bulk_cancel_reservation(
    customer_name: str,
    planned_outbound_date: date,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_auth),
) -> BulkCancelAllocationResult:
    """按客户名+计划出库日期批量取消（典型用途：上传时填错日期，整批撤销重传）。

    只取消 waiting/reserved 状态的行；shipped/cancelled 不受影响。
    """
    count = await bulk_cancel_allocations(session, customer_name, planned_outbound_date)
    return BulkCancelAllocationResult(cancelled_count=count)
