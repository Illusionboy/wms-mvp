"""报损（破损品）端点。

破损品用独立商品行承载（jan_code = "D-" + 正常JAN），因此：
- 报损 = 同仓库内 正常桶 → 破损桶 的转移，是变更操作，需要 admin
- 破损品清单是只读的，与 /negative-stock 一致不要求认证
- **折价出售不在这里**：直接走现有出库端点，sku 填 "D-xxx" 即可精确命中破损桶
"""
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.db.session import get_db_session
from app.schemas.inventory import (
    DamagedStockRead,
    DamageReportCreate,
    DamageReportResult,
)
from app.services.auth import CurrentUser
from app.services.damage import list_damaged_stock, report_damage
from app.services.inventory import (
    InsufficientStockError,
    InventoryRecordNotFoundError,
    InventoryServiceError,
    InventoryTargetNotFoundError,
)

router = APIRouter()


@router.post("/report", response_model=DamageReportResult)
async def create_damage_report(
    payload: DamageReportCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> DamageReportResult:
    """仓内发现破损：从正常库存扣减，同数量入到破损桶。

    写两笔 StockTransaction（OUT + IN，共用 reference_id），全程可追溯。
    """
    try:
        result = await report_damage(
            session,
            jan=payload.sku,
            warehouse_id=payload.warehouse_id,
            quantity=payload.quantity,
            reason=payload.reason,
            user_id=current_user.id,
            transaction_date=payload.transaction_date,
        )
    except InventoryTargetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InventoryRecordNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该商品在此仓库没有库存记录，无法报损",
        ) from exc
    except InsufficientStockError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="库存不足，报损数量不能超过当前库存",
        ) from exc
    except InventoryServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return DamageReportResult(**result)


@router.get("/stock", response_model=list[DamagedStockRead])
async def damaged_stock(
    warehouse_id: int | None = Query(None, gt=0),
    session: AsyncSession = Depends(get_db_session),
) -> list[DamagedStockRead]:
    """破损品清单（只读）。"""
    rows = await list_damaged_stock(session, warehouse_id=warehouse_id)
    return [DamagedStockRead(**r) for r in rows]
