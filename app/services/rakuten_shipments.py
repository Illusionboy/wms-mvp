import csv
from collections import defaultdict
from io import StringIO
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.inventory_record import InventoryRecord
from app.models.rakuten_shipment_draft import RakutenShipmentDraft
from app.models.warehouse import Warehouse
from app.schemas.inventory import (
    ProductRead,
    RakutenShipmentDraftDocument,
    RakutenShipmentImportResult,
    RakutenShipmentIssue,
    RakutenShipmentLine,
    RakutenShipmentMutation,
    StockOutCreate,
    StockTransactionRead,
)
from app.services.inventory import InsufficientStockError, InventoryRecordNotFoundError, search_inventory_items, stock_out_item
from app.tools.convert_rakuten_csv_encoding import decode_csv_bytes


DEFAULT_RAKUTEN_WAREHOUSE = "乐天仓库"
DEFAULT_RAKUTEN_CUSTOMER = "乐天"
RAKUTEN_SOURCE = "rakuten_csv"
IGNORABLE_RAKUTEN_ISSUE_TYPES = {
    "product_not_found",
    "inventory_record_not_found",
    "insufficient_stock",
}


def parse_rakuten_shipment_csv(content: bytes) -> list[RakutenShipmentLine]:
    text, _ = decode_csv_bytes(content)
    reader = csv.DictReader(StringIO(text))
    lines: list[RakutenShipmentLine] = []
    for row in reader:
        raw_product_number = _clean_text(row.get("商品番号"))
        if not raw_product_number:
            continue
        parsed = parse_rakuten_product_number(
            raw_product_number=raw_product_number,
            order_count_value=row.get("個数"),
        )
        if parsed is None:
            continue
        jan_code, quantity = parsed
        lines.append(
            RakutenShipmentLine(
                jan_code=jan_code,
                quantity=quantity,
                order_number=_clean_text(row.get("注文番号")) or None,
                product_name=_clean_text(row.get("商品名")) or None,
                raw_product_number=raw_product_number,
            )
        )
    return lines


def parse_rakuten_product_number(raw_product_number: str, order_count_value: object) -> tuple[str, int] | None:
    product_number = _clean_text(raw_product_number)
    if not product_number:
        return None
    if "decorte-sf-new" in product_number.lower():
        return None

    order_count = _parse_positive_int(order_count_value, default=1)
    if "-" in product_number:
        jan_code, raw_set_count = product_number.rsplit("-", 1)
        set_count = _parse_positive_int(raw_set_count, default=1)
    else:
        jan_code = product_number
        set_count = 1

    jan_code = "".join(ch for ch in jan_code if ch.isdigit())
    if not jan_code:
        return None
    return jan_code, set_count * order_count


async def import_rakuten_shipment_csv(
    session: AsyncSession,
    content: bytes,
    warehouse_name: str = DEFAULT_RAKUTEN_WAREHOUSE,
    customer_name: str = DEFAULT_RAKUTEN_CUSTOMER,
) -> RakutenShipmentImportResult:
    lines = parse_rakuten_shipment_csv(content)
    merged_lines = _merge_shipment_lines(lines)
    return await apply_rakuten_shipment_lines(
        session=session,
        lines=merged_lines,
        warehouse_name=warehouse_name,
        customer_name=customer_name,
    )


async def create_rakuten_shipment_draft(
    session: AsyncSession,
    content: bytes,
    original_filename: str,
    warehouse_name: str = DEFAULT_RAKUTEN_WAREHOUSE,
    customer_name: str = DEFAULT_RAKUTEN_CUSTOMER,
    telegram_user_id: int | None = None,
) -> RakutenShipmentDraft:
    lines = _merge_shipment_lines(parse_rakuten_shipment_csv(content))
    document = RakutenShipmentDraftDocument(
        warehouse_name=warehouse_name,
        customer_name=customer_name,
        lines=lines,
    )
    draft = RakutenShipmentDraft(
        telegram_user_id=telegram_user_id,
        original_filename=original_filename,
        status="parsed",
        warehouse_name=warehouse_name,
        customer_name=customer_name,
        document=document.model_dump(mode="json"),
    )
    session.add(draft)
    await session.commit()
    await session.refresh(draft)
    return draft


