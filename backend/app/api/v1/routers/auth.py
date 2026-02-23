"""
api/v1/routers/auth.py - Authentication endpoints.

POST /api/v1/auth/login    : Obtain access + refresh tokens.
POST /api/v1/auth/refresh  : Exchange a refresh token for a new access token.
GET  /api/v1/auth/me       : Return the current user's profile.
POST /api/v1/auth/register : Create a new user (admin only).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_roles
from app.core.constants import UserRole
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import RefreshRequest, TokenResponse, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Authenticate with username + password and return JWT tokens."""
    user = db.execute(
        select(User).where(User.username == form_data.username)
    ).scalar_one_or_none()

    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    body: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Exchange a valid refresh token for a new access + refresh token pair."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        payload = decode_token(body.refresh_token, expected_type="refresh")
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    import uuid

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    user = db.get(User, user_id)
    if user is None or not user.is_active or user.is_deleted:
        raise credentials_exception

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    """Return the authenticated user's profile."""
    return current_user


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN))],
)
def register(
    body: UserCreate,
    db: Session = Depends(get_db),
) -> User:
    """Create a new user account (admin only)."""
    import uuid as _uuid

    existing = db.execute(
        select(User).where(
            (User.username == body.username) | (User.email == body.email)
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered",
        )

    company_id = _uuid.UUID(body.company_id) if body.company_id else None

    user = User(
        username=body.username,
        email=body.email,
        password_hash=get_password_hash(body.password),
        full_name=body.full_name,
        role=UserRole(body.role),
        company_id=company_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
