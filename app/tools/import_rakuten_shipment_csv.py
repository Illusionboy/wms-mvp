import argparse
import asyncio
from pathlib import Path

from app.db.init_db import init_db
from app.db.session import AsyncSessionLocal, engine
from app.services.rakuten_shipments import import_rakuten_shipment_csv, parse_rakuten_shipment_csv


async def main() -> None:
    args = _parse_args()
    content = Path(args.file).read_bytes()
    if args.preview:
        lines = parse_rakuten_shipment_csv(content)
        for line in lines:
            print(f"{line.jan_code},{line.quantity},{line.raw_product_number},{line.order_number or ''}")
        print(f"Parsed lines: {len(lines)}")
        return

    await init_db()
    async with AsyncSessionLocal() as session:
        result = await import_rakuten_shipment_csv(
            session=session,
            content=content,
            warehouse_name=args.warehouse,
            customer_name=args.customer,
        )
    await engine.dispose()

    if not result.applied:
        print("Not applied. Issues:")
        for issue in result.issues:
            print(f"- line {issue.line_index + 1}: {issue.issue_type}: {issue.message}")
            for candidate in issue.candidates:
                print(f"  candidate: {candidate.jan_code} {candidate.name_jp}")
        raise SystemExit(1)

    print(f"Applied Rakuten shipment CSV. Items: {len(result.mutations)}")
    for mutation in result.mutations:
        print(f"- {mutation.jan_code}: -{mutation.quantity}, tx={mutation.transaction.id}")
        if mutation.low_stock_alert:
            alert = mutation.low_stock_alert
            print(f"  LOW STOCK: {alert.product_name}, remaining={alert.total_quantity}, threshold={alert.threshold_quantity}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import Rakuten RMS shipment CSV as stock-out records.")
    parser.add_argument("--file", required=True, help="Rakuten RMS CSV path.")
    parser.add_argument("--warehouse", default="乐天仓库", help="Warehouse name. Default: 乐天仓库")
    parser.add_argument("--customer", default="乐天", help="Customer name. Default: 乐天")
    parser.add_argument("--preview", action="store_true", help="Only parse JAN and quantity. Do not update database.")
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main())
