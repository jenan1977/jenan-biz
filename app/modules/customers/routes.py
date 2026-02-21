"""Customers routes."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.customers.schemas import CustomerCreate, CustomerUpdate, CustomerResponse
from app.modules.customers.services import CustomersService
from app.modules.auth.dependencies import get_current_active_user
from app.shared.models.user import User

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(data: CustomerCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await CustomersService(db).create(data)


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(company_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await CustomersService(db).list_by_company(company_id)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await CustomersService(db).get(customer_id)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: uuid.UUID, data: CustomerUpdate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await CustomersService(db).update(customer_id, data)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    await CustomersService(db).delete(customer_id)
