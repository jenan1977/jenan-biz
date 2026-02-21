"""Field and business-rule validators."""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Return True if *email* matches a basic email pattern."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Return True for phone numbers containing 7-15 digits (with optional +/spaces)."""
    digits = re.sub(r"[\s\-\(\)\+]", "", phone)
    return digits.isdigit() and 7 <= len(digits) <= 15


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Return (is_valid, message).
    A strong password must have ≥8 chars, a digit, a letter, and a special char.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, "OK"


def validate_tax_number(tax_number: str) -> bool:
    """Basic Saudi VAT number validation (15 digits starting with 3)."""
    cleaned = re.sub(r"\s", "", tax_number)
    return bool(re.match(r"^3\d{14}$", cleaned))


def validate_positive_amount(amount: float) -> bool:
    """Return True if *amount* is strictly positive."""
    return amount > 0
