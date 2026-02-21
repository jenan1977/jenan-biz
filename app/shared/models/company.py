"""Company model."""

from typing import Optional, List

from sqlalchemy import String, Boolean, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.models.base_model import BaseModel


class Company(BaseModel):
    """Business company / tenant model."""

    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    business_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tax_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True)
    registration_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="Saudi Arabia")
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="SAR")
    vat_rate: Mapped[float] = mapped_column(Float, default=15.0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    users: Mapped[List["User"]] = relationship("User", back_populates="company")

    def __repr__(self) -> str:
        return f"<Company {self.name}>"
