"""Product-specific validation helpers."""

from decimal import Decimal


def validate_price(price: Decimal) -> bool:
    """Return True if price is non-negative."""
    return price >= Decimal("0.00")


def validate_selling_vs_cost(selling_price: Decimal, cost_price: Decimal) -> bool:
    """Return True if selling price is greater than or equal to cost price."""
    return selling_price >= cost_price
