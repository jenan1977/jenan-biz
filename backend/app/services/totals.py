"""
services/totals.py - Server-side financial total calculations.

All arithmetic uses Python's Decimal type for exact precision.
"""

from decimal import ROUND_HALF_UP, Decimal
from typing import Iterable


TWO_PLACES = Decimal("0.01")


def compute_line_total(quantity: Decimal, unit_price: Decimal) -> Decimal:
    """Return quantity * unit_price rounded to 2 decimal places."""
    return (quantity * unit_price).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def compute_invoice_totals(
    line_totals: Iterable[Decimal],
    tax_rate: Decimal,
    discount_amount: Decimal,
) -> dict:
    """
    Compute invoice financial totals from line totals.

    Returns a dict with keys: subtotal, tax_amount, total_amount.

    Raises
    ------
    ValueError
        When total_amount would be negative.
    """
    subtotal = sum(line_totals, Decimal("0.00")).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    tax_amount = (subtotal * tax_rate).quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
    total_amount = subtotal + tax_amount - discount_amount

    if total_amount < Decimal("0.00"):
        raise ValueError(
            f"total_amount ({total_amount}) cannot be negative. "
            "Reduce discount_amount or add more line items."
        )

    return {
        "subtotal": subtotal,
        "tax_amount": tax_amount,
        "total_amount": total_amount.quantize(TWO_PLACES, rounding=ROUND_HALF_UP),
    }
