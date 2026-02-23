"""
main.py - Application entry point.

This module wires together the core components and provides:
- A FastAPI application instance (``app``) that mounts the agents router.
- A ``startup()`` helper for CLI / testing.

Run the API server with:
    uvicorn app.main:app --reload
"""

import logging

from fastapi import FastAPI

from app.api.agents import router as agents_router
from app.core.config import settings
from app.core.database import check_db_connection, init_db

logger = logging.getLogger(__name__)


def startup() -> None:
    """
    Validate configuration, check database connectivity and create tables.

    Raises
    ------
    ValueError
        If any required setting is missing or invalid.
    RuntimeError
        If the database is unreachable at startup.
    """
    settings.validate()

    logger.info("Starting %s (debug=%s)", settings.APP_NAME, settings.DEBUG)

    if not check_db_connection():
        raise RuntimeError(
            f"Cannot connect to the database at {settings.DATABASE_URL!r}. "
            "Check DATABASE_URL and ensure the database server is running."
        )

    logger.info("Database connection verified.")
    init_db()
    logger.info("All tables created / verified.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
    )
    application.include_router(agents_router)
    return application


# ASGI app instance used by uvicorn / gunicorn
app = create_app()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    startup()
