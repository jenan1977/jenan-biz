"""
user.py - User model for authentication and authorisation.
"""

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import UserRole
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.purchase_invoice import PurchaseInvoice
    from app.models.sales_invoice import SalesInvoice


class User(BaseModel):
    """
    System user (employee / operator) attached to a single company.

    Roles
    -----
    admin       : Full system access.
    manager     : Operational access, reports.
    accountant  : Financial data access.
    operator    : Day-to-day data entry.
    """

    __tablename__ = "users"

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique login handle",
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Bcrypt or Argon2 hashed password",
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Authorisation
    # ------------------------------------------------------------------
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.OPERATOR,
        comment="Access level within the application",
    )

    # ------------------------------------------------------------------
    # Soft-delete
    # ------------------------------------------------------------------
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="True when the user has been soft-deleted",
    )

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("companies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Owning company",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    company: Mapped[Optional["Company"]] = relationship(
        "Company",
        back_populates="users",
        lazy="select",
    )
    created_sales_invoices: Mapped[List["SalesInvoice"]] = relationship(
        "SalesInvoice",
        back_populates="created_by",
        foreign_keys="SalesInvoice.created_by_id",
        lazy="select",
    )
    created_purchase_invoices: Mapped[List["PurchaseInvoice"]] = relationship(
        "PurchaseInvoice",
        back_populates="created_by",
        foreign_keys="PurchaseInvoice.created_by_id",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r} role={self.role}>"
