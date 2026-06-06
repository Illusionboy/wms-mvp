from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db_session
from app.services.auth import CurrentUser, decode_access_token, get_user_by_id

_bearer = HTTPBearer(auto_error=False)
_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
    api_key: str | None = Security(_api_key_header),
    session: AsyncSession = Depends(get_db_session),
) -> CurrentUser:
    """Accept either a JWT Bearer token (web UI) or X-API-Key header (scripts/tools)."""
    if credentials and credentials.scheme.lower() == "bearer":
        secret = settings.jwt_secret_key
        payload = decode_access_token(credentials.credentials, secret)
        if payload:
            user = await get_user_by_id(session, int(payload["sub"]))
            if user:
                return CurrentUser(id=user.id, username=user.username)

    if api_key and settings.api_key and api_key == settings.api_key:
        return CurrentUser(id=None, username="api_key")

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide Authorization: Bearer <token> or X-API-Key header.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def require_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    """Legacy dependency kept for backward compatibility with tool scripts."""
    configured_key = settings.api_key
    if not configured_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API_KEY is not configured on this server.",
        )
    if api_key != configured_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
        )
