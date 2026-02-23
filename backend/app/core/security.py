"""
security.py - Password hashing and JWT token utilities.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Passlib context: bcrypt for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ------------------------------------------------------------------
# Password helpers
# ------------------------------------------------------------------

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True when *plain_password* matches *hashed_password*."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Return the bcrypt hash of *password*."""
    return pwd_context.hash(password)


# ------------------------------------------------------------------
# JWT helpers
# ------------------------------------------------------------------

def _create_token(subject: Any, expires_delta: timedelta, token_type: str) -> str:
    """Internal helper that encodes a signed JWT."""
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(subject),
        "exp": expire,
        "type": token_type,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: Any) -> str:
    """Return a short-lived JWT access token for *subject* (user ID)."""
    return _create_token(
        subject,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        token_type="access",
    )


def create_refresh_token(subject: Any) -> str:
    """Return a long-lived JWT refresh token for *subject* (user ID)."""
    return _create_token(
        subject,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        token_type="refresh",
    )


def decode_token(token: str, expected_type: Optional[str] = None) -> dict:
    """
    Decode and validate a JWT.

    Parameters
    ----------
    token:
        Raw JWT string.
    expected_type:
        If provided, the ``type`` claim must equal this value.

    Raises
    ------
    JWTError
        When the token is invalid, expired, or has the wrong type.
    """
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if expected_type and payload.get("type") != expected_type:
        raise JWTError(f"Expected token type '{expected_type}'")
    return payload
