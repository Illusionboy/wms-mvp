"""乐天订单 CSV 自动下载端点（P2b）。手动触发用于监督首跑；每步截图可查。"""
import base64
import csv as _csv
import io
import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_auth
from app.db.session import get_db_session
from app.scrapers.rakuten_scraper import download_shipping_orders
from app.services.rakuten_credentials import get_credential_plain

router = APIRouter()

_DEBUG_DIR = Path("app/data/rms_debug")
_SHOT_RE = re.compile(r"^\d{2}_[\w.]+\.png$")


@router.post("/auto-download", dependencies=[Depends(require_auth)])
async def auto_download(
    store: str = Query(..., description="店铺标识（与凭据一致，如 1）"),
    days: int = Query(10, ge=1, le=60, description="下载近 N 天発送待ち（最多 60）"),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """跑一遍 RMS 登录+下载。返回每步日志/截图名 + 成功时的 CSV（base64）。首跑请监督。"""
    creds = await get_credential_plain(session, store)
    if creds is None:
        raise HTTPException(status_code=404, detail=f"店铺「{store}」凭据未配置")
    missing = [k for k in ("rms_login_id", "rms_password", "member_email", "member_password", "csv_user", "csv_password") if not creds.get(k)]
    if missing:
        raise HTTPException(status_code=400, detail=f"凭据不全，缺：{', '.join(missing)}（去 设置→乐天账号 补全）")

    result = await download_shipping_orders(creds, days=days)

    row_count = None
    csv_b64 = None
    if result.success and result.csv_bytes:
        csv_b64 = base64.b64encode(result.csv_bytes).decode("ascii")
        try:
            text = result.csv_bytes.decode("cp932", errors="replace")
            row_count = max(0, len(list(_csv.reader(io.StringIO(text)))) - 1)
        except Exception:
            row_count = None

    return {
        "success": result.success,
        "error": result.error,
        "steps": result.steps,
        "shots": result.shots,
        "csv_name": result.csv_name,
        "csv_row_count": row_count,
        "csv_b64": csv_b64,
    }


@router.get("/auto-download/shot/{store}/{name}", dependencies=[Depends(require_auth)])
async def get_shot(store: str, name: str) -> FileResponse:
    """取某步截图（供前端内联显示调试）。"""
    if not _SHOT_RE.match(name) or "/" in store or ".." in store:
        raise HTTPException(status_code=400, detail="非法文件名")
    p = _DEBUG_DIR / store / name
    if not p.is_file():
        raise HTTPException(status_code=404, detail="截图不存在")
    return FileResponse(str(p), media_type="image/png")
