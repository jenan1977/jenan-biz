"""
api/v1/routers/customers.py - Customer CRUD endpoints.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_company
from app.core.database import get_db
from app.models.company import Company
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate

router = APIRouter(
    prefix="/companies/{company_id}/customers",
    tags=["customers"],
)


@router.get("", response_model=List[CustomerRead])
def list_customers(
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> List[Customer]:
    return (
        db.execute(
            select(Customer)
            .where(Customer.company_id == company.id)
            .order_by(Customer.name)
        )
        .scalars()
        .all()
    )


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
def create_customer(
    body: CustomerCreate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Customer:
    customer = Customer(company_id=company.id, **body.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/{customer_id}", response_model=CustomerRead)
def get_customer(
    customer_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None or customer.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.patch("/{customer_id}", response_model=CustomerRead)
def update_customer(
    customer_id: uuid.UUID,
    body: CustomerUpdate,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None or customer.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def disable_customer(
    customer_id: uuid.UUID,
    company: Company = Depends(get_current_company),
    db: Session = Depends(get_db),
) -> None:
    customer = db.get(Customer, customer_id)
    if customer is None or customer.company_id != company.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    customer.is_active = False
    db.commit()