async def get_rakuten_shipment_draft(session: AsyncSession, draft_id: int) -> RakutenShipmentDraft | None:
    return await session.scalar(select(RakutenShipmentDraft).where(RakutenShipmentDraft.id == draft_id))


async def preview_rakuten_shipment_draft(
    session: AsyncSession,
    draft: RakutenShipmentDraft,
) -> RakutenShipmentImportResult:
    document = RakutenShipmentDraftDocument.model_validate(draft.document)
    issues, _ = await _validate_rakuten_shipment_lines(
        session=session,
        lines=document.lines,
        warehouse_name=document.warehouse_name,
        customer_name=document.customer_name,
    )
    return RakutenShipmentImportResult(applied=False, total_lines=len(document.lines), issues=issues)


async def apply_rakuten_shipment_draft(
    session: AsyncSession,
    draft: RakutenShipmentDraft,
    ignore_missing: bool = False,
) -> RakutenShipmentImportResult:
    document = RakutenShipmentDraftDocument.model_validate(draft.document)
    result = await apply_rakuten_shipment_lines(
        session=session,
        lines=document.lines,
        warehouse_name=document.warehouse_name,
        customer_name=document.customer_name,
        ignore_missing=ignore_missing,
    )
    if result.applied:
        draft.status = "applied_with_skips" if result.issues else "applied"
        await session.commit()
        await session.refresh(draft)
    return result


async def apply_rakuten_shipment_lines(
    session: AsyncSession,
    lines: list[RakutenShipmentLine],
    warehouse_name: str = DEFAULT_RAKUTEN_WAREHOUSE,
    customer_name: str = DEFAULT_RAKUTEN_CUSTOMER,
    ignore_missing: bool = False,
) -> RakutenShipmentImportResult:
    issues, resolved = await _validate_rakuten_shipment_lines(
        session=session,
        lines=lines,
        warehouse_name=warehouse_name,
        customer_name=customer_name,
    )
    ignored_issues: list[RakutenShipmentIssue] = []
    if ignore_missing:
        ignored_issues = [
            issue for issue in issues if issue.issue_type in IGNORABLE_RAKUTEN_ISSUE_TYPES
        ]
        issues = [
            issue for issue in issues if issue.issue_type not in IGNORABLE_RAKUTEN_ISSUE_TYPES
        ]

    if issues:
        return RakutenShipmentImportResult(applied=False, total_lines=len(lines), issues=issues)

    mutations: list[RakutenShipmentMutation] = []
    reference_id = f"rakuten_csv:{uuid4().hex}"
    for _, jan_code, quantity, record in resolved:
        try:
            result = await stock_out_item(
                session=session,
                payload=StockOutCreate(
                    sku=jan_code,
                    warehouse_id=record.warehouse_id,
                    customer_id=record.customer_id,
                    quantity=quantity,
                    source=RAKUTEN_SOURCE,
                    location_code=record.location_code,
                    expiration_date=record.expiration_date,
                    reference_id=reference_id,
                    note="rakuten shipment csv",
                ),
            )
        except (InsufficientStockError, InventoryRecordNotFoundError) as exc:
            raise RuntimeError(f"Rakuten shipment import failed after validation: {exc}") from exc
        mutations.append(
            RakutenShipmentMutation(
                jan_code=jan_code,
                quantity=quantity,
                transaction=StockTransactionRead.model_validate(result.transaction),
                low_stock_alert=result.low_stock_alert,
            )
        )

    return RakutenShipmentImportResult(
        applied=True,
        total_lines=len(lines),
        mutations=mutations,
        issues=ignored_issues,
    )


