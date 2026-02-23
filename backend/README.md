# Jenan-Biz Backend

Python backend for the Jenan-Biz business management platform.

## Tech Stack

| Component | Library |
|-----------|---------|
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL (via psycopg2) |
| Migrations | Alembic |
| Settings | python-dotenv + Pydantic |

## Project Structure

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py       # Settings from environment variables
│   │   ├── database.py     # Engine, SessionLocal, Base, get_db()
│   │   └── constants.py    # Enums: UserRole, InvoiceStatus, …
│   │
│   ├── models/
│   │   ├── base.py               # Shared id / timestamps / is_active
│   │   ├── company.py
│   │   ├── user.py
│   │   ├── customer.py
│   │   ├── supplier.py
│   │   ├── product.py
│   │   ├── sales_invoice.py
│   │   ├── sales_line_item.py
│   │   ├── purchase_invoice.py
│   │   ├── purchase_line_item.py
│   │   └── inventory.py
│   │
│   └── main.py             # startup() helper
│
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set DATABASE_URL to your PostgreSQL connection string
```

### 4. Create the database

```sql
CREATE DATABASE jenan_biz;
```

### 5. Run database initialisation

```bash
python -m app.main
```

This creates all tables if they do not already exist.

### 6. (Optional) Run Alembic migrations

```bash
alembic init alembic
# Configure alembic/env.py to use settings.DATABASE_URL
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/jenan_biz` | Full SQLAlchemy DB URL |
| `DATABASE_ECHO` | `False` | Log all SQL statements |
| `DATABASE_POOL_SIZE` | `5` | Connection pool size |
| `DATABASE_MAX_OVERFLOW` | `10` | Extra connections allowed |
| `DEBUG` | `False` | Development mode flag |
| `TIMEZONE` | `UTC` | Application timezone |

## Data Models

```
Company  ──< User
         ──< Customer  ──< SalesInvoice   ──< SalesLineItem   >── Product
         ──< Supplier  ──< PurchaseInvoice──< PurchaseLineItem >── Product
         ──< Product   ──  Inventory
```

All primary keys are UUIDs. All timestamps are stored in UTC.
Financial amounts use `Numeric(12, 2)` for precision.
