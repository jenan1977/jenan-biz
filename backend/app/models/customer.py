"""
customer.py - Customer model.
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import CustomerType
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.sales_invoice import SalesInvoice


class Customer(BaseModel):
    """
    A customer of a company that purchases goods/services.

    customer_type distinguishes retail walk-in, wholesale, and corporate
    accounts which may have different pricing and credit rules.
    """

    __tablename__ = "customers"

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Customer full name or company name",
    )

    # ------------------------------------------------------------------
    # Contact
    # ------------------------------------------------------------------
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # ------------------------------------------------------------------
    # Address
    # ------------------------------------------------------------------
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # ------------------------------------------------------------------
    # Financial
    # ------------------------------------------------------------------
    tax_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Customer VAT / tax ID",
    )
    credit_limit: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Maximum outstanding balance allowed",
    )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------
    customer_type: Mapped[CustomerType] = mapped_column(
        Enum(CustomerType, name="customer_type"),
        nullable=False,
        default=CustomerType.RETAIL,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="customers",
        lazy="select",
    )
    sales_invoices: Mapped[List["SalesInvoice"]] = relationship(
        "SalesInvoice",
        back_populates="customer",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Customer id={self.id} name={self.name!r}>"
