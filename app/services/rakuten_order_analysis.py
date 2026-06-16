"""Rakuten order analysis service.

Parses Rakuten RMS order-detail CSV/XLSX files (cp932 / utf-8-sig), resolves
JAN codes via the shared `resolve_jan_quantities` (see
`app/common/jan_resolver.py` and `Shipping-tools/JAN_QUANTITY_SPEC.md`),
aggregates quantities per JAN, and compares against 乐天仓库 inventory.

Lines whose JAN cannot be resolved are returned as `unresolved` for manual
SKU/JAN registration ("需人工登记新SKU/JAN"). `analyse_rakuten_orders` itself
performs no stock mutations; the resulting draft can be applied via
`apply_rakuten_order_draft`, which deducts 乐天仓库 stock for `status=="ok"`
lines and leaves `insufficient` / `no_record` / `unknown` lines (plus
`unresolved`) for "调货" follow-up.
"""
from __future__ import annotations

import io
from collections import defaultdict

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.jan_resolver import resolve_jan_quantities
from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.models.rakuten_order_draft import RakutenOrderDraft
from app.models.stock_transaction import StockTransaction
from app.models.warehouse import Warehouse
from app.schemas.inventory import (
    RakutenOrderAnalysisResult,
    RakutenOrderApplyResult,
    RakutenOrderDraftDocument,
    RakutenOrderLine,
    RakutenOrderMutation,
    StockOutCreate,
    StockTransactionRead,
    UnresolvedOrderLine,
)
from app.services.inventory import (
    InsufficientStockError,
    InventoryRecordNotFoundError,
    stock_out_item,
)


# Columns required from the Rakuten order CSV
_NEEDED_COLS = ["商品番号", "システム連携用SKU番号", "個数"]

# dtype overrides to prevent pandas from mangling product numbers / phone numbers
_DTYPE = {"商品番号": str, "システム連携用SKU番号": str, "商品管理番号": str, "SKU管理番号": str}

RAKUTEN_WAREHOUSE_NAME = "乐天仓库"
RAKUTEN_ORDER_SOURCE = "rakuten_order"
DEFAULT_RAKUTEN_ORDER_CUSTOMER = "乐天"


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def _detect_encoding(raw: bytes) -> str:
    """Try common Japanese encodings; return the first that decodes cleanly."""
    for enc in ("cp932", "utf-8-sig", "shift_jis", "utf-8"):
        try:
            raw.decode(enc)
            return enc
        except (UnicodeDecodeError, LookupError):
            continue
    return "cp932"  # fallback with errors='replace'


def _read_order_file(filename: str, content: bytes) -> tuple[pd.DataFrame, int]:
    """Read a Rakuten order file (CSV or XLSX) and return (df with needed cols, raw line count)."""
    name_lower = filename.lower()
    if name_lower.endswith(".xlsx") or name_lower.endswith(".xls"):
        df = pd.read_excel(io.BytesIO(content), dtype=_DTYPE)
    else:
        enc = _detect_encoding(content)
        try:
            df = pd.read_csv(
                io.BytesIO(content),
                dtype=_DTYPE,
                encoding=enc,
                encoding_errors="replace",
            )
        except TypeError:
            # pandas < 1.3 does not support encoding_errors keyword
            df = pd.read_csv(
                io.BytesIO(content),
                dtype=_DTYPE,
                encoding=enc,
            )

    # Keep only the columns we need (ignore missing optional cols gracefully)
    available = [c for c in _NEEDED_COLS if c in df.columns]
    if "商品番号" not in available:
        raise ValueError(f"ファイル '{filename}' に '商品番号' 列が見つかりません")

    df = df[available].copy()
    if "システム連携用SKU番号" not in df.columns:
        df["システム連携用SKU番号"] = ""
    if "個数" not in df.columns:
        df["個数"] = 1

    raw_count = len(df)
    df = df.dropna(subset=["商品番号"])
    return df, raw_count


def _parse_order_count(raw) -> int:
    try:
        order_count = int(float(raw))
    except (ValueError, TypeError):
        order_count = 1
    return order_count if order_count > 0 else 1


