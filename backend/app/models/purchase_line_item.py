"""
purchase_line_item.py - Individual line on a purchase invoice.
"""

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.purchase_invoice import PurchaseInvoice


class PurchaseLineItem(BaseModel):
    """
    A single product line on a PurchaseInvoice.

    line_total = ordered_quantity × unit_price  (DB check constraint)
    """

    __tablename__ = "purchase_line_items"
    __table_args__ = (
        CheckConstraint(
            "ordered_quantity > 0", name="ck_purchase_line_ordered_qty_positive"
        ),
        CheckConstraint(
            "received_quantity <= ordered_quantity",
            name="ck_purchase_line_received_lte_ordered",
        ),
        CheckConstraint(
            "unit_price >= 0", name="ck_purchase_line_price_non_negative"
        ),
        CheckConstraint(
            "line_total = ordered_quantity * unit_price",
            name="ck_purchase_line_total",
        ),
        Index("ix_purchase_line_invoice", "purchase_invoice_id"),
        Index("ix_purchase_line_product", "product_id"),
    )

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------
    purchase_invoice_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("purchase_invoices.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Quantities & pricing
    # ------------------------------------------------------------------
    ordered_quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Number of units ordered (must be > 0)",
    )
    received_quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Cumulative units received (updated on goods receipt)",
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        comment="Purchase price per unit",
    )
    line_total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        comment="ordered_quantity × unit_price",
    )

    # ------------------------------------------------------------------
    # Optional notes
    # ------------------------------------------------------------------
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    purchase_invoice: Mapped["PurchaseInvoice"] = relationship(
        "PurchaseInvoice",
        back_populates="line_items",
        lazy="select",
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="purchase_line_items",
        lazy="select",
    )

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------
    @property
    def pending_quantity(self) -> Decimal:
        """Return ordered_quantity minus received_quantity."""
        return self.ordered_quantity - self.received_quantity

    def __repr__(self) -> str:
        return (
            f"<PurchaseLineItem id={self.id} "
            f"invoice={self.purchase_invoice_id} "
            f"product={self.product_id} qty={self.ordered_quantity}>"
        )
