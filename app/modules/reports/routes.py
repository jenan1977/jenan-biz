"""Reports routes."""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.reports.services import ReportsService
from app.modules.auth.dependencies import get_current_active_user
from app.shared.models.user import User

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/sales")
async def sales_report(
    company_id: uuid.UUID,
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return await ReportsService(db).sales(company_id, date_from, date_to)


@router.get("/purchases")
async def purchases_report(
    company_id: uuid.UUID,
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return await ReportsService(db).purchases(company_id, date_from, date_to)


@router.get("/profit")
async def profit_report(
    company_id: uuid.UUID,
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return await ReportsService(db).profit(company_id, date_from, date_to)


@router.get("/inventory")
async def inventory_report(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return await ReportsService(db).inventory(company_id)


@router.get("/tax")
async def tax_report(
    company_id: uuid.UUID,
    date_from: date = Query(...),
    date_to: date = Query(...),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    return await ReportsService(db).tax(company_id, date_from, date_to)
