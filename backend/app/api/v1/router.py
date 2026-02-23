"""
api/v1/router.py - Aggregate router for API v1.
"""

from fastapi import APIRouter

from app.api.v1.routers import (
    auth,
    customers,
    inventory,
    products,
    purchase_invoices,
    sales_invoices,
    suppliers,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(products.router)
api_router.include_router(inventory.router)
api_router.include_router(customers.router)
api_router.include_router(suppliers.router)
api_router.include_router(sales_invoices.router)
api_router.include_router(purchase_invoices.router)
