"""Inventory routes."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.inventory.schemas import StockMovementCreate, StockMovementResponse, StockAdjustment
from app.modules.inventory.services import InventoryService
from app.modules.auth.dependencies import get_current_active_user
from app.shared.models.user import User

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/movements", response_model=StockMovementResponse, status_code=status.HTTP_201_CREATED)
async def record_movement(
    data: StockMovementCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = InventoryService(db)
    return await service.record_movement(data)


@router.post("/adjust", response_model=StockMovementResponse)
async def adjust_stock(
    data: StockAdjustment,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = InventoryService(db)
    return await service.adjust_stock(data)


@router.get("/movements/{product_id}", response_model=List[StockMovementResponse])
async def get_movements(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = InventoryService(db)
    return await service.get_movements(product_id)
