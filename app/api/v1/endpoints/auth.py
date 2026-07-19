from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin, require_auth
from app.core.config import settings
from app.db.session import get_db_session
from app.models.user import User
from app.services.auth import CurrentUser, create_access_token, create_user, get_user_by_credentials

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    is_admin: bool = False


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=6)


class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool
    is_admin: bool = False

    model_config = {"from_attributes": True}


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
) -> TokenResponse:
    user = await get_user_by_credentials(session, payload.username, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    token = create_access_token(
        user_id=user.id,
        username=user.username,
        secret=settings.jwt_secret_key,
        expire_days=settings.jwt_expire_days,
    )
    return TokenResponse(access_token=token, user_id=user.id, username=user.username, is_admin=user.is_admin)


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def add_user(
    payload: UserCreate,
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> UserRead:
    try:
        user = await create_user(session, payload.username, payload.password)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists.")
    return UserRead.model_validate(user)


@router.get("/me", response_model=UserRead)
async def get_me(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_auth),
) -> UserRead:
    if current_user.id is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No user record for API key auth.")
    user = await session.get(User, current_user.id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return UserRead.model_validate(user)


@router.get("/users", response_model=list[UserRead])
async def list_users(
    session: AsyncSession = Depends(get_db_session),
    current_user: CurrentUser = Depends(require_admin),
) -> list[UserRead]:
    rows = await session.scalars(select(User).order_by(User.id))
    return [UserRead.model_validate(u) for u in rows.all()]
