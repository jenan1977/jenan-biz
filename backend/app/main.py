"""
main.py - Application entry point.

This module creates the FastAPI application, registers all routers, and
provides a ``startup()`` helper that validates configuration and initialises
the database.
"""

import logging

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import check_db_connection, init_db

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Factory that builds and returns the configured FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG,
        version="1.0.0",
    )

    app.include_router(api_router)

    @app.on_event("startup")
    def on_startup() -> None:
        startup()

    return app


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


# ASGI app used by uvicorn / gunicorn
app = create_app()


if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(level=logging.INFO)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
