"""Rakuten order analysis service.

Parses Rakuten RMS order-detail CSV/XLSX files (cp932 / utf-8-sig),
aggregates quantities per JAN, and compares against 乐天仓库 inventory.
No stock mutations are performed.
"""
from __future__ import annotations

import io
from collections import defaultdict

import pandas as pd
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.models.warehouse import Warehouse


# Columns required from the Rakuten order CSV
_NEEDED_COLS = ["商品番号", "個数"]

# dtype overrides to prevent pandas from mangling product numbers / phone numbers
_DTYPE = {"商品番号": str, "商品管理番号": str, "SKU管理番号": str}

# Product numbers matching these patterns are silently skipped (no JAN, handled offline)
_SKIP_PREFIXES = ("decorte-",)


# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------

class OrderedItem(BaseModel):
    jan_code: str
    product_name: str | None
    ordered_qty: int
    current_stock: int | None  # None = product in DB but no 乐天仓库 record
    shortage: int               # max(0, ordered - max(0, stock))
    status: str                 # "ok" | "insufficient" | "no_record" | "unknown"


class OrderAnalysisResult(BaseModel):
    store1_lines: int           # raw item-lines parsed from file 1
    store2_lines: int           # 0 if only one file uploaded
    silently_skipped: int       # decorte-* etc.
    unknown_jan_count: int      # JAN not found in WMS product catalog
    items: list[OrderedItem]    # aggregated, sorted by status then jan_code


# ---------------------------------------------------------------------------
# Parsing helpers (mirrors merge_tool.py logic, read-only)
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
    if "個数" not in df.columns:
        df["個数"] = 1

    raw_count = len(df)
    df = df.dropna(subset=["商品番号"])
    return df, raw_count


def _parse_product_number(product_number: str, order_count_raw) -> tuple[str, int] | None:
    """Convert 商品番号 + 個数 into (jan_code, total_quantity).

    Format: JAN[-setCount]  (e.g. "4902806314946-2" means 2 units/set)
    Returns None for non-JAN entries (decorte-*, empty, etc.).
    """
    p = str(product_number).strip()
    if not p or p.lower() in ("nan", "none", ""):
        return None

    # Silently skip known non-JAN patterns
    p_lower = p.lower()
    if any(p_lower.startswith(prefix) for prefix in _SKIP_PREFIXES):
        return None
    # Also skip if the barcode part contains letters (not a real JAN)
    barcode_part = p.rsplit("-", 1)[0] if "-" in p else p
    if not barcode_part.isdigit():
        return None

    try:
        order_count = int(float(order_count_raw))
    except (ValueError, TypeError):
        order_count = 1
    if order_count <= 0:
        order_count = 1

    if "-" in p:
        parts = p.rsplit("-", 1)
        barcode = parts[0]
        try:
            set_count = int(parts[1])
        except ValueError:
            set_count = 1
    else:
        barcode = p
        set_count = 1

    if set_count <= 0:
        set_count = 1

    return barcode, set_count * order_count


def _aggregate_orders(*dfs: tuple[pd.DataFrame, int]) -> tuple[dict[str, int], int, list[int]]:
    """Aggregate JAN → total_quantity across all DataFrames.

    Returns (jan_totals, silently_skipped_count, per_file_line_counts).
    """
    jan_totals: dict[str, int] = defaultdict(int)
    skipped = 0
    line_counts: list[int] = []

    for df, raw_count in dfs:
        line_counts.append(raw_count)
        for _, row in df.iterrows():
            result = _parse_product_number(row["商品番号"], row.get("個数", 1))
            if result is None:
                skipped += 1
            else:
                jan, qty = result
                jan_totals[jan] += qty

    return dict(jan_totals), skipped, line_counts


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------

RAKUTEN_WAREHOUSE_NAME = "乐天仓库"


async def analyse_rakuten_orders(
    session: AsyncSession,
    file1_name: str,
    file1_content: bytes,
    file2_name: str | None = None,
    file2_content: bytes | None = None,
) -> OrderAnalysisResult:
    """Parse order files and compare against 乐天仓库 inventory."""

    df1, rc1 = _read_order_file(file1_name, file1_content)
    pairs: list[tuple[pd.DataFrame, int]] = [(df1, rc1)]

    rc2 = 0
    if file2_name and file2_content:
        df2, rc2 = _read_order_file(file2_name, file2_content)
        pairs.append((df2, rc2))

    jan_totals, skipped, line_counts = _aggregate_orders(*pairs)

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

    items: list[OrderedItem] = []
    unknown_jan_count = 0

    for jan, ordered_qty in sorted(jan_totals.items()):
        product = products.get(jan)
        if product is None:
            unknown_jan_count += 1
            items.append(OrderedItem(
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

        items.append(OrderedItem(
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

    return OrderAnalysisResult(
        store1_lines=line_counts[0] if line_counts else 0,
        store2_lines=line_counts[1] if len(line_counts) > 1 else 0,
        silently_skipped=skipped,
        unknown_jan_count=unknown_jan_count,
        items=items,
    )
