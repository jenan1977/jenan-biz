"""Sales routes."""

import uuid
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.sales.schemas import InvoiceCreate, InvoiceResponse
from app.modules.sales.services import SalesService
from app.modules.auth.dependencies import get_current_active_user
from app.shared.models.user import User

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(data: InvoiceCreate, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await SalesService(db).create(data)


@router.get("/invoices", response_model=List[InvoiceResponse])
async def list_invoices(company_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await SalesService(db).list_by_company(company_id)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: uuid.UUID, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await SalesService(db).get(invoice_id)


@router.post("/invoices/{invoice_id}/pay", response_model=InvoiceResponse)
async def mark_invoice_paid(invoice_id: uuid.UUID, amount: Decimal, db: AsyncSession = Depends(get_db), _: User = Depends(get_current_active_user)):
    return await SalesService(db).mark_paid(invoice_id, amount)
