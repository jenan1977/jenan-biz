"""General-purpose helper utilities."""

import uuid
import re
from datetime import date, datetime
from typing import Any, Dict, Optional


def generate_invoice_number(prefix: str = "INV", sequence: int = 1) -> str:
    """Generate a formatted invoice number, e.g. INV-2024-000001."""
    year = datetime.now().year
    return f"{prefix}-{year}-{sequence:06d}"


def generate_purchase_number(sequence: int = 1) -> str:
    """Generate a purchase order number."""
    return generate_invoice_number("PO", sequence)


def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from a file name."""
    return re.sub(r"[^\w.\-]", "_", filename)


def mask_sensitive(value: str, visible: int = 4) -> str:
    """Mask all but the last *visible* characters of a string."""
    if len(value) <= visible:
        return "*" * len(value)
    return "*" * (len(value) - visible) + value[-visible:]


def flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """Flatten a nested dictionary."""
    items: list = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def is_valid_uuid(value: str) -> bool:
    """Check whether a string is a valid UUID."""
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False
