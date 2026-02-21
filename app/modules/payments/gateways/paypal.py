"""PayPal payment gateway integration (stub)."""

from decimal import Decimal
from typing import Dict, Any


def create_paypal_order(amount: Decimal, currency: str = "USD") -> Dict[str, Any]:
    """Create a PayPal order. Requires paypalrestsdk package."""
    return {"status": "stub", "amount": str(amount), "currency": currency}
