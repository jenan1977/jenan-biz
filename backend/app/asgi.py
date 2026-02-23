"""
asgi.py - FastAPI ASGI application entrypoint.

Features
--------
- Calls ``startup()`` from main.py on application startup.
- Mounts ``webroot/`` at ``/`` (static analytics UI).
- Mounts ``assets/`` at ``/assets``.
- Includes the agents API router (if available).
- Optional CORS controlled by ``ALLOWED_ORIGINS`` env var
  (comma-separated list of allowed origins, e.g. "http://localhost:3000,https://example.com").

Run with uvicorn
----------------
    PYTHONPATH=backend uvicorn app.asgi:app --reload --port 8000
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Create FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Jenan-Biz API",
    version="1.0.0",
    description="Business management API with job queue and analytics.",
)

# ---------------------------------------------------------------------------
# Optional CORS middleware
# ---------------------------------------------------------------------------
_allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "")
if _allowed_origins_raw.strip():
    from fastapi.middleware.cors import CORSMiddleware

    _origins = [o.strip() for o in _allowed_origins_raw.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info("CORS enabled for origins: %s", _origins)

# ---------------------------------------------------------------------------
# Agents router – graceful fallback if unavailable
# ---------------------------------------------------------------------------
try:
    from app.api.routers.agents import router as agents_router

    app.include_router(agents_router)
    logger.info("Agents router registered at /api/v1/agents")
except Exception as exc:  # pragma: no cover
    logger.warning("Agents router not available: %s", exc)

# ---------------------------------------------------------------------------
# Blog router
# ---------------------------------------------------------------------------
try:
    from app.blog.routes import router as blog_router

    app.include_router(blog_router)
    logger.info("Blog router registered at /api/v1/blog")
except Exception as exc:  # pragma: no cover
    logger.warning("Blog router not available: %s", exc)

# ---------------------------------------------------------------------------
# Static file mounts
# ---------------------------------------------------------------------------
# Resolve paths relative to the repository root (two levels above backend/app)
_repo_root = Path(__file__).resolve().parents[2]

_webroot = _repo_root / "webroot"
_assets = _repo_root / "assets"

if _webroot.exists():
    app.mount("/", StaticFiles(directory=str(_webroot), html=True), name="webroot")
else:
    logger.warning("webroot directory not found at %s – static UI not served", _webroot)

if _assets.exists():
    app.mount("/assets", StaticFiles(directory=str(_assets)), name="assets")
else:
    logger.warning("assets directory not found at %s", _assets)


# ---------------------------------------------------------------------------
# Startup event
# ---------------------------------------------------------------------------
@app.on_event("startup")
def on_startup() -> None:
    """Run database initialisation on application startup."""
    try:
        from app.main import startup

        startup()
    except Exception as exc:
        logger.error("Startup failed: %s", exc)
        raise
