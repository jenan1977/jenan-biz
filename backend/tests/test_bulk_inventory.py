"""
test_bulk_inventory.py - Unit tests for the bulk inventory update handler.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
# Ensure all models are registered
import app.models  # noqa: F401
from app.worker.handlers.bulk_inventory import run as bulk_update


# ---------------------------------------------------------------------------
# Fixtures – function-scoped for full isolation
# ---------------------------------------------------------------------------


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=eng)
    yield eng
    Base.metadata.drop_all(bind=eng)
    eng.dispose()


@pytest.fixture
def db(engine):
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def sample_inventory(db):
    """Insert minimal supporting rows (Company, Product, Inventory) for tests."""
    from app.models.company import Company
    from app.models.product import Product
    from app.models.inventory import Inventory

    company = Company(name="Test Co", tax_number="123456")
    db.add(company)
    db.flush()

    product = Product(
        company_id=company.id,
        name="Widget",
        unit_price=Decimal("10.00"),
    )
    db.add(product)
    db.flush()

    inv = Inventory(
        company_id=company.id,
        product_id=product.id,
        quantity_on_hand=Decimal("100.00"),
        quantity_reserved=Decimal("10.00"),
        quantity_available=Decimal("90.00"),
        reorder_level=Decimal("20.00"),
    )
    db.add(inv)
    db.flush()
    return inv


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestBulkInventory:
    def test_add_stock(self, db, sample_inventory):
        inv_id = str(sample_inventory.id)
        result = bulk_update(
            db,
            {"updates": [{"inventory_id": inv_id, "quantity_delta": "25.00"}]},
        )

        assert len(result["updated"]) == 1
        assert len(result["skipped"]) == 0
        updated = result["updated"][0]
        assert Decimal(updated["quantity_on_hand"]) == Decimal("125.00")
        assert Decimal(updated["quantity_available"]) == Decimal("115.00")

    def test_remove_stock(self, db, sample_inventory):
        inv_id = str(sample_inventory.id)
        # Remove 20 from initial 100
        result = bulk_update(
            db,
            {"updates": [{"inventory_id": inv_id, "quantity_delta": "-20.00"}]},
        )

        assert len(result["updated"]) == 1
        updated = result["updated"][0]
        assert Decimal(updated["quantity_on_hand"]) == Decimal("80.00")
        assert Decimal(updated["quantity_available"]) == Decimal("70.00")

    def test_reject_negative_on_hand(self, db, sample_inventory):
        inv_id = str(sample_inventory.id)
        result = bulk_update(
            db,
            {"updates": [{"inventory_id": inv_id, "quantity_delta": "-9999.00"}]},
        )
        assert len(result["skipped"]) == 1
        assert "negative" in result["skipped"][0]["reason"].lower()

    def test_reject_invalid_uuid(self, db):
        result = bulk_update(
            db,
            {"updates": [{"inventory_id": "not-a-uuid", "quantity_delta": "5"}]},
        )
        assert len(result["skipped"]) == 1
        assert "invalid" in result["skipped"][0]["reason"].lower()

    def test_reject_missing_inventory_id(self, db):
        result = bulk_update(
            db,
            {"updates": [{"quantity_delta": "5"}]},
        )
        assert len(result["skipped"]) == 1
        assert "missing" in result["skipped"][0]["reason"].lower()

    def test_reject_missing_delta(self, db, sample_inventory):
        inv_id = str(sample_inventory.id)
        result = bulk_update(
            db,
            {"updates": [{"inventory_id": inv_id}]},
        )
        assert len(result["skipped"]) == 1
        assert "missing" in result["skipped"][0]["reason"].lower()

    def test_nonexistent_inventory_row(self, db):
        result = bulk_update(
            db,
            {"updates": [{"inventory_id": str(uuid.uuid4()), "quantity_delta": "1"}]},
        )
        assert len(result["skipped"]) == 1
        assert "not found" in result["skipped"][0]["reason"].lower()

    def test_mixed_valid_and_invalid(self, db, sample_inventory):
        inv_id = str(sample_inventory.id)
        result = bulk_update(
            db,
            {
                "updates": [
                    {"inventory_id": inv_id, "quantity_delta": "5.00"},
                    {"inventory_id": str(uuid.uuid4()), "quantity_delta": "1.00"},
                ]
            },
        )
        assert len(result["updated"]) == 1
        assert len(result["skipped"]) == 1

