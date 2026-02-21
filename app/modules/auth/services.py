"""Auth service: registration, login, token management."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.shared.models.user import User
from app.shared.exceptions.custom_exceptions import (
    UnauthorizedException,
    AlreadyExistsException,
    NotFoundException,
)
from app.modules.auth.schemas import RegisterRequest, LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def register(self, data: RegisterRequest) -> User:
        """Create a new user account."""
        result = await self.db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise AlreadyExistsException("Email already registered.")

        result = await self.db.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none():
            raise AlreadyExistsException("Username already taken.")

        user = User(
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            hashed_password=hash_password(data.password),
            phone=data.phone,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate user and return tokens."""
        result = await self.db.execute(select(User).where(User.email == data.email))
        user: Optional[User] = result.scalar_one_or_none()

        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedException("Account is deactivated.")

        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )

    async def get_current_user(self, token: str) -> User:
        """Decode token and return the authenticated user."""
        try:
            payload = decode_token(token)
            user_id = payload.get("sub")
        except Exception:
            raise UnauthorizedException("Invalid or expired token.")

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("User not found.")
        return user

    async def change_password(self, user: User, current_password: str, new_password: str) -> None:
        """Change user's password after verifying the current one."""
        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedException("Current password is incorrect.")
        user.hashed_password = hash_password(new_password)
        await self.db.flush()
