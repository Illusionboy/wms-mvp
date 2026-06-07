from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.api.deps import require_auth
from app.db.session import get_db_session
from app.models.inventory_record import InventoryRecord
from app.models.product import Product
from app.schemas.inventory import (
    ChatReportApplyResult,
    ChatReportDocument,
    ChatReportDraftRead,
    ChatReportParseRequest,
    InventoryRecordRead,
    ProductCatalogImportResult,
    ProductCreate,
    ProductInventoryRead,
    ProductRead,
    ProductUpdate,
    RakutenShipmentImportResult,
    StockAdjustCreate,
    StockAdjustResult,
    StockInCreate,
    StockInResult,
    StockOutCreate,
    StockOutResult,
    StockTransactionRead,
)
from app.services.auth import CurrentUser
from app.services.chat_reports import apply_chat_report, create_chat_report_draft, get_chat_report_draft, mark_chat_report_draft_applied
from app.services.product_catalog import import_product_catalog_from_bytes
from app.services.inventory import (
    AmbiguousInventoryRecordError,
    InsufficientStockError,
    InventoryRecordNotFoundError,
    InventoryTargetNotFoundError,
    adjust_stock_item,
    search_inventory_items,
    search_products,
    stock_in_item,
    stock_out_item,
)
from app.services.rakuten_shipments import import_rakuten_shipment_csv

router = APIRouter()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


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
) -> list[Product]:
    return await search_inventory_items(session=session, keyword=keyword)


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
    current_user: CurrentUser = Depends(require_auth),
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
    await session.commit()
    await session.refresh(product)
    return product


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_auth),
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
    current_user: CurrentUser = Depends(require_auth),
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
    current_user: CurrentUser = Depends(require_auth),
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
    current_user: CurrentUser = Depends(require_auth),
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
    current_user: CurrentUser = Depends(require_auth),
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


@router.post("/stock-in", response_model=StockInResult)
async def stock_in(
    payload: StockInCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_auth),
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
    current_user: CurrentUser = Depends(require_auth),
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
    current_user: CurrentUser = Depends(require_auth),
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


@router.post("/imports/product-catalog", response_model=ProductCatalogImportResult)
async def upload_product_catalog(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_auth),
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
