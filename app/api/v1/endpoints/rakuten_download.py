"""乐天订单 CSV 自动下载端点（P2b）。手动触发用于监督首跑；每步截图可查。"""
import base64
import csv as _csv
import io
import re
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.api.deps import require_auth
from app.db.session import get_db_session
from app.models.rakuten_auto_run import RakutenAutoRun
from app.scrapers.rakuten_scraper import download_shipping_orders
from app.services.rakuten_auto import OUT_DIR, run_all
from app.services.rakuten_credentials import get_credential_plain

router = APIRouter()

_DEBUG_DIR = Path("app/data/rms_debug")
_SHOT_RE = re.compile(r"^\d{2}_[\w.]+\.png$")
_STORE_RE = re.compile(r"^[A-Za-z0-9_-]+$")


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


# ── P2c 定时自动下载：结果面板 + 下载 + 手动触发 ─────────────────────────────
@router.get("/auto-runs", dependencies=[Depends(require_auth)])
async def auto_runs(session: AsyncSession = Depends(get_db_session)) -> list[dict]:
    """每店最新一次自动运行的状态 + 产物是否就绪（供「今日自动生成」面板）。"""
    rows = (await session.scalars(
        select(RakutenAutoRun).order_by(RakutenAutoRun.created_at.desc())
    )).all()
    seen: set[str] = set()
    out: list[dict] = []
    for r in rows:
        if r.store in seen:
            continue
        seen.add(r.store)
        d = OUT_DIR / r.store
        out.append({
            "store": r.store, "status": r.status, "trigger": r.trigger,
            "order_rows": r.order_rows, "counts": r.counts, "error": r.error,
            "run_at": r.created_at.isoformat(),
            "has_labels": (d / "labels.zip").is_file(),
            "has_orders": (d / "orders.csv").is_file(),
        })
    return out


@router.get("/auto-runs/{store}/{kind}", dependencies=[Depends(require_auth)])
async def download_auto_result(store: str, kind: str) -> FileResponse:
    """下载某店最新产物：kind=labels(快递单ZIP) / orders(订单CSV)。"""
    if not _STORE_RE.match(store):
        raise HTTPException(status_code=400, detail="非法店铺标识")
    if kind == "labels":
        p, media, fname = OUT_DIR / store / "labels.zip", "application/zip", f"rakuten_labels_store{store}.zip"
    elif kind == "orders":
        p, media, fname = OUT_DIR / store / "orders.csv", "text/csv", f"rakuten_orders_store{store}.csv"
    else:
        raise HTTPException(status_code=400, detail="kind 仅支持 labels / orders")
    if not p.is_file():
        raise HTTPException(status_code=404, detail="产物不存在（还没跑过或已失败）")
    return FileResponse(str(p), media_type=media, filename=fname)


@router.post("/auto-run-now", dependencies=[Depends(require_auth)])
async def auto_run_now(
    days: int = Query(10, ge=1, le=60),
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """手动触发"两店一起"跑一遍（=定时任务同一条路径），用于测试。耗时约 1~3 分钟。"""
    return {"results": await run_all(session, days=days, trigger="manual")}
