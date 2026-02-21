"""Suppliers routes."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.suppliers.schemas import SupplierCreate, SupplierUpdate, SupplierResponse
from app.modules.suppliers.services import SuppliersService
from app.modules.auth.dependencies import get_current_active_user
from app.shared.models.user import User

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post("/", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(data: SupplierCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await SuppliersService(db).create(data)


@router.get("/", response_model=List[SupplierResponse])
async def list_suppliers(company_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await SuppliersService(db).list_by_company(company_id)


@router.get("/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await SuppliersService(db).get(supplier_id)


@router.put("/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(supplier_id: uuid.UUID, data: SupplierUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await SuppliersService(db).update(supplier_id, data)


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier(supplier_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    await SuppliersService(db).delete(supplier_id)
