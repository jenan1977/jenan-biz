"""Email notification channel."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


def send_email(to: List[str], subject: str, body: str, html: bool = False) -> bool:
    """Send an email via SMTP. Returns True on success."""
    if not settings.SMTP_USER:
        logger.warning("SMTP not configured; skipping email send.")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.EMAILS_FROM_EMAIL
        msg["To"] = ", ".join(to)
        part = MIMEText(body, "html" if html else "plain", "utf-8")
        msg.attach(part)
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, to, msg.as_string())
        return True
    except Exception as exc:
        logger.error("Failed to send email: %s", exc)
        return False
