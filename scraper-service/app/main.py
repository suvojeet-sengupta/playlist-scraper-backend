"""FastAPI application entry point.

Configures middleware, routes, and lifecycle events for the
playlist scraper microservice.
"""

from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.routes.playlist import router as playlist_router

settings = get_settings()

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Playlist Scraper Service",
    description="Scrapes playlist data from Spotify, Apple Music, YouTube Music and more.",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request Logging Middleware ────────────────────────────────────────
@app.middleware("http")
async def log_requests(request: Request, call_next) -> Response:
    """Log every incoming request with method, path, status and duration."""
    start = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s → %s (%.1f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ── Global exception fallback ─────────────────────────────────────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all so unhandled errors still return structured JSON."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "details": str(exc) if settings.debug else None,
            },
        },
    )


# ── Routers ───────────────────────────────────────────────────────────
app.include_router(playlist_router)


# ── Lifecycle Events ──────────────────────────────────────────────────
@app.on_event("startup")
async def on_startup():
    logger.info(
        "🚀 Scraper service starting on %s:%s (debug=%s)",
        settings.host,
        settings.port,
        settings.debug,
    )


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Scraper service shutting down")
