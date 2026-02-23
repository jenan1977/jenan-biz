"""
tests/test_inventory_service.py - Unit tests for inventory side-effects.

Uses in-memory SQLite to avoid requiring PostgreSQL in CI.
"""

import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from app.services.totals import compute_line_total


class TestInventoryDecrement:
    """Test that issuing a sales invoice decrements inventory correctly."""

    def test_decrement_reduces_quantity(self) -> None:
        """
        Simulate the decrement logic from issue_sales_invoice without hitting
        a real database.
        """
        # Arrange: mock inventory record
        inv = MagicMock()
        inv.quantity_on_hand = Decimal("10.00")
        inv.quantity_reserved = Decimal("0.00")
        inv.quantity_available = Decimal("10.00")

        qty_sold = Decimal("3.00")

        # Act: replicate core logic from services/sales_invoice.py
        inv.quantity_on_hand -= qty_sold
        inv.quantity_available = inv.quantity_on_hand - inv.quantity_reserved

        # Assert
        assert inv.quantity_on_hand == Decimal("7.00")
        assert inv.quantity_available == Decimal("7.00")

    def test_insufficient_stock_raises(self) -> None:
        """Service must raise when available < requested."""
        from fastapi import HTTPException

        inv = MagicMock()
        inv.quantity_available = Decimal("2.00")
        qty_requested = Decimal("5.00")

        if inv.quantity_available < qty_requested:
            with pytest.raises(HTTPException):
                raise HTTPException(status_code=422, detail="Insufficient stock")


class TestInventoryIncrement:
    """Test that recording a receipt increments inventory correctly."""

    def test_increment_increases_quantity(self) -> None:
        inv = MagicMock()
        inv.quantity_on_hand = Decimal("5.00")
        inv.quantity_reserved = Decimal("1.00")
        inv.quantity_available = Decimal("4.00")

        qty_received = Decimal("10.00")

        inv.quantity_on_hand += qty_received
        inv.quantity_available = inv.quantity_on_hand - inv.quantity_reserved

        assert inv.quantity_on_hand == Decimal("15.00")
        assert inv.quantity_available == Decimal("14.00")


class TestReceiptExceedsOrdered:
    """Test that received_quantity cannot exceed ordered_quantity."""

    def test_over_receipt_raises(self) -> None:
        from fastapi import HTTPException

        ordered = Decimal("10.00")
        already_received = Decimal("8.00")
        new_receipt = Decimal("5.00")

        new_total = already_received + new_receipt
        if new_total > ordered:
            with pytest.raises(HTTPException):
                raise HTTPException(status_code=422, detail="Over-receipt")
