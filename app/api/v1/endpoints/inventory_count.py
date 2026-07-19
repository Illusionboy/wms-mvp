from datetime import date

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_db_session
from app.models.customer import Customer
from app.models.warehouse import Warehouse
from app.schemas.inventory_count import (
    InventoryCountApplyResult,
    InventoryCountDraftRead,
    InventoryCountDocument,
    QinsiSessionListResult,
)
from app.services.auth import CurrentUser
from app.services.inventory_count import (
    apply_inventory_count_draft,
    create_inventory_count_draft,
    export_draft_to_excel,
    get_inventory_count_draft,
    list_qinsi_sessions,
)

router = APIRouter()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/list-sessions", response_model=QinsiSessionListResult)
async def list_count_sessions(file: UploadFile) -> QinsiSessionListResult:
    """Parse a 秦丝生意通 HTML file and return available count sessions.

    Use this before /upload when the HTML may contain multiple count batches.
    The returned session_index values are then passed to /upload.
    """
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="文件超过 10MB 限制")
    filename = file.filename or "upload"
    if not (filename.lower().endswith(".html") or filename.lower().endswith(".htm")):
        raise HTTPException(status_code=422, detail="list-sessions 仅支持 .html 文件")
    try:
        return list_qinsi_sessions(content, filename)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/upload", response_model=InventoryCountDraftRead, status_code=status.HTTP_201_CREATED)
async def upload_count_file(
    file: UploadFile,
    count_date: date = Form(...),
    warehouse_name: str = Form(...),
    customer_name: str | None = Form(None),
    session_index: int = Form(0),
    cover_uncovered: bool = Form(True),
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> InventoryCountDraftRead:
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="文件超过 10MB 限制")
    try:
        draft = await create_inventory_count_draft(
            session=session,
            content=content,
            filename=file.filename or "upload",
            count_date=count_date,
            warehouse_name=warehouse_name,
            customer_name=customer_name,
            session_index=session_index,
            cover_uncovered=cover_uncovered,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return InventoryCountDraftRead.model_validate(draft)


@router.get("/warehouses")
async def list_warehouses(session: AsyncSession = Depends(get_db_session)) -> list[dict]:
    rows = await session.scalars(select(Warehouse).order_by(Warehouse.name))
    return [{"id": w.id, "name": w.name} for w in rows.all()]


@router.get("/customers")
async def list_customers(session: AsyncSession = Depends(get_db_session)) -> list[dict]:
    rows = await session.scalars(select(Customer).order_by(Customer.name))
    return [{"id": c.id, "name": c.name} for c in rows.all()]


@router.get("/{draft_id}", response_model=InventoryCountDraftRead)
async def get_draft(
    draft_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> InventoryCountDraftRead:
    draft = await get_inventory_count_draft(session, draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    return InventoryCountDraftRead.model_validate(draft)


@router.get("/{draft_id}/export")
async def export_draft_excel(
    draft_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    draft = await get_inventory_count_draft(session, draft_id)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    document = InventoryCountDocument.model_validate(draft.document)
    excel_bytes = export_draft_to_excel(document)
    filename = f"盘点对账_{draft.count_date}_{draft.warehouse_name}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/{draft_id}/apply", response_model=InventoryCountApplyResult)
async def apply_draft(
    draft_id: int,
    force: bool = False,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> InventoryCountApplyResult:
    draft = await get_inventory_count_draft(session, draft_id, with_for_update=True)
    if draft is None:
        raise HTTPException(status_code=404, detail="Draft not found")
    return await apply_inventory_count_draft(session, draft, user_id=current_user.id, force=force)
