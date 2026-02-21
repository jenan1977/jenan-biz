"""Formatting utilities."""

from decimal import Decimal, ROUND_HALF_UP
from typing import Union


def format_currency(amount: Union[float, Decimal], currency: str = "SAR", decimals: int = 2) -> str:
    """Format a numeric amount with currency symbol."""
    symbols = {"SAR": "﷼", "USD": "$", "EUR": "€", "AED": "د.إ", "KWD": "د.ك"}
    symbol = symbols.get(currency, currency)
    rounded = Decimal(str(amount)).quantize(Decimal(f"0.{'0'*decimals}"), rounding=ROUND_HALF_UP)
    return f"{symbol} {rounded:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format a float as a percentage string."""
    return f"{value:.{decimals}f}%"


def format_phone(phone: str) -> str:
    """Return a normalized phone string (digits + leading +)."""
    import re
    digits = re.sub(r"[^\d+]", "", phone)
    return digits


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate a string and append suffix if it exceeds *max_length*."""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def arabic_numeral(n: int) -> str:
    """Convert an integer to Eastern Arabic numerals."""
    eastern = "٠١٢٣٤٥٦٧٨٩"
    return "".join(eastern[int(d)] for d in str(n))
