"""报损（破损品）：把仓内发现的破损货物从可售库存里隔离出来，可折价出售。

编码方案：破损品是一条**独立的商品行**，`jan_code = "D-" + 正常JAN`（如 `D-4902750735590`）。
这个码不实际打印条码，只作系统内标记。

为什么这样就能满足"出库除非JAN完全一致否则只出正常品"：
`_find_single_inventory_record`（services/inventory.py）是严格等值 `product_jan == sku`，
所有出库上层取桶也全是等值匹配 —— 破损品用了不同的 JAN，正常出库在库存桶层面
天然碰不到它。真正需要防的是上游「JAN→商品解析层」的模糊后缀匹配，
那部分由 `_product_search_statement` 的 `include_damaged` 参数控制。

为什么前缀用 `D-` 而不是数字：前端 resolveScan() 对 14 位纯数字码会走 GTIN-14 换算
（`_gtin14ToEan13` / `digits.slice(1)`），"9+13位"的报损码会被静默还原成正常商品JAN。
非数字前缀彻底避开这条路径。
"""
from __future__ import annotations

from datetime import date
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.schemas.inventory import StockInCreate, StockOutCreate
from app.services.inventory import (
    InventoryServiceError,
    InventoryTargetNotFoundError,
    stock_in_item,
    stock_out_item,
)

DAMAGE_PREFIX = "D-"
DAMAGE_SOURCE = "damage_report"


def is_damaged_jan(jan: str | None) -> bool:
    return bool(jan) and str(jan).strip().startswith(DAMAGE_PREFIX)


def damaged_jan(normal_jan: str) -> str:
    """正常JAN → 破损JAN（幂等：已是破损JAN则原样返回）。"""
    j = str(normal_jan).strip()
    return j if is_damaged_jan(j) else DAMAGE_PREFIX + j


def normal_jan_of(jan: str) -> str:
    """破损JAN → 正常JAN（幂等）。"""
    j = str(jan).strip()
    return j[len(DAMAGE_PREFIX):] if is_damaged_jan(j) else j


async def ensure_damaged_product(session: AsyncSession, normal_jan: str) -> Product:
    """保证破损商品行存在（幂等）。InventoryRecord.product_jan 是 FK RESTRICT，
    所以破损库存桶必须先有对应的 products 行。"""
    if is_damaged_jan(normal_jan):
        raise InventoryServiceError("不能对破损品再次报损")

    dmg_jan = damaged_jan(normal_jan)
    existing = await session.get(Product, dmg_jan)
    if existing is not None:
        return existing

    normal = await session.get(Product, normal_jan)
    if normal is None:
        raise InventoryTargetNotFoundError(f"商品不存在: {normal_jan}")

    product = Product(
        jan_code=dmg_jan,
        name_jp=f"[破损] {normal.name_jp}"[:255],
        name_zh=(f"[破损] {normal.name_zh}"[:255] if normal.name_zh else None),
        # 刻意留空：units_per_case 为 None 会直接短路 _maybe_create_low_stock_alert，
        # 破损品不产生低库存告警噪音
        units_per_case=None,
        outer_jan=None,
        is_damaged=True,
        damaged_of_jan=normal_jan,
    )
    session.add(product)
    await session.flush()
    return product


async def get_damaged_quantity(session: AsyncSession, normal_jan: str, warehouse_id: int) -> int:
    """某正常JAN在某仓库的破损库存数量（盘点自动扣除、查询页展示都用它）。"""
    qty = await session.scalar(
        select(func.coalesce(func.sum(InventoryRecord.quantity), 0)).where(
            InventoryRecord.product_jan == damaged_jan(normal_jan),
            InventoryRecord.warehouse_id == warehouse_id,
        )
    )
    return int(qty or 0)


async def list_damaged_stock(session: AsyncSession, warehouse_id: int | None = None) -> list[dict]:
    """破损品清单：所有 quantity != 0 的破损库存桶。"""
    stmt = (
        select(InventoryRecord, Product, Warehouse)
        .join(Product, Product.jan_code == InventoryRecord.product_jan)
        .join(Warehouse, Warehouse.id == InventoryRecord.warehouse_id)
        .where(Product.is_damaged.is_(True), InventoryRecord.quantity != 0)
        .order_by(Warehouse.name.asc(), InventoryRecord.product_jan.asc())
    )
    if warehouse_id is not None:
        stmt = stmt.where(InventoryRecord.warehouse_id == warehouse_id)

    rows = (await session.execute(stmt)).all()
    return [
        {
            "damaged_jan": rec.product_jan,
            "normal_jan": prod.damaged_of_jan or normal_jan_of(rec.product_jan),
            "product_name": prod.name_jp,
            "warehouse_id": wh.id,
            "warehouse_name": wh.name,
            "quantity": rec.quantity,
        }
        for rec, prod, wh in rows
    ]


async def report_damage(
    session: AsyncSession,
    *,
    jan: str,
    warehouse_id: int,
    quantity: int,
    reason: str,
    user_id: int | None = None,
    transaction_date: date | None = None,
) -> dict:
    """仓内发现破损：同一仓库内，从正常JAN桶转移到破损JAN桶。

    照 transfer_stock_item 的结构：OUT + IN 共用一个 reference_id，一次 commit。
    两笔都写 StockTransaction，符合"每次库存变动必须留痕"的项目约定。
    """
    if is_damaged_jan(jan):
        raise InventoryServiceError("不能对破损品再次报损")
    if quantity <= 0:
        raise InventoryServiceError("报损数量必须大于 0")

    reason_text = (reason or "").strip()
    if not reason_text:
        raise InventoryServiceError("请填写报损原因")

    await ensure_damaged_product(session, jan)

    ref = f"damage:{uuid4().hex}"  # 39 字符，未超 reference_id 的 64 上限
    note = f"报损 原因:{reason_text}"

    out_result = await stock_out_item(
        session,
        StockOutCreate(
            sku=jan,
            warehouse_id=warehouse_id,
            quantity=quantity,
            source=DAMAGE_SOURCE,
            reference_id=ref,
            note=note,
            transaction_date=transaction_date,
        ),
        commit=False,
        user_id=user_id,
    )

    in_result = await stock_in_item(
        session,
        StockInCreate(
            sku=damaged_jan(jan),
            warehouse_id=warehouse_id,
            quantity=quantity,
            location_code="A-00-00",
            source=DAMAGE_SOURCE,
            reference_id=ref,
            note=note,
            transaction_date=transaction_date,
        ),
        commit=False,
        user_id=user_id,
    )

    await session.commit()
    return {
        "normal_jan": jan,
        "damaged_jan": damaged_jan(jan),
        "warehouse_id": warehouse_id,
        "quantity": quantity,
        "reason": reason_text,
        "reference_id": ref,
        "normal_quantity_after": out_result.record.quantity,
        "damaged_quantity_after": in_result.record.quantity,
    }
