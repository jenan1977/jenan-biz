"""
bulk_inventory.py - Handler: bulk inventory update with row locks and validation.

Payload schema
--------------
updates : list of objects
    Each object must contain:
    - inventory_id   : str  UUID of the Inventory row
    - quantity_delta : str  Decimal string (positive = add stock, negative = remove)
    - reason         : str  (optional) free-text audit note

The handler acquires a row-level lock on each Inventory row (SELECT … FOR UPDATE)
before applying the delta so that concurrent updates remain consistent.

Validation rules
----------------
- quantity_on_hand + delta >= 0   (stock cannot go negative)
- quantity_available after update = quantity_on_hand_new - quantity_reserved

Returns
-------
{
    "updated": [{"inventory_id": ..., "quantity_on_hand": ...}, ...],
    "skipped": [{"inventory_id": ..., "reason": ...}, ...]
}
"""

from __future__ import annotations

import uuid
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List

from sqlalchemy.orm import Session

from app.models.inventory import Inventory


def run(db: Session, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process a bulk inventory update."""
    updates: List[Dict[str, Any]] = payload.get("updates", [])

    if not isinstance(updates, list):
        raise ValueError("payload.updates must be a list")

    updated: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []

    for item in updates:
        inv_id_str = item.get("inventory_id")
        delta_str = item.get("quantity_delta")
        reason = item.get("reason", "")

        # ── Parse and validate inputs ──────────────────────────────────
        if not inv_id_str:
            skipped.append({"inventory_id": None, "reason": "missing inventory_id"})
            continue

        try:
            inv_id = uuid.UUID(str(inv_id_str))
        except (ValueError, AttributeError):
            skipped.append({"inventory_id": inv_id_str, "reason": "invalid inventory_id UUID"})
            continue

        if delta_str is None:
            skipped.append({"inventory_id": inv_id_str, "reason": "missing quantity_delta"})
            continue

        try:
            delta = Decimal(str(delta_str))
        except InvalidOperation:
            skipped.append({"inventory_id": inv_id_str, "reason": "invalid quantity_delta"})
            continue

        # ── Acquire row lock ───────────────────────────────────────────
        inv: Inventory | None = (
            db.query(Inventory)
            .filter(Inventory.id == inv_id)
            .with_for_update()
            .first()
        )

        if inv is None:
            skipped.append({"inventory_id": inv_id_str, "reason": "inventory row not found"})
            continue

        # ── Apply validation ───────────────────────────────────────────
        new_on_hand = inv.quantity_on_hand + delta
        if new_on_hand < Decimal("0"):
            skipped.append(
                {
                    "inventory_id": inv_id_str,
                    "reason": (
                        f"quantity_on_hand would become negative "
                        f"({inv.quantity_on_hand} + {delta} = {new_on_hand})"
                    ),
                }
            )
            continue

        new_available = new_on_hand - inv.quantity_reserved
        if new_available < Decimal("0"):
            skipped.append(
                {
                    "inventory_id": inv_id_str,
                    "reason": (
                        f"quantity_available would become negative "
                        f"({new_on_hand} - {inv.quantity_reserved} = {new_available})"
                    ),
                }
            )
            continue

        # ── Apply update ───────────────────────────────────────────────
        inv.quantity_on_hand = new_on_hand
        inv.quantity_available = new_available
        db.flush()

        updated.append(
            {
                "inventory_id": inv_id_str,
                "quantity_on_hand": str(inv.quantity_on_hand),
                "quantity_available": str(inv.quantity_available),
                "reason": reason,
            }
        )

    return {"updated": updated, "skipped": skipped}
