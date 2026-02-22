"""
database.py - SQLAlchemy engine, session factory, and helper utilities.

The engine and session factory are created lazily (on first use) so that
model modules can be imported without an active database connection or the
psycopg2 driver installed.  Call ``get_engine()`` / ``get_session_factory()``
to obtain the configured instances.
"""

from typing import Generator, Optional

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

# ------------------------------------------------------------------
# Declarative base  (must be importable without a live DB)
# ------------------------------------------------------------------


class Base(DeclarativeBase):
    """Base class that all ORM models must inherit from."""

    pass


# ------------------------------------------------------------------
# Lazy singletons
# ------------------------------------------------------------------
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None  # type: ignore[type-arg]


def get_engine() -> Engine:
    """Return (and lazily create) the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,  # verify connection health before checkout
        )
    return _engine


def get_session_factory() -> sessionmaker:  # type: ignore[type-arg]
    """Return (and lazily create) the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _SessionLocal


# ------------------------------------------------------------------
# Convenience aliases used by application code
# ------------------------------------------------------------------
def SessionLocal() -> Session:
    """Create and return a new database session."""
    return get_session_factory()()


# ------------------------------------------------------------------
# Dependency helper (for future FastAPI integration)
# ------------------------------------------------------------------
def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session and ensure it is closed afterwards.

    Usage (FastAPI)::

        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            ...
    """
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()


# ------------------------------------------------------------------
# Initialisation helper
# ------------------------------------------------------------------
def init_db() -> None:
    """
    Create all tables defined by ORM models.

    Import all model modules before calling this function so that
    SQLAlchemy's metadata is fully populated.
    """
    # Ensure all models are imported before create_all
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=get_engine())


def check_db_connection() -> bool:
    """Return True when the database is reachable, False otherwise."""
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