async def _validate_rakuten_shipment_lines(
    session: AsyncSession,
    lines: list[RakutenShipmentLine],
    warehouse_name: str,
    customer_name: str,
) -> tuple[list[RakutenShipmentIssue], list[tuple[int, str, int, InventoryRecord]]]:
    warehouse = await _resolve_warehouse(session, warehouse_name)
    customer = await _resolve_customer(session, customer_name)
    issues: list[RakutenShipmentIssue] = []

    if not lines:
        issues.append(
            RakutenShipmentIssue(
                line_index=-1,
                jan_code="",
                issue_type="empty_csv",
                message="No valid Rakuten shipment lines were parsed from this CSV.",
            )
        )

    if warehouse is None:
        issues.append(
            RakutenShipmentIssue(
                line_index=-1,
                jan_code="",
                issue_type="warehouse_not_found",
                message=f"Warehouse not found: {warehouse_name}",
            )
        )
    if customer is None:
        issues.append(
            RakutenShipmentIssue(
                line_index=-1,
                jan_code="",
                issue_type="customer_not_found",
                message=f"Customer not found: {customer_name}",
            )
        )

    resolved: list[tuple[int, str, int, InventoryRecord]] = []
    for index, line in enumerate(lines):
        products = await search_inventory_items(session=session, keyword=line.jan_code, limit=6)
        if not products:
            issues.append(
                RakutenShipmentIssue(
                    line_index=index,
                    jan_code=line.jan_code,
                    issue_type="product_not_found",
                    message=f"Product not found: {line.jan_code}",
                )
            )
            continue
        if len(products) > 1:
            issues.append(
                RakutenShipmentIssue(
                    line_index=index,
                    jan_code=line.jan_code,
                    issue_type="ambiguous_product",
                    message="Multiple products matched. Confirm with full JAN before applying.",
                    candidates=[ProductRead.model_validate(product) for product in products],
                )
            )
            continue
        if warehouse is None or customer is None:
            continue

        record = await _resolve_first_inventory_record(
            session=session,
            jan_code=products[0].jan_code,
            warehouse_id=warehouse.id,
            customer_id=customer.id,
        )
        if record is None:
            issues.append(
                RakutenShipmentIssue(
                    line_index=index,
                    jan_code=line.jan_code,
                    issue_type="inventory_record_not_found",
                    message=f"No stock record found for {products[0].jan_code}.",
                )
            )
            continue
        if record.quantity < line.quantity:
            issues.append(
                RakutenShipmentIssue(
                    line_index=index,
                    jan_code=line.jan_code,
                    issue_type="insufficient_stock",
                    message=f"Insufficient stock for {products[0].jan_code}: have {record.quantity}, need {line.quantity}.",
                )
            )
            continue
        resolved.append((index, products[0].jan_code, line.quantity, record))

    return issues, resolved


def _merge_shipment_lines(lines: list[RakutenShipmentLine]) -> list[RakutenShipmentLine]:
    quantities: defaultdict[str, int] = defaultdict(int)
    first_line: dict[str, RakutenShipmentLine] = {}
    for line in lines:
        quantities[line.jan_code] += line.quantity
        first_line.setdefault(line.jan_code, line)
    return [
        first_line[jan_code].model_copy(update={"quantity": quantity})
        for jan_code, quantity in quantities.items()
    ]


async def _resolve_warehouse(session: AsyncSession, warehouse_name: str) -> Warehouse | None:
    return await session.scalar(
        select(Warehouse)
        .where(Warehouse.name.ilike(f"%{warehouse_name}%"))
        .order_by(Warehouse.id.asc())
        .limit(1)
    )


async def _resolve_customer(session: AsyncSession, customer_name: str) -> Customer | None:
    return await session.scalar(
        select(Customer)
        .where(Customer.name.ilike(f"%{customer_name}%"))
        .order_by(Customer.id.asc())
        .limit(1)
    )


async def _resolve_first_inventory_record(
    session: AsyncSession,
    jan_code: str,
    warehouse_id: int,
    customer_id: int | None,
) -> InventoryRecord | None:
    return await session.scalar(
        select(InventoryRecord)
        .where(
            InventoryRecord.product_jan == jan_code,
            InventoryRecord.warehouse_id == warehouse_id,
            InventoryRecord.customer_id == customer_id,
        )
        .order_by(InventoryRecord.id.asc())
        .limit(1)
    )


def _parse_positive_int(value: object, default: int) -> int:
    try:
        parsed = int(float(_clean_text(value)))
    except ValueError:
        return default
    if parsed <= 0:
        return default
    return parsed


def _clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() == "nan":
        return ""
    if text.endswith(".0"):
        text = text[:-2]
    return text
