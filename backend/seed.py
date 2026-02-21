"""
Seed script: creates admin user, 5 products, 2 suppliers, 2 customers.

Usage:
    DATABASE_URL=postgresql://... python seed.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from app.database import SessionLocal, engine, Base
import app.models  # ensure all models are registered

from app.models.user import User
from app.models.product import Product
from app.models.supplier import Supplier
from app.models.customer import Customer
from app.models.stock import Stock
from app.auth.utils import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Admin user
        if not db.query(User).filter(User.email == "admin@jenan.biz").first():
            admin = User(
                email="admin@jenan.biz",
                password_hash=hash_password("admin123"),
                full_name="Admin User",
                is_active=True,
                is_admin=True,
            )
            db.add(admin)
            db.flush()
            print(f"Created admin user: {admin.email}")

        # Suppliers
        suppliers_data = [
            {"name": "Alpha Supplies Co.", "contact_name": "Ali Hassan", "phone": "+966500000001", "email": "ali@alphasupplies.com"},
            {"name": "Beta Trading Ltd.", "contact_name": "Sara Ahmed", "phone": "+966500000002", "email": "sara@betatrading.com"},
        ]
        for s_data in suppliers_data:
            if not db.query(Supplier).filter(Supplier.name == s_data["name"]).first():
                supplier = Supplier(**s_data)
                db.add(supplier)
                print(f"Created supplier: {s_data['name']}")

        # Customers
        customers_data = [
            {"name": "Riyadh Retail Group", "contact_name": "Mohammed Al-Otaibi", "phone": "+966500000010", "email": "m.otaibi@rrg.sa"},
            {"name": "Jeddah Distribution LLC", "contact_name": "Fatima Al-Zahrani", "phone": "+966500000011", "email": "f.zahrani@jdl.sa"},
        ]
        for c_data in customers_data:
            if not db.query(Customer).filter(Customer.name == c_data["name"]).first():
                customer = Customer(**c_data)
                db.add(customer)
                print(f"Created customer: {c_data['name']}")

        # Products
        products_data = [
            {"name": "Office Paper A4", "sku": "PAPER-A4-500", "purchase_price": 15.0, "sale_price": 22.0, "unit": "ream", "category": "Stationery", "min_stock": 10.0},
            {"name": "Ballpoint Pen Box", "sku": "PEN-BP-12", "purchase_price": 8.0, "sale_price": 14.0, "unit": "box", "category": "Stationery", "min_stock": 5.0},
            {"name": "Stapler Heavy Duty", "sku": "STAPLER-HD", "purchase_price": 25.0, "sale_price": 40.0, "unit": "unit", "category": "Office Equipment", "min_stock": 3.0},
            {"name": "Printer Toner Cartridge", "sku": "TONER-BLK-01", "purchase_price": 120.0, "sale_price": 180.0, "unit": "unit", "category": "Printer Supplies", "min_stock": 2.0},
            {"name": "Notebook A5 Ruled", "sku": "NB-A5-R", "purchase_price": 5.0, "sale_price": 9.0, "unit": "unit", "category": "Stationery", "min_stock": 20.0},
        ]
        for p_data in products_data:
            if not db.query(Product).filter(Product.sku == p_data["sku"]).first():
                product = Product(**p_data)
                db.add(product)
                db.flush()
                stock = Stock(product_id=product.id, current_quantity=0.0)
                db.add(stock)
                print(f"Created product: {p_data['name']}")

        db.commit()
        print("\nSeed completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
