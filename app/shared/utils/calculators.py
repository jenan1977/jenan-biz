"""Business calculation utilities."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Union


Number = Union[float, Decimal]


def _d(value: Number) -> Decimal:
    return Decimal(str(value))


def calculate_vat(amount: Number, vat_rate: Number = 15.0) -> Decimal:
    """Return the VAT amount for the given *amount* and *vat_rate* (%)."""
    return (_d(amount) * _d(vat_rate) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_total_with_vat(amount: Number, vat_rate: Number = 15.0) -> Decimal:
    """Return the amount inclusive of VAT."""
    return (_d(amount) + calculate_vat(amount, vat_rate)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def calculate_discount(amount: Number, discount_percent: Number) -> Decimal:
    """Return the discount value for a percentage-based discount."""
    return (_d(amount) * _d(discount_percent) / 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def calculate_profit(selling_price: Number, cost_price: Number) -> Decimal:
    """Return the gross profit."""
    return (_d(selling_price) - _d(cost_price)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_profit_margin(selling_price: Number, cost_price: Number) -> Decimal:
    """Return gross profit margin as a percentage."""
    if _d(selling_price) == 0:
        return Decimal("0.00")
    profit = calculate_profit(selling_price, cost_price)
    return (profit / _d(selling_price) * 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_line_total(
    unit_price: Number,
    quantity: Number,
    discount_percent: Number = 0,
    vat_rate: Number = 15.0,
    include_vat: bool = True,
) -> dict:
    """
    Calculate full line totals for an invoice item.

    Returns a dict with: subtotal, discount_amount, taxable_amount, vat_amount, total.
    """
    subtotal = (_d(unit_price) * _d(quantity)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    discount_amount = calculate_discount(subtotal, discount_percent)
    taxable_amount = (subtotal - discount_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    vat_amount = calculate_vat(taxable_amount, vat_rate) if include_vat else Decimal("0.00")
    total = (taxable_amount + vat_amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "taxable_amount": taxable_amount,
        "vat_amount": vat_amount,
        "total": total,
    }
