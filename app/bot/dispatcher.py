from io import BytesIO
from uuid import uuid4

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Document, Message
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.customer import Customer
from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.schemas.inventory import (
    ChatReportDocument,
    ChatReportDirection,
    ChatReportLine,
    ChatReportParseRequest,
    RakutenShipmentDraftDocument,
    RakutenShipmentImportResult,
    StockAdjustCreate,
    StockInCreate,
    StockOutCreate,
)
from app.services.chat_reports import (
    apply_chat_report,
    create_chat_report_draft,
    get_chat_report_draft,
    mark_chat_report_draft_applied,
    save_chat_report_draft_document,
)
from app.services.inventory import (
    InsufficientStockError,
    InventoryRecordNotFoundError,
    InventoryTargetNotFoundError,
    adjust_stock_item,
    search_inventory_items,
    search_products,
    stock_in_item,
    stock_out_item,
)
from app.services.rakuten_shipments import (
    DEFAULT_RAKUTEN_CUSTOMER,
    DEFAULT_RAKUTEN_WAREHOUSE,
    apply_rakuten_shipment_draft,
    create_rakuten_shipment_draft,
    get_rakuten_shipment_draft,
    preview_rakuten_shipment_draft,
)


DEFAULT_LOCATION_CODE = "A-00-00"
DEFAULT_WAREHOUSE_NAME = "普通仓库"
DEFAULT_CUSTOMER_NAME = "店铺"
TELEGRAM_SOURCE = "telegram"


telegram_router = Router(name="telegram")


@telegram_router.message(Command("start"))
async def start(message: Message) -> None:
    await message.answer(
        "WMS inventory bot is ready.\n"
        "Use /search JAN_OR_NAME, /search_sku JAN_OR_NAME, /stock_in SKU WAREHOUSE QUANTITY, "
        "/stock_out SKU WAREHOUSE QUANTITY, /stock_adjust SKU WAREHOUSE ACTUAL_QUANTITY, "
        "/add_product JAN NAME_JP [NAME_ZH], /add_customer NAME [CONTACT], or "
        "/transfer SKU FROM_WAREHOUSE TO_WAREHOUSE QUANTITY, or "
        "/transfer_customer SKU WAREHOUSE FROM_CUSTOMER TO_CUSTOMER QUANTITY.\n"
        "Batch chat import: /parse_report then paste records; /apply_report ID to apply saved draft.\n"
        "Rakuten CSV: send a CSV file with caption /rakuten_csv, or reply /rakuten_csv to a CSV file."
    )


@telegram_router.message(Command("whoami"))
async def whoami(message: Message) -> None:
    user = message.from_user
    if user is None:
        await message.answer("Cannot identify this Telegram user.")
        return
    await message.answer(
        f"user_id: {user.id}\n"
        f"username: @{user.username or '-'}\n"
        f"name: {user.full_name}"
    )


@telegram_router.message(Command("search"))
async def search(message: Message) -> None:
    if not await _require_query_permission(message):
        return

    keyword = _command_args(message.text)
    if not keyword:
        await message.answer("Usage: /search JAN_OR_NAME")
        return

    async with AsyncSessionLocal() as session:
        items = await search_inventory_items(session=session, keyword=keyword, limit=10)

    if not items:
        await message.answer(_product_missing_message(keyword))
        return

    lines: list[str] = []
    for product in items:
        lines.append(f"{product.jan_code} | {product.name_jp} | {product.name_zh or '-'}")
        if not product.inventory_records:
            lines.append("  no stock records")
            continue
        for record in product.inventory_records:
            expiration = record.expiration_date.isoformat() if record.expiration_date else "-"
            customer = record.customer.name if record.customer else "-"
            lines.append(
                f"  {record.warehouse.name} | qty: {record.quantity} | "
                f"loc: {record.location_code} | customer: {customer} | exp: {expiration}"
            )
    await message.answer("\n".join(lines))


@telegram_router.message(Command("search_sku", "search_SKU", "search_SUK"))
async def search_sku(message: Message) -> None:
    if not await _require_query_permission(message):
        return

    keyword = _command_args(message.text)
    if not keyword:
        await message.answer("Usage: /search_sku JAN_OR_NAME")
        return

    async with AsyncSessionLocal() as session:
        products = await search_products(session=session, keyword=keyword, limit=10)

    if not products:
        await message.answer(_product_missing_message(keyword))
        return

    lines = ["Product matches:"]
    for product in products:
        case_text = f"{product.units_per_case}/箱" if product.units_per_case else "-"
        lines.append(
            f"{product.jan_code} | JP: {product.name_jp} | ZH: {product.name_zh or '-'} | case: {case_text}"
        )
    await message.answer("\n".join(lines))


