"""
product.py - Product / SKU model.
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.inventory import Inventory
    from app.models.purchase_line_item import PurchaseLineItem
    from app.models.sales_line_item import SalesLineItem


class Product(BaseModel):
    """
    A product or service that can be sold or purchased.

    ``sku`` must be unique within a company (enforced by a composite unique
    constraint) but two different companies may share the same SKU string.
    """

    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("company_id", "sku", name="uq_product_company_sku"),
    )

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
        comment="Human-readable product name",
    )
    description: Mapped[Optional[str]] = mapped_column(
        String(1000),
        nullable=True,
    )
    sku: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="Stock-keeping unit identifier (unique per company)",
    )
    barcode: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment="EAN / UPC / QR barcode value",
    )

    # ------------------------------------------------------------------
    # Pricing
    # ------------------------------------------------------------------
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Default selling price per unit",
    )
    cost_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Average or standard cost price per unit",
    )

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------
    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="products",
        lazy="select",
    )
    sales_line_items: Mapped[List["SalesLineItem"]] = relationship(
        "SalesLineItem",
        back_populates="product",
        lazy="select",
    )
    purchase_line_items: Mapped[List["PurchaseLineItem"]] = relationship(
        "PurchaseLineItem",
        back_populates="product",
        lazy="select",
    )
    inventory: Mapped[Optional["Inventory"]] = relationship(
        "Inventory",
        back_populates="product",
        uselist=False,
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Product id={self.id} sku={self.sku!r} name={self.name!r}>"
