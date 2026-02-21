from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.invoice import Invoice
from app.schemas.invoice_schema import InvoiceCreate, InvoiceUpdate, InvoiceOut
from app.auth.utils import get_current_active_user
from app.models.user import User
from app.services.invoice_service import InvoiceService

router = APIRouter()


@router.get("/", response_model=List[InvoiceOut])
def list_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return db.query(Invoice).all()


@router.post("/", response_model=InvoiceOut, status_code=201)
def create_invoice(
    data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return InvoiceService.create_invoice(data, db, current_user.id)


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


@router.put("/{invoice_id}", response_model=InvoiceOut)
def update_invoice(
    invoice_id: int,
    data: InvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(inv, key, value)
    db.commit()
    db.refresh(inv)
    return inv


@router.delete("/{invoice_id}", status_code=204)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    InvoiceService.delete_invoice(invoice_id, db)
