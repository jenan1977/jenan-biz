import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import (
    auth_routes,
    products_routes,
    suppliers_routes,
    customers_routes,
    purchases_routes,
    invoices_routes,
    inventory_routes,
    dashboard_routes,
)

# Create upload directory
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Jenan Business API", version="1.0.0")

# CORS — restrict allow_origins to specific domains in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Routers
app.include_router(auth_routes.router, prefix="/api/auth", tags=["Auth"])
app.include_router(products_routes.router, prefix="/api/products", tags=["Products"])
app.include_router(suppliers_routes.router, prefix="/api/suppliers", tags=["Suppliers"])
app.include_router(customers_routes.router, prefix="/api/customers", tags=["Customers"])
app.include_router(purchases_routes.router, prefix="/api/purchases", tags=["Purchases"])
app.include_router(invoices_routes.router, prefix="/api/invoices", tags=["Invoices"])
app.include_router(inventory_routes.router, prefix="/api/inventory", tags=["Inventory"])
app.include_router(dashboard_routes.router, prefix="/api/dashboard", tags=["Dashboard"])


@app.get("/")
def root():
    return {"message": "Jenan Business API is running"}
