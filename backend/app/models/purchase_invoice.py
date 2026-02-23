"""
purchase_invoice.py - Purchase Invoice model.
"""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import TAX_RATE, PaymentStatus, PurchaseInvoiceStatus, ReceiptStatus
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.purchase_line_item import PurchaseLineItem
    from app.models.supplier import Supplier
    from app.models.user import User


class PurchaseInvoice(BaseModel):
    """
    A purchase invoice received from a supplier.

    Financial totals
    ----------------
    total_amount   = subtotal + tax_amount - discount_amount
    remaining_amount = total_amount - paid_amount

    Invoice number format: PUR-YYYY-MM-XXXXX
    """

    __tablename__ = "purchase_invoices"
    __table_args__ = (
        CheckConstraint(
            "subtotal + tax_amount - discount_amount = total_amount",
            name="ck_purchase_invoice_total",
        ),
        CheckConstraint(
            "paid_amount <= total_amount",
            name="ck_purchase_invoice_paid_lte_total",
        ),
        UniqueConstraint(
            "invoice_number", "company_id", name="uq_purchase_invoice_number"
        ),
        Index("ix_purchase_invoice_number", "invoice_number"),
        Index("ix_purchase_invoice_date", "invoice_date"),
        Index("ix_purchase_invoice_status", "status"),
        Index("ix_purchase_invoice_supplier", "supplier_id"),
        Index("ix_purchase_invoice_company", "company_id"),
    )

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    supplier_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("suppliers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Invoice metadata
    # ------------------------------------------------------------------
    invoice_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Formatted number e.g. PUR-2026-02-00001",
    )
    invoice_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Tax rate
    # ------------------------------------------------------------------
    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
        default=Decimal(str(TAX_RATE)),
        comment="Tax rate applied to this invoice (e.g. 0.15 = 15%)",
    )

    # ------------------------------------------------------------------
    # Financial totals
    # ------------------------------------------------------------------
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="15% VAT",
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="subtotal + tax_amount - discount_amount",
    )
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    remaining_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="total_amount - paid_amount",
    )

    # ------------------------------------------------------------------
    # Receipt tracking
    # ------------------------------------------------------------------
    received_quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Cumulative quantity of goods received so far",
    )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------
    status: Mapped[PurchaseInvoiceStatus] = mapped_column(
        Enum(PurchaseInvoiceStatus, name="purchase_invoice_status"),
        nullable=False,
        default=PurchaseInvoiceStatus.DRAFT,
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="purchase_payment_status"),
        nullable=False,
        default=PaymentStatus.UNPAID,
    )
    receipt_status: Mapped[ReceiptStatus] = mapped_column(
        Enum(ReceiptStatus, name="receipt_status"),
        nullable=False,
        default=ReceiptStatus.PENDING,
    )

    # ------------------------------------------------------------------
    # Soft-delete / notes
    # ------------------------------------------------------------------
    notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    company: Mapped["Company"] = relationship(
        "Company",
        back_populates="purchase_invoices",
        lazy="select",
    )
    supplier: Mapped["Supplier"] = relationship(
        "Supplier",
        back_populates="purchase_invoices",
        lazy="select",
    )
    line_items: Mapped[List["PurchaseLineItem"]] = relationship(
        "PurchaseLineItem",
        back_populates="purchase_invoice",
        cascade="all, delete-orphan",
        lazy="select",
    )
    created_by: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="created_purchase_invoices",
        foreign_keys=[created_by_id],
        lazy="select",
    )

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------
    @property
    def is_overdue(self) -> bool:
        """Return True when the invoice is past due and not yet fully paid."""
        if self.due_date is None or self.payment_status == PaymentStatus.PAID:
            return False
        return datetime.now(timezone.utc) > self.due_date

    @property
    def days_overdue(self) -> int:
        """Return the number of days past the due date (0 if not overdue)."""
        if not self.is_overdue or self.due_date is None:
            return 0
        delta = datetime.now(timezone.utc) - self.due_date
        return delta.days

    @property
    def is_partially_received(self) -> bool:
        """Return True when some but not all ordered goods have been received."""
        return self.receipt_status == ReceiptStatus.PARTIALLY_RECEIVED

    @property
    def pending_quantity(self) -> Decimal:
        """Return total ordered quantity minus received quantity across all lines."""
        total_ordered = sum(
            (item.ordered_quantity for item in self.line_items), Decimal("0.00")
        )
        return total_ordered - self.received_quantity

    def __repr__(self) -> str:
        return (
            f"<PurchaseInvoice id={self.id} "
            f"number={self.invoice_number!r} "
            f"status={self.status}>"
        )
