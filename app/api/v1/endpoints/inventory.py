from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.product import Product
from app.schemas.inventory import (
    ChatReportApplyResult,
    ChatReportDocument,
    ChatReportDraftRead,
    ChatReportParseRequest,
    InventoryImportCreate,
    InventoryImportRead,
    InventoryRecordRead,
    ProductInventoryRead,
    RakutenShipmentImportResult,
    StockAdjustCreate,
    StockAdjustResult,
    StockInCreate,
    StockInResult,
    StockOutCreate,
    StockOutResult,
    StockTransactionRead,
)
from app.services.chat_reports import apply_chat_report, create_chat_report_draft, get_chat_report_draft, mark_chat_report_draft_applied
from app.services.inventory import (
    AmbiguousInventoryRecordError,
    InsufficientStockError,
    InventoryRecordNotFoundError,
    InventoryTargetNotFoundError,
    adjust_stock_item,
    create_inventory_import_job,
    search_inventory_items,
    stock_in_item,
    stock_out_item,
)
from app.services.rakuten_shipments import import_rakuten_shipment_csv

router = APIRouter()


@router.get("/search", response_model=list[ProductInventoryRead])
async def search_inventory(
    keyword: str = Query(min_length=1, max_length=255),
    session: AsyncSession = Depends(get_db_session),
) -> list[Product]:
    return await search_inventory_items(session=session, keyword=keyword)


@router.post("/chat-reports/parse", response_model=ChatReportDraftRead)
async def parse_chat_report(
    payload: ChatReportParseRequest,
    session: AsyncSession = Depends(get_db_session),
) -> ChatReportDraftRead:
    try:
        draft = await create_chat_report_draft(session=session, payload=payload)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return ChatReportDraftRead(
        id=draft.id,
        status=draft.status,
        document=ChatReportDocument.model_validate(draft.document),
        created_at=draft.created_at,
        updated_at=draft.updated_at,
    )


@router.post(
    "/imports/rakuten-shipment",
    response_model=RakutenShipmentImportResult,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_rakuten_shipment_csv(
    file: UploadFile = File(...),
    warehouse_name: str = "乐天仓库",
    customer_name: str = "乐天",
    session: AsyncSession = Depends(get_db_session),
) -> RakutenShipmentImportResult:
    if file.content_type not in {"text/csv", "application/vnd.ms-excel", "application/octet-stream"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Rakuten RMS CSV files are accepted.",
        )
    content = await file.read()
    return await import_rakuten_shipment_csv(
        session=session,
        content=content,
        warehouse_name=warehouse_name,
        customer_name=customer_name,
    )


@router.post("/chat-reports/{draft_id}/apply", response_model=ChatReportApplyResult)
async def apply_chat_report_draft(
    draft_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> ChatReportApplyResult:
    draft = await get_chat_report_draft(session=session, draft_id=draft_id)
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found.")
    if draft.status == "applied":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Draft already applied.")
    result = await apply_chat_report(session=session, document=ChatReportDocument.model_validate(draft.document))
    if result.applied:
        await mark_chat_report_draft_applied(session=session, draft=draft)
    return result


@router.post("/chat-reports/apply", response_model=ChatReportApplyResult)
async def apply_parsed_chat_report(
    payload: ChatReportDocument,
    session: AsyncSession = Depends(get_db_session),
) -> ChatReportApplyResult:
    return await apply_chat_report(session=session, document=payload)


@router.post("/stock-in", response_model=StockInResult, status_code=status.HTTP_200_OK)
async def stock_in(
    payload: StockInCreate,
    session: AsyncSession = Depends(get_db_session),
) -> StockInResult:
    products = await search_inventory_items(session=session, keyword=payload.sku, limit=6)
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Product not found. Please add the product before stock-in.",
                "add_product_hint": f"/add_product {payload.sku} 商品名日文 商品名中文",
            },
        )
    if len(products) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Multiple products matched. Confirm by retrying with the full JAN code.",
                "candidates": [
                    {"jan_code": product.jan_code, "name_jp": product.name_jp, "name_zh": product.name_zh}
                    for product in products
                ],
            },
        )
    payload = payload.model_copy(update={"sku": products[0].jan_code})
    try:
        result = await stock_in_item(session=session, payload=payload)
    except InventoryTargetNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SKU, warehouse, or customer not found. Please resolve before stock-in.",
        ) from exc

    return StockInResult(
        record=InventoryRecordRead.model_validate(result.record),
        transaction=StockTransactionRead.model_validate(result.transaction),
        quantity_added=payload.quantity,
        message="Stock-in recorded successfully.",
    )


