"""
tests/test_invoice_numbers.py - Unit tests for invoice number generation.

Uses an in-memory SQLite database to avoid needing PostgreSQL in CI.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.services.invoice_number import (
    generate_purchase_invoice_number,
    generate_sales_invoice_number,
)

# Import all models to ensure metadata is populated
import app.models  # noqa: F401


@pytest.fixture(scope="module")
def db_session():
    """Provide a fresh in-memory SQLite session for the module."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    # SQLite does not support FOR UPDATE; patch _next_sequence to use the fallback
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


class TestGenerateSalesInvoiceNumber:
    def test_first_number(self, db_session) -> None:
        company_id = uuid.uuid4()
        now = datetime(2026, 2, 1, tzinfo=timezone.utc)
        with patch("app.services.invoice_number.datetime") as mock_dt:
            mock_dt.now.return_value = now
            number = generate_sales_invoice_number(db_session, company_id)
        assert number == "INV-2026-02-00001"

    def test_sequential_numbers(self, db_session) -> None:
        """Second call for the same company+month should return 00002."""
        from decimal import Decimal

        from app.models.company import Company
        from app.models.customer import Customer
        from app.models.sales_invoice import SalesInvoice
        from app.core.constants import InvoiceStatus, PaymentStatus

        company_id = uuid.uuid4()
        now = datetime(2026, 3, 15, tzinfo=timezone.utc)

        # Create required company
        company = Company(id=company_id, name="Test Co")
        db_session.add(company)
        db_session.flush()

        # Create a customer
        customer = Customer(id=uuid.uuid4(), company_id=company_id, name="Test Customer")
        db_session.add(customer)
        db_session.flush()

        with patch("app.services.invoice_number.datetime") as mock_dt:
            mock_dt.now.return_value = now
            num1 = generate_sales_invoice_number(db_session, company_id)

        # Persist first invoice so the next call sees it
        inv = SalesInvoice(
            id=uuid.uuid4(),
            company_id=company_id,
            customer_id=customer.id,
            invoice_number=num1,
            invoice_date=now,
            subtotal=Decimal("0.00"),
            tax_amount=Decimal("0.00"),
            tax_rate=Decimal("0.15"),
            discount_amount=Decimal("0.00"),
            total_amount=Decimal("0.00"),
            paid_amount=Decimal("0.00"),
            remaining_amount=Decimal("0.00"),
            status=InvoiceStatus.DRAFT,
            payment_status=PaymentStatus.UNPAID,
        )
        db_session.add(inv)
        db_session.commit()

        with patch("app.services.invoice_number.datetime") as mock_dt:
            mock_dt.now.return_value = now
            num2 = generate_sales_invoice_number(db_session, company_id)

        assert num1 == "INV-2026-03-00001"
        assert num2 == "INV-2026-03-00002"

    def test_different_companies_independent(self, db_session) -> None:
        """Different companies must have independent sequences."""
        company_a = uuid.uuid4()
        company_b = uuid.uuid4()
        now = datetime(2026, 4, 1, tzinfo=timezone.utc)

        with patch("app.services.invoice_number.datetime") as mock_dt:
            mock_dt.now.return_value = now
            num_a = generate_sales_invoice_number(db_session, company_a)
            num_b = generate_sales_invoice_number(db_session, company_b)

        assert num_a == "INV-2026-04-00001"
        assert num_b == "INV-2026-04-00001"


class TestGeneratePurchaseInvoiceNumber:
    def test_prefix(self, db_session) -> None:
        company_id = uuid.uuid4()
        now = datetime(2026, 5, 1, tzinfo=timezone.utc)
        with patch("app.services.invoice_number.datetime") as mock_dt:
            mock_dt.now.return_value = now
            number = generate_purchase_invoice_number(db_session, company_id)
        assert number == "PUR-2026-05-00001"
