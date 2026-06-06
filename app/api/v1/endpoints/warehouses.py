from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_auth
from app.services.auth import CurrentUser
from app.db.session import get_db_session
from app.models.warehouse import Warehouse
from app.schemas.inventory import WarehouseCreate, WarehouseRead

router = APIRouter()


@router.post("", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_auth)])
async def create_warehouse(
    payload: WarehouseCreate,
    session: AsyncSession = Depends(get_db_session),
) -> WarehouseRead:
    warehouse = Warehouse(name=payload.name)
    session.add(warehouse)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Warehouse name already exists.",
        ) from exc
    await session.refresh(warehouse)
    return WarehouseRead.model_validate(warehouse)


@router.get("", response_model=list[WarehouseRead])
async def list_warehouses(
    session: AsyncSession = Depends(get_db_session),
) -> list[Warehouse]:
    result = await session.scalars(select(Warehouse).order_by(Warehouse.name.asc()))
    return list(result.all())


@router.patch(
    "/{warehouse_id}/allow-negative",
    response_model=WarehouseRead,
    dependencies=[Depends(require_auth)],
)
async def set_allow_negative_stock(
    warehouse_id: int,
    enabled: bool,
    session: AsyncSession = Depends(get_db_session),
) -> WarehouseRead:
    warehouse = await session.get(Warehouse, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found.")
    warehouse.allow_negative_stock = enabled
    await session.commit()
    await session.refresh(warehouse)
    return WarehouseRead.model_validate(warehouse)
