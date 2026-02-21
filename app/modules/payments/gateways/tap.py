"""Tap Payments gateway integration (stub - Saudi Arabia)."""

from decimal import Decimal
from typing import Dict, Any


def create_tap_charge(amount: Decimal, currency: str = "SAR", source: str = "card") -> Dict[str, Any]:
    """Create a Tap payment charge. Requires tap-python SDK."""
    return {"status": "stub", "amount": str(amount), "currency": currency}
