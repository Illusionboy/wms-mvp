import csv
import io
from datetime import datetime
from urllib.parse import quote

import openpyxl
from fastapi import APIRouter, Body, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.api.deps import require_admin
from app.db.session import get_db_session
from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.schemas.inventory import (
    AliasMergePreview,
    ChatReportApplyResult,
    ChatReportDocument,
    ChatReportDraftRead,
    ChatReportParseRequest,
    InventoryRecordRead,
    ProductCatalogImportResult,
    ProductCreate,
    ProductInventoryRead,
    ProductJanAliasCreate,
    ProductJanAliasRead,
    ProductRead,
    ProductUpdate,
    RakutenApplyRequest,
    RakutenDraftPreview,
    RakutenShipmentImportResult,
    StockAdjustCreate,
    StockAdjustResult,
    StockInCreate,
    StockInResult,
    StockOutCreate,
    StockOutResult,
    StockTransactionRead,
    StockTransferCreate,
    TradeShipmentApplyRequest,
    TradeShipmentDraftDocument,
    TradeShipmentDraftPreview,
    TradeShipmentImportResult,
)
from app.services.auth import CurrentUser
from app.services.chat_reports import apply_chat_report, create_chat_report_draft, get_chat_report_draft, mark_chat_report_draft_applied
from app.services.product_catalog import import_product_catalog_from_bytes
from app.services.product_alias import create_alias, list_aliases, preview_alias_merge, remove_alias
from app.services.inventory import (
    AmbiguousInventoryRecordError,
    InsufficientStockError,
    InventoryRecordNotFoundError,
    InventoryTargetNotFoundError,
    adjust_stock_item,
    export_warehouse_inventory,
    is_outer_jan_match,
    search_inventory_items,
    search_products,
    stock_in_item,
    stock_out_item,
    transfer_stock_item,
)
from app.services.rakuten_shipments import (
    apply_rakuten_shipment_draft,
    create_rakuten_shipment_draft,
    get_rakuten_shipment_draft,
    import_rakuten_shipment_csv,
    preview_rakuten_shipment_draft,
)
from app.services.trade_shipments import (
    DEFAULT_TRADE_WAREHOUSE,
    apply_trade_shipment_draft,
    create_trade_shipment_draft,
    get_trade_shipment_draft,
    parse_trade_shipment_excel,
    parse_trade_shipment_images_with_gemini,
    preview_trade_shipment_draft,
    update_trade_shipment_draft_lines,
)

router = APIRouter()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
MAX_IMAGE_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB (phone camera photos can be large)


@router.get("/export")
async def export_inventory(
    warehouse_id: int = Query(..., description="仓库ID"),
    fmt: str = Query(default="xlsx", alias="format", description="xlsx 或 csv"),
    session: AsyncSession = Depends(get_db_session),
) -> StreamingResponse:
    """导出指定仓库全部库存为 Excel 或 CSV。无需认证。"""
    if fmt not in ("xlsx", "csv"):
        raise HTTPException(status_code=400, detail="format 仅支持 xlsx 或 csv")
    try:
        warehouse_name, rows = await export_warehouse_inventory(session, warehouse_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"库存_{warehouse_name}_{timestamp}.{fmt}"
    # Content-Disposition headers must be latin-1; CJK filenames need RFC 5987 encoding
    # (filename*=UTF-8''...) plus an ASCII fallback, or Starlette raises UnicodeEncodeError.
    content_disposition = f"attachment; filename=\"export.{fmt}\"; filename*=UTF-8''{quote(filename)}"

    if fmt == "csv":
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()) if rows else [])
        writer.writeheader()
        writer.writerows(rows)
        content = buf.getvalue().encode("utf-8-sig")  # BOM for Excel compatibility
        return StreamingResponse(
            io.BytesIO(content),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": content_disposition},
        )

    # xlsx
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = warehouse_name[:31]  # sheet name max 31 chars
    headers = ["JAN码", "商品名(日语)", "商品名(中文)", "库存数量", "箱规(个/箱)", "库位", "最后更新"]
    ws.append(headers)
    for row in rows:
        ws.append([row[h] for h in headers])
    # Auto-fit column widths (heuristic)
    for col in ws.columns:
        max_len = max((len(str(cell.value or "")) for cell in col), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": content_disposition},
    )


