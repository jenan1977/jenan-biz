"""Export report to Excel."""

from typing import Dict, Any, List


def export_to_excel(rows: List[Dict[str, Any]], filename: str = "report.xlsx") -> bytes:
    """Export data rows to Excel bytes (requires openpyxl)."""
    try:
        import openpyxl
        from io import BytesIO

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Report"

        if rows:
            headers = list(rows[0].keys())
            ws.append(headers)
            for row in rows:
                ws.append(list(row.values()))

        buffer = BytesIO()
        wb.save(buffer)
        return buffer.getvalue()
    except ImportError:
        return b"Excel export requires openpyxl package."
