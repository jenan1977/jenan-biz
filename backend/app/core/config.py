"""
config.py - Application configuration loaded from environment variables.
"""

import os

from dotenv import load_dotenv

# Load variables from .env file if it exists
load_dotenv()


class Settings:
    """
    Application settings backed by environment variables.

    Required variables must be set before the application starts.
    """

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/jenan_biz",
    )
    """Full SQLAlchemy-compatible database URL."""

    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"
    """When True SQLAlchemy logs all SQL statements (development only)."""

    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "5"))
    """Number of connections kept open in the connection pool."""

    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    """Additional connections allowed beyond pool_size under load."""

    # ------------------------------------------------------------------
    # Timezone
    # ------------------------------------------------------------------
    TIMEZONE: str = os.getenv("TIMEZONE", "UTC")
    """Application timezone; all timestamps are stored in UTC."""

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    APP_NAME: str = os.getenv("APP_NAME", "Jenan-Biz")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # ------------------------------------------------------------------
    # JWT / Security
    # ------------------------------------------------------------------
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "changeme-secret-key-for-development-only-do-not-use-in-production",
    )
    """JWT signing secret – override with a long random value in production."""

    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    """JWT signing algorithm."""

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    """Lifetime of an access token in minutes."""

    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )
    """Lifetime of a refresh token in days."""

    def validate(self) -> None:
        """Raise ValueError if any required setting is missing or invalid."""
        if not self.DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable is required.")
        if self.DATABASE_POOL_SIZE < 1:
            raise ValueError("DATABASE_POOL_SIZE must be at least 1.")
        if self.DATABASE_MAX_OVERFLOW < 0:
            raise ValueError("DATABASE_MAX_OVERFLOW must be non-negative.")


# Singleton settings instance used throughout the application
settings = Settings()
