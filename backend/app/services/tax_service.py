from typing import Dict


TAX_RATE = 0.15


def calculate_tax(amount: float, rate: float = TAX_RATE) -> Dict[str, float]:
    tax_amount = round(amount * rate, 2)
    grand_total = round(amount + tax_amount, 2)
    return {
        "subtotal": round(amount, 2),
        "tax_amount": tax_amount,
        "grand_total": grand_total,
    }
