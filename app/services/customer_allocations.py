"""客户货量软预留服务。

流程：
1. 上传 Excel → `upsert_allocations_from_excel` → 解析行，UPSERT 到 CustomerAllocation，
   立即调 `_revalidate_for_jan` 评估哪些可以 reserved
2. 每次入库后 → `try_auto_reserve(session, jan_code, warehouse_id)` 触发同 JAN 的重新评估
3. 手动调转 → `try_reserve_one(session, allocation_id)`
4. 撤销 → `revert_to_waiting(session, allocation_id)` + 重新评估
5. 取消 → `cancel_allocation(session, allocation_id)`

防抽风核心：`_revalidate_for_jan` 持有 InventoryRecord 行锁（SELECT FOR UPDATE），
在同一事务内原子地重分配所有 reserved/waiting 行。
"""
from __future__ import annotations

import io
import re
from datetime import date, datetime

import openpyxl
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer_allocation import CustomerAllocation
from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.schemas.inventory import (
    CustomerAllocationRead,
    CustomerAllocationStatusResult,
    CustomerAllocationUploadResult,
)

ALLOCATION_WAREHOUSE_NAME = "普通仓库"


# ---------------------------------------------------------------------------
# 文件名日期解析
# ---------------------------------------------------------------------------

def _parse_date_from_filename(filename: str) -> date | None:
    """从文件名提取计划出库日期。

    优先匹配 YYYYMMDD，其次 YYYY-MM-DD / YYYY/MM/DD。
    """
    name = filename.replace("\\", "/").rsplit("/", 1)[-1]
    m = re.search(r"(\d{4})[/-]?(\d{2})[/-]?(\d{2})", name)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass
    return None


# ---------------------------------------------------------------------------
# Excel 解析
# ---------------------------------------------------------------------------

def _parse_allocation_excel(
    content: bytes,
) -> list[tuple[str, str, int]]:
    """解析客户需求 Excel，返回 [(customer_name, jan_code, quantity), ...]。

    支持格式：
      - 每个 sheet 名即客户代码（mm / kk / cp 等）
      - 每行有 JAN（13位纯数字）和数量两列；列名不敏感，只要含 jan/JAN 和 数量/qty/quantity
      - 数量 ≤ 0 的行跳过
    """
    wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
    rows: list[tuple[str, str, int]] = []

    for sheet in wb.worksheets:
        customer_name = sheet.title.strip()
        if not customer_name:
            continue

        # detect header row
        header_row_idx: int | None = None
        jan_col: int | None = None
        qty_col: int | None = None

        for row in sheet.iter_rows(max_row=10):
            for cell in row:
                if cell.value is None:
                    continue
                val = str(cell.value).strip().lower()
                if "jan" in val or "条码" in val or "barcode" in val:
                    jan_col = cell.column
                    header_row_idx = cell.row
                if "数量" in val or "qty" in val or "quantity" in val or "個数" in val:
                    qty_col = cell.column
            if jan_col and qty_col:
                break

        if not (jan_col and qty_col and header_row_idx):
            continue

        for row in sheet.iter_rows(min_row=header_row_idx + 1):
            jan_raw = row[jan_col - 1].value
            qty_raw = row[qty_col - 1].value
            if jan_raw is None or qty_raw is None:
                continue
            jan = "".join(c for c in str(jan_raw) if c.isdigit())
            if len(jan) != 13:
                continue
            try:
                qty = int(float(qty_raw))
            except (ValueError, TypeError):
                continue
            if qty <= 0:
                continue
            rows.append((customer_name, jan, qty))

    return rows


# ---------------------------------------------------------------------------
# 核心：重新评估某 JAN 在普通仓库的所有预留（持锁，原子）
# ---------------------------------------------------------------------------

async def _revalidate_for_jan(
    session: AsyncSession,
    jan_code: str,
    warehouse: Warehouse,
) -> None:
    """原子地重分配该 JAN 的所有 waiting/reserved 行。

    持有 InventoryRecord 行锁，按 planned_outbound_date ASC 贪心：
    累积量 ≤ 当前库存 → reserved；超出 → waiting。
    """
    inv_record = await session.scalar(
        select(InventoryRecord).where(
            InventoryRecord.product_jan == jan_code,
            InventoryRecord.warehouse_id == warehouse.id,
        ).with_for_update()
    )
    current_stock = inv_record.quantity if inv_record else 0

    allocs = (await session.scalars(
        select(CustomerAllocation).where(
            CustomerAllocation.jan_code == jan_code,
            CustomerAllocation.status.in_(["waiting", "reserved"]),
        ).order_by(CustomerAllocation.planned_outbound_date.asc(), CustomerAllocation.id.asc())
        .with_for_update()
    )).all()

    running = 0
    for alloc in allocs:
        running += alloc.quantity
        alloc.status = "reserved" if running <= current_stock else "waiting"


# ---------------------------------------------------------------------------
# UPSERT：上传 Excel 时写入/更新预留行
# ---------------------------------------------------------------------------

