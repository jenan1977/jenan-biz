import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import engine, Base
from .routers import auth, products, suppliers, customers, purchases, sales, inventory, dashboard

# Import models so they are registered with Base
from .models import user, product, supplier, customer, purchase, sale, stock  # noqa: F401

app = FastAPI(title="Jenan Business Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)


app.include_router(auth.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(suppliers.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(purchases.router, prefix="/api/v1")
app.include_router(sales.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/")
def root():
    return {"message": "Jenan Business Management API", "docs": "/docs"}
