"""Products routes."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.products.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.modules.products.services import ProductsService
from app.modules.auth.dependencies import get_current_active_user
from app.shared.models.user import User

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = ProductsService(db)
    return await service.create_product(data)


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = ProductsService(db)
    return await service.list_products(company_id)


@router.get("/low-stock", response_model=List[ProductResponse])
async def low_stock_products(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = ProductsService(db)
    return await service.get_low_stock_products(company_id)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = ProductsService(db)
    return await service.get_product(product_id)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = ProductsService(db)
    return await service.update_product(product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = ProductsService(db)
    await service.delete_product(product_id)
