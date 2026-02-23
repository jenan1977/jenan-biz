"""
supplier.py - Supplier model.
"""

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.purchase_invoice import PurchaseInvoice


class Supplier(BaseModel):
    """
    A supplier (vendor) from whom the company purchases goods/services.
    """

    __tablename__ = "suppliers"

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
        comment="Supplier trading name",
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
    # Financial / Commercial
    # ------------------------------------------------------------------
    tax_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Supplier VAT / tax ID",
    )
    payment_terms: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="e.g. Net 30, Net 60",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="suppliers",
        lazy="select",
    )
    purchase_invoices: Mapped[List["PurchaseInvoice"]] = relationship(
        "PurchaseInvoice",
        back_populates="supplier",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Supplier id={self.id} name={self.name!r}>"
