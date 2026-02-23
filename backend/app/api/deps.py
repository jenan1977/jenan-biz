"""
api/deps.py - FastAPI dependency injection helpers.

Provides:
  - get_db              : Yield a SQLAlchemy session.
  - get_current_user    : Decode JWT and return the active User.
  - require_roles       : Factory that returns a dependency enforcing roles.
  - get_current_company : Verify the current user belongs to the requested company.
"""

import uuid
from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.constants import UserRole
from app.core.database import get_db
from app.core.security import decode_token
from app.models.company import Company
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Decode the JWT access token and return the corresponding User."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token, expected_type="access")
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    user = db.get(User, user_id)
    if user is None or not user.is_active or user.is_deleted:
        raise credentials_exception
    return user


def require_roles(*roles: UserRole) -> Callable:
    """
    Return a FastAPI dependency that ensures the current user has one of *roles*.

    Usage::

        @router.get("/admin", dependencies=[Depends(require_roles(UserRole.ADMIN))])
        def admin_endpoint(): ...
    """

    def _check(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in roles]}",
            )
        return current_user

    return _check


def get_current_company(
    company_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Company:
    """
    Return the Company with *company_id*, enforcing that:
      - The company exists.
      - The current user belongs to the company OR has the ADMIN role.
    """
    company = db.get(Company, company_id)
    if company is None or not company.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )
    if current_user.role != UserRole.ADMIN and current_user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this company",
        )
    return company
