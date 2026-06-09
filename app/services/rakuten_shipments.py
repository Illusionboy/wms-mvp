import csv
from collections import defaultdict
from io import StringIO
from typing import NamedTuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.models.rakuten_shipment_draft import RakutenShipmentDraft
from app.models.stock_transaction import StockTransaction
from app.models.warehouse import Warehouse
from app.schemas.inventory import (
    NonJanLine,
    ProductRead,
    RakutenDraftPreview,
    RakutenShipmentDraftDocument,
    RakutenShipmentImportResult,
    RakutenShipmentIssue,
    RakutenShipmentLine,
    RakutenShipmentMutation,
    StockOutCreate,
    StockTransactionRead,
)
from app.services.inventory import (
    InsufficientStockError,
    InventoryRecordNotFoundError,
    resolve_customer,
    resolve_warehouse,
    search_inventory_items,
    stock_out_item,
)
from app.tools.convert_rakuten_csv_encoding import decode_csv_bytes


DEFAULT_RAKUTEN_WAREHOUSE = "乐天仓库"
DEFAULT_RAKUTEN_CUSTOMER = "乐天"
RAKUTEN_SOURCE = "rakuten_csv"


class _ValidationResult(NamedTuple):
    blocking_issues: list[RakutenShipmentIssue]
    needs_decision: list[RakutenShipmentIssue]  # no record or insufficient stock
    resolved: list[tuple[int, str, int, InventoryRecord]]
    auto_skipped_count: int  # product_not_found lines silently dropped


def parse_rakuten_shipment_csv(content: bytes) -> tuple[list[RakutenShipmentLine], list[NonJanLine]]:
    text, _ = decode_csv_bytes(content)
    reader = csv.DictReader(StringIO(text))
    lines: list[RakutenShipmentLine] = []
    non_jan: list[NonJanLine] = []
    for row in reader:
        raw_product_number = _clean_text(row.get("商品番号"))
        if not raw_product_number:
            continue
        sku_number = _clean_text(row.get("システム連携用SKU番号"))
        order_number = _clean_text(row.get("注文番号")) or None
        product_name = _clean_text(row.get("商品名")) or None
        new_lines, err = _parse_rakuten_row(
            product_number=raw_product_number,
            sku_number=sku_number,
            order_count_value=row.get("個数"),
            order_number=order_number,
            product_name=product_name,
        )
        lines.extend(new_lines)
        if err is not None:
            non_jan.append(err)
    return lines, non_jan


def _parse_rakuten_row(
    product_number: str,
    sku_number: str,
    order_count_value: object,
    order_number: str | None,
    product_name: str | None,
) -> tuple[list[RakutenShipmentLine], NonJanLine | None]:
    """Implements JAN_QUANTITY_SPEC.md resolution logic.

    Returns (shipment_lines, non_jan_err). Exactly one side is non-empty.
    Bundle products (套装) expand into multiple lines, one per JAN.
    """
    order_count = _parse_positive_int(order_count_value, default=1)

    # --- Step 1: parse 商品番号 for barcode + set_count ---
    barcode = product_number
    set_count = 1
    if "-" in product_number:
        parts = product_number.rsplit("-", 1)
        suffix = parts[1].strip()
        if suffix.isdigit() and 1 <= len(suffix) <= 3:
            barcode = parts[0].strip()
            set_count = int(suffix) if int(suffix) > 0 else 1

    # 13-digit JAN in 商品番号 → use directly, skip システム連携用SKU番号
    if barcode.isdigit() and len(barcode) == 13:
        return [RakutenShipmentLine(
            jan_code=barcode,
            quantity=set_count * order_count,
            order_number=order_number,
            product_name=product_name,
            raw_product_number=product_number,
        )], None

    # --- Step 2: use システム連携用SKU番号 ---
    if sku_number:
        sys_parts = sku_number.split("-")

        # Bundle detection: 13-digit + one-or-more 4-digit parts + trailing digit count
        # e.g. "4971710376227-7002-2" → JANs [4971710376227, 4971710377002], qty = order_count each
        if (
            len(sys_parts) >= 3
            and sys_parts[0].isdigit() and len(sys_parts[0]) == 13
            and all(p.isdigit() and len(p) == 4 for p in sys_parts[1:-1])
            and sys_parts[-1].isdigit()
        ):
            first_jan = sys_parts[0]
            prefix9 = first_jan[:9]
            all_jans = [first_jan] + [prefix9 + p for p in sys_parts[1:-1]]
            return [
                RakutenShipmentLine(
                    jan_code=jan,
                    quantity=order_count,
                    order_number=order_number,
                    product_name=product_name,
                    raw_product_number=product_number,
                )
                for jan in all_jans
            ], None

        # Regular single product: JAN13[-set_count]
        sku_jan = sku_number
        sku_qty = 1
        if "-" in sku_number:
            parts = sku_number.rsplit("-", 1)
            suffix = parts[1].strip()
            if suffix.isdigit() and 1 <= len(suffix) <= 3:
                sku_jan = parts[0].strip()
                sku_qty = int(suffix) if int(suffix) > 0 else 1

        if sku_jan.isdigit() and len(sku_jan) == 13:
            return [RakutenShipmentLine(
                jan_code=sku_jan,
                quantity=sku_qty * order_count,
                order_number=order_number,
                product_name=product_name,
                raw_product_number=product_number,
            )], None

    # --- All failed: report to operator for manual handling ---
    try:
        qty = int(float(order_count_value or 1))
    except (ValueError, TypeError):
        qty = 1
    return [], NonJanLine(
        order_number=order_number,
        product_number=product_number,
        quantity=max(1, qty),
    )


