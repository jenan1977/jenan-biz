"""Application logging configuration."""

import logging
import sys
from typing import Any

from app.core.config import settings


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    level = logging.DEBUG if settings.DEBUG else logging.INFO
    logger.setLevel(level)
    return logger


def log_request(logger: logging.Logger, method: str, path: str, status: int, duration: float) -> None:
    """Log an HTTP request."""
    logger.info(
        "%(method)s %(path)s -> %(status)d (%(duration).3fs)",
        {"method": method, "path": path, "status": status, "duration": duration},
    )


app_logger = get_logger("jenan_biz")