@router.post("/stock-out", response_model=StockOutResult, status_code=status.HTTP_200_OK)
async def stock_out(
    payload: StockOutCreate,
    session: AsyncSession = Depends(get_db_session),
) -> StockOutResult:
    products = await search_inventory_items(session=session, keyword=payload.sku, limit=6)
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Product not found. Please add the product before stock-out.",
                "add_product_hint": f"/add_product {payload.sku} 商品名日文 商品名中文",
            },
        )
    if len(products) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Multiple products matched. Confirm by retrying with the full JAN code.",
                "candidates": [
                    {"jan_code": product.jan_code, "name_jp": product.name_jp, "name_zh": product.name_zh}
                    for product in products
                ],
            },
        )
    payload = payload.model_copy(update={"sku": products[0].jan_code})
    try:
        result = await stock_out_item(session=session, payload=payload)
    except InventoryRecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found for the given SKU and warehouse.",
        ) from exc
    except AmbiguousInventoryRecordError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Multiple inventory records matched. Add location_code, expiration_date, or customer_id.",
        ) from exc
    except InsufficientStockError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient stock for this stock-out request.",
        ) from exc

    return StockOutResult(
        record=InventoryRecordRead.model_validate(result.record),
        transaction=StockTransactionRead.model_validate(result.transaction),
        quantity_removed=payload.quantity,
        message="Stock-out recorded successfully.",
    )


@router.post("/stock-adjust", response_model=StockAdjustResult, status_code=status.HTTP_200_OK)
async def stock_adjust(
    payload: StockAdjustCreate,
    session: AsyncSession = Depends(get_db_session),
) -> StockAdjustResult:
    products = await search_inventory_items(session=session, keyword=payload.sku, limit=6)
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": "Product not found. Please add the product before stock-adjust.",
                "add_product_hint": f"/add_product {payload.sku} 商品名日文 商品名中文",
            },
        )
    if len(products) > 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Multiple products matched. Confirm by retrying with the full JAN code.",
                "candidates": [
                    {"jan_code": product.jan_code, "name_jp": product.name_jp, "name_zh": product.name_zh}
                    for product in products
                ],
            },
        )
    payload = payload.model_copy(update={"sku": products[0].jan_code})
    try:
        result = await adjust_stock_item(session=session, payload=payload)
    except InventoryRecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found for the given SKU and warehouse.",
        ) from exc
    except AmbiguousInventoryRecordError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Multiple inventory records matched. Add location_code, expiration_date, or customer_id.",
        ) from exc

    return StockAdjustResult(
        record=InventoryRecordRead.model_validate(result.record),
        transaction=StockTransactionRead.model_validate(result.transaction),
        previous_quantity=result.previous_quantity,
        actual_quantity=payload.actual_quantity,
        quantity_delta=result.quantity_delta,
        message="Stock adjustment recorded successfully.",
    )


@router.post(
    "/imports/monthly-count",
    response_model=InventoryImportRead,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_monthly_count(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
) -> InventoryImportRead:
    allowed_content_types = {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "text/csv",
    }
    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .xlsx, .xls, and .csv inventory count files are accepted.",
        )

    content = await file.read()
    payload = InventoryImportCreate(
        original_filename=file.filename or "inventory-count",
        content_type=file.content_type,
        file_size=len(content),
    )
    job = await create_inventory_import_job(session=session, payload=payload)
    return InventoryImportRead.model_validate(job)
