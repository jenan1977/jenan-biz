"""Export report to PDF."""

from typing import Dict, Any


def export_to_pdf(report_data: Dict[str, Any], title: str = "Report") -> bytes:
    """Export report data to PDF bytes (requires reportlab)."""
    try:
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = [Paragraph(title, styles['Title'])]

        for key, value in report_data.items():
            elements.append(Paragraph(f"{key}: {value}", styles['Normal']))
            elements.append(Spacer(1, 12))

        doc.build(elements)
        return buffer.getvalue()
    except ImportError:
        return b"PDF export requires reportlab package."
