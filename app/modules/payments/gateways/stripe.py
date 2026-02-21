"""Stripe payment gateway integration (stub)."""

from decimal import Decimal
from typing import Dict, Any


def create_payment_intent(amount: Decimal, currency: str = "sar") -> Dict[str, Any]:
    """Create a Stripe PaymentIntent. Requires stripe package and API key."""
    try:
        import stripe
        from app.core.config import settings
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency=currency.lower(),
        )
        return {"client_secret": intent.client_secret, "id": intent.id}
    except ImportError:
        return {"error": "stripe package not installed"}
