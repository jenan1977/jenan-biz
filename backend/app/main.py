"""
main.py - Application entry point.

This module wires together the core components and provides a simple
``startup()`` helper that can be called from a future ASGI framework
(e.g. FastAPI lifespan) or from CLI tooling.

No HTTP routes or framework decorators are defined here; those will be
added in a later step.
"""

import logging

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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    startup()
