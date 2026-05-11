from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.warehouse import Warehouse
from app.schemas.inventory import WarehouseCreate, WarehouseRead

router = APIRouter()


@router.post("", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED)
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
