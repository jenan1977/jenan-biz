from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime(timezone=True), nullable=False)
    payment_method = Column(String, default="cash")  # cash, bank, card
    notes = Column(String, nullable=True)

    invoice = relationship("Invoice", back_populates="payments")
