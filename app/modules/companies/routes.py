"""Companies routes."""

import uuid
from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.companies.schemas import CompanyCreate, CompanyUpdate, CompanyResponse
from app.modules.companies.services import CompaniesService
from app.modules.auth.dependencies import get_current_active_user
from app.shared.models.user import User

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = CompaniesService(db)
    return await service.create(data)


@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = CompaniesService(db)
    return await service.list_all()


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = CompaniesService(db)
    return await service.get(company_id)


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: uuid.UUID,
    data: CompanyUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = CompaniesService(db)
    return await service.update(company_id, data)


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_active_user),
):
    service = CompaniesService(db)
    await service.delete(company_id)
