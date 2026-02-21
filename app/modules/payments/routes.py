"""Payments routes."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.payments.schemas import PaymentCreate, PaymentResponse
from app.modules.payments.services import PaymentsService
from app.modules.auth.dependencies import get_current_active_user
from app.shared.models.user import User

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(data: PaymentCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await PaymentsService(db).create(data)


@router.get("/", response_model=List[PaymentResponse])
async def list_payments(company_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await PaymentsService(db).list_by_company(company_id)


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await PaymentsService(db).get(payment_id)