def _aggregate_orders(
    *dfs: tuple[pd.DataFrame, int],
) -> tuple[dict[str, int], list[UnresolvedOrderLine], list[int]]:
    """Aggregate JAN → total_quantity across all DataFrames.

    Returns (jan_totals, unresolved_lines, per_file_line_counts).
    """
    jan_totals: dict[str, int] = defaultdict(int)
    unresolved: list[UnresolvedOrderLine] = []
    line_counts: list[int] = []

    for df, raw_count in dfs:
        line_counts.append(raw_count)
        for _, row in df.iterrows():
            product_number = str(row["商品番号"]).strip()
            if not product_number or product_number.lower() in ("nan", "none"):
                continue
            sku_number = str(row.get("システム連携用SKU番号", "") or "").strip()
            if sku_number.lower() in ("nan", "none"):
                sku_number = ""
            order_count = _parse_order_count(row.get("個数", 1))

            resolved = resolve_jan_quantities(product_number, sku_number, order_count)
            if not resolved:
                unresolved.append(UnresolvedOrderLine(
                    product_number=product_number,
                    sku_number=sku_number or None,
                    quantity=order_count,
                ))
                continue
            for jan, qty in resolved:
                jan_totals[jan] += qty

    return dict(jan_totals), unresolved, line_counts


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------

async def analyse_rakuten_orders(
    session: AsyncSession,
    file1_name: str,
    file1_content: bytes,
    file2_name: str | None = None,
    file2_content: bytes | None = None,
) -> RakutenOrderAnalysisResult:
    """Parse order files and compare against 乐天仓库 inventory, creating a draft."""

    df1, rc1 = _read_order_file(file1_name, file1_content)
    pairs: list[tuple[pd.DataFrame, int]] = [(df1, rc1)]

    rc2 = 0
    if file2_name and file2_content:
        df2, rc2 = _read_order_file(file2_name, file2_content)
        pairs.append((df2, rc2))

    jan_totals, unresolved, line_counts = _aggregate_orders(*pairs)

    # Fetch 乐天仓库
    warehouse = await session.scalar(
        select(Warehouse).where(Warehouse.name == RAKUTEN_WAREHOUSE_NAME)
    )

    # Bulk-fetch all relevant products and inventory records
    if jan_totals:
        jan_list = list(jan_totals.keys())
        products_rows = await session.scalars(
            select(Product).where(Product.jan_code.in_(jan_list))
        )
        products: dict[str, Product] = {p.jan_code: p for p in products_rows.all()}

        if warehouse:
            inv_rows = await session.scalars(
                select(InventoryRecord).where(
                    InventoryRecord.product_jan.in_(jan_list),
                    InventoryRecord.warehouse_id == warehouse.id,
                )
            )
            inventory: dict[str, int] = {}
            for rec in inv_rows.all():
                inventory[rec.product_jan] = inventory.get(rec.product_jan, 0) + rec.quantity
        else:
            inventory = {}
    else:
        products = {}
        inventory = {}

    items: list[RakutenOrderLine] = []
    unknown_jan_count = 0

    for jan, ordered_qty in sorted(jan_totals.items()):
        product = products.get(jan)
        if product is None:
            unknown_jan_count += 1
            items.append(RakutenOrderLine(
                jan_code=jan,
                product_name=None,
                ordered_qty=ordered_qty,
                current_stock=None,
                shortage=ordered_qty,
                status="unknown",
            ))
            continue

        current_stock = inventory.get(jan)
        if current_stock is None:
            shortage = ordered_qty
            status = "no_record"
        elif current_stock >= ordered_qty:
            shortage = 0
            status = "ok"
        else:
            shortage = ordered_qty - current_stock
            status = "insufficient"

        items.append(RakutenOrderLine(
            jan_code=jan,
            product_name=product.name_jp,
            ordered_qty=ordered_qty,
            current_stock=current_stock,
            shortage=shortage,
            status=status,
        ))

    # Sort: problems first (unknown → no_record → insufficient → ok), then jan_code
    _order = {"unknown": 0, "no_record": 1, "insufficient": 2, "ok": 3}
    items.sort(key=lambda x: (_order.get(x.status, 9), x.jan_code))

    draft = await create_rakuten_order_draft(
        session=session,
        items=items,
        unresolved=unresolved,
        original_filename=file1_name if not file2_name else f"{file1_name}, {file2_name}",
    )

    return RakutenOrderAnalysisResult(
        draft_id=draft.id,
        store1_lines=line_counts[0] if line_counts else 0,
        store2_lines=line_counts[1] if len(line_counts) > 1 else 0,
        unresolved_count=len(unresolved),
        unknown_jan_count=unknown_jan_count,
        items=items,
        unresolved=unresolved,
    )


