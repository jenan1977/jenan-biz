"""
tests/test_totals.py - Unit tests for invoice total calculations.

These tests run without a database; they exercise pure Python logic only.
"""

from decimal import Decimal

import pytest

from app.services.totals import compute_invoice_totals, compute_line_total


class TestComputeLineTotal:
    def test_basic(self) -> None:
        assert compute_line_total(Decimal("2"), Decimal("10.00")) == Decimal("20.00")

    def test_fractional_rounds_half_up(self) -> None:
        # 3 × 1.005 = 3.015 → rounds to 3.02
        assert compute_line_total(Decimal("3"), Decimal("1.005")) == Decimal("3.02")

    def test_zero_price(self) -> None:
        assert compute_line_total(Decimal("5"), Decimal("0.00")) == Decimal("0.00")


class TestComputeInvoiceTotals:
    def test_standard_15_percent(self) -> None:
        line_totals = [Decimal("100.00"), Decimal("50.00")]
        result = compute_invoice_totals(
            line_totals=line_totals,
            tax_rate=Decimal("0.15"),
            discount_amount=Decimal("0.00"),
        )
        assert result["subtotal"] == Decimal("150.00")
        assert result["tax_amount"] == Decimal("22.50")
        assert result["total_amount"] == Decimal("172.50")

    def test_with_discount(self) -> None:
        result = compute_invoice_totals(
            line_totals=[Decimal("200.00")],
            tax_rate=Decimal("0.10"),
            discount_amount=Decimal("20.00"),
        )
        # subtotal=200, tax=20, total=200+20-20=200
        assert result["subtotal"] == Decimal("200.00")
        assert result["tax_amount"] == Decimal("20.00")
        assert result["total_amount"] == Decimal("200.00")

    def test_zero_tax_rate(self) -> None:
        result = compute_invoice_totals(
            line_totals=[Decimal("100.00")],
            tax_rate=Decimal("0.00"),
            discount_amount=Decimal("0.00"),
        )
        assert result["tax_amount"] == Decimal("0.00")
        assert result["total_amount"] == Decimal("100.00")

    def test_negative_total_raises(self) -> None:
        with pytest.raises(ValueError, match="negative"):
            compute_invoice_totals(
                line_totals=[Decimal("10.00")],
                tax_rate=Decimal("0.00"),
                discount_amount=Decimal("100.00"),
            )

    def test_empty_lines(self) -> None:
        result = compute_invoice_totals(
            line_totals=[],
            tax_rate=Decimal("0.15"),
            discount_amount=Decimal("0.00"),
        )
        assert result["subtotal"] == Decimal("0.00")
        assert result["total_amount"] == Decimal("0.00")
