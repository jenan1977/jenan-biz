"""User model."""

import uuid
from typing import Optional, List

from sqlalchemy import String, Boolean, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.shared.models.base_model import BaseModel


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    ACCOUNTANT = "accountant"
    SALESPERSON = "salesperson"
    VIEWER = "viewer"


class User(BaseModel):
    """User account model."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole), default=UserRole.VIEWER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True
    )

    company: Mapped[Optional["Company"]] = relationship("Company", back_populates="users")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.email}>"
