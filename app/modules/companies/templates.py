"""Business setup templates for different business types."""

from typing import List, Dict, Any

TEMPLATES: Dict[str, List[Dict[str, Any]]] = {
    "retail": [
        {"name": "Electronics", "type": "category"},
        {"name": "Clothing", "type": "category"},
        {"name": "Food & Beverages", "type": "category"},
    ],
    "restaurant": [
        {"name": "Appetizers", "type": "category"},
        {"name": "Main Course", "type": "category"},
        {"name": "Desserts", "type": "category"},
        {"name": "Beverages", "type": "category"},
    ],
    "pharmacy": [
        {"name": "Medicines", "type": "category"},
        {"name": "Vitamins & Supplements", "type": "category"},
        {"name": "Personal Care", "type": "category"},
    ],
    "wholesale": [
        {"name": "Raw Materials", "type": "category"},
        {"name": "Finished Goods", "type": "category"},
        {"name": "Packaging", "type": "category"},
    ],
}


def get_template(business_type: str) -> List[Dict[str, Any]]:
    """Return product category templates for the given business type."""
    return TEMPLATES.get(business_type, [])
