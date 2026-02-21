"""Auth FastAPI dependencies."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.shared.models.user import User, UserRole
from app.modules.auth.services import AuthService
from app.shared.exceptions.custom_exceptions import UnauthorizedException, ForbiddenException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI dependency: resolve the authenticated user from JWT."""
    service = AuthService(db)
    try:
        return await service.get_current_user(token)
    except (UnauthorizedException, Exception) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user.")
    return user


def require_roles(*roles: UserRole):
    """Dependency factory: ensure user has one of the specified roles."""
    async def _checker(user: User = Depends(get_current_active_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions.")
        return user
    return _checker
