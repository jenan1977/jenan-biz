"""Auth schemas."""

from typing import Optional
from pydantic import EmailStr, Field

from app.shared.schemas.base_schema import BaseSchema, BaseResponseSchema
from app.shared.models.user import UserRole


class LoginRequest(BaseSchema):
    email: EmailStr
    password: str


class RegisterRequest(BaseSchema):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8)
    phone: Optional[str] = None


class TokenResponse(BaseSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseSchema):
    refresh_token: str


class UserResponse(BaseResponseSchema):
    email: str
    username: str
    full_name: str
    phone: Optional[str]
    role: UserRole
    is_active: bool
    is_verified: bool


class ChangePasswordRequest(BaseSchema):
    current_password: str
    new_password: str = Field(min_length=8)