# ---------------------------------------------------------------------------
# Draft-Apply
# ---------------------------------------------------------------------------

async def create_rakuten_order_draft(
    session: AsyncSession,
    items: list[RakutenOrderLine],
    unresolved: list[UnresolvedOrderLine],
    original_filename: str,
) -> RakutenOrderDraft:
    document = RakutenOrderDraftDocument(items=items, unresolved=unresolved)
    draft = RakutenOrderDraft(
        original_filename=original_filename,
        status="parsed",
        document=document.model_dump(mode="json"),
    )
    session.add(draft)
    await session.commit()
    await session.refresh(draft)
    return draft


async def get_rakuten_order_draft(
    session: AsyncSession,
    draft_id: int,
    *,
    with_for_update: bool = False,
) -> RakutenOrderDraft | None:
    stmt = select(RakutenOrderDraft).where(RakutenOrderDraft.id == draft_id)
    if with_for_update:
        stmt = stmt.with_for_update()
    return await session.scalar(stmt)


async def apply_rakuten_order_draft(
    session: AsyncSession,
    draft: RakutenOrderDraft,
    user_id: int | None = None,
) -> RakutenOrderApplyResult:
    document = RakutenOrderDraftDocument.model_validate(draft.document)

    warehouse = await session.scalar(
        select(Warehouse).where(Warehouse.name == RAKUTEN_WAREHOUSE_NAME)
    )
    if warehouse is None:
        return RakutenOrderApplyResult(
            applied=False,
            shortage_items=document.items,
            unresolved=document.unresolved,
        )

    mutations: list[RakutenOrderMutation] = []
    shortage_items: list[RakutenOrderLine] = []
    skipped_duplicates = 0

    for item in document.items:
        if item.status != "ok":
            shortage_items.append(item)
            continue

        reference_id = f"rakuten_order:{draft.id}:{item.jan_code}"
        existing = await session.scalar(
            select(StockTransaction.id).where(
                StockTransaction.source == RAKUTEN_ORDER_SOURCE,
                StockTransaction.reference_id == reference_id,
            ).limit(1)
        )
        if existing:
            skipped_duplicates += 1
            continue

        try:
            result = await stock_out_item(
                session=session,
                payload=StockOutCreate(
                    sku=item.jan_code,
                    warehouse_id=warehouse.id,
                    quantity=item.ordered_qty,
                    source=RAKUTEN_ORDER_SOURCE,
                    reference_id=reference_id,
                    note="乐天采购分析自动出库",
                    customer=DEFAULT_RAKUTEN_ORDER_CUSTOMER,
                ),
                commit=False,
                user_id=user_id,
            )
        except (InsufficientStockError, InventoryRecordNotFoundError):
            shortage_items.append(item)
            continue

        mutations.append(RakutenOrderMutation(
            jan_code=item.jan_code,
            quantity=item.ordered_qty,
            transaction=StockTransactionRead.model_validate(result.transaction),
            low_stock_alert=result.low_stock_alert,
        ))

    draft.status = "applied"
    await session.commit()
    await session.refresh(draft)

    return RakutenOrderApplyResult(
        applied=True,
        mutations=mutations,
        shortage_items=shortage_items,
        unresolved=document.unresolved,
        skipped_duplicates=skipped_duplicates,
    )
