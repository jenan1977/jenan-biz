from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    sku = Column(String, unique=True, index=True, nullable=True)
    purchase_price = Column(Float, nullable=False, default=0.0)
    sale_price = Column(Float, nullable=False, default=0.0)
    unit = Column(String, default="unit")
    category = Column(String, nullable=True)
    min_stock = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
