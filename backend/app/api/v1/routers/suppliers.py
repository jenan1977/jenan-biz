"""
api/v1/routers/suppliers.py - Supplier CRUD endpoints.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_company
from app.core.database import get_db
from app.models.company import Company
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierRead, SupplierUpdate

router = APIRouter(
    prefix="/companies/{company_id}/suppliers",
    tags=["suppliers"],
)


@router.get("", response_model=List[SupplierRead])
def list_suppliers(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> List[Supplier]:
    return (
        db.execute(
            select(Supplier)
            .where(Supplier.company_id == company.id)
            .order_by(Supplier.name)
        )
        .scalars()
        .all()
    )


@router.post("", response_model=SupplierRead, status_code=status.HTTP_201_CREATED)
def create_supplier(
    body: SupplierCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Supplier:
    supplier = Supplier(company_id=company.id, **body.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("/{supplier_id}", response_model=SupplierRead)
def get_supplier(
    supplier_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Supplier:
    supplier = db.get(Supplier, supplier_id)
    if supplier is None or supplier.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return supplier


@router.patch("/{supplier_id}", response_model=SupplierRead)
def update_supplier(
    supplier_id: uuid.UUID,
    body: SupplierUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Supplier:
    supplier = db.get(Supplier, supplier_id)
    if supplier is None or supplier.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def disable_supplier(
    supplier_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> None:
    supplier = db.get(Supplier, supplier_id)
    if supplier is None or supplier.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    supplier.is_active = False
    db.commit()
