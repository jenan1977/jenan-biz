from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.user import User
from ..schemas.purchase import PurchaseInvoiceCreate, PurchaseInvoiceUpdate, PurchaseInvoiceResponse
from ..crud import purchases as crud
from ..utils.auth import get_current_active_user
from ..utils.file_upload import save_upload_file

router = APIRouter(prefix="/purchases", tags=["purchases"])


@router.get("/", response_model=List[PurchaseInvoiceResponse])
def list_invoices(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return crud.get_purchase_invoices(db, skip=skip, limit=limit)


@router.get("/{invoice_id}", response_model=PurchaseInvoiceResponse)
def get_invoice(invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    invoice = crud.get_purchase_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.post("/", response_model=PurchaseInvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice: PurchaseInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return crud.create_purchase_invoice(db, invoice, current_user.id)


@router.put("/{invoice_id}", response_model=PurchaseInvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice: PurchaseInvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    updated = crud.update_purchase_invoice(db, invoice_id, invoice)
    if not updated:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return updated


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if not crud.delete_purchase_invoice(db, invoice_id):
        raise HTTPException(status_code=404, detail="Invoice not found")


@router.post("/{invoice_id}/upload-file", response_model=PurchaseInvoiceResponse)
async def upload_file(
    invoice_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    invoice = crud.get_purchase_invoice(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    file_url = await save_upload_file(file)
    return crud.update_invoice_file(db, invoice_id, file_url)