async def upsert_allocations_from_excel(
    session: AsyncSession,
    content: bytes,
    filename: str,
    planned_outbound_date: date | None,
) -> CustomerAllocationUploadResult:
    if planned_outbound_date is None:
        planned_outbound_date = _parse_date_from_filename(filename)
    if planned_outbound_date is None:
        raise ValueError("无法从文件名解析出库日期，请在上传时手动指定日期")

    rows = _parse_allocation_excel(content)
    if not rows:
        raise ValueError("Excel 中未解析到有效行（需要 JAN 13位 + 数量列）")

    warehouse = await session.scalar(
        select(Warehouse).where(Warehouse.name == ALLOCATION_WAREHOUSE_NAME)
    )
    if warehouse is None:
        raise ValueError(f"找不到仓库「{ALLOCATION_WAREHOUSE_NAME}」，请先在系统中创建")

    stats = {"reserved": 0, "waiting": 0, "updated": 0, "skipped": 0}
    affected_jans: set[str] = set()

    for customer_name, jan_code, quantity in rows:
        # UPSERT: (date, customer, jan) 唯一，若 quantity 相同则跳过，否则更新
        stmt = pg_insert(CustomerAllocation).values(
            planned_outbound_date=planned_outbound_date,
            customer_name=customer_name,
            jan_code=jan_code,
            quantity=quantity,
            status="waiting",
            source_filename=filename,
        ).on_conflict_do_update(
            constraint="uq_customer_alloc_date_customer_jan",
            set_={
                "quantity": quantity,
                "source_filename": filename,
                "updated_at": datetime.utcnow(),
            },
            where=CustomerAllocation.quantity != quantity,
        )
        result = await session.execute(stmt)
        if result.rowcount == 0:
            stats["skipped"] += 1
        else:
            stats["updated"] += 1
        affected_jans.add(jan_code)

    await session.flush()

    # 重新评估所有受影响的 JAN
    for jan_code in affected_jans:
        await _revalidate_for_jan(session, jan_code, warehouse)

    await session.flush()

    # 统计最终状态
    for customer_name, jan_code, _ in rows:
        if jan_code in affected_jans:
            pass  # counted below

    allocs = (await session.scalars(
        select(CustomerAllocation).where(
            CustomerAllocation.jan_code.in_(affected_jans),
            CustomerAllocation.planned_outbound_date == planned_outbound_date,
        )
    )).all()
    customer_names_in_upload = {r[0] for r in rows}
    for a in allocs:
        if a.customer_name not in customer_names_in_upload:
            continue
        if a.status == "reserved":
            stats["reserved"] += 1
        elif a.status == "waiting":
            stats["waiting"] += 1

    # subtract skipped/updated from reserved/waiting to avoid double-counting
    # Actually: recalculate properly
    stats["reserved"] = sum(1 for a in allocs if a.status == "reserved" and a.customer_name in customer_names_in_upload)
    stats["waiting"] = sum(1 for a in allocs if a.status == "waiting" and a.customer_name in customer_names_in_upload)

    await session.commit()

    return CustomerAllocationUploadResult(
        planned_outbound_date=planned_outbound_date,
        source_filename=filename,
        total_rows=len(rows),
        reserved=stats["reserved"],
        waiting=stats["waiting"],
        updated=stats["updated"],
        skipped=stats["skipped"],
    )


# ---------------------------------------------------------------------------
# 入库后自动调转钩子
# ---------------------------------------------------------------------------

async def try_auto_reserve(
    session: AsyncSession,
    jan_code: str,
    warehouse_id: int,
) -> None:
    """入库后调用，尝试将 waiting 行升级为 reserved。

    在调用方的事务内运行（不自行 commit），由调用方统一提交。
    只在仓库为普通仓库且存在 waiting 行时执行重分配。
    """
    warehouse = await session.get(Warehouse, warehouse_id)
    if warehouse is None or warehouse.name != ALLOCATION_WAREHOUSE_NAME:
        return

    has_waiting = await session.scalar(
        select(CustomerAllocation.id).where(
            CustomerAllocation.jan_code == jan_code,
            CustomerAllocation.status == "waiting",
        ).limit(1)
    )
    if has_waiting is None:
        return

    await _revalidate_for_jan(session, jan_code, warehouse)


# ---------------------------------------------------------------------------
# 手动调转 / 撤销 / 取消
# ---------------------------------------------------------------------------

async def try_reserve_one(
    session: AsyncSession,
    allocation_id: int,
) -> CustomerAllocation:
    """手动将一条 waiting 行调转为 reserved（若库存足够）。"""
    alloc = await session.scalar(
        select(CustomerAllocation).where(CustomerAllocation.id == allocation_id).with_for_update()
    )
    if alloc is None:
        raise ValueError("预留记录不存在")
    if alloc.status not in ("waiting",):
        raise ValueError(f"当前状态 {alloc.status}，无法调转")

    warehouse = await session.scalar(
        select(Warehouse).where(Warehouse.name == ALLOCATION_WAREHOUSE_NAME)
    )
    if warehouse is None:
        raise ValueError(f"仓库「{ALLOCATION_WAREHOUSE_NAME}」不存在")

    await _revalidate_for_jan(session, alloc.jan_code, warehouse)
    await session.flush()

    # Refresh to get updated status
    await session.refresh(alloc)
    if alloc.status == "waiting":
        raise ValueError("库存不足，无法调转")

    await session.commit()
    return alloc