@telegram_router.message(Command("stock_in"))
async def stock_in(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    parsed = _parse_stock_command(message.text)
    if parsed is None:
        await message.answer("Usage: /stock_in SKU [WAREHOUSE] QUANTITY [CUSTOMER]")
        return

    sku, warehouse_name, quantity, customer_name = parsed
    if quantity <= 0:
        await message.answer("Quantity must be greater than 0.")
        return

    async with AsyncSessionLocal() as session:
        warehouse = await _resolve_warehouse(session, warehouse_name)
        if warehouse is None:
            await message.answer(f"Warehouse not found: {warehouse_name}")
            return
        customer_name = customer_name or _default_customer_name_for_warehouse(warehouse)
        customer = await _resolve_customer(session, customer_name)
        if customer is None:
            await message.answer(f"Customer not found: {customer_name}")
            return
        product = await _resolve_product_for_operation(session, sku, warehouse.id, customer.id)
        if product is None:
            await message.answer(_product_missing_message(sku))
            return
        if isinstance(product, list):
            await message.answer(_product_ambiguous_message(sku, product, "/stock_in"))
            return

        try:
            payload = StockInCreate(
                sku=product.jan_code,
                warehouse_id=warehouse.id,
                customer_id=customer.id,
                quantity=quantity,
                location_code=DEFAULT_LOCATION_CODE,
                source=TELEGRAM_SOURCE,
            )
        except Exception as exc:
            await message.answer(f"Invalid stock-in request: {exc}")
            return
        try:
            result = await stock_in_item(session=session, payload=payload)
        except InventoryTargetNotFoundError:
            result = None

    if result is None:
        await message.answer("SKU or warehouse not found. Please resolve the SKU/JAN and warehouse before stock-in.")
        return

    record = result.record
    await message.answer(
        f"Stock-in recorded: {record.product_jan} | warehouse: {record.warehouse.name} | "
        f"customer: {record.customer.name if record.customer else '-'} | "
        f"+{payload.quantity} | qty: {record.quantity} | loc: {record.location_code}"
    )


@telegram_router.message(Command("parse_report"))
async def parse_report(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    parsed = _parse_report_command(message.text)
    if parsed is None:
        await message.answer(_report_usage("/parse_report"))
        return

    warehouse_name, customer_name, report_text = parsed
    await message.answer("Parsing chat report with Gemini...")
    async with AsyncSessionLocal() as session:
        try:
            draft = await create_chat_report_draft(
                session=session,
                payload=ChatReportParseRequest(
                    text=report_text,
                    default_warehouse_name=warehouse_name,
                    default_customer_name=customer_name,
                    source=TELEGRAM_SOURCE,
                ),
                telegram_user_id=_message_user_id(message),
            )
        except RuntimeError as exc:
            await message.answer(str(exc))
            return
        except Exception as exc:
            await message.answer(f"Failed to parse report: {exc}")
            return

    document = ChatReportDocument.model_validate(draft.document)
    await _answer_long(message, f"Draft ID: {draft.id}\n" + _format_report_document(document) + "\n\n" + _draft_help(draft.id))


@telegram_router.message(Command("apply_report"))
async def apply_report(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    draft_id = _parse_draft_id_command(message.text)
    if draft_id is None:
        await message.answer("Usage: /apply_report DRAFT_ID")
        return

    async with AsyncSessionLocal() as session:
        draft = await get_chat_report_draft(session=session, draft_id=draft_id)
        if draft is None:
            await message.answer(f"Draft not found: {draft_id}")
            return
        if draft.status == "applied":
            await message.answer(f"Draft already applied: {draft_id}")
            return
        document = ChatReportDocument.model_validate(draft.document)
        result = await apply_chat_report(session=session, document=document)
        if result.applied:
            await mark_chat_report_draft_applied(session=session, draft=draft)

    if not result.applied:
        await _answer_long(message, f"Draft ID: {draft_id}\n" + _format_report_document(document) + "\n\n" + _format_apply_issues(result.issues))
        return

    await _answer_long(message, _format_apply_success(document, result.mutations))


@telegram_router.message(Command("rakuten_csv"))
async def rakuten_csv(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    parsed = _parse_rakuten_csv_command(message.text or message.caption)
    if parsed is None:
        await message.answer("Usage: send/reply to Rakuten CSV with /rakuten_csv [WAREHOUSE] [CUSTOMER]")
        return
    warehouse_name, customer_name = parsed

    document = _document_from_message_or_reply(message)
    if document is None:
        await message.answer("Please attach a Rakuten RMS CSV file, or reply /rakuten_csv to a CSV file.")
        return

    await _create_and_preview_rakuten_csv_draft(
        message=message,
        document=document,
        warehouse_name=warehouse_name,
        customer_name=customer_name,
    )


@telegram_router.message(Command("apply_rakuten_csv"))
async def apply_rakuten_csv(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    parsed = _parse_apply_rakuten_csv_command(message.text)
    if parsed is None:
        await message.answer("Usage: /apply_rakuten_csv DRAFT_ID [ignore]")
        return
    draft_id, ignore_missing = parsed

    async with AsyncSessionLocal() as session:
        draft = await get_rakuten_shipment_draft(session=session, draft_id=draft_id)
        if draft is None:
            await message.answer(f"Rakuten CSV draft not found: {draft_id}")
            return
        if draft.status.startswith("applied"):
            await message.answer(f"Rakuten CSV draft already applied: {draft_id}")
            return
        result = await apply_rakuten_shipment_draft(
            session=session,
            draft=draft,
            ignore_missing=ignore_missing,
        )

    if not result.applied:
        await _answer_long(message, _format_rakuten_csv_result(draft_id=draft_id, result=result))
        return

    await _answer_long(message, _format_rakuten_csv_apply_success(draft_id=draft_id, result=result))


@telegram_router.message(Command("show_report"))
async def show_report(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    draft_id = _parse_draft_id_command(message.text)
    if draft_id is None:
        await message.answer("Usage: /show_report DRAFT_ID")
        return

    async with AsyncSessionLocal() as session:
        draft = await get_chat_report_draft(session=session, draft_id=draft_id)
    if draft is None:
        await message.answer(f"Draft not found: {draft_id}")
        return
    document = ChatReportDocument.model_validate(draft.document)
    await _answer_long(message, f"Draft ID: {draft.id} | status: {draft.status}\n" + _format_report_document(document) + "\n\n" + _draft_help(draft.id))


@telegram_router.message(Command("set_report_meta"))
async def set_report_meta(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    parsed = _parse_report_meta_command(message.text)
    if parsed is None:
        await message.answer("Usage: /set_report_meta DRAFT_ID IN|OUT WAREHOUSE CUSTOMER")
        return
    draft_id, direction, warehouse_name, customer_name = parsed

    async with AsyncSessionLocal() as session:
        draft = await get_chat_report_draft(session=session, draft_id=draft_id)
        if draft is None:
            await message.answer(f"Draft not found: {draft_id}")
            return
        document = ChatReportDocument.model_validate(draft.document).model_copy(
            update={
                "direction": direction,
                "warehouse_name": warehouse_name,
                "customer_name": customer_name,
            }
        )
        await save_chat_report_draft_document(session=session, draft=draft, document=document)

    await message.answer(f"Draft updated: {draft_id}")


@telegram_router.message(Command("set_report_line"))
async def set_report_line(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    parsed = _parse_report_line_command(message.text)
    if parsed is None:
        await message.answer("Usage: /set_report_line DRAFT_ID LINE_NO JAN_HINT QUANTITY [PRODUCT_NAME]")
        return
    draft_id, line_no, jan_hint, quantity, product_name_hint = parsed

    async with AsyncSessionLocal() as session:
        draft = await get_chat_report_draft(session=session, draft_id=draft_id)
        if draft is None:
            await message.answer(f"Draft not found: {draft_id}")
            return
        document = ChatReportDocument.model_validate(draft.document)
        if line_no < 1 or line_no > len(document.lines):
            await message.answer(f"Line number out of range: {line_no}")
            return
        lines = list(document.lines)
        line = lines[line_no - 1]
        lines[line_no - 1] = line.model_copy(
            update={
                "jan_hint": jan_hint,
                "quantity": quantity,
                "product_name_hint": product_name_hint if product_name_hint is not None else line.product_name_hint,
            }
        )
        document = document.model_copy(update={"lines": lines})
        await save_chat_report_draft_document(session=session, draft=draft, document=document)

    await message.answer(f"Draft line updated: {draft_id} #{line_no}")


@telegram_router.message(Command("add_report_line"))
async def add_report_line(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    parsed = _parse_add_report_line_command(message.text)
    if parsed is None:
        await message.answer("Usage: /add_report_line DRAFT_ID JAN_HINT QUANTITY [PRODUCT_NAME]")
        return
    draft_id, jan_hint, quantity, product_name_hint = parsed

    async with AsyncSessionLocal() as session:
        draft = await get_chat_report_draft(session=session, draft_id=draft_id)
        if draft is None:
            await message.answer(f"Draft not found: {draft_id}")
            return
        document = ChatReportDocument.model_validate(draft.document)
        lines = list(document.lines)
        lines.append(ChatReportLine(jan_hint=jan_hint, quantity=quantity, product_name_hint=product_name_hint))
        document = document.model_copy(update={"lines": lines})
        await save_chat_report_draft_document(session=session, draft=draft, document=document)

    await message.answer(f"Draft line added: {draft_id}")


@telegram_router.message(Command("del_report_line"))
async def del_report_line(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    parsed = _parse_delete_report_line_command(message.text)
    if parsed is None:
        await message.answer("Usage: /del_report_line DRAFT_ID LINE_NO")
        return
    draft_id, line_no = parsed

    async with AsyncSessionLocal() as session:
        draft = await get_chat_report_draft(session=session, draft_id=draft_id)
        if draft is None:
            await message.answer(f"Draft not found: {draft_id}")
            return
        document = ChatReportDocument.model_validate(draft.document)
        if line_no < 1 or line_no > len(document.lines):
            await message.answer(f"Line number out of range: {line_no}")
            return
        lines = list(document.lines)
        del lines[line_no - 1]
        document = document.model_copy(update={"lines": lines})
        await save_chat_report_draft_document(session=session, draft=draft, document=document)

    await message.answer(f"Draft line deleted: {draft_id} #{line_no}")


@telegram_router.message(Command("stock_out"))
async def stock_out(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    parsed = _parse_stock_command(message.text)
    if parsed is None:
        await message.answer("Usage: /stock_out SKU [WAREHOUSE] QUANTITY [CUSTOMER]")
        return

    sku, warehouse_name, quantity, customer_name = parsed
    if quantity <= 0:
        await message.answer("Quantity must be greater than 0.")
        return

    async with AsyncSessionLocal() as session:
        warehouse = await _resolve_warehouse(session, warehouse_name)
        if warehouse is None:
            await message.answer(f"Warehouse not found: {warehouse_name}")
            return
        customer_name = customer_name or _default_customer_name_for_warehouse(warehouse)
        customer = await _resolve_customer(session, customer_name)
        if customer is None:
            await message.answer(f"Customer not found: {customer_name}")
            return
        product = await _resolve_product_for_operation(session, sku, warehouse.id, customer.id)
        if product is None:
            await message.answer(_product_missing_message(sku))
            return
        if isinstance(product, list):
            await message.answer(_product_ambiguous_message(sku, product, "/stock_out"))
            return

        record = await _resolve_first_inventory_record(session, product.jan_code, warehouse.id, customer.id)
        if record is None:
            await message.answer("No inventory record found for this SKU, warehouse, and customer.")
            return

        try:
            payload = StockOutCreate(
                sku=product.jan_code,
                warehouse_id=warehouse.id,
                customer_id=customer.id,
                quantity=quantity,
                location_code=record.location_code,
                expiration_date=record.expiration_date,
                source=TELEGRAM_SOURCE,
            )
        except Exception as exc:
            await message.answer(f"Invalid stock-out request: {exc}")
            return
        try:
            result = await stock_out_item(session=session, payload=payload)
        except InsufficientStockError:
            await message.answer("Insufficient stock for this stock-out request.")
            return
        except InventoryRecordNotFoundError:
            await message.answer("Inventory record disappeared before stock-out. Please search and retry.")
            return

    record = result.record
    await message.answer(
        f"Stock-out recorded: {record.product_jan} | warehouse: {record.warehouse.name} | "
        f"customer: {record.customer.name if record.customer else '-'} | "
        f"-{quantity} | qty: {record.quantity} | loc: {record.location_code}"
    )
    if result.low_stock_alert:
        await message.answer(_format_low_stock_alert(result.low_stock_alert))


@telegram_router.message(Command("stock_adjust"))
async def stock_adjust(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    parsed = _parse_stock_command(message.text)
    if parsed is None:
        await message.answer("Usage: /stock_adjust SKU [WAREHOUSE] ACTUAL_QUANTITY [CUSTOMER]")
        return

    sku, warehouse_name, actual_quantity, customer_name = parsed
    async with AsyncSessionLocal() as session:
        warehouse = await _resolve_warehouse(session, warehouse_name)
        if warehouse is None:
            await message.answer(f"Warehouse not found: {warehouse_name}")
            return
        customer_name = customer_name or _default_customer_name_for_warehouse(warehouse)
        customer = await _resolve_customer(session, customer_name)
        if customer is None:
            await message.answer(f"Customer not found: {customer_name}")
            return
        product = await _resolve_product_for_operation(session, sku, warehouse.id, customer.id)
        if product is None:
            await message.answer(_product_missing_message(sku))
            return
        if isinstance(product, list):
            await message.answer(_product_ambiguous_message(sku, product, "/stock_adjust"))
            return

        record = await _resolve_first_inventory_record(session, product.jan_code, warehouse.id, customer.id)
        if record is None:
            await message.answer("No inventory record found for this SKU, warehouse, and customer.")
            return

        try:
            payload = StockAdjustCreate(
                sku=product.jan_code,
                warehouse_id=warehouse.id,
                customer_id=customer.id,
                actual_quantity=actual_quantity,
                location_code=record.location_code,
                expiration_date=record.expiration_date,
                source=TELEGRAM_SOURCE,
            )
        except Exception as exc:
            await message.answer(f"Invalid stock-adjust request: {exc}")
            return
        try:
            result = await adjust_stock_item(session=session, payload=payload)
        except InventoryRecordNotFoundError:
            await message.answer("Inventory record disappeared before adjustment. Please search and retry.")
            return

    record = result.record
    await message.answer(
        f"Stock adjusted: {record.product_jan} | warehouse: {record.warehouse.name} | "
        f"customer: {record.customer.name if record.customer else '-'} | "
        f"{result.previous_quantity} -> {actual_quantity} | delta: {result.quantity_delta} | "
        f"loc: {record.location_code}"
    )
    if result.low_stock_alert:
        await message.answer(_format_low_stock_alert(result.low_stock_alert))


@telegram_router.message(Command("add_customer"))
async def add_customer(message: Message) -> None:
    if not await _require_admin_permission(message):
        return

    args = _command_args(message.text).split(maxsplit=1)
    if not args:
        await message.answer("Usage: /add_customer NAME [CONTACT]")
        return

    name = args[0]
    contact_info = args[1] if len(args) == 2 else None
    async with AsyncSessionLocal() as session:
        customer = Customer(name=name, contact_info=contact_info)
        session.add(customer)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            await message.answer(f"Customer already exists: {name}")
            return
        await session.refresh(customer)

    await message.answer(f"Customer added: {customer.name}")


@telegram_router.message(Command("add_product"))
async def add_product(message: Message) -> None:
    if not await _require_admin_permission(message):
        return

    parsed = _parse_add_product_command(message.text)
    if parsed is None:
        await message.answer("Usage: /add_product JAN NAME_JP [UNITS_PER_CASE] [NAME_ZH]")
        return
    jan_code, name_jp, units_per_case, name_zh = parsed
    async with AsyncSessionLocal() as session:
        product = Product(
            jan_code=jan_code,
            name_jp=name_jp,
            name_zh=name_zh,
            units_per_case=units_per_case,
        )
        session.add(product)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            await message.answer(f"Product already exists: {jan_code}")
            return
        await session.refresh(product)

    case_text = f" | {product.units_per_case}/箱" if product.units_per_case else " | no case alert"
    await message.answer(f"Product added: {product.jan_code} | {product.name_jp} | {product.name_zh or '-'}{case_text}")


@telegram_router.message(Command("transfer"))
async def transfer_stock(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    args = _command_args(message.text).split()
    if len(args) not in {4, 5}:
        await message.answer("Usage: /transfer SKU FROM_WAREHOUSE TO_WAREHOUSE QUANTITY [CUSTOMER]")
        return

    sku, from_warehouse_name, to_warehouse_name, raw_quantity = args[:4]
    customer_name = args[4] if len(args) == 5 else None
    try:
        quantity = int(raw_quantity)
    except ValueError:
        await message.answer("Quantity must be an integer.")
        return
    if quantity <= 0:
        await message.answer("Quantity must be greater than 0.")
        return

    async with AsyncSessionLocal() as session:
        from_warehouse = await _resolve_warehouse(session, from_warehouse_name)
        to_warehouse = await _resolve_warehouse(session, to_warehouse_name)
        if from_warehouse is None:
            await message.answer(f"Source warehouse not found: {from_warehouse_name}")
            return
        if to_warehouse is None:
            await message.answer(f"Target warehouse not found: {to_warehouse_name}")
            return
        customer_name = customer_name or _default_customer_name_for_warehouse(from_warehouse)
        customer = await _resolve_customer(session, customer_name)
        if customer is None:
            await message.answer(f"Customer not found: {customer_name}")
            return
        product = await _resolve_product_for_operation(session, sku, from_warehouse.id, customer.id)
        if product is None:
            await message.answer(_product_missing_message(sku))
            return
        if isinstance(product, list):
            await message.answer(_product_ambiguous_message(sku, product, "/transfer"))
            return

        source_record = await _resolve_first_inventory_record(session, product.jan_code, from_warehouse.id, customer.id)
        if source_record is None:
            await message.answer("No source inventory record found for this SKU, warehouse, and customer.")
            return

        try:
            reference_id = f"transfer:{uuid4().hex}"
            out_payload = StockOutCreate(
                sku=product.jan_code,
                warehouse_id=from_warehouse.id,
                customer_id=customer.id,
                quantity=quantity,
                location_code=source_record.location_code,
                expiration_date=source_record.expiration_date,
                source=TELEGRAM_SOURCE,
                reference_id=reference_id,
                note=f"transfer to warehouse {to_warehouse.name}",
                suppress_low_stock_alert=True,
            )
            out_result = await stock_out_item(session=session, payload=out_payload)
            in_payload = StockInCreate(
                sku=product.jan_code,
                warehouse_id=to_warehouse.id,
                customer_id=customer.id,
                quantity=quantity,
                location_code=DEFAULT_LOCATION_CODE,
                expiration_date=source_record.expiration_date,
                source=TELEGRAM_SOURCE,
                reference_id=reference_id,
                note=f"transfer from warehouse {from_warehouse.name}",
            )
            in_result = await stock_in_item(session=session, payload=in_payload)
        except InsufficientStockError:
            await message.answer("Insufficient stock for transfer.")
            return
        except InventoryRecordNotFoundError:
            await message.answer("Source inventory record disappeared before transfer. Please search and retry.")
            return
        except InventoryTargetNotFoundError:
            await message.answer("SKU, warehouse, or customer not found during transfer.")
            return

    await message.answer(
        f"Transfer recorded: {product.jan_code} | {from_warehouse.name} -> {to_warehouse.name} | "
        f"customer: {customer.name} | qty: {quantity} | "
        f"source left: {out_result.record.quantity} | target qty: {in_result.record.quantity}"
    )


@telegram_router.message(Command("transfer_customer"))
async def transfer_customer_stock(message: Message) -> None:
    if not await _require_operator_permission(message):
        return

    args = _command_args(message.text).split()
    if len(args) != 5:
        await message.answer("Usage: /transfer_customer SKU WAREHOUSE FROM_CUSTOMER TO_CUSTOMER QUANTITY")
        return

    sku, warehouse_name, from_customer_name, to_customer_name, raw_quantity = args
    try:
        quantity = int(raw_quantity)
    except ValueError:
        await message.answer("Quantity must be an integer.")
        return
    if quantity <= 0:
        await message.answer("Quantity must be greater than 0.")
        return

    async with AsyncSessionLocal() as session:
        product = await _resolve_product_for_operation(session, sku)
        warehouse = await _resolve_warehouse(session, warehouse_name)
        from_customer = await _resolve_customer(session, from_customer_name)
        to_customer = await _resolve_customer(session, to_customer_name)
        if product is None:
            await message.answer(_product_missing_message(sku))
            return
        if isinstance(product, list):
            await message.answer(_product_ambiguous_message(sku, product, "/transfer_customer"))
            return
        if warehouse is None:
            await message.answer(f"Warehouse not found: {warehouse_name}")
            return
        if from_customer is None:
            await message.answer(f"Source customer not found: {from_customer_name}")
            return
        if to_customer is None:
            await message.answer(f"Target customer not found: {to_customer_name}")
            return

        source_record = await _resolve_first_inventory_record(session, product.jan_code, warehouse.id, from_customer.id)
        if source_record is None:
            await message.answer("No source inventory record found for this SKU, warehouse, and source customer.")
            return

        try:
            reference_id = f"transfer_customer:{uuid4().hex}"
            out_payload = StockOutCreate(
                sku=product.jan_code,
                warehouse_id=warehouse.id,
                customer_id=from_customer.id,
                quantity=quantity,
                location_code=source_record.location_code,
                expiration_date=source_record.expiration_date,
                source=TELEGRAM_SOURCE,
                reference_id=reference_id,
                note=f"transfer to customer {to_customer.name}",
                suppress_low_stock_alert=True,
            )
            out_result = await stock_out_item(session=session, payload=out_payload)
            in_payload = StockInCreate(
                sku=product.jan_code,
                warehouse_id=warehouse.id,
                customer_id=to_customer.id,
                quantity=quantity,
                location_code=source_record.location_code,
                expiration_date=source_record.expiration_date,
                source=TELEGRAM_SOURCE,
                reference_id=reference_id,
                note=f"transfer from customer {from_customer.name}",
            )
            in_result = await stock_in_item(session=session, payload=in_payload)
        except InsufficientStockError:
            await message.answer("Insufficient stock for customer transfer.")
            return
        except InventoryRecordNotFoundError:
            await message.answer("Source inventory record disappeared before customer transfer. Please search and retry.")
            return
        except InventoryTargetNotFoundError:
            await message.answer("SKU, warehouse, or customer not found during customer transfer.")
            return

    await message.answer(
        f"Customer transfer recorded: {product.jan_code} | warehouse: {warehouse.name} | "
        f"{from_customer.name} -> {to_customer.name} | qty: {quantity} | "
        f"source left: {out_result.record.quantity} | target qty: {in_result.record.quantity}"
    )


def create_dispatcher() -> Dispatcher:
    dispatcher = Dispatcher()
    dispatcher.include_router(telegram_router)
    return dispatcher


def create_bot(token: str) -> Bot:
    return Bot(token=token)


def _command_args(text: str | None) -> str:
    if not text:
        return ""
    parts = text.split(maxsplit=1)
    if len(parts) == 1:
        return ""
    return parts[1].strip()


def _parse_stock_command(text: str | None) -> tuple[str, str, int, str | None] | None:
    args = _command_args(text).split()
    if len(args) == 2:
        sku, raw_quantity = args
        warehouse_name = DEFAULT_WAREHOUSE_NAME
        customer_name = None
    elif len(args) == 3:
        sku, warehouse_name, raw_quantity = args
        customer_name = None
    elif len(args) == 4:
        sku, warehouse_name, raw_quantity, customer_name = args
    else:
        return None

    try:
        quantity = int(raw_quantity)
    except ValueError:
        return None
    if quantity < 0:
        return None
    return sku, warehouse_name, quantity, customer_name


def _parse_add_product_command(text: str | None) -> tuple[str, str, int | None, str | None] | None:
    args = _command_args(text).split(maxsplit=3)
    if len(args) < 2:
        return None

    jan_code = args[0]
    name_jp = args[1]
    units_per_case: int | None = None
    name_zh: str | None = None

    if len(args) >= 3:
        try:
            units_per_case = int(args[2])
            if units_per_case <= 0:
                return None
            name_zh = args[3] if len(args) == 4 else None
        except ValueError:
            name_zh = args[2]

    return jan_code, name_jp, units_per_case, name_zh


def _parse_report_command(text: str | None) -> tuple[str, str, str] | None:
    if not text:
        return None
    lines = text.splitlines()
    if len(lines) < 2:
        return None

    first_line = lines[0].strip()
    first_parts = first_line.split()
    option_parts = first_parts[1:]
    if len(option_parts) == 0:
        warehouse_name = DEFAULT_WAREHOUSE_NAME
        customer_name = DEFAULT_CUSTOMER_NAME
    elif len(option_parts) == 1:
        warehouse_name = option_parts[0]
        customer_name = DEFAULT_CUSTOMER_NAME
    elif len(option_parts) == 2:
        warehouse_name, customer_name = option_parts
    else:
        return None

    report_text = "\n".join(lines[1:]).strip()
    if not report_text:
        return None
    return warehouse_name, customer_name, report_text


def _parse_rakuten_csv_command(text: str | None) -> tuple[str, str] | None:
    args = _command_args(text).split()
    if len(args) == 0:
        return DEFAULT_RAKUTEN_WAREHOUSE, DEFAULT_RAKUTEN_CUSTOMER
    if len(args) == 1:
        return args[0], DEFAULT_RAKUTEN_CUSTOMER
    if len(args) == 2:
        return args[0], args[1]
    return None


def _parse_draft_id_command(text: str | None) -> int | None:
    args = _command_args(text).split()
    if len(args) != 1:
        return None
    try:
        return int(args[0])
    except ValueError:
        return None


def _parse_apply_rakuten_csv_command(text: str | None) -> tuple[int, bool] | None:
    args = _command_args(text).split()
    if len(args) not in {1, 2}:
        return None
    try:
        draft_id = int(args[0])
    except ValueError:
        return None
    if len(args) == 1:
        return draft_id, False
    ignore_flag = args[1].lower()
    if ignore_flag not in {"ignore", "--ignore", "skip", "--skip-missing"}:
        return None
    return draft_id, True


def _parse_report_meta_command(text: str | None) -> tuple[int, ChatReportDirection, str, str] | None:
    args = _command_args(text).split()
    if len(args) != 4:
        return None
    raw_draft_id, raw_direction, warehouse_name, customer_name = args
    try:
        draft_id = int(raw_draft_id)
        direction = ChatReportDirection(raw_direction.upper())
    except ValueError:
        return None
    return draft_id, direction, warehouse_name, customer_name


def _parse_report_line_command(text: str | None) -> tuple[int, int, str, int, str | None] | None:
    args = _command_args(text).split(maxsplit=4)
    if len(args) < 4:
        return None
    raw_draft_id, raw_line_no, jan_hint, raw_quantity = args[:4]
    product_name_hint = args[4] if len(args) == 5 else None
    try:
        draft_id = int(raw_draft_id)
        line_no = int(raw_line_no)
        quantity = int(raw_quantity)
    except ValueError:
        return None
    if quantity <= 0:
        return None
    return draft_id, line_no, jan_hint, quantity, product_name_hint


def _parse_add_report_line_command(text: str | None) -> tuple[int, str, int, str | None] | None:
    args = _command_args(text).split(maxsplit=3)
    if len(args) < 3:
        return None
    raw_draft_id, jan_hint, raw_quantity = args[:3]
    product_name_hint = args[3] if len(args) == 4 else None
    try:
        draft_id = int(raw_draft_id)
        quantity = int(raw_quantity)
    except ValueError:
        return None
    if quantity <= 0:
        return None
    return draft_id, jan_hint, quantity, product_name_hint


def _parse_delete_report_line_command(text: str | None) -> tuple[int, int] | None:
    args = _command_args(text).split()
    if len(args) != 2:
        return None
    try:
        return int(args[0]), int(args[1])
    except ValueError:
        return None


def _message_user_id(message: Message) -> int | None:
    if message.from_user is None:
        return None
    return message.from_user.id


def _document_from_message_or_reply(message: Message) -> Document | None:
    if message.document is not None:
        return message.document
    if message.reply_to_message is not None:
        return message.reply_to_message.document
    return None


def _looks_like_csv(document: Document) -> bool:
    filename = (document.file_name or "").lower()
    content_type = (document.mime_type or "").lower()
    return filename.endswith(".csv") or content_type in {"text/csv", "application/vnd.ms-excel"}


async def _download_document_bytes(bot: Bot, document: Document) -> bytes:
    buffer = BytesIO()
    await bot.download(document.file_id, destination=buffer)
    buffer.seek(0)
    return buffer.read()


async def _create_and_preview_rakuten_csv_draft(
    message: Message,
    document: Document,
    warehouse_name: str,
    customer_name: str,
) -> None:
    if not _looks_like_csv(document):
        await message.answer("This does not look like a CSV file. Please send the Rakuten RMS CSV.")
        return

    await message.answer("Reading Rakuten CSV and creating a saved draft...")
    try:
        content = await _download_document_bytes(message.bot, document)
    except Exception as exc:
        await message.answer(f"Failed to download CSV from Telegram: {exc}")
        return

    async with AsyncSessionLocal() as session:
        try:
            draft = await create_rakuten_shipment_draft(
                session=session,
                content=content,
                original_filename=document.file_name or "rakuten.csv",
                warehouse_name=warehouse_name,
                customer_name=customer_name,
                telegram_user_id=_message_user_id(message),
            )
            result = await preview_rakuten_shipment_draft(session=session, draft=draft)
        except Exception as exc:
            await message.answer(f"Failed to parse Rakuten CSV: {exc}")
            return

    document_model = RakutenShipmentDraftDocument.model_validate(draft.document)
    await _answer_long(
        message,
        _format_rakuten_csv_draft(draft_id=draft.id, document=document_model, result=result),
    )


def _parse_user_ids(raw_value: str) -> set[int]:
    user_ids: set[int] = set()
    for item in raw_value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            user_ids.add(int(item))
        except ValueError:
            continue
    return user_ids


def _query_user_ids() -> set[int]:
    return (
        _parse_user_ids(settings.telegram_query_user_ids)
        | _operator_user_ids()
        | _admin_user_ids()
    )


def _operator_user_ids() -> set[int]:
    return _parse_user_ids(settings.telegram_operator_user_ids) | _admin_user_ids()


def _admin_user_ids() -> set[int]:
    return _parse_user_ids(settings.telegram_admin_user_ids)


def _has_query_permission(user_id: int | None) -> bool:
    if not settings.telegram_query_user_ids.strip():
        return True
    return user_id in _query_user_ids()


def _has_operator_permission(user_id: int | None) -> bool:
    return user_id in _operator_user_ids()


def _has_admin_permission(user_id: int | None) -> bool:
    return user_id in _admin_user_ids()


async def _require_query_permission(message: Message) -> bool:
    if _has_query_permission(_message_user_id(message)):
        return True
    await message.answer("You do not have permission to query inventory.")
    return False


async def _require_operator_permission(message: Message) -> bool:
    if _has_operator_permission(_message_user_id(message)):
        return True
    await message.answer("You do not have permission to modify inventory. Use /whoami and ask an admin to authorize you.")
    return False


async def _require_admin_permission(message: Message) -> bool:
    if _has_admin_permission(_message_user_id(message)):
        return True
    await message.answer("You do not have admin permission. Use /whoami and ask the system owner to authorize you.")
    return False


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


def _default_customer_name_for_warehouse(warehouse: Warehouse) -> str:
    if "乐天" in warehouse.name:
        return DEFAULT_RAKUTEN_CUSTOMER
    return DEFAULT_CUSTOMER_NAME


async def _resolve_product_for_operation(
    session: AsyncSession,
    keyword: str,
    warehouse_id: int | None = None,
    customer_id: int | None = None,
) -> Product | list[Product] | None:
    products = await search_inventory_items(session=session, keyword=keyword, limit=6)
    if not products:
        return None
    if len(products) == 1:
        return products[0]
    if warehouse_id is not None:
        stocked_products: list[Product] = []
        for product in products:
            if any(
                record.warehouse_id == warehouse_id
                and (customer_id is None or record.customer_id == customer_id)
                and record.quantity > 0
                for record in product.inventory_records
            ):
                stocked_products.append(product)
        if len(stocked_products) == 1:
            return stocked_products[0]
    return products


async def _resolve_first_inventory_record(
    session: AsyncSession,
    sku: str,
    warehouse_id: int,
    customer_id: int,
) -> InventoryRecord | None:
    return await session.scalar(
        select(InventoryRecord)
        .where(
            InventoryRecord.product_jan == sku,
            InventoryRecord.warehouse_id == warehouse_id,
            InventoryRecord.customer_id == customer_id,
        )
        .order_by(InventoryRecord.id.asc())
        .limit(1)
    )


def _product_missing_message(keyword: str) -> str:
    return (
        f"Product not found: {keyword}\n"
        f"To add it, send: /add_product {keyword} 商品名日文"
    )


def _product_ambiguous_message(keyword: str, products: list[Product], command: str) -> str:
    lines = [
        f"Multiple products matched: {keyword}",
        "Please confirm the product by resending the command with the full JAN code.",
    ]
    for product in products:
        lines.append(f"{product.jan_code} | {product.name_jp} | {product.name_zh or '-'}")
    lines.append(f"Example: {command} FULL_JAN ...")
    return "\n".join(lines)


def _report_usage(command: str) -> str:
    return (
        f"Usage:\n"
        f"{command} [WAREHOUSE] [CUSTOMER]\n"
        f"paste one or many chat records here\n\n"
        f"Example:\n"
        f"{command} 普通仓库 店铺\n"
        f"4.29 到库 シンビューティ\n"
        f"htc绿色面膜 321547*3箱（40入）"
    )


def _format_report_document(document: ChatReportDocument) -> str:
    lines = [
        "Parsed report:",
        f"direction: {document.direction.value}",
        f"warehouse: {document.warehouse_name}",
        f"customer: {document.customer_name}",
        f"lines: {len(document.lines)}",
    ]
    for index, line in enumerate(document.lines, start=1):
        hint = f" | {line.product_name_hint}" if line.product_name_hint else ""
        direction = (line.direction or document.direction).value
        lines.append(f"{index}. {direction} | {line.jan_hint} | qty: {line.quantity}{hint}")
    if document.warnings:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in document.warnings)
    return "\n".join(lines)


def _draft_help(draft_id: int) -> str:
    return (
        "Next:\n"
        f"/apply_report {draft_id}\n"
        f"/show_report {draft_id}\n"
        f"/set_report_meta {draft_id} IN 普通仓库 店铺\n"
        f"/set_report_line {draft_id} 1 JAN_HINT QUANTITY 商品名\n"
        f"/add_report_line {draft_id} JAN_HINT QUANTITY 商品名\n"
        f"/del_report_line {draft_id} 1"
    )


def _format_apply_issues(issues: object) -> str:
    lines = ["Not applied. Please resolve these issues:"]
    for issue in issues:
        lines.append(f"- line {issue.line_index + 1}: {issue.issue_type} | {issue.message}")
        for candidate in issue.candidates:
            lines.append(f"  candidate: {candidate.jan_code} | {candidate.name_jp} | {candidate.name_zh or '-'}")
    return "\n".join(lines)


def _format_apply_success(document: ChatReportDocument, mutations: object) -> str:
    total_quantity = sum(mutation.quantity for mutation in mutations)
    lines = [
        "Applied chat report:",
        f"direction: {document.direction.value}",
        f"warehouse: {document.warehouse_name}",
        f"customer: {document.customer_name}",
        f"items: {len(mutations)}",
        f"total quantity: {total_quantity}",
    ]
    for mutation in mutations:
        sign = "+" if mutation.direction.value == "IN" else "-"
        lines.append(f"- {mutation.direction.value} | {mutation.jan_code} | {sign}{mutation.quantity} | tx: {mutation.transaction.id}")
        if mutation.low_stock_alert:
            lines.append(
                f"  LOW STOCK: {mutation.low_stock_alert.product_name} "
                f"remaining {mutation.low_stock_alert.total_quantity}, "
                f"threshold {mutation.low_stock_alert.threshold_quantity}"
            )
    return "\n".join(lines)


def _format_rakuten_csv_draft(
    draft_id: int,
    document: RakutenShipmentDraftDocument,
    result: RakutenShipmentImportResult,
) -> str:
    lines = [
        f"Rakuten CSV Draft ID: {draft_id}",
        f"warehouse: {document.warehouse_name}",
        f"customer: {document.customer_name}",
        f"items: {len(document.lines)}",
    ]
    preview_limit = 40
    for index, line in enumerate(document.lines[:preview_limit], start=1):
        name = f" | {line.product_name}" if line.product_name else ""
        lines.append(f"{index}. {line.jan_code} | qty: {line.quantity}{name}")
    if len(document.lines) > preview_limit:
        lines.append(f"... {len(document.lines) - preview_limit} more lines")

    lines.append("")
    lines.append(_format_rakuten_csv_result(draft_id=draft_id, result=result))
    if not result.issues:
        lines.append("")
        lines.append(f"Confirm apply: /apply_rakuten_csv {draft_id}")
    elif _rakuten_issues_can_skip(result):
        lines.append("")
        lines.append(f"Apply valid lines and skip missing stock/products: /apply_rakuten_csv {draft_id} ignore")
    else:
        lines.append("")
        lines.append("Only product_not_found, inventory_record_not_found, and insufficient_stock can be skipped with ignore.")
    return "\n".join(lines)


def _format_rakuten_csv_result(draft_id: int, result: RakutenShipmentImportResult) -> str:
    if not result.issues:
        return f"Validation OK. Total lines: {result.total_lines}"
    lines = [
        f"Rakuten CSV draft {draft_id} not applied.",
        "Please resolve these issues first:",
    ]
    for issue in result.issues:
        line_text = "-" if issue.line_index < 0 else str(issue.line_index + 1)
        lines.append(f"- line {line_text}: {issue.issue_type} | {issue.jan_code} | {issue.message}")
        for candidate in issue.candidates:
            lines.append(f"  candidate: {candidate.jan_code} | {candidate.name_jp} | {candidate.name_zh or '-'}")
    return "\n".join(lines)


def _rakuten_issues_can_skip(result: RakutenShipmentImportResult) -> bool:
    skippable = {"product_not_found", "inventory_record_not_found", "insufficient_stock"}
    return bool(result.issues) and all(issue.issue_type in skippable for issue in result.issues)


def _format_rakuten_csv_apply_success(draft_id: int, result: RakutenShipmentImportResult) -> str:
    total_quantity = sum(mutation.quantity for mutation in result.mutations)
    lines = [
        f"Applied Rakuten CSV draft: {draft_id}",
        f"items: {len(result.mutations)}",
        f"total quantity: {total_quantity}",
    ]
    for mutation in result.mutations:
        lines.append(f"- OUT | {mutation.jan_code} | -{mutation.quantity} | tx: {mutation.transaction.id}")
        if mutation.low_stock_alert:
            lines.append(
                f"  LOW STOCK: {mutation.low_stock_alert.product_name} "
                f"remaining {mutation.low_stock_alert.total_quantity}, "
                f"threshold {mutation.low_stock_alert.threshold_quantity}"
            )
    if result.issues:
        lines.append("")
        lines.append("Skipped lines:")
        for issue in result.issues:
            line_text = "-" if issue.line_index < 0 else str(issue.line_index + 1)
            lines.append(f"- line {line_text}: {issue.issue_type} | {issue.jan_code} | {issue.message}")
    return "\n".join(lines)


def _format_low_stock_alert(alert: object) -> str:
    return (
        "采购提醒：库存低于 2 箱\n"
        f"{alert.jan_code} | {alert.product_name}\n"
        f"当前库存: {alert.total_quantity}\n"
        f"箱入: {alert.units_per_case}\n"
        f"提醒阈值: {alert.threshold_quantity}"
    )


async def _answer_long(message: Message, text: str) -> None:
    chunk_size = 3500
    for start in range(0, len(text), chunk_size):
        await message.answer(text[start : start + chunk_size])
