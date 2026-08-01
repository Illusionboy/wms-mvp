from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
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


@router.post("/order-analysis/from-auto", response_model=RakutenOrderAnalysisResult)
async def rakuten_order_analysis_from_auto(
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(require_admin),
) -> RakutenOrderAnalysisResult:
    """用今日自动下载(9:00)存在服务器上的两店订单文件分析采购需求，免手动上传。
    文件位置：app/data/rakuten_auto/{1,2}/orders.csv（自动下载覆盖为最新）。"""
    from pathlib import Path
    base = Path("app/data/rakuten_auto")
    f1, f2 = base / "1" / "orders.csv", base / "2" / "orders.csv"
    c1 = f1.read_bytes() if f1.is_file() else None
    c2 = f2.read_bytes() if f2.is_file() else None
    if c1 is None and c2 is None:
        raise HTTPException(status_code=404, detail="没找到今日自动下载的订单文件（自动下载可能还没跑或失败）——请手动选文件上传")
    # 只有二号店时，把它当作 file1
    if c1 is None:
        c1, c2 = c2, None
    try:
        return await analyse_rakuten_orders(
            session=session,
            file1_name="auto_store1.csv",
            file1_content=c1,
            file2_name="auto_store2.csv" if c2 is not None else None,
            file2_content=c2,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/order-analysis/{draft_id}/apply",
    response_model=RakutenOrderApplyResult,
    dependencies=[Depends(require_admin)],
)
async def apply_rakuten_order_analysis(
    draft_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
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
