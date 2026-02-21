"""Purchases routes."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.purchases.schemas import PurchaseCreate, PurchaseResponse
from app.modules.purchases.services import PurchasesService
from app.modules.auth.dependencies import get_current_active_user
from app.shared.models.user import User

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.post("/", response_model=PurchaseResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase(data: PurchaseCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await PurchasesService(db).create(data)


@router.get("/", response_model=List[PurchaseResponse])
async def list_purchases(company_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await PurchasesService(db).list_by_company(company_id)


@router.get("/{purchase_id}", response_model=PurchaseResponse)
async def get_purchase(purchase_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await PurchasesService(db).get(purchase_id)
