"""
company.py - Company model: the top-level tenant entity.
"""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.product import Product
    from app.models.purchase_invoice import PurchaseInvoice
    from app.models.sales_invoice import SalesInvoice
    from app.models.supplier import Supplier
    from app.models.user import User


class Company(BaseModel):
    """
    Represents a business entity (tenant) in the system.

    All other entities (users, customers, products, invoices, etc.) belong
    to a company to support multi-tenant isolation.
    """

    __tablename__ = "companies"

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Legal / trading name of the company",
    )
    registration_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        comment="Official company registration number",
    )

    # ------------------------------------------------------------------
    # Contact
    # ------------------------------------------------------------------
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Primary contact e-mail",
    )
    phone: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Primary contact phone number",
    )

    # ------------------------------------------------------------------
    # Address
    # ------------------------------------------------------------------
    address: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Street address",
    )
    city: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )
    country: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Tax / Legal
    # ------------------------------------------------------------------
    tax_number: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="VAT / tax identification number",
    )

    # ------------------------------------------------------------------
    # Branding
    # ------------------------------------------------------------------
    logo_url: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="URL to the company logo image",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    users: Mapped[List["User"]] = relationship(
        "User",
        back_populates="company",
        lazy="select",
    )
    customers: Mapped[List["Customer"]] = relationship(
        "Customer",
        back_populates="company",
        lazy="select",
    )
    suppliers: Mapped[List["Supplier"]] = relationship(
        "Supplier",
        back_populates="company",
        lazy="select",
    )
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="company",
        lazy="select",
    )
    sales_invoices: Mapped[List["SalesInvoice"]] = relationship(
        "SalesInvoice",
        back_populates="company",
        lazy="select",
    )
    purchase_invoices: Mapped[List["PurchaseInvoice"]] = relationship(
        "PurchaseInvoice",
        back_populates="company",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name!r}>"
