"""
api/v1/routers/inventory.py - Inventory read + manual update endpoints.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_company
from app.core.database import get_db
from app.models.company import Company
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryRead, InventoryUpdate

router = APIRouter(
    prefix="/companies/{company_id}",
    tags=["inventory"],
)


@router.get("/inventory", response_model=List[InventoryRead])
def list_inventory(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> List[Inventory]:
    return (
        db.execute(
            select(Inventory)
            .where(Inventory.company_id == company.id)
        )
        .scalars()
        .all()
    )


@router.get("/products/{product_id}/inventory", response_model=InventoryRead)
def get_product_inventory(
    product_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Inventory:
    inv = db.execute(
        select(Inventory).where(
            Inventory.company_id == company.id,
            Inventory.product_id == product_id,
        )
    ).scalar_one_or_none()
    if inv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found for this product",
        )
    return inv


@router.patch("/products/{product_id}/inventory", response_model=InventoryRead)
def update_product_inventory(
    product_id: uuid.UUID,
    body: InventoryUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Inventory:
    inv = db.execute(
        select(Inventory).where(
            Inventory.company_id == company.id,
            Inventory.product_id == product_id,
        )
    ).scalar_one_or_none()
    if inv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory record not found for this product",
        )

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(inv, field, value)

    db.commit()
    db.refresh(inv)
    return inv
