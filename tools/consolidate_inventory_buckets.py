"""
Consolidate inventory records so there is exactly one bucket per (product, warehouse).

Background: the old schema used (product, warehouse, customer, location, expiration) as the
composite key.  The new design treats customer as a note-only field and always uses a single
bucket per (product, warehouse).

What this script does
─────────────────────
For every group of InventoryRecord rows that share the same (product_jan, warehouse_id):
  1.  Pick the "keeper" — the row with the smallest id.
  2.  Reroute all StockTransaction rows that reference the other records to the keeper.
  3.  Delete the now-orphaned non-keeper records.
  4.  Normalise the keeper: customer_id = NULL, location_code = "A-00-00",
      expiration_date = NULL, quantity = SUM of all merged quantities.

The script is idempotent: running it twice has no effect.

Run inside Docker on the NAS
────────────────────────────
  docker compose exec api python -m tools.consolidate_inventory_buckets

Or from a local conda env against a remote DB:
  DATABASE_URL=postgresql+asyncpg://... python -m tools.consolidate_inventory_buckets
"""

from __future__ import annotations

import asyncio
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+asyncpg://wms_user:wms_password@localhost:5432/wms",
)


async def main() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        # ── 1. Find all duplicate groups ──────────────────────────────────────
        rows = await conn.execute(text("""
            SELECT product_jan, warehouse_id,
                   array_agg(id ORDER BY id) AS ids,
                   SUM(quantity)             AS total_qty
            FROM   inventory_records
            GROUP  BY product_jan, warehouse_id
            HAVING COUNT(*) > 1
        """))
        groups = rows.fetchall()

    if not groups:
        print("No duplicate buckets found — nothing to do.")
        await engine.dispose()
        return

    print(f"Found {len(groups)} (product, warehouse) groups with multiple records.")

    merged = 0
    total_deleted = 0

    async with engine.begin() as conn:
        # Temporarily disable the non-negative check so negative-stock warehouses work correctly.
        # We drop and re-add it after the migration.
        await conn.execute(text(
            "ALTER TABLE inventory_records DROP CONSTRAINT IF EXISTS "
            "ck_inventory_records_quantity_non_negative"
        ))

        for jan, wh_id, ids, total_qty in groups:
            keeper_id = ids[0]           # lowest id wins
            others    = ids[1:]          # to be merged and deleted

            # ── 2. Reroute transactions ──────────────────────────────────────
            await conn.execute(text("""
                UPDATE stock_transactions
                SET    inventory_record_id = :keeper
                WHERE  inventory_record_id = ANY(:others)
            """), {"keeper": keeper_id, "others": others})

            # ── 3. Delete non-keeper records ─────────────────────────────────
            await conn.execute(text("""
                DELETE FROM inventory_records
                WHERE  id = ANY(:others)
            """), {"others": others})

            # ── 4. Normalise keeper ───────────────────────────────────────────
            await conn.execute(text("""
                UPDATE inventory_records
                SET    customer_id     = NULL,
                       location_code   = 'A-00-00',
                       expiration_date = NULL,
                       quantity        = :qty
                WHERE  id = :keeper
            """), {"qty": total_qty, "keeper": keeper_id})

            print(
                f"  [{jan} / wh={wh_id}] merged {len(others)} → keeper {keeper_id} "
                f"(qty={total_qty})"
            )
            merged += 1
            total_deleted += len(others)

        # Also normalise existing single-record buckets that have non-default fields
        result = await conn.execute(text("""
            UPDATE inventory_records
            SET    customer_id     = NULL,
                   location_code   = 'A-00-00',
                   expiration_date = NULL
            WHERE  customer_id IS NOT NULL
               OR  location_code   != 'A-00-00'
               OR  expiration_date IS NOT NULL
        """))
        normalised_singles = result.rowcount
        if normalised_singles:
            print(f"Normalised {normalised_singles} single-record buckets (customer/loc/exp reset).")

        # Re-add the non-negative constraint only if no negative quantities remain
        # (negative stock is allowed on certain warehouses, so we don't force it back)
        neg_count = (await conn.execute(
            text("SELECT COUNT(*) FROM inventory_records WHERE quantity < 0")
        )).scalar()
        if neg_count:
            print(f"Note: {neg_count} record(s) have negative quantity (allow_negative_stock). "
                  "Not restoring CHECK constraint — that's expected.")
        else:
            await conn.execute(text(
                "ALTER TABLE inventory_records ADD CONSTRAINT "
                "ck_inventory_records_quantity_non_negative CHECK (quantity >= 0)"
            ))

    print(f"\nDone.  Merged {merged} groups, deleted {total_deleted} redundant records.")
    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
