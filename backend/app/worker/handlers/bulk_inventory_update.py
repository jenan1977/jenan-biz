"""
bulk_inventory_update.py - Handler for BULK_INVENTORY_UPDATE jobs.

Payload schema:
    {
        "company_id": "<uuid>",
        "adjustments": [
            {
                "product_id":    "<uuid>",
                "delta_on_hand": <float>,   # positive = stock in, negative = stock out
                "delta_reserved": <float>   # optional, defaults to 0
            },
            ...
        ]
    }

Result schema:
    {
        "updated": <int>,   # number of inventory rows updated
        "skipped": [...]    # list of product_ids that were skipped with reason
    }
"""

import uuid
from decimal import Decimal
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory import Inventory
from app.models.job import Job


def handle_bulk_inventory_update(db: Session, job: Job) -> Dict[str, Any]:
    """Execute a BULK_INVENTORY_UPDATE job inside a single transaction."""
    payload = job.payload
    company_id = uuid.UUID(payload["company_id"])
    adjustments: List[Dict[str, Any]] = payload.get("adjustments", [])

    if not adjustments:
        raise ValueError("Payload must contain at least one adjustment.")

    updated = 0
    skipped: List[Dict[str, Any]] = []

    for adj in adjustments:
        product_id = uuid.UUID(adj["product_id"])
        delta_on_hand = Decimal(str(adj.get("delta_on_hand", 0)))
        delta_reserved = Decimal(str(adj.get("delta_reserved", 0)))

        # Row-lock the inventory record for this product
        row = db.execute(
            select(Inventory)
            .where(Inventory.company_id == company_id)
            .where(Inventory.product_id == product_id)
            .with_for_update()
        ).scalars().first()

        if row is None:
            skipped.append(
                {"product_id": str(product_id), "reason": "inventory record not found"}
            )
            continue

        new_on_hand = row.quantity_on_hand + delta_on_hand
        new_reserved = row.quantity_reserved + delta_reserved
        new_available = new_on_hand - new_reserved

        if new_on_hand < Decimal("0"):
            skipped.append(
                {
                    "product_id": str(product_id),
                    "reason": f"on_hand would become negative ({new_on_hand})",
                }
            )
            continue

        if new_reserved < Decimal("0"):
            skipped.append(
                {
                    "product_id": str(product_id),
                    "reason": f"reserved would become negative ({new_reserved})",
                }
            )
            continue

        row.quantity_on_hand = new_on_hand
        row.quantity_reserved = new_reserved
        row.quantity_available = new_available
        db.flush()
        updated += 1

    return {"updated": updated, "skipped": skipped}