@router.get("/negative-stock")
async def list_negative_stock(
    warehouse_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> list[dict]:
    """Return all inventory records with quantity < 0. No auth required."""
    from sqlalchemy.orm import selectinload as sl
    stmt = (
        select(InventoryRecord)
        .options(sl(InventoryRecord.product), sl(InventoryRecord.warehouse))
        .where(InventoryRecord.quantity < 0)
    )
    if warehouse_id is not None:
        stmt = stmt.where(InventoryRecord.warehouse_id == warehouse_id)
    rows = await session.scalars(stmt.order_by(InventoryRecord.quantity.asc()))
    return [
        {
            "jan_code": r.product_jan,
            "name_jp": r.product.name_jp,
            "name_zh": r.product.name_zh,
            "warehouse_name": r.warehouse.name,
            "quantity": r.quantity,
        }
        for r in rows.all()
    ]


@router.get("/search", response_model=list[ProductInventoryRead])
async def search_inventory(
    keyword: str = Query(min_length=1, max_length=255),
    session: AsyncSession = Depends(get_db_session),
) -> list[ProductInventoryRead]:
    products = await search_inventory_items(session=session, keyword=keyword)
    results = []
    for p in products:
        r = ProductInventoryRead.model_validate(p)
        if is_outer_jan_match(keyword, p):
            r.outer_jan_warning = f"⚠ 此条码为外箱JAN（{p.outer_jan}），实际商品JAN为 {p.jan_code}"
        results.append(r)
    return results


@router.get("/products/search", response_model=list[ProductRead])
@router.get("/search_sku", response_model=list[ProductRead])
async def search_product_master(
    keyword: str = Query(min_length=1, max_length=255),
    session: AsyncSession = Depends(get_db_session),
) -> list[Product]:
    return await search_products(session=session, keyword=keyword)


@router.patch("/products/{jan_code}", response_model=ProductRead)
async def update_product(
    jan_code: str,
    payload: ProductUpdate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> Product:
    product = await session.scalar(select(Product).where(Product.jan_code == jan_code))
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"JAN {jan_code} 不存在")
    if payload.name_jp is not None:
        product.name_jp = payload.name_jp
    if payload.name_zh is not None:
        product.name_zh = payload.name_zh
    if payload.units_per_case is not None:
        product.units_per_case = payload.units_per_case
    if "outer_jan" in payload.model_fields_set:
        product.outer_jan = payload.outer_jan  # allows setting to None to clear
    await session.commit()
    await session.refresh(product)
    return product


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> Product:
    existing = await session.scalar(select(Product).where(Product.jan_code == payload.jan_code))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"JAN {payload.jan_code} 已存在")
    product = Product(
        jan_code=payload.jan_code,
        name_jp=payload.name_jp,
        name_zh=payload.name_zh,
        units_per_case=payload.units_per_case,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


@router.get("/products/{jan_code}/aliases", response_model=list[ProductJanAliasRead])
async def get_product_aliases(
    jan_code: str,
    session: AsyncSession = Depends(get_db_session),
) -> list[ProductJanAliasRead]:
    """列出该商品（主JAN）的所有别名。无需认证（只读）。"""
    return await list_aliases(session, jan_code)


@router.get("/products/{jan_code}/aliases/preview", response_model=AliasMergePreview)
async def preview_product_alias(
    jan_code: str,
    alias_jan: str = Query(..., description="待合并的别名JAN"),
    session: AsyncSession = Depends(get_db_session),
) -> AliasMergePreview:
    """预览将 alias_jan 合并为 jan_code 的别名会产生的库存变化。无需认证（只读，不写库）。"""
    try:
        return await preview_alias_merge(session, jan_code, alias_jan)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post(
    "/products/{jan_code}/aliases",
    response_model=ProductJanAliasRead,
    dependencies=[Depends(require_admin)],
)
async def add_product_alias(
    jan_code: str,
    payload: ProductJanAliasCreate,
    session: AsyncSession = Depends(get_db_session),
) -> ProductJanAliasRead:
    """确认合并：将 alias_jan 设为 jan_code 的别名，合并两边库存与历史流水。此操作不可逆。"""
    try:
        return await create_alias(session, jan_code, payload.alias_jan, payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete(
    "/products/aliases/{alias_jan}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)],
)
async def delete_product_alias(
    alias_jan: str,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """删除别名映射本身（不会撤销已经合并的库存历史）。"""
    try:
        await remove_alias(session, alias_jan)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


class _JanBatchRequest(BaseModel):
    jan_codes: list[str]


@router.post("/products/missing-batch", response_model=list[str])
async def check_missing_products(
    payload: _JanBatchRequest,
    session: AsyncSession = Depends(get_db_session),
) -> list[str]:
    """Return JAN codes that are NOT in the products catalog. No auth required."""
    if not payload.jan_codes:
        return []
    unique = list(dict.fromkeys(payload.jan_codes))  # deduplicate, preserve order
    existing = set(await session.scalars(
        select(Product.jan_code).where(Product.jan_code.in_(unique))
    ))
    return [j for j in unique if j not in existing]


@router.post("/chat-reports/parse", response_model=ChatReportDraftRead)
async def parse_chat_report(
    payload: ChatReportParseRequest,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> ChatReportDraftRead:
    try:
        draft = await create_chat_report_draft(session=session, payload=payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return ChatReportDraftRead(
        id=draft.id,
        status=draft.status,
        document=ChatReportDocument.model_validate(draft.document),
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )


@router.post("/chat-reports/{draft_id}/apply", response_model=ChatReportApplyResult)
async def apply_chat_report_draft(
    draft_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> ChatReportApplyResult:
    draft = await get_chat_report_draft(session=session, draft_id=draft_id, with_for_update=True)
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")
    if draft.status == "applied":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Draft already applied.")
    result = await apply_chat_report(
        session=session,
        document=ChatReportDocument.model_validate(draft.document),
        user_id=current_user.id,
    )
    if result.applied:
        await mark_chat_report_draft_applied(session=session, draft=draft, commit=False)
        await session.commit()
    return result


@router.post("/chat-reports/apply", response_model=ChatReportApplyResult)
async def apply_parsed_chat_report(
    payload: ChatReportDocument,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> ChatReportApplyResult:
    result = await apply_chat_report(session=session, document=payload, user_id=current_user.id)
    if result.applied:
        await session.commit()
    return result


@router.post("/imports/rakuten-shipment", response_model=RakutenShipmentImportResult, status_code=status.HTTP_202_ACCEPTED)
async def upload_rakuten_shipment_csv(
    file: UploadFile = File(...),
    warehouse_name: str = "乐天仓库",
    customer_name: str = "乐天",
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> RakutenShipmentImportResult:
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds 10 MB limit.")
    return await import_rakuten_shipment_csv(
        session=session,
        content=content,
        warehouse_name=warehouse_name,
        customer_name=customer_name,
    )


@router.post("/imports/rakuten-shipment/draft", response_model=RakutenDraftPreview, status_code=status.HTTP_202_ACCEPTED)
async def create_rakuten_draft(
    file: UploadFile = File(...),
    warehouse_name: str = "乐天仓库",
    customer_name: str = "乐天",
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> RakutenDraftPreview:
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds 10 MB limit.")
    draft = await create_rakuten_shipment_draft(
        session=session,
        content=content,
        original_filename=file.filename or "rakuten.csv",
        warehouse_name=warehouse_name,
        customer_name=customer_name,
    )
    return await preview_rakuten_shipment_draft(session=session, draft=draft)


@router.post("/imports/rakuten-shipment/draft/{draft_id}/apply", response_model=RakutenShipmentImportResult)
async def apply_rakuten_draft(
    draft_id: int,
    body: RakutenApplyRequest = Body(default_factory=RakutenApplyRequest),
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> RakutenShipmentImportResult:
    draft = await get_rakuten_shipment_draft(session, draft_id, with_for_update=True)
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")
    if draft.status in ("applied", "applied_with_skips"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Draft already applied.")
    return await apply_rakuten_shipment_draft(
        session=session,
        draft=draft,
        force_negative_jans=set(body.force_negative_jans),
        user_id=current_user.id,
    )


@router.post("/imports/trade-shipment/draft/excel", response_model=TradeShipmentDraftPreview, status_code=status.HTTP_202_ACCEPTED)
async def create_trade_shipment_draft_excel(
    file: UploadFile = File(...),
    warehouse_name: str = DEFAULT_TRADE_WAREHOUSE,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> TradeShipmentDraftPreview:
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds 10 MB limit.")
    lines = parse_trade_shipment_excel(content)
    draft = await create_trade_shipment_draft(
        session=session,
        lines=lines,
        original_filename=file.filename or "trade_shipment.xlsx",
        warehouse_name=warehouse_name,
    )
    return await preview_trade_shipment_draft(session=session, draft=draft)


@router.post("/imports/trade-shipment/draft/image", response_model=TradeShipmentDraftPreview, status_code=status.HTTP_202_ACCEPTED)
async def create_trade_shipment_draft_image(
    files: list[UploadFile] = File(...),
    warehouse_name: str = DEFAULT_TRADE_WAREHOUSE,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> TradeShipmentDraftPreview:
    images: list[tuple[bytes, str]] = []
    for file in files:
        content = await file.read(MAX_IMAGE_UPLOAD_BYTES + 1)
        if len(content) > MAX_IMAGE_UPLOAD_BYTES:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds 20 MB limit.")
        images.append((content, file.content_type or "image/jpeg"))
    if not images:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No images uploaded.")
    lines = await parse_trade_shipment_images_with_gemini(images)
    draft = await create_trade_shipment_draft(
        session=session,
        lines=lines,
        original_filename=files[0].filename or "trade_shipment.jpg",
        warehouse_name=warehouse_name,
    )
    return await preview_trade_shipment_draft(session=session, draft=draft)


@router.get("/imports/trade-shipment/draft/{draft_id}", response_model=TradeShipmentDraftPreview)
async def get_trade_shipment_draft_preview(
    draft_id: int,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> TradeShipmentDraftPreview:
    draft = await get_trade_shipment_draft(session, draft_id)
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")
    return await preview_trade_shipment_draft(session=session, draft=draft)


@router.put("/imports/trade-shipment/draft/{draft_id}", response_model=TradeShipmentDraftPreview)
async def update_trade_shipment_draft(
    draft_id: int,
    body: TradeShipmentDraftDocument,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> TradeShipmentDraftPreview:
    draft = await get_trade_shipment_draft(session, draft_id, with_for_update=True)
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")
    if draft.status in ("applied", "applied_with_skips"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Draft already applied.")
    draft = await update_trade_shipment_draft_lines(session, draft, body.lines)
    return await preview_trade_shipment_draft(session=session, draft=draft)


@router.post("/imports/trade-shipment/draft/{draft_id}/apply", response_model=TradeShipmentImportResult)
async def apply_trade_shipment_draft_endpoint(
    draft_id: int,
    body: TradeShipmentApplyRequest = Body(default_factory=TradeShipmentApplyRequest),
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> TradeShipmentImportResult:
    draft = await get_trade_shipment_draft(session, draft_id, with_for_update=True)
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")
    if draft.status in ("applied", "applied_with_skips"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Draft already applied.")
    return await apply_trade_shipment_draft(
        session=session,
        draft=draft,
        force_negative_jans=set(body.force_negative_jans),
        user_id=current_user.id,
    )


@router.post("/stock-in", response_model=StockInResult)
async def stock_in(
    payload: StockInCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> StockInResult:
    products = await search_inventory_items(session=session, keyword=payload.sku, limit=6)
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Product not found."})
    if len(products) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Multiple products matched. Use the full JAN code.", "candidates": [
                {"jan_code": p.jan_code, "name_jp": p.name_jp, "name_zh": p.name_zh} for p in products
            ]},
        )
    payload = payload.model_copy(update={"sku": products[0].jan_code})
    try:
        result = await stock_in_item(session=session, payload=payload, user_id=current_user.id)
    except InventoryTargetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SKU, warehouse, or customer not found.") from exc
    return StockInResult(
        record=InventoryRecordRead.model_validate(result.record),
        transaction=StockTransactionRead.model_validate(result.transaction),
        quantity_added=payload.quantity,
        message="Stock-in recorded successfully.",
    )


@router.post("/stock-out", response_model=StockOutResult)
async def stock_out(
    payload: StockOutCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> StockOutResult:
    products = await search_inventory_items(session=session, keyword=payload.sku, limit=6)
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Product not found."})
    if len(products) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Multiple products matched. Use the full JAN code.", "candidates": [
                {"jan_code": p.jan_code, "name_jp": p.name_jp, "name_zh": p.name_zh} for p in products
            ]},
        )
    payload = payload.model_copy(update={"sku": products[0].jan_code})
    try:
        result = await stock_out_item(session=session, payload=payload, user_id=current_user.id)
    except InventoryRecordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory record not found.") from exc
    except AmbiguousInventoryRecordError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Multiple records matched. Specify location or customer.") from exc
    except InsufficientStockError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock.") from exc
    return StockOutResult(
        record=InventoryRecordRead.model_validate(result.record),
        transaction=StockTransactionRead.model_validate(result.transaction),
        quantity_removed=payload.quantity,
        message="Stock-out recorded successfully.",
    )


@router.post("/stock-adjust", response_model=StockAdjustResult)
async def stock_adjust(
    payload: StockAdjustCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> StockAdjustResult:
    products = await search_inventory_items(session=session, keyword=payload.sku, limit=6)
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Product not found."})
    if len(products) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Multiple products matched. Use the full JAN code.", "candidates": [
                {"jan_code": p.jan_code, "name_jp": p.name_jp, "name_zh": p.name_zh} for p in products
            ]},
        )
    payload = payload.model_copy(update={"sku": products[0].jan_code})
    try:
        result = await adjust_stock_item(session=session, payload=payload, user_id=current_user.id)
    except InventoryRecordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory record not found.") from exc
    except AmbiguousInventoryRecordError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Multiple records matched.") from exc
    return StockAdjustResult(
        record=InventoryRecordRead.model_validate(result.record),
        transaction=StockTransactionRead.model_validate(result.transaction),
        previous_quantity=result.previous_quantity,
        actual_quantity=payload.actual_quantity,
        quantity_delta=result.quantity_delta,
        message="Stock adjustment recorded successfully.",
    )


@router.post("/stock-transfer")
async def stock_transfer(
    payload: StockTransferCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> dict:
    products = await search_inventory_items(session=session, keyword=payload.sku, limit=6)
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"message": "Product not found."})
    if len(products) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"message": "Multiple products matched. Use the full JAN code.", "candidates": [
                {"jan_code": p.jan_code, "name_jp": p.name_jp, "name_zh": p.name_zh} for p in products
            ]},
        )
    payload = payload.model_copy(update={"sku": products[0].jan_code})
    from app.services.inventory import InventoryServiceError
    try:
        out_result, in_result = await transfer_stock_item(session=session, payload=payload, user_id=current_user.id)
    except InventoryServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except InventoryRecordNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="调出仓库中无此商品库存记录。") from exc
    except InsufficientStockError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="调出仓库库存不足。") from exc
    return {
        "message": f"调库成功：{payload.quantity} 件从仓库 {payload.from_warehouse_id} 移至仓库 {payload.to_warehouse_id}。",
        "from_quantity_after": out_result.record.quantity,
        "to_quantity_after": in_result.record.quantity,
    }


@router.post("/imports/product-catalog", response_model=ProductCatalogImportResult)
async def upload_product_catalog(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> ProductCatalogImportResult:
    fname = (file.filename or "").lower()
    if not (fname.endswith(".xlsx") or fname.endswith(".xls")):
        raise HTTPException(status_code=400, detail="仅支持 .xlsx / .xls 文件")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="文件超过 10 MB 限制")
    try:
        counts = await import_product_catalog_from_bytes(session=session, content=content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ProductCatalogImportResult(
        created=counts["created"],
        updated=counts["updated"],
        skipped=counts["skipped"],
        total=counts["created"] + counts["updated"] + counts["skipped"],
    )
