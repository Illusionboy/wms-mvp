"""乐天自动下载定时器（P2c）：Mon–Sat 08:50 JST 跑两店。

容器时区已是 Asia/Tokyo，故 datetime.now() 即 JST。用简单 asyncio 循环，无需额外依赖。
仅当 settings.rakuten_auto_enabled=True 时由 main lifespan 启动（只在 VPS 开）。
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta

from app.db.session import AsyncSessionLocal
from app.services.rakuten_auto import run_all

logger = logging.getLogger(__name__)

_RUN_HOUR = 8
_RUN_MIN = 50


def _next_run(now: datetime) -> datetime:
    target = now.replace(hour=_RUN_HOUR, minute=_RUN_MIN, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    while target.weekday() == 6:  # 6 = 周日，跳过
        target += timedelta(days=1)
    return target


async def rakuten_scheduler_loop() -> None:
    logger.info("乐天自动下载 scheduler 启动（Mon–Sat %02d:%02d JST）", _RUN_HOUR, _RUN_MIN)
    while True:
        now = datetime.now()
        target = _next_run(now)
        try:
            await asyncio.sleep((target - now).total_seconds())
        except asyncio.CancelledError:
            break
        try:
            async with AsyncSessionLocal() as session:
                results = await run_all(session, trigger="schedule")
            logger.info("乐天自动下载完成：%s", results)
        except Exception:  # noqa: BLE001
            logger.exception("乐天自动下载调度执行异常")
        await asyncio.sleep(90)  # 防同一分钟内重复触发
