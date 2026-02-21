"""Companies schemas."""

from typing import Optional
from pydantic import EmailStr, Field

from app.shared.schemas.base_schema import BaseSchema, BaseResponseSchema


class CompanyCreate(BaseSchema):
    name: str = Field(min_length=2, max_length=255)
    legal_name: Optional[str] = None
    business_type: Optional[str] = None
    tax_number: Optional[str] = None
    registration_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Saudi Arabia"
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    currency: str = "SAR"
    vat_rate: float = 15.0


class CompanyUpdate(BaseSchema):
    name: Optional[str] = None
    legal_name: Optional[str] = None
    business_type: Optional[str] = None
    tax_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    currency: Optional[str] = None
    vat_rate: Optional[float] = None


class CompanyResponse(BaseResponseSchema):
    name: str
    legal_name: Optional[str]
    business_type: Optional[str]
    tax_number: Optional[str]
    registration_number: Optional[str]
    address: Optional[str]
    city: Optional[str]
    country: str
    phone: Optional[str]
    email: Optional[str]
    website: Optional[str]
    logo_url: Optional[str]
    currency: str
    vat_rate: float
    is_active: bool
