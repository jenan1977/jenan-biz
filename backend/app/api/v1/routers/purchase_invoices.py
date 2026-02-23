"""
api/v1/routers/purchase_invoices.py - Purchase invoice lifecycle endpoints.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_company, get_current_user
from app.core.database import get_db
from app.models.company import Company
from app.models.purchase_invoice import PurchaseInvoice
from app.models.user import User
from app.schemas.purchase_invoice import (
    PaymentCreate,
    PurchaseInvoiceCreate,
    PurchaseInvoiceRead,
    PurchaseInvoiceUpdate,
    ReceiptCreate,
)
from app.services import purchase_invoice as svc

router = APIRouter(
    prefix="/companies/{company_id}/purchase-invoices",
    tags=["purchase_invoices"],
)


def _get_invoice(
    invoice_id: uuid.UUID, company: Company, db: Session
) -> PurchaseInvoice:
    inv = db.get(PurchaseInvoice, invoice_id)
    if inv is None or inv.company_id != company.id or inv.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase invoice not found",
        )
    return inv


@router.get("", response_model=List[PurchaseInvoiceRead])
def list_purchase_invoices(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> List[PurchaseInvoice]:
    return (
        db.execute(
            select(PurchaseInvoice)
            .where(
                PurchaseInvoice.company_id == company.id,
                PurchaseInvoice.is_deleted.is_(False),
            )
            .order_by(PurchaseInvoice.invoice_date.desc())
        )
        .scalars()
        .all()
    )


@router.post("", response_model=PurchaseInvoiceRead, status_code=status.HTTP_201_CREATED)
def create_purchase_invoice(
    body: PurchaseInvoiceCreate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PurchaseInvoice:
    return svc.create_purchase_invoice(db, company.id, body, current_user.id)


@router.get("/{invoice_id}", response_model=PurchaseInvoiceRead)
def get_purchase_invoice(
    invoice_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PurchaseInvoice:
    return _get_invoice(invoice_id, company, db)


@router.patch("/{invoice_id}", response_model=PurchaseInvoiceRead)
def update_purchase_invoice(
    invoice_id: uuid.UUID,
    body: PurchaseInvoiceUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PurchaseInvoice:
    inv = _get_invoice(invoice_id, company, db)
    return svc.update_purchase_invoice(db, inv, body)


@router.post("/{invoice_id}/issue", response_model=PurchaseInvoiceRead)
def issue_purchase_invoice(
    invoice_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PurchaseInvoice:
    inv = _get_invoice(invoice_id, company, db)
    return svc.issue_purchase_invoice(db, inv)


@router.post("/{invoice_id}/void", response_model=PurchaseInvoiceRead)
def void_purchase_invoice(
    invoice_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PurchaseInvoice:
    inv = _get_invoice(invoice_id, company, db)
    return svc.void_purchase_invoice(db, inv)


@router.post("/{invoice_id}/receipts", response_model=PurchaseInvoiceRead)
def record_receipt(
    invoice_id: uuid.UUID,
    body: ReceiptCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PurchaseInvoice:
    inv = _get_invoice(invoice_id, company, db)
    return svc.record_receipt(db, inv, body)


@router.post("/{invoice_id}/payments", response_model=PurchaseInvoiceRead)
def add_payment(
    invoice_id: uuid.UUID,
    body: PaymentCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> PurchaseInvoice:
    inv = _get_invoice(invoice_id, company, db)
    return svc.add_purchase_payment(db, inv, body)