async def import_rakuten_shipment_csv(
    session: AsyncSession,
    content: bytes,
    warehouse_name: str = DEFAULT_RAKUTEN_WAREHOUSE,
    customer_name: str = DEFAULT_RAKUTEN_CUSTOMER,
) -> RakutenShipmentImportResult:
    lines, _non_jan = parse_rakuten_shipment_csv(content)
    merged_lines = _merge_shipment_lines(lines)
    result = await apply_rakuten_shipment_lines(
        session=session,
        lines=merged_lines,
        warehouse_name=warehouse_name,
        customer_name=customer_name,
    )
    if result.applied:
        await session.commit()
    return result


async def create_rakuten_shipment_draft(
    session: AsyncSession,
    content: bytes,
    original_filename: str,
    warehouse_name: str = DEFAULT_RAKUTEN_WAREHOUSE,
    customer_name: str = DEFAULT_RAKUTEN_CUSTOMER,
    telegram_user_id: int | None = None,
) -> RakutenShipmentDraft:
    raw_lines, non_jan_lines = parse_rakuten_shipment_csv(content)
    lines = _merge_shipment_lines(raw_lines)
    document = RakutenShipmentDraftDocument(
        warehouse_name=warehouse_name,
        customer_name=customer_name,
        lines=lines,
        non_jan_lines=non_jan_lines,
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


async def get_rakuten_shipment_draft(
    session: AsyncSession,
    draft_id: int,
    *,
    with_for_update: bool = False,
) -> RakutenShipmentDraft | None:
    stmt = select(RakutenShipmentDraft).where(RakutenShipmentDraft.id == draft_id)
    if with_for_update:
        stmt = stmt.with_for_update()
    return await session.scalar(stmt)


async def preview_rakuten_shipment_draft(
    session: AsyncSession,
    draft: RakutenShipmentDraft,
) -> RakutenDraftPreview:
    document = RakutenShipmentDraftDocument.model_validate(draft.document)
    vr = await _validate_rakuten_shipment_lines(
        session=session,
        lines=document.lines,
        warehouse_name=document.warehouse_name,
        customer_name=document.customer_name,
    )
    return RakutenDraftPreview(
        draft_id=draft.id,
        total_lines=len(document.lines),
        ok_count=len(vr.resolved),
        auto_skipped_count=vr.auto_skipped_count,
        needs_decision=vr.needs_decision,
        blocking_issues=vr.blocking_issues,
        non_jan_lines=document.non_jan_lines,
    )


async def apply_rakuten_shipment_draft(
    session: AsyncSession,
    draft: RakutenShipmentDraft,
    force_negative_jans: set[str] | None = None,
    user_id: int | None = None,
) -> RakutenShipmentImportResult:
    document = RakutenShipmentDraftDocument.model_validate(draft.document)
    result = await apply_rakuten_shipment_lines(
        session=session,
        lines=document.lines,
        warehouse_name=document.warehouse_name,
        customer_name=document.customer_name,
        force_negative_jans=force_negative_jans,
        user_id=user_id,
    )
    if result.applied:
        has_skips = bool(result.auto_skipped_count or result.skipped_duplicates)
        draft.status = "applied_with_skips" if has_skips else "applied"
        await session.commit()
        await session.refresh(draft)
    return result


async def apply_rakuten_shipment_lines(
    session: AsyncSession,
    lines: list[RakutenShipmentLine],
    warehouse_name: str = DEFAULT_RAKUTEN_WAREHOUSE,
    customer_name: str = DEFAULT_RAKUTEN_CUSTOMER,
    force_negative_jans: set[str] | None = None,
    user_id: int | None = None,
) -> RakutenShipmentImportResult:
    names_synced = await _sync_product_names_from_rakuten_lines(session=session, lines=lines)
    vr = await _validate_rakuten_shipment_lines(
        session=session,
        lines=lines,
        warehouse_name=warehouse_name,
        customer_name=customer_name,
    )

    if vr.blocking_issues:
        return RakutenShipmentImportResult(
            applied=False,
            total_lines=len(lines),
            issues=vr.blocking_issues,
            names_synced=names_synced,
            auto_skipped_count=vr.auto_skipped_count,
        )

    force_negative_jans = force_negative_jans or set()
    line_map = {i: lines[i] for i in range(len(lines))}
    mutations: list[RakutenShipmentMutation] = []
    skipped_duplicates = 0

    # Apply normal (sufficient-stock) lines
    for line_index, jan_code, quantity, record in vr.resolved:
        order_no = line_map[line_index].order_number or "noorder"
        reference_id = f"rakuten:{order_no}:{jan_code}"
        existing = await session.scalar(
            select(StockTransaction.id).where(
                StockTransaction.source == RAKUTEN_SOURCE,
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
                commit=False,
                user_id=user_id,
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

    # Apply force-negative lines (user explicitly chose to record as negative stock)
    force_negated_count = 0
    warehouse = await resolve_warehouse(session, warehouse_name)
    customer = await resolve_customer(session, customer_name)
    for issue in vr.needs_decision:
        if issue.jan_code not in force_negative_jans:
            continue  # user chose silent skip (direct shipment from partner)
        quantity = issue.quantity_needed
        if quantity is None or warehouse is None:
            continue
        original_line = line_map.get(issue.line_index)
        order_no = (original_line.order_number if original_line else None) or "noorder"
        reference_id = f"rakuten:{order_no}:{issue.jan_code}"
        existing = await session.scalar(
            select(StockTransaction.id).where(
                StockTransaction.source == RAKUTEN_SOURCE,
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
                    sku=issue.jan_code,
                    warehouse_id=warehouse.id,
                    customer_id=customer.id if customer else None,
                    quantity=quantity,
                    source=RAKUTEN_SOURCE,
                    reference_id=reference_id,
                    note="rakuten shipment csv (负库存确认)",
                ),
                commit=False,
                user_id=user_id,
                force_negative=True,
            )
        except (InsufficientStockError, InventoryRecordNotFoundError) as exc:
            raise RuntimeError(f"Rakuten force-negative apply failed: {exc}") from exc
        mutations.append(
            RakutenShipmentMutation(
                jan_code=issue.jan_code,
                quantity=quantity,
                transaction=StockTransactionRead.model_validate(result.transaction),
                low_stock_alert=result.low_stock_alert,
            )
        )
        force_negated_count += 1

    return RakutenShipmentImportResult(
        applied=True,
        total_lines=len(lines),
        mutations=mutations,
        names_synced=names_synced,
        skipped_duplicates=skipped_duplicates,
        auto_skipped_count=vr.auto_skipped_count,
        force_negated_count=force_negated_count,
    )


async def _validate_rakuten_shipment_lines(
    session: AsyncSession,
    lines: list[RakutenShipmentLine],
    warehouse_name: str,
    customer_name: str,
) -> _ValidationResult:
    warehouse = await resolve_warehouse(session, warehouse_name)
    customer = await resolve_customer(session, customer_name)
    blocking_issues: list[RakutenShipmentIssue] = []
    needs_decision: list[RakutenShipmentIssue] = []
    resolved: list[tuple[int, str, int, InventoryRecord]] = []
    auto_skipped_count = 0

    if not lines:
        blocking_issues.append(RakutenShipmentIssue(
            line_index=-1, jan_code="", issue_type="empty_csv",
            message="No valid Rakuten shipment lines were parsed from this CSV.",
        ))
    if warehouse is None:
        blocking_issues.append(RakutenShipmentIssue(
            line_index=-1, jan_code="", issue_type="warehouse_not_found",
            message=f"Warehouse not found: {warehouse_name}",
        ))
    for index, line in enumerate(lines):
        products = await search_inventory_items(session=session, keyword=line.jan_code, limit=6)
        if not products:
            # Product not in DB at all — likely direct-ship from partner, silently skip
            auto_skipped_count += 1
            continue
        if len(products) > 1:
            blocking_issues.append(RakutenShipmentIssue(
                line_index=index,
                jan_code=line.jan_code,
                issue_type="ambiguous_product",
                message="Multiple products matched. Confirm with full JAN before applying.",
                candidates=[ProductRead.model_validate(p) for p in products],
            ))
            continue
        if warehouse is None:
            continue

        jan_code = products[0].jan_code
        record = await _resolve_first_inventory_record(
            session=session,
            jan_code=jan_code,
            warehouse_id=warehouse.id,
        )
        if record is None:
            # Product exists in DB but no stock record in this warehouse
            needs_decision.append(RakutenShipmentIssue(
                line_index=index,
                jan_code=jan_code,
                issue_type="inventory_record_not_found",
                message=f"乐天仓库无 {jan_code} 库存记录（商品已知但未入库）",
                current_stock=None,
                quantity_needed=line.quantity,
            ))
            continue
        if record.quantity < line.quantity:
            needs_decision.append(RakutenShipmentIssue(
                line_index=index,
                jan_code=jan_code,
                issue_type="insufficient_stock",
                message=f"库存不足：{jan_code} 现有 {record.quantity}，出库需 {line.quantity}",
                current_stock=record.quantity,
                quantity_needed=line.quantity,
            ))
            continue
        resolved.append((index, jan_code, line.quantity, record))

    return _ValidationResult(blocking_issues, needs_decision, resolved, auto_skipped_count)


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


async def _sync_product_names_from_rakuten_lines(
    session: AsyncSession,
    lines: list[RakutenShipmentLine],
) -> int:
    names_by_jan: dict[str, str] = {}
    for line in lines:
        product_name = _clean_text(line.product_name)
        if product_name:
            names_by_jan.setdefault(line.jan_code, product_name)
    if not names_by_jan:
        return 0

    result = await session.scalars(
        select(Product).where(Product.jan_code.in_(names_by_jan.keys()))
    )
    updated_count = 0
    for product in result.all():
        product_name = names_by_jan.get(product.jan_code)
        if product_name and _is_placeholder_product_name(product):
            product.name_jp = product_name[:255]
            updated_count += 1
    if updated_count:
        await session.flush()
    return updated_count


async def sync_product_names_from_rakuten_drafts(session: AsyncSession) -> int:
    result = await session.scalars(select(RakutenShipmentDraft).order_by(RakutenShipmentDraft.id.asc()))
    updated_count = 0
    for draft in result.all():
        document = RakutenShipmentDraftDocument.model_validate(draft.document)
        updated_count += await _sync_product_names_from_rakuten_lines(
            session=session,
            lines=document.lines,
        )
    if updated_count:
        await session.commit()
    return updated_count


def _is_placeholder_product_name(product: Product) -> bool:
    name_jp = _clean_text(product.name_jp)
    return not name_jp or name_jp == product.jan_code


async def _resolve_first_inventory_record(
    session: AsyncSession,
    jan_code: str,
    warehouse_id: int,
) -> InventoryRecord | None:
    return await session.scalar(
        select(InventoryRecord)
        .where(
            InventoryRecord.product_jan == jan_code,
            InventoryRecord.warehouse_id == warehouse_id,
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
