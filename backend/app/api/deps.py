"""
deps.py - FastAPI dependency helpers (JWT authentication).

The app uses a symmetric HS256 JWT.  Set SECRET_KEY and JWT_ALGORITHM in
environment variables (or .env).
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.constants import UserRole
from app.core.database import get_db

try:
    from jose import JWTError, jwt
except ImportError:  # pragma: no cover
    jwt = None  # type: ignore[assignment]
    JWTError = Exception  # type: ignore[assignment, misc]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)


class TokenData:
    """Parsed JWT claims."""

    def __init__(
        self,
        user_id: uuid.UUID,
        company_id: Optional[uuid.UUID],
        role: UserRole,
    ) -> None:
        self.user_id = user_id
        self.company_id = company_id
        self.role = role


def _decode_token(token: str) -> TokenData:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if jwt is None:
        raise credentials_exc
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = uuid.UUID(payload["sub"])
        company_id = (
            uuid.UUID(payload["company_id"]) if payload.get("company_id") else None
        )
        role = UserRole(payload["role"])
    except (JWTError, KeyError, ValueError):
        raise credentials_exc
    return TokenData(user_id=user_id, company_id=company_id, role=role)


def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """Validate JWT and return parsed token data."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _decode_token(token)


def require_agent_role(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """Require admin, manager, or accountant role."""
    allowed = {UserRole.ADMIN, UserRole.MANAGER, UserRole.ACCOUNTANT}
    if current_user.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions for agents endpoint",
        )
    return current_user
