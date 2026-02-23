"""
services/sales_invoice.py - Service layer for sales invoice operations.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import InvoiceStatus, PaymentStatus
from app.models.inventory import Inventory
from app.models.sales_invoice import SalesInvoice
from app.models.sales_line_item import SalesLineItem
from app.schemas.sales_invoice import (
    PaymentCreate,
    SalesInvoiceCreate,
    SalesInvoiceUpdate,
)
from app.services.invoice_number import generate_sales_invoice_number
from app.services.totals import compute_invoice_totals, compute_line_total


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _build_line_items(db: Session, line_data: list) -> List[SalesLineItem]:
    """Build SalesLineItem ORM objects from schema data (no DB flush yet)."""
    items = []
    for ld in line_data:
        line_total = compute_line_total(ld.quantity, ld.unit_price)
        items.append(
            SalesLineItem(
                product_id=ld.product_id,
                quantity=ld.quantity,
                unit_price=ld.unit_price,
                line_total=line_total,
                notes=ld.notes,
            )
        )
    return items


def _recalculate_totals(invoice: SalesInvoice) -> None:
    """Recompute and set all financial totals on *invoice* in-place."""
    totals = compute_invoice_totals(
        line_totals=[li.line_total for li in invoice.line_items],
        tax_rate=invoice.tax_rate,
        discount_amount=invoice.discount_amount,
    )
    invoice.subtotal = totals["subtotal"]
    invoice.tax_amount = totals["tax_amount"]
    invoice.total_amount = totals["total_amount"]
    invoice.remaining_amount = invoice.total_amount - invoice.paid_amount


# ------------------------------------------------------------------
# CRUD operations
# ------------------------------------------------------------------


def create_sales_invoice(
    db: Session, company_id: UUID, data: SalesInvoiceCreate, created_by_id: UUID
) -> SalesInvoice:
    invoice_number = generate_sales_invoice_number(db, company_id)
    invoice = SalesInvoice(
        company_id=company_id,
        customer_id=data.customer_id,
        created_by_id=created_by_id,
        invoice_number=invoice_number,
        invoice_date=data.invoice_date,
        due_date=data.due_date,
        discount_amount=data.discount_amount,
        tax_rate=data.tax_rate,
        notes=data.notes,
        status=InvoiceStatus.DRAFT,
        payment_status=PaymentStatus.UNPAID,
        subtotal=Decimal("0.00"),
        tax_amount=Decimal("0.00"),
        total_amount=Decimal("0.00"),
        paid_amount=Decimal("0.00"),
        remaining_amount=Decimal("0.00"),
    )
    line_items = _build_line_items(db, data.line_items)
    invoice.line_items = line_items
    _recalculate_totals(invoice)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def update_sales_invoice(
    db: Session, invoice: SalesInvoice, data: SalesInvoiceUpdate
) -> SalesInvoice:
    if invoice.status != InvoiceStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft invoices can be updated",
        )

    if data.customer_id is not None:
        invoice.customer_id = data.customer_id
    if data.invoice_date is not None:
        invoice.invoice_date = data.invoice_date
    if data.due_date is not None:
        invoice.due_date = data.due_date
    if data.discount_amount is not None:
        invoice.discount_amount = data.discount_amount
    if data.tax_rate is not None:
        invoice.tax_rate = data.tax_rate
    if data.notes is not None:
        invoice.notes = data.notes

    if data.line_items is not None:
        # Replace all line items
        for li in list(invoice.line_items):
            db.delete(li)
        invoice.line_items = _build_line_items(db, data.line_items)

    _recalculate_totals(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


# ------------------------------------------------------------------
# Lifecycle transitions
# ------------------------------------------------------------------


def issue_sales_invoice(db: Session, invoice: SalesInvoice) -> SalesInvoice:
    """Issue a draft invoice and decrement inventory with row-level locking."""
    if invoice.status != InvoiceStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft invoices can be issued",
        )

    # Lock inventory rows and decrement
    for line in invoice.line_items:
        inv = (
            db.execute(
                select(Inventory)
                .where(
                    Inventory.company_id == invoice.company_id,
                    Inventory.product_id == line.product_id,
                )
                .with_for_update()
            )
            .scalars()
            .first()
        )
        if inv is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"No inventory record found for product {line.product_id}",
            )
        if inv.quantity_available < line.quantity:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Insufficient stock for product {line.product_id}: "
                    f"available={inv.quantity_available}, requested={line.quantity}"
                ),
            )
        inv.quantity_on_hand -= line.quantity
        inv.quantity_available = inv.quantity_on_hand - inv.quantity_reserved
        inv.last_sold_date = datetime.now(timezone.utc)

    invoice.status = InvoiceStatus.ISSUED
    db.commit()
    db.refresh(invoice)
    return invoice


def void_sales_invoice(db: Session, invoice: SalesInvoice) -> SalesInvoice:
    """Void a sales invoice, restocking inventory if it was already issued."""
    if invoice.status == InvoiceStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invoice is already cancelled",
        )

    was_issued = invoice.status in (
        InvoiceStatus.ISSUED,
        InvoiceStatus.PARTIALLY_PAID,
        InvoiceStatus.PAID,
        InvoiceStatus.OVERDUE,
    )

    if was_issued:
        # Restock inventory
        for line in invoice.line_items:
            inv = (
                db.execute(
                    select(Inventory)
                    .where(
                        Inventory.company_id == invoice.company_id,
                        Inventory.product_id == line.product_id,
                    )
                    .with_for_update()
                )
                .scalars()
                .first()
            )
            if inv is not None:
                inv.quantity_on_hand += line.quantity
                inv.quantity_available = inv.quantity_on_hand - inv.quantity_reserved

    invoice.status = InvoiceStatus.CANCELLED
    db.commit()
    db.refresh(invoice)
    return invoice


def add_sales_payment(
    db: Session, invoice: SalesInvoice, data: PaymentCreate
) -> SalesInvoice:
    if invoice.status == InvoiceStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot add payment to a cancelled invoice",
        )
    if invoice.status == InvoiceStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot add payment to a draft invoice",
        )

    new_paid = invoice.paid_amount + data.amount
    if new_paid > invoice.total_amount:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Payment would exceed total: "
                f"paid={new_paid}, total={invoice.total_amount}"
            ),
        )

    invoice.paid_amount = new_paid
    invoice.remaining_amount = invoice.total_amount - new_paid

    if invoice.remaining_amount == Decimal("0.00"):
        invoice.payment_status = PaymentStatus.PAID
        invoice.status = InvoiceStatus.PAID
    else:
        invoice.payment_status = PaymentStatus.PARTIALLY_PAID
        invoice.status = InvoiceStatus.PARTIALLY_PAID

    db.commit()
    db.refresh(invoice)
    return invoice