async def revert_to_waiting(
    session: AsyncSession,
    allocation_id: int,
) -> CustomerAllocation:
    """撤销 reserved → waiting，并重新评估同 JAN 的其他 waiting 行。"""
    alloc = await session.scalar(
        select(CustomerAllocation).where(CustomerAllocation.id == allocation_id).with_for_update()
    )
    if alloc is None:
        raise ValueError("预留记录不存在")
    if alloc.status != "reserved":
        raise ValueError(f"当前状态 {alloc.status}，只有 reserved 状态可以撤销")

    alloc.status = "waiting"
    await session.flush()

    warehouse = await session.scalar(
        select(Warehouse).where(Warehouse.name == ALLOCATION_WAREHOUSE_NAME)
    )
    if warehouse:
        await _revalidate_for_jan(session, alloc.jan_code, warehouse)

    await session.commit()
    await session.refresh(alloc)
    return alloc


async def cancel_allocation(
    session: AsyncSession,
    allocation_id: int,
) -> CustomerAllocation:
    """取消预留（reserved/waiting → cancelled）。"""
    alloc = await session.scalar(
        select(CustomerAllocation).where(CustomerAllocation.id == allocation_id).with_for_update()
    )
    if alloc is None:
        raise ValueError("预留记录不存在")
    if alloc.status in ("shipped", "cancelled"):
        raise ValueError(f"当前状态 {alloc.status}，无法取消")

    prev_status = alloc.status
    alloc.status = "cancelled"
    await session.flush()

    # If was reserved, release capacity and re-evaluate others
    if prev_status == "reserved":
        warehouse = await session.scalar(
            select(Warehouse).where(Warehouse.name == ALLOCATION_WAREHOUSE_NAME)
        )
        if warehouse:
            await _revalidate_for_jan(session, alloc.jan_code, warehouse)

    await session.commit()
    await session.refresh(alloc)
    return alloc


# ---------------------------------------------------------------------------
# 查询：货齐了状态
# ---------------------------------------------------------------------------

async def get_allocation_status(
    session: AsyncSession,
    customer_name: str | None = None,
    planned_outbound_date: date | None = None,
    status_filter: str | None = None,
) -> list[CustomerAllocationRead]:
    """查询预留状态，实时附带当前库存和商品名。"""
    warehouse = await session.scalar(
        select(Warehouse).where(Warehouse.name == ALLOCATION_WAREHOUSE_NAME)
    )

    stmt = select(CustomerAllocation)
    if customer_name:
        stmt = stmt.where(CustomerAllocation.customer_name == customer_name)
    if planned_outbound_date:
        stmt = stmt.where(CustomerAllocation.planned_outbound_date == planned_outbound_date)
    if status_filter:
        stmt = stmt.where(CustomerAllocation.status == status_filter)
    stmt = stmt.order_by(
        CustomerAllocation.planned_outbound_date.asc(),
        CustomerAllocation.customer_name.asc(),
        CustomerAllocation.jan_code.asc(),
    )

    allocs = (await session.scalars(stmt)).all()
    if not allocs:
        return []

    jan_codes = list({a.jan_code for a in allocs})

    products_map: dict[str, str] = {}
    for p in (await session.scalars(select(Product).where(Product.jan_code.in_(jan_codes)))).all():
        products_map[p.jan_code] = p.name_jp

    stock_map: dict[str, int] = {}
    if warehouse:
        for rec in (await session.scalars(
            select(InventoryRecord).where(
                InventoryRecord.product_jan.in_(jan_codes),
                InventoryRecord.warehouse_id == warehouse.id,
            )
        )).all():
            stock_map[rec.product_jan] = stock_map.get(rec.product_jan, 0) + rec.quantity

    result = []
    for a in allocs:
        r = CustomerAllocationRead.model_validate(a)
        r.product_name = products_map.get(a.jan_code)
        r.current_stock = stock_map.get(a.jan_code)
        result.append(r)
    return result


async def get_allocation_summary(
    session: AsyncSession,
    customer_name: str,
    planned_outbound_date: date,
) -> CustomerAllocationStatusResult:
    items = await get_allocation_status(session, customer_name=customer_name, planned_outbound_date=planned_outbound_date)
    return CustomerAllocationStatusResult(
        customer_name=customer_name,
        planned_outbound_date=planned_outbound_date,
        ready_count=sum(1 for i in items if i.status == "reserved"),
        waiting_count=sum(1 for i in items if i.status == "waiting"),
        shipped_count=sum(1 for i in items if i.status == "shipped"),
        items=items,
    )
