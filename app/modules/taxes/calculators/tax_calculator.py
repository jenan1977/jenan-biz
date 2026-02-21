"""Generic tax calculator."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Union


def apply_tax_rate(amount: Union[float, Decimal], rate: Union[float, Decimal]) -> dict:
    """Return tax breakdown for any tax rate."""
    base = Decimal(str(amount))
    tax = (base * Decimal(str(rate)) / 100).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {
        "base_amount": base,
        "tax_rate": Decimal(str(rate)),
        "tax_amount": tax,
        "total": base + tax,
    }
