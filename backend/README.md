# Jenan-Biz Backend

Python backend for the Jenan-Biz business management platform.

## Tech Stack

| Component | Library |
|-----------|---------|
| API Framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL (via psycopg2) |
| Migrations | Alembic |
| Settings | python-dotenv + Pydantic |
| Auth | python-jose (HS256 JWT) |
| PDF | reportlab |

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── agents.py       # Agents router (enqueue jobs, poll results)
│   │   └── deps.py         # JWT auth dependencies
│   │
│   ├── core/
│   │   ├── config.py       # Settings from environment variables
│   │   ├── database.py     # Engine, SessionLocal, Base, get_db()
│   │   └── constants.py    # Enums: UserRole, InvoiceStatus, JobType, …
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
│   │   ├── inventory.py
│   │   └── job.py                # Background job queue model
│   │
│   ├── worker/
│   │   ├── __init__.py
│   │   ├── worker.py             # Worker loop (SKIP LOCKED polling)
│   │   └── handlers/
│   │       ├── __init__.py
│   │       ├── financial_analysis.py
│   │       ├── pdf_report.py
│   │       └── bulk_inventory_update.py
│   │
│   └── main.py             # FastAPI app + startup() helper
│
├── tests/
│   ├── __init__.py
│   └── test_jobs.py        # Job model + worker unit tests
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

### 6. Run the API server

```bash
uvicorn app.main:app --reload
```

### 7. Run the background worker

```bash
python -m app.worker.worker
```

The worker polls the `jobs` table every 2 seconds (configurable via `WORKER_POLL_INTERVAL`).
It uses `SELECT ... FOR UPDATE SKIP LOCKED` for exactly-once job dispatch across multiple worker processes.

### 8. Run tests

```bash
cd backend
PYTHONPATH=. python -m pytest tests/ -v
```

### 9. (Optional) Run Alembic migrations

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
| `SECRET_KEY` | `change-me-in-production` | HS256 JWT signing secret |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token expiry in minutes |
| `WORKER_POLL_INTERVAL` | `2` | Worker poll interval in seconds |

## Data Models

```
Company  ──< User
         ──< Customer  ──< SalesInvoice   ──< SalesLineItem   >── Product
         ──< Supplier  ──< PurchaseInvoice──< PurchaseLineItem >── Product
         ──< Product   ──  Inventory
```

All primary keys are UUIDs. All timestamps are stored in UTC.
Financial amounts use `Numeric(12, 2)` for precision.
