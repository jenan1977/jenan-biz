"""SMS notification channel (stub)."""

from app.core.logger import get_logger

logger = get_logger(__name__)


def send_sms(to: str, message: str) -> bool:
    """Send an SMS via a third-party provider (stub implementation)."""
    logger.info("SMS to %s: %s", to, message)
    # Integrate with Twilio, Unifonic, etc. here
    return True
