"""秦丝出入库流水（采购/销售单）写入 WMS。

原本这段逻辑写在 `POST /qinsi/apply` 端点体内，定时任务无法复用。抽成服务函数后，
人工页面与自动同步走**同一条路径**——否则两边会慢慢长出不一致的行为，而这类
"手动能跑、自动跑错"的差异在生产里最难察觉。

与库存快照的分工：
- **流水**（本模块）决定"卖得多快"——安全库存与需求预测的输入
- **快照**（erp_reconciliation）决定"现在有多少"

所以镜像仓库两者都要同步，且**顺序是先流水后快照**：快照只修数字、不补流水，
先覆盖快照的话那段流水就永远是个洞。
"""
from __future__ import annotations

import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.stock_transaction import StockTransaction
from app.schemas.inventory import StockInCreate, StockOutCreate
from app.services.inventory import (
    InventoryRecordNotFoundError,
    InventoryTargetNotFoundError,
    stock_in_item,
    stock_out_item,
)
from app.services.qinsi_transfers import resolve_warehouse_id

logger = logging.getLogger(__name__)

FLOW_SOURCE = "qinsi_scrape"


async def apply_scraped_flow(
    session: AsyncSession,
    records: list,
    *,
    default_warehouse_id: int | None = None,
    customer_id: int | None = None,
    user_id: int | None = None,
    only_warehouse_ids: set[int] | None = None,
    force_negative: bool = False,
) -> dict:
    """把秦丝爬取到的出入库记录写入 WMS。

    幂等：`reference_id = qinsi:{order_no}:{jan_code}`，重复提交同一订单行自动跳过。
    仓库解析走 depotId 优先（秦丝改名不影响）。
    `only_warehouse_ids` 用于自动同步时限定范围——乐天仓库的出入库权威在 WMS，
    不能被自动流程写入，必须由人工在「秦丝同步」页决定。

    `force_negative`：人工页面保持原行为（库存不足就报错，让人看见）；
    自动同步镜像仓库时传 True——那边 ERP 是权威，流水必须如实记下，
    数字由随后的快照覆盖修正，否则会在流水里留洞。
    """
    applied = skipped = duplicate = filtered = 0
    errors: list[str] = []

    ref_ids = [f"qinsi:{r.order_no}:{r.jan_code}" for r in records if r.jan_code and r.order_no]
    existing_refs: set[str] = set()
    if ref_ids:
        existing_refs = set((await session.scalars(
            select(StockTransaction.reference_id).where(
                StockTransaction.source == FLOW_SOURCE,
                StockTransaction.reference_id.in_(ref_ids),
            )
        )).all())

    for rec in records:
        if not rec.jan_code:
            errors.append(f"{rec.product_name}: 无有效 JAN 条码（原始值: {rec.raw_jan}）")
            skipped += 1
            continue

        ref_id = f"qinsi:{rec.order_no}:{rec.jan_code}" if rec.order_no else None
        if ref_id and ref_id in existing_refs:
            duplicate += 1
            continue

        qinsi_name = rec.warehouse_name or ""
        wh_id = await resolve_warehouse_id(
            session, depot_id=getattr(rec, "warehouse_depot_id", None), qinsi_name=qinsi_name
        ) or default_warehouse_id
        if not wh_id:
            errors.append(
                f"{rec.jan_code} ({rec.product_name}): 无法确定仓库"
                f"（秦丝仓库 {qinsi_name!r} depotId={getattr(rec, 'warehouse_depot_id', None)}）"
            )
            skipped += 1
            continue
        if only_warehouse_ids is not None and wh_id not in only_warehouse_ids:
            filtered += 1
            continue

        txn_date: date | None = None
        try:
            txn_date = date.fromisoformat(rec.record_date) if rec.record_date else None
        except ValueError:
            pass

        note = f" 备注:{rec.note}" if rec.note else None
        counterparty = rec.customer_name or None   # IN→供应商 / OUT→客户

        try:
            if rec.direction == "IN":
                await stock_in_item(session, StockInCreate(
                    sku=rec.jan_code, warehouse_id=wh_id, customer_id=customer_id,
                    quantity=rec.quantity, location_code="A-00-00", source=FLOW_SOURCE,
                    reference_id=ref_id, note=note, transaction_date=txn_date,
                    supplier=counterparty,
                ), commit=False, user_id=user_id)
            else:
                await stock_out_item(session, StockOutCreate(
                    sku=rec.jan_code, warehouse_id=wh_id, customer_id=customer_id,
                    quantity=rec.quantity, source=FLOW_SOURCE, reference_id=ref_id,
                    note=note, transaction_date=txn_date, customer=counterparty,
                ), commit=False, user_id=user_id, force_negative=force_negative)
            applied += 1
        except InventoryTargetNotFoundError:
            errors.append(f"{rec.jan_code} ({rec.product_name}): 商品字典中不存在该 JAN")
            skipped += 1
        except InventoryRecordNotFoundError:
            errors.append(f"{rec.jan_code} ({rec.product_name}): 该仓库无此商品库存记录")
            skipped += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{rec.jan_code} ({rec.product_name}): {exc or type(exc).__name__}")
            skipped += 1

    if applied:
        await session.commit()
    return {"applied": applied, "skipped": skipped, "duplicate": duplicate,
            "filtered_out_of_scope": filtered, "errors": errors}
