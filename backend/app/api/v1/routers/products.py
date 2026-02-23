"""
api/v1/routers/products.py - Product CRUD endpoints.

All endpoints are scoped under /api/v1/companies/{company_id}/products.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_company, get_current_user
from app.core.database import get_db
from app.models.company import Company
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(
    prefix="/companies/{company_id}/products",
    tags=["products"],
)


@router.get("", response_model=List[ProductRead])
def list_products(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> List[Product]:
    return (
        db.execute(
            select(Product)
            .where(Product.company_id == company.id)
            .order_by(Product.name)
        )
        .scalars()
        .all()
    )


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(
    body: ProductCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Product:
    product = Product(company_id=company.id, **body.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductRead)
def get_product(
    product_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Product:
    product = db.get(Product, product_id)
    if product is None or product.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(
    product_id: uuid.UUID,
    body: ProductUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Product:
    product = db.get(Product, product_id)
    if product is None or product.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def disable_product(
    product_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> None:
    product = db.get(Product, product_id)
    if product is None or product.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    product.is_active = False
    db.commit()
