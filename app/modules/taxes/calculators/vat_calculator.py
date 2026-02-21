"""VAT calculation utilities."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Union


def calculate_vat_exclusive(amount: Union[float, Decimal], rate: Union[float, Decimal] = 15.0) -> Decimal:
    """Calculate VAT on a pre-tax (exclusive) amount."""
    return (Decimal(str(amount)) * Decimal(str(rate)) / 100).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def calculate_vat_inclusive(amount: Union[float, Decimal], rate: Union[float, Decimal] = 15.0) -> Decimal:
    """Extract VAT from a VAT-inclusive amount."""
    factor = Decimal(str(rate)) / 100
    return (Decimal(str(amount)) * factor / (1 + factor)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def get_pre_tax_amount(inclusive_amount: Union[float, Decimal], rate: Union[float, Decimal] = 15.0) -> Decimal:
    """Get the pre-tax amount from a VAT-inclusive total."""
    factor = 1 + Decimal(str(rate)) / 100
    return (Decimal(str(inclusive_amount)) / factor).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
