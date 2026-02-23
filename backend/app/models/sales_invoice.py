"""
sales_invoice.py - Sales Invoice model.
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

from app.core.constants import TAX_RATE, InvoiceStatus, PaymentStatus
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.company import Company
    from app.models.customer import Customer
    from app.models.sales_line_item import SalesLineItem
    from app.models.user import User


class SalesInvoice(BaseModel):
    """
    A sales invoice issued to a customer.

    Financial totals
    ----------------
    total_amount  = subtotal + tax_amount - discount_amount
    remaining_amount = total_amount - paid_amount

    Invoice number format: INV-YYYY-MM-XXXXX
    """

    __tablename__ = "sales_invoices"
    __table_args__ = (
        # Arithmetic integrity
        CheckConstraint(
            "subtotal + tax_amount - discount_amount = total_amount",
            name="ck_sales_invoice_total",
        ),
        CheckConstraint(
            "paid_amount <= total_amount",
            name="ck_sales_invoice_paid_lte_total",
        ),
        # Invoice numbers are unique per company
        UniqueConstraint("invoice_number", "company_id", name="uq_sales_invoice_number"),
        # Performance indexes
        Index("ix_sales_invoice_number", "invoice_number"),
        Index("ix_sales_invoice_date", "invoice_date"),
        Index("ix_sales_invoice_status", "status"),
        Index("ix_sales_invoice_customer", "customer_id"),
        Index("ix_sales_invoice_company", "company_id"),
    )

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------
    company_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"),
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
        comment="Formatted number e.g. INV-2026-02-00001",
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
        comment="Sum of all line totals before tax/discount",
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="15% VAT applied to subtotal",
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
    # Status
    # ------------------------------------------------------------------
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus, name="invoice_status"),
        nullable=False,
        default=InvoiceStatus.DRAFT,
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"),
        nullable=False,
        default=PaymentStatus.UNPAID,
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
        back_populates="sales_invoices",
        lazy="select",
    )
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="sales_invoices",
        lazy="select",
    )
    line_items: Mapped[List["SalesLineItem"]] = relationship(
        "SalesLineItem",
        back_populates="sales_invoice",
        cascade="all, delete-orphan",
        lazy="select",
    )
    created_by: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="created_sales_invoices",
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

    def __repr__(self) -> str:
        return (
            f"<SalesInvoice id={self.id} "
            f"number={self.invoice_number!r} "
            f"status={self.status}>"
        )
