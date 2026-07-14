"""乐天店铺凭据管理端点（P2a）。均需认证。密码只写不读。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_auth
from app.db.session import get_db_session
from app.schemas.rakuten_credential import RakutenCredentialRead, RakutenCredentialUpsert
from app.services import rakuten_credentials as svc

router = APIRouter()


@router.get("/credentials", response_model=list[RakutenCredentialRead], dependencies=[Depends(require_auth)])
async def list_credentials(
    session: AsyncSession = Depends(get_db_session),
) -> list[RakutenCredentialRead]:
    return await svc.list_credentials(session)


@router.put("/credentials", response_model=RakutenCredentialRead, dependencies=[Depends(require_auth)])
async def upsert_credential(
    payload: RakutenCredentialUpsert,
    session: AsyncSession = Depends(get_db_session),
) -> RakutenCredentialRead:
    return await svc.upsert_credential(session, payload)


@router.delete("/credentials/{store}", dependencies=[Depends(require_auth)])
async def delete_credential(
    store: str,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, bool]:
    ok = await svc.delete_credential(session, store)
    if not ok:
        raise HTTPException(status_code=404, detail=f"店铺「{store}」凭据不存在")
    return {"deleted": True}
