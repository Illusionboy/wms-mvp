from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_auth
from app.db.session import get_db_session
from app.schemas.inventory import RakutenOrderAnalysisResult, RakutenOrderApplyResult
from app.services.auth import CurrentUser
from app.services.rakuten_order_analysis import (
    analyse_rakuten_orders,
    apply_rakuten_order_draft,
    get_rakuten_order_draft,
)

router = APIRouter()

MAX_BYTES = 20 * 1024 * 1024  # 20 MB per file


@router.post("/order-analysis", response_model=RakutenOrderAnalysisResult)
async def rakuten_order_analysis(
    file1: UploadFile = File(..., description="一号店订单 CSV/XLSX"),
    file2: UploadFile | None = File(None, description="二号店订单 CSV/XLSX（可选）"),
    session: AsyncSession = Depends(get_db_session),
) -> RakutenOrderAnalysisResult:
    """Parse one or two Rakuten order files and compare against 乐天仓库 inventory.

    Returns aggregated quantities per JAN with status:
    - ok: sufficient stock
    - insufficient: have record but stock < ordered
    - no_record: product known but no 乐天仓库 inventory record
    - unknown: JAN not in WMS product catalog

    Lines whose JAN cannot be resolved (via システム連携用SKU番号 / product_dict
    fallback) are returned in `unresolved` for manual SKU/JAN registration.

    Creates a `RakutenOrderDraft` (returned as `draft_id`); no stock mutations
    are performed until `POST /order-analysis/{draft_id}/apply` is called.
    """
    content1 = await file1.read(MAX_BYTES + 1)
    if len(content1) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="一号店文件超过 20MB 限制")

    content2: bytes | None = None
    name2: str | None = None
    if file2 and file2.filename:
        content2 = await file2.read(MAX_BYTES + 1)
        if len(content2) > MAX_BYTES:
            raise HTTPException(status_code=413, detail="二号店文件超过 20MB 限制")
        name2 = file2.filename

    try:
        return await analyse_rakuten_orders(
            session=session,
            file1_name=file1.filename or "store1.csv",
            file1_content=content1,
            file2_name=name2,
            file2_content=content2,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/order-analysis/{draft_id}/apply",
    response_model=RakutenOrderApplyResult,
    dependencies=[Depends(require_auth)],
)
async def apply_rakuten_order_analysis(
    draft_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_auth),
) -> RakutenOrderApplyResult:
    """Deduct 乐天仓库 stock for `status=="ok"` lines in the draft.

    `insufficient` / `no_record` / `unknown` lines (and unresolved JAN lines)
    are returned as `shortage_items` / `unresolved` for "调货"/"登记新SKU" follow-up
    without any stock mutation.
    """
    draft = await get_rakuten_order_draft(session, draft_id, with_for_update=True)
    if draft is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    if draft.status != "parsed":
        raise HTTPException(status_code=409, detail=f"草稿状态为 {draft.status}，无法重复确认")

    return await apply_rakuten_order_draft(session, draft, user_id=current_user.id)
