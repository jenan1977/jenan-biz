"""Bulk purchase import from CSV/Excel."""

import csv
import io
from typing import List, Dict, Any


def parse_purchase_csv(content: bytes) -> List[Dict[str, Any]]:
    """Parse CSV content into a list of purchase item dicts."""
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    return [row for row in reader]
