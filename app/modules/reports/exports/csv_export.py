"""Export report to CSV."""

import csv
import io
from typing import Dict, Any, List


def export_to_csv(rows: List[Dict[str, Any]]) -> str:
    """Convert a list of dicts to CSV string."""
    if not rows:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
