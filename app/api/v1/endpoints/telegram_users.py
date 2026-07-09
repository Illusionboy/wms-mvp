from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_auth
from app.db.session import get_db_session
from app.models.telegram_allowed_user import TelegramAllowedUser
from app.services.auth import CurrentUser

router = APIRouter()


class TelegramUserRead(BaseModel):
    id: int
    telegram_user_id: int
    username: str | None
    note: str | None

    model_config = {"from_attributes": True}


class TelegramUserCreate(BaseModel):
    telegram_user_id: int
    username: str | None = None
    note: str | None = None


@router.get("", response_model=list[TelegramUserRead])
async def list_telegram_users(
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(require_auth),
) -> list[TelegramAllowedUser]:
    rows = await session.scalars(
        select(TelegramAllowedUser).order_by(TelegramAllowedUser.id)
    )
    return list(rows.all())


@router.post("", response_model=TelegramUserRead, status_code=status.HTTP_201_CREATED)
async def add_telegram_user(
    body: TelegramUserCreate,
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(require_auth),
) -> TelegramAllowedUser:
    existing = await session.scalar(
        select(TelegramAllowedUser).where(
            TelegramAllowedUser.telegram_user_id == body.telegram_user_id
        )
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Telegram user {body.telegram_user_id} already authorised.",
        )
    user = TelegramAllowedUser(
        telegram_user_id=body.telegram_user_id,
        username=body.username,
        note=body.note,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.delete("/{telegram_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_telegram_user(
    telegram_user_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: CurrentUser = Depends(require_auth),
) -> None:
    user = await session.scalar(
        select(TelegramAllowedUser).where(
            TelegramAllowedUser.telegram_user_id == telegram_user_id
        )
    )
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    await session.delete(user)
    await session.commit()
