"""
sales_line_item.py - Individual line on a sales invoice.
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.sales_invoice import SalesInvoice


class SalesLineItem(BaseModel):
    """
    A single product line on a SalesInvoice.

    line_total = quantity × unit_price  (enforced by DB check constraint)
    """

    __tablename__ = "sales_line_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_sales_line_qty_positive"),
        CheckConstraint("unit_price >= 0", name="ck_sales_line_price_non_negative"),
        CheckConstraint(
            "line_total = quantity * unit_price",
            name="ck_sales_line_total",
        ),
        Index("ix_sales_line_invoice", "sales_invoice_id"),
        Index("ix_sales_line_product", "product_id"),
    )

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------
    sales_invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sales_invoices.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Quantities & pricing
    # ------------------------------------------------------------------
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Number of units sold (must be > 0)",
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Selling price per unit at time of sale",
    )
    line_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="quantity × unit_price",
    )

    # ------------------------------------------------------------------
    # Optional notes
    # ------------------------------------------------------------------
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    sales_invoice: Mapped["SalesInvoice"] = relationship(
        "SalesInvoice",
        back_populates="line_items",
        lazy="select",
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="sales_line_items",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<SalesLineItem id={self.id} "
            f"invoice={self.sales_invoice_id} "
            f"product={self.product_id} qty={self.quantity}>"
        )
