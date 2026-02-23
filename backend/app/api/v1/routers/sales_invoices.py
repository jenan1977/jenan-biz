"""
api/v1/routers/sales_invoices.py - Sales invoice lifecycle endpoints.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_company, get_current_user
from app.core.database import get_db
from app.models.company import Company
from app.models.sales_invoice import SalesInvoice
from app.models.user import User
from app.schemas.sales_invoice import (
    PaymentCreate,
    SalesInvoiceCreate,
    SalesInvoiceRead,
    SalesInvoiceUpdate,
)
from app.services import sales_invoice as svc

router = APIRouter(
    prefix="/companies/{company_id}/sales-invoices",
    tags=["sales_invoices"],
)


def _get_invoice(
    invoice_id: uuid.UUID, company: Company, db: Session
) -> SalesInvoice:
    inv = db.get(SalesInvoice, invoice_id)
    if inv is None or inv.company_id != company.id or inv.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales invoice not found",
        )
    return inv


@router.get("", response_model=List[SalesInvoiceRead])
def list_sales_invoices(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> List[SalesInvoice]:
    return (
        db.execute(
            select(SalesInvoice)
            .where(SalesInvoice.company_id == company.id, SalesInvoice.is_deleted.is_(False))
            .order_by(SalesInvoice.invoice_date.desc())
        )
        .scalars()
        .all()
    )


@router.post("", response_model=SalesInvoiceRead, status_code=status.HTTP_201_CREATED)
def create_sales_invoice(
    body: SalesInvoiceCreate,
    company: Company = Depends(get_current_company),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SalesInvoice:
    return svc.create_sales_invoice(db, company.id, body, current_user.id)


@router.get("/{invoice_id}", response_model=SalesInvoiceRead)
def get_sales_invoice(
    invoice_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SalesInvoice:
    return _get_invoice(invoice_id, company, db)


@router.patch("/{invoice_id}", response_model=SalesInvoiceRead)
def update_sales_invoice(
    invoice_id: uuid.UUID,
    body: SalesInvoiceUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SalesInvoice:
    inv = _get_invoice(invoice_id, company, db)
    return svc.update_sales_invoice(db, inv, body)


@router.post("/{invoice_id}/issue", response_model=SalesInvoiceRead)
def issue_sales_invoice(
    invoice_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SalesInvoice:
    inv = _get_invoice(invoice_id, company, db)
    return svc.issue_sales_invoice(db, inv)


@router.post("/{invoice_id}/void", response_model=SalesInvoiceRead)
def void_sales_invoice(
    invoice_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SalesInvoice:
    inv = _get_invoice(invoice_id, company, db)
    return svc.void_sales_invoice(db, inv)


@router.post("/{invoice_id}/payments", response_model=SalesInvoiceRead)
def add_payment(
    invoice_id: uuid.UUID,
    body: PaymentCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> SalesInvoice:
    inv = _get_invoice(invoice_id, company, db)
    return svc.add_sales_payment(db, inv, body)
