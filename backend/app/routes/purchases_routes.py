from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.purchase import PurchaseInvoice
from app.schemas.purchase_schema import PurchaseInvoiceCreate, PurchaseInvoiceUpdate, PurchaseInvoiceOut
from app.auth.utils import get_current_active_user
from app.models.user import User
from app.services.purchase_service import PurchaseService
from app.services.file_service import FileService

router = APIRouter()


@router.get("/", response_model=List[PurchaseInvoiceOut])
def list_purchases(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return db.query(PurchaseInvoice).all()


@router.post("/", response_model=PurchaseInvoiceOut, status_code=201)
def create_purchase(
    data: PurchaseInvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return PurchaseService.create_purchase(data, db, current_user.id)


@router.get("/{invoice_id}", response_model=PurchaseInvoiceOut)
def get_purchase(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    inv = db.query(PurchaseInvoice).filter(PurchaseInvoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Purchase invoice not found")
    return inv


@router.put("/{invoice_id}", response_model=PurchaseInvoiceOut)
def update_purchase(
    invoice_id: int,
    data: PurchaseInvoiceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    inv = db.query(PurchaseInvoice).filter(PurchaseInvoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Purchase invoice not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(inv, key, value)
    db.commit()
    db.refresh(inv)
    return inv


@router.delete("/{invoice_id}", status_code=204)
def delete_purchase(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    PurchaseService.delete_purchase(invoice_id, db)


@router.post("/{invoice_id}/upload")
async def upload_file(
    invoice_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    inv = db.query(PurchaseInvoice).filter(PurchaseInvoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Purchase invoice not found")
    path = await FileService.save_file(file)
    inv.file_path = path
    db.commit()
    return {"file_path": path}
