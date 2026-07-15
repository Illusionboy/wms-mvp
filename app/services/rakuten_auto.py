"""乐天自动下载 + 生成快递单编排（P2c）。

每店：登录 RMS 下载近 N 天発送待ち CSV → 复用 P1 generate_courier_files 生成三家快递单 →
产物(订单CSV + 快递单ZIP[3家CSV + mapping.json])存磁盘，写一条 RakutenAutoRun。
"""
from __future__ import annotations

import csv as _csv
import io
import json
import logging
import zipfile
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rakuten_auto_run import RakutenAutoRun
from app.models.rakuten_credential import RakutenCredential
from app.scrapers.rakuten_scraper import download_shipping_orders
from app.services.rakuten_credentials import get_credential_plain
from app.services.rakuten_label import generate_courier_files

logger = logging.getLogger(__name__)

OUT_DIR = Path("app/data/rakuten_auto")
_COURIER_LABEL = {"sagawa": "佐川", "yamato": "yamato", "post": "郵便"}
_REQUIRED = ("rms_login_id", "rms_password", "member_email", "member_password", "csv_user", "csv_password")


def _count_rows(csv_bytes: bytes) -> int | None:
    try:
        text = csv_bytes.decode("cp932", errors="replace")
        return max(0, len(list(_csv.reader(io.StringIO(text)))) - 1)
    except Exception:
        return None


async def run_store(session: AsyncSession, store: str, *, days: int = 10, trigger: str = "schedule") -> dict:
    """跑单店：下载 + 生成快递单 + 存产物 + 记录。返回结果摘要。"""
    run = RakutenAutoRun(store=store, status="failed", trigger=trigger)
    session.add(run)

    creds = await get_credential_plain(session, store)
    if creds is None or not creds.get("enabled"):
        run.error = "凭据未配置或未启用"
        await session.commit()
        return {"store": store, "status": "failed", "error": run.error}
    missing = [k for k in _REQUIRED if not creds.get(k)]
    if missing:
        run.error = f"凭据不全：缺 {', '.join(missing)}"
        await session.commit()
        return {"store": store, "status": "failed", "error": run.error}

    try:
        dl = await download_shipping_orders(creds, days=days)
    except Exception as exc:  # noqa: BLE001
        run.error = f"抓取异常：{type(exc).__name__}: {exc}"
        await session.commit()
        logger.exception("rakuten auto download store=%s failed", store)
        return {"store": store, "status": "failed", "error": run.error}

    if not dl.success or not dl.csv_bytes:
        run.error = dl.error or "下载失败（见 rms_debug 截图）"
        await session.commit()
        return {"store": store, "status": "failed", "error": run.error}

    run.order_rows = _count_rows(dl.csv_bytes)
    # 生成三家快递单（复用 P1）
    try:
        lab = generate_courier_files(dl.csv_bytes, store)
        run.counts = {**lab.counts, "err": len(lab.err_rows)}
    except Exception as exc:  # noqa: BLE001
        run.error = f"生成快递单失败：{exc}（订单CSV已下载 {run.order_rows} 行）"
        # 仍保存订单 CSV，供人工用
        lab = None

    d = OUT_DIR / store
    d.mkdir(parents=True, exist_ok=True)
    (d / "orders.csv").write_bytes(dl.csv_bytes)
    (d / "orders_name.txt").write_text(dl.csv_name or f"orders_{store}.csv", encoding="utf-8")

    if lab is not None:
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for courier, data in lab.files.items():
                z.writestr(f"{ts}-store{store}-{_COURIER_LABEL[courier]}.csv", data)
            z.writestr("mapping.json", json.dumps(lab.mapping, ensure_ascii=False, indent=2))
            if lab.err_rows:
                sio = io.StringIO()
                w = _csv.DictWriter(sio, fieldnames=list(lab.err_rows[0].keys()))
                w.writeheader()
                w.writerows(lab.err_rows)
                z.writestr("err_export.csv", sio.getvalue())
        (d / "labels.zip").write_bytes(buf.getvalue())
        run.status = "success"
    else:
        (d / "labels.zip").unlink(missing_ok=True)  # 生成失败则无 ZIP

    await session.commit()
    return {
        "store": store, "status": run.status, "order_rows": run.order_rows,
        "counts": run.counts, "error": run.error,
    }


async def run_all(session: AsyncSession, *, days: int = 10, trigger: str = "schedule") -> list[dict]:
    """跑所有已启用店铺（两店）。逐店串行（避免同时开两个 chromium）。"""
    stores = (await session.scalars(
        select(RakutenCredential.store).where(RakutenCredential.enabled.is_(True)).order_by(RakutenCredential.store)
    )).all()
    results = []
    for store in stores:
        logger.info("rakuten auto run store=%s trigger=%s", store, trigger)
        results.append(await run_store(session, store, days=days, trigger=trigger))
    return results
