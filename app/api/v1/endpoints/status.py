from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.inventory import WarehouseStatusRead
from app.services.inventory import get_system_status

router = APIRouter()


@router.get("", response_model=list[WarehouseStatusRead])
async def system_status(
    session: AsyncSession = Depends(get_db_session),
) -> list[WarehouseStatusRead]:
    return await get_system_status(session)
