"""乐天店铺凭据存取。密码加密存库；读取列表时掩码（只回是否已设置）；
`get_credential_plain` 供 P2 抓取内部解密使用（不经 API 暴露）。"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rakuten_credential import RakutenCredential
from app.schemas.rakuten_credential import RakutenCredentialRead, RakutenCredentialUpsert
from app.services.crypto import decrypt, encrypt


def _to_read(c: RakutenCredential) -> RakutenCredentialRead:
    return RakutenCredentialRead(
        id=c.id,
        store=c.store,
        store_label=c.store_label,
        rms_login_id=c.rms_login_id,
        csv_user=c.csv_user,
        has_rms_password=bool(c.rms_password_enc),
        has_csv_password=bool(c.csv_password_enc),
        enabled=c.enabled,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


async def list_credentials(session: AsyncSession) -> list[RakutenCredentialRead]:
    rows = (await session.scalars(
        select(RakutenCredential).order_by(RakutenCredential.store.asc())
    )).all()
    return [_to_read(c) for c in rows]


async def upsert_credential(
    session: AsyncSession, payload: RakutenCredentialUpsert
) -> RakutenCredentialRead:
    """按 store UPSERT。密码字段留空 = 保持原值不变（前端显示掩码、只在改时传新密码）。"""
    c = await session.scalar(
        select(RakutenCredential).where(RakutenCredential.store == payload.store).with_for_update()
    )
    if c is None:
        c = RakutenCredential(store=payload.store)
        session.add(c)

    if payload.store_label is not None:
        c.store_label = payload.store_label
    if payload.rms_login_id is not None:
        c.rms_login_id = payload.rms_login_id
    if payload.csv_user is not None:
        c.csv_user = payload.csv_user
    if payload.rms_password:  # 非空才覆盖，留空保持原密文
        c.rms_password_enc = encrypt(payload.rms_password)
    if payload.csv_password:
        c.csv_password_enc = encrypt(payload.csv_password)
    c.enabled = payload.enabled

    await session.commit()
    await session.refresh(c)
    return _to_read(c)


async def delete_credential(session: AsyncSession, store: str) -> bool:
    c = await session.scalar(select(RakutenCredential).where(RakutenCredential.store == store))
    if c is None:
        return False
    await session.delete(c)
    await session.commit()
    return True


async def get_credential_plain(session: AsyncSession, store: str) -> dict | None:
    """P2 抓取内部用：返回解密后的明文凭据。不经 API 暴露。"""
    c = await session.scalar(select(RakutenCredential).where(RakutenCredential.store == store))
    if c is None:
        return None
    return {
        "store": c.store,
        "store_label": c.store_label,
        "rms_login_id": c.rms_login_id,
        "rms_password": decrypt(c.rms_password_enc),
        "csv_user": c.csv_user,
        "csv_password": decrypt(c.csv_password_enc),
        "enabled": c.enabled,
    }
