"""秦丝 ERP 自动同步定时器。

同步范围（按作者确认的口径）：

| 对象 | 是否自动 | 原因 |
| --- | --- | --- |
| **调拨单（调库）** | ✅ 全部自动，**含乐天** | 调库是仓间内部搬运，两边都在秦丝里做，WMS 只需跟随 |
| **ERP_MIRROR 仓库的库存快照** | ✅ 自动（普通仓库 / 一号店备货仓） | 这些仓库的权威源已交给秦丝 |
| **乐天仓库的出入库** | ❌ 保持手动 | 乐天渠道的权威源在 WMS，由「秦丝同步」页与「乐天日常」人工操作 |

注意"快照同步"只覆盖 `inventory_source_mode = ERP_MIRROR` 的仓库——
所以要不要自动同步某个仓库，是**切模式**这个配置动作决定的，不需要改这里的代码。
乐天仓库保持 `WMS_NATIVE`，因此天然不会被快照覆盖。

调拨单回溯窗口刻意取 14 天而不是 1 天：秦丝的单据可能补录、也可能当天没跑成，
靠 `reference_id` 幂等保证重复扫描不会重复写入。
"""
from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime, timedelta

from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

_RUN_HOUR = 9
_RUN_MIN = 30          # 错开乐天 09:00，避免两个重任务叠在一起
_LOOKBACK_DAYS = 14


def _next_run(now: datetime) -> datetime:
    target = now.replace(hour=_RUN_HOUR, minute=_RUN_MIN, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return target


async def run_once(trigger: str = "schedule") -> dict:
    """跑一轮：先补调库流水，再覆盖镜像仓库的库存快照。

    顺序不能反：快照只修"现在有多少"，不补流水。先补流水再覆盖，
    历史记录才完整，剩下的对账差异也才有诊断价值。
    """
    from app.scrapers.qinsi_scraper import fetch_transfer_orders
    from app.services.erp_reconciliation import list_mirror_warehouses, sync_snapshot
    from app.services.qinsi_transfers import annotate_orders, apply_transfers

    result: dict = {"trigger": trigger, "at": datetime.now().isoformat(),
                    "transfers": None, "snapshots": [], "errors": []}

    # ── 1. 调拨单（全仓，含乐天）──
    try:
        today = date.today()
        r = await fetch_transfer_orders(today - timedelta(days=_LOOKBACK_DAYS), today)
        if not r["success"]:
            result["errors"].append(f"调拨单拉取失败: {r['error']}")
        else:
            async with AsyncSessionLocal() as session:
                orders = await annotate_orders(session, r["orders"])
                # 疑似与 WMS 手工调库重复的单不自动写——自动流程里静默重复扣减最难查，
                # 留给人在界面上确认。
                todo = [o for o in orders
                        if o["pending_lines"] > 0 and not o["blocked"]
                        and not o["suspected_duplicate"]]
                held = [o["order_sn"] for o in orders
                        if o["pending_lines"] > 0 and o["suspected_duplicate"]]
                applied = await apply_transfers(session, todo, user_id=None) if todo else \
                    {"applied_orders": 0, "applied_lines": 0, "errors": []}
            result["transfers"] = {
                "scanned": len(r["orders"]),
                "applied_orders": applied["applied_orders"],
                "applied_lines": applied["applied_lines"],
                "held_suspected_duplicate": held,
                "errors": applied.get("errors", [])[:5],
            }
    except Exception as exc:  # noqa: BLE001
        logger.exception("调拨单自动同步失败")
        result["errors"].append(f"调拨单同步异常: {type(exc).__name__}: {exc}")

    # ── 2. 镜像仓库库存快照 ──
    try:
        async with AsyncSessionLocal() as session:
            mirrors = await list_mirror_warehouses(session)
        for wh in mirrors:
            try:
                async with AsyncSessionLocal() as session:
                    r2 = await sync_snapshot(session, wh.id, dry_run=False,
                                             create_missing_products=True)
                result["snapshots"].append({
                    "warehouse": wh.name,
                    "ok": r2.get("success", False),
                    "applied": r2.get("applied", 0),
                    "delta_abs_total": r2.get("delta_abs_total", 0),
                    "created_products": len(r2.get("created_products") or []),
                    "error": r2.get("error"),
                })
            except Exception as exc:  # noqa: BLE001
                logger.exception("仓库 %s 快照同步失败", wh.name)
                result["snapshots"].append({"warehouse": wh.name, "ok": False,
                                            "error": f"{type(exc).__name__}: {exc}"})
    except Exception as exc:  # noqa: BLE001
        logger.exception("快照同步阶段失败")
        result["errors"].append(f"快照同步异常: {type(exc).__name__}: {exc}")

    logger.info("秦丝 ERP 自动同步完成: %s", result)
    return result


async def erp_sync_scheduler_loop() -> None:
    logger.info("秦丝 ERP 自动同步 scheduler 启动（每日 %02d:%02d JST）", _RUN_HOUR, _RUN_MIN)
    while True:
        now = datetime.now()
        target = _next_run(now)
        try:
            await asyncio.sleep((target - now).total_seconds())
        except asyncio.CancelledError:
            break
        try:
            await run_once(trigger="schedule")
        except Exception:  # noqa: BLE001
            logger.exception("秦丝 ERP 自动同步调度执行异常")
        await asyncio.sleep(90)  # 防同一分钟内重复触发
