from datetime import datetime, timezone


def generate_invoice_number(prefix: str = "INV") -> str:
    now = datetime.now(timezone.utc)
    return f"{prefix}-{now.strftime('%Y%m%d%H%M%S')}"


def format_currency(amount: float, currency: str = "SAR") -> str:
    return f"{currency} {amount:,.2f}"
