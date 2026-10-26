from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.services.auth import CurrentUser
from app.db.session import get_db_session
from app.models.warehouse import Warehouse
from app.schemas.inventory import WarehouseCreate, WarehouseRead

router = APIRouter()


@router.post("", response_model=WarehouseRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
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
    dependencies=[Depends(require_admin)],
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


@router.patch(
    "/{warehouse_id}/inventory-source-mode",
    response_model=WarehouseRead,
    dependencies=[Depends(require_admin)],
)
async def set_inventory_source_mode(
    warehouse_id: int,
    mode: str,
    session: AsyncSession = Depends(get_db_session),
) -> WarehouseRead:
    """切换该仓库的库存权威源。

    ERP_MIRROR = 库存以秦丝 ERP 为准，WMS 侧拒绝手动写入（只接受秦丝同步）。
    切到 ERP_MIRROR 必须先设置 qinsi_depot_id —— 没有它镜像无从同步，
    放行只会得到一个永远同步不了、又不能手动改的死仓库。
    """
    from app.models.warehouse import InventorySourceMode

    try:
        new_mode = InventorySourceMode(mode)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的模式 {mode!r}，只能是 WMS_NATIVE 或 ERP_MIRROR",
        ) from None

    warehouse = await session.get(Warehouse, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Warehouse not found.")

    if new_mode == InventorySourceMode.erp_mirror and not warehouse.qinsi_depot_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(f"仓库「{warehouse.name}」还没关联秦丝仓库（qinsi_depot_id 为空），"
                    f"不能切换到 ERP_MIRROR —— 否则库存既同步不过来、又不许手动改。"),
        )

    warehouse.inventory_source_mode = new_mode
    await session.commit()
    await session.refresh(warehouse)
    return WarehouseRead.model_validate(warehouse)
