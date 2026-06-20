"""JAN 别名（重复JAN指向同一商品）合并服务。

与 `Product.outer_jan`（外箱码，含数量换算）是两套独立机制，互不复用——
这里是单纯的 1:1 别名映射：alias_jan 不再单独累积库存，所有出入库自动归一化到 canonical_jan。
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.models.product_jan_alias import ProductJanAlias
from app.models.stock_transaction import StockTransaction
from app.models.warehouse import Warehouse
from app.schemas.inventory import AliasMergePreview, AliasMergeWarehouseDiff


async def resolve_canonical_jan(session: AsyncSession, jan_code: str) -> str:
    """若 jan_code 是某个别名，返回其主JAN；否则原样返回。"""
    alias = await session.get(ProductJanAlias, jan_code)
    return alias.canonical_jan if alias else jan_code


async def list_aliases(session: AsyncSession, canonical_jan: str) -> list[ProductJanAlias]:
    result = await session.execute(
        select(ProductJanAlias)
        .where(ProductJanAlias.canonical_jan == canonical_jan)
        .order_by(ProductJanAlias.alias_jan)
    )
    return list(result.scalars().all())


async def _validate_alias_pair(session: AsyncSession, canonical_jan: str, alias_jan: str) -> tuple[Product, Product]:
    if alias_jan == canonical_jan:
        raise ValueError("别名JAN不能与主JAN相同")

    canonical_product = await session.get(Product, canonical_jan)
    if canonical_product is None:
        raise ValueError(f"主JAN {canonical_jan} 不存在")

    alias_product = await session.get(Product, alias_jan)
    if alias_product is None:
        raise ValueError(f"别名JAN {alias_jan} 不存在")

    if await session.get(ProductJanAlias, canonical_jan) is not None:
        raise ValueError(f"{canonical_jan} 本身是别名，请使用它的主JAN")

    existing_alias = await session.get(ProductJanAlias, alias_jan)
    if existing_alias is not None:
        raise ValueError(f"{alias_jan} 已经是 {existing_alias.canonical_jan} 的别名")

    is_someone_else_canonical = await session.execute(
        select(ProductJanAlias.alias_jan).where(ProductJanAlias.canonical_jan == alias_jan).limit(1)
    )
    if is_someone_else_canonical.scalar_one_or_none() is not None:
        raise ValueError(f"{alias_jan} 已经是其他别名的主JAN，不能再被设为别名")

    return canonical_product, alias_product


async def preview_alias_merge(session: AsyncSession, canonical_jan: str, alias_jan: str) -> AliasMergePreview:
    canonical_product, alias_product = await _validate_alias_pair(session, canonical_jan, alias_jan)

    warehouses = (await session.execute(select(Warehouse))).scalars().all()
    canonical_records = {
        r.warehouse_id: r
        for r in (
            await session.execute(select(InventoryRecord).where(InventoryRecord.product_jan == canonical_jan))
        ).scalars()
    }
    alias_records = {
        r.warehouse_id: r
        for r in (
            await session.execute(select(InventoryRecord).where(InventoryRecord.product_jan == alias_jan))
        ).scalars()
    }

    diffs: list[AliasMergeWarehouseDiff] = []
    for wh in warehouses:
        canonical_qty = canonical_records[wh.id].quantity if wh.id in canonical_records else 0
        alias_qty = alias_records[wh.id].quantity if wh.id in alias_records else 0
        if canonical_qty == 0 and alias_qty == 0:
            continue
        diffs.append(
            AliasMergeWarehouseDiff(
                warehouse_id=wh.id,
                warehouse_name=wh.name,
                canonical_quantity=canonical_qty,
                alias_quantity=alias_qty,
                merged_quantity=canonical_qty + alias_qty,
            )
        )

    return AliasMergePreview(
        canonical_jan=canonical_jan,
        alias_jan=alias_jan,
        canonical_name=canonical_product.name_zh or canonical_product.name_jp,
        alias_name=alias_product.name_zh or alias_product.name_jp,
        warehouses=diffs,
    )


async def create_alias(
    session: AsyncSession, canonical_jan: str, alias_jan: str, note: str | None = None
) -> ProductJanAlias:
    await _validate_alias_pair(session, canonical_jan, alias_jan)

    canonical_records = {
        r.warehouse_id: r
        for r in (
            await session.execute(
                select(InventoryRecord).where(InventoryRecord.product_jan == canonical_jan).with_for_update()
            )
        ).scalars()
    }
    alias_records = (
        await session.execute(
            select(InventoryRecord).where(InventoryRecord.product_jan == alias_jan).with_for_update()
        )
    ).scalars().all()

    for alias_record in alias_records:
        canonical_record = canonical_records.get(alias_record.warehouse_id)
        if canonical_record is None:
            # 该仓库只有别名有桶：直接把桶过户给主JAN，历史 StockTransaction 跟着 inventory_record_id 走。
            alias_record.product_jan = canonical_jan
        else:
            # 两边都有桶：把数量并入主JAN的桶，重指流水，再删除已清空的别名桶。
            canonical_record.quantity += alias_record.quantity
            await session.execute(
                StockTransaction.__table__.update()
                .where(StockTransaction.inventory_record_id == alias_record.id)
                .values(inventory_record_id=canonical_record.id)
            )
            await session.delete(alias_record)

    alias = ProductJanAlias(alias_jan=alias_jan, canonical_jan=canonical_jan, note=note)
    session.add(alias)
    await session.commit()
    return alias


async def remove_alias(session: AsyncSession, alias_jan: str) -> None:
    alias = await session.get(ProductJanAlias, alias_jan)
    if alias is None:
        raise ValueError(f"别名 {alias_jan} 不存在")
    await session.delete(alias)
    await session.commit()
