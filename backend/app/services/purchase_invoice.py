"""
services/purchase_invoice.py - Service layer for purchase invoice operations.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import (
    PaymentStatus,
    PurchaseInvoiceStatus,
    ReceiptStatus,
)
from app.models.inventory import Inventory
from app.models.purchase_invoice import PurchaseInvoice
from app.models.purchase_line_item import PurchaseLineItem
from app.schemas.purchase_invoice import (
    PaymentCreate,
    PurchaseInvoiceCreate,
    PurchaseInvoiceUpdate,
    ReceiptCreate,
)
from app.services.invoice_number import generate_purchase_invoice_number
from app.services.totals import compute_invoice_totals, compute_line_total


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _build_line_items(line_data: list) -> List[PurchaseLineItem]:
    items = []
    for ld in line_data:
        line_total = compute_line_total(ld.ordered_quantity, ld.unit_price)
        items.append(
            PurchaseLineItem(
                product_id=ld.product_id,
                ordered_quantity=ld.ordered_quantity,
                unit_price=ld.unit_price,
                line_total=line_total,
                notes=ld.notes,
                received_quantity=Decimal("0.00"),
            )
        )
    return items


def _recalculate_totals(invoice: PurchaseInvoice) -> None:
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


def create_purchase_invoice(
    db: Session,
    company_id: UUID,
    data: PurchaseInvoiceCreate,
    created_by_id: UUID,
) -> PurchaseInvoice:
    invoice_number = generate_purchase_invoice_number(db, company_id)
    invoice = PurchaseInvoice(
        company_id=company_id,
        supplier_id=data.supplier_id,
        created_by_id=created_by_id,
        invoice_number=invoice_number,
        invoice_date=data.invoice_date,
        due_date=data.due_date,
        discount_amount=data.discount_amount,
        tax_rate=data.tax_rate,
        notes=data.notes,
        status=PurchaseInvoiceStatus.DRAFT,
        payment_status=PaymentStatus.UNPAID,
        receipt_status=ReceiptStatus.PENDING,
        subtotal=Decimal("0.00"),
        tax_amount=Decimal("0.00"),
        total_amount=Decimal("0.00"),
        paid_amount=Decimal("0.00"),
        remaining_amount=Decimal("0.00"),
        received_quantity=Decimal("0.00"),
    )
    invoice.line_items = _build_line_items(data.line_items)
    _recalculate_totals(invoice)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


def update_purchase_invoice(
    db: Session, invoice: PurchaseInvoice, data: PurchaseInvoiceUpdate
) -> PurchaseInvoice:
    if invoice.status != PurchaseInvoiceStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft invoices can be updated",
        )

    if data.supplier_id is not None:
        invoice.supplier_id = data.supplier_id
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
        for li in list(invoice.line_items):
            db.delete(li)
        invoice.line_items = _build_line_items(data.line_items)

    _recalculate_totals(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


# ------------------------------------------------------------------
# Lifecycle transitions
# ------------------------------------------------------------------


def issue_purchase_invoice(db: Session, invoice: PurchaseInvoice) -> PurchaseInvoice:
    """Issue a draft purchase invoice (does NOT change inventory)."""
    if invoice.status != PurchaseInvoiceStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft invoices can be issued",
        )
    invoice.status = PurchaseInvoiceStatus.ISSUED
    db.commit()
    db.refresh(invoice)
    return invoice


def void_purchase_invoice(db: Session, invoice: PurchaseInvoice) -> PurchaseInvoice:
    """Void a purchase invoice (blocked if any goods have been received)."""
    if invoice.status == PurchaseInvoiceStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invoice is already cancelled",
        )
    if invoice.received_quantity > Decimal("0.00"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot void: goods have already been received against this invoice",
        )
    invoice.status = PurchaseInvoiceStatus.CANCELLED
    db.commit()
    db.refresh(invoice)
    return invoice


def record_receipt(
    db: Session, invoice: PurchaseInvoice, data: ReceiptCreate
) -> PurchaseInvoice:
    """
    Record receipt of goods for a purchase invoice.

    Increments inventory and updates received quantities on line items.
    """
    if invoice.status not in (
        PurchaseInvoiceStatus.ISSUED,
        PurchaseInvoiceStatus.PARTIALLY_RECEIVED,
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Receipts can only be recorded for issued or partially-received invoices",
        )

    # Index line items by product id for quick lookup
    lines_by_product: dict = {str(li.product_id): li for li in invoice.line_items}

    for receipt_line in data.lines:
        key = str(receipt_line.product_id)
        line_item = lines_by_product.get(key)
        if line_item is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Product {receipt_line.product_id} is not on this invoice",
            )

        new_received = line_item.received_quantity + receipt_line.received_quantity
        if new_received > line_item.ordered_quantity:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Receipt would exceed ordered quantity for product "
                    f"{receipt_line.product_id}: "
                    f"ordered={line_item.ordered_quantity}, "
                    f"already_received={line_item.received_quantity}, "
                    f"new_receipt={receipt_line.received_quantity}"
                ),
            )

        line_item.received_quantity = new_received

        # Update inventory with row-level lock
        inv = (
            db.execute(
                select(Inventory)
                .where(
                    Inventory.company_id == invoice.company_id,
                    Inventory.product_id == receipt_line.product_id,
                )
                .with_for_update()
            )
            .scalars()
            .first()
        )
        if inv is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"No inventory record found for product {receipt_line.product_id}",
            )
        inv.quantity_on_hand += receipt_line.received_quantity
        inv.quantity_available = inv.quantity_on_hand - inv.quantity_reserved
        inv.last_received_date = datetime.now(timezone.utc)

    # Update invoice-level received_quantity and receipt_status
    total_ordered = sum(li.ordered_quantity for li in invoice.line_items)
    total_received = sum(li.received_quantity for li in invoice.line_items)
    invoice.received_quantity = total_received

    if total_received >= total_ordered:
        invoice.receipt_status = ReceiptStatus.FULLY_RECEIVED
        invoice.status = PurchaseInvoiceStatus.RECEIVED
    else:
        invoice.receipt_status = ReceiptStatus.PARTIALLY_RECEIVED
        invoice.status = PurchaseInvoiceStatus.PARTIALLY_RECEIVED

    db.commit()
    db.refresh(invoice)
    return invoice


def add_purchase_payment(
    db: Session, invoice: PurchaseInvoice, data: PaymentCreate
) -> PurchaseInvoice:
    if invoice.status == PurchaseInvoiceStatus.CANCELLED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot add payment to a cancelled invoice",
        )
    if invoice.status == PurchaseInvoiceStatus.DRAFT:
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
        invoice.status = PurchaseInvoiceStatus.PAID
    else:
        invoice.payment_status = PaymentStatus.PARTIALLY_PAID
        invoice.status = PurchaseInvoiceStatus.PARTIALLY_PAID

    db.commit()
    db.refresh(invoice)
    return invoice
