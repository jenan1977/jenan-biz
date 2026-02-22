"""
inventory.py - Inventory / stock level model.
"""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import StockStatus
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.product import Product


class Inventory(BaseModel):
    """
    Tracks real-time stock levels for a product within a company.

    quantity_available = quantity_on_hand - quantity_reserved
    (enforced by DB check constraint)
    """

    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint(
            "quantity_on_hand >= 0", name="ck_inventory_on_hand_non_negative"
        ),
        CheckConstraint(
            "quantity_reserved >= 0", name="ck_inventory_reserved_non_negative"
        ),
        CheckConstraint(
            "quantity_available = quantity_on_hand - quantity_reserved",
            name="ck_inventory_available",
        ),
        UniqueConstraint("company_id", "product_id", name="uq_inventory_company_product"),
        Index("ix_inventory_company", "company_id"),
        Index("ix_inventory_product", "product_id"),
        Index("ix_inventory_available", "quantity_available"),
    )

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Stock quantities
    # ------------------------------------------------------------------
    quantity_on_hand: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Physical stock currently in warehouse",
    )
    quantity_reserved: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Stock committed to open sales orders",
    )
    quantity_available: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="quantity_on_hand - quantity_reserved",
    )

    # ------------------------------------------------------------------
    # Reorder alert
    # ------------------------------------------------------------------
    reorder_level: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Trigger replenishment when quantity_available falls to or below this",
    )

    # ------------------------------------------------------------------
    # Activity timestamps
    # ------------------------------------------------------------------
    last_stock_check_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date/time of the last physical stock count",
    )
    last_received_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date/time goods were last received from a purchase invoice",
    )
    last_sold_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Date/time goods were last dispatched via a sales invoice",
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    company: Mapped["Company"] = relationship(
        "Company",
        lazy="select",
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="inventory",
        lazy="select",
    )

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------
    @property
    def is_low_stock(self) -> bool:
        """Return True when available quantity is at or below the reorder level."""
        if self.reorder_level is None:
            return False
        return self.quantity_available <= self.reorder_level

    @property
    def stock_status(self) -> StockStatus:
        """Categorise the current stock position."""
        if self.quantity_available <= Decimal("0.00"):
            return StockStatus.OUT_OF_STOCK
        if self.is_low_stock:
            return StockStatus.LOW_STOCK
        return StockStatus.IN_STOCK

    def __repr__(self) -> str:
        return (
            f"<Inventory id={self.id} "
            f"product={self.product_id} "
            f"available={self.quantity_available}>"
        )
