"""Analytics routes."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.analytics.services import AnalyticsService
from app.modules.auth.dependencies import get_current_active_user
from app.shared.models.user import User

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/heatmap")
async def sales_heatmap(
    company_id: uuid.UUID,
    year: int = Query(default=datetime.now().year),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return await AnalyticsService(db).sales_heatmap(company_id, year)


@router.get("/top-products")
async def top_products(
    company_id: uuid.UUID,
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return await AnalyticsService(db).top_products(company_id, limit)
