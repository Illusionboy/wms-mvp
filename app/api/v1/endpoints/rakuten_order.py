from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services.rakuten_order_analysis import OrderAnalysisResult, analyse_rakuten_orders

router = APIRouter()

MAX_BYTES = 20 * 1024 * 1024  # 20 MB per file


@router.post("/order-analysis", response_model=OrderAnalysisResult)
async def rakuten_order_analysis(
    file1: UploadFile = File(..., description="一号店订单 CSV/XLSX"),
    file2: UploadFile | None = File(None, description="二号店订单 CSV/XLSX（可选）"),
    session: AsyncSession = Depends(get_db_session),
) -> OrderAnalysisResult:
    """Parse one or two Rakuten order files and compare against 乐天仓库 inventory.

    Returns aggregated quantities per JAN with status:
    - ok: sufficient stock
    - insufficient: have record but stock < ordered
    - no_record: product known but no 乐天仓库 inventory record
    - unknown: JAN not in WMS product catalog

    No stock mutations are performed.
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
