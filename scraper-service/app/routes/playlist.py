"""Playlist API routes.

Exposes endpoints for scraping playlists, listing supported platforms,
and performing health checks.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from app.models.responses import (
    ErrorDetail,
    ErrorResponse,
    PlatformsResponse,
    ScrapeRequest,
)
from app.scrapers.factory import ScraperFactory
from app.utils.url_parser import URLParser

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["playlist"])


@router.post("/scrape")
async def scrape_playlist(body: ScrapeRequest):
    """Scrape a playlist from its URL (POST)."""
    return await _do_scrape(body.url)


@router.get("/scrape")
async def scrape_playlist_get(
    url: str = Query(..., description="Playlist URL to scrape"),
):
    """Scrape a playlist from its URL (GET)."""
    return await _do_scrape(url)


@router.get("/platforms", response_model=PlatformsResponse)
async def list_platforms():
    """List all supported music platforms."""
    return PlatformsResponse(
        success=True,
        platforms=ScraperFactory.get_supported_platforms(),
    )


@router.get("/health")
async def health_check():
    """Simple health-check endpoint."""
    return {
        "status": "healthy",
        "service": "scraper-service",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ── Internal helper ───────────────────────────────────────────────────

async def _do_scrape(url: str):
    """Shared scraping logic for POST and GET endpoints."""
    # Validate URL
    try:
        parsed = URLParser.parse(url)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="INVALID_URL",
                    message=str(exc),
                )
            ).model_dump(),
        )

    # Get scraper
    try:
        scraper = ScraperFactory.get_scraper(url)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="PLATFORM_NOT_SUPPORTED",
                    message=str(exc),
                )
            ).model_dump(),
        )

    # Scrape
    try:
        result = await scraper.scrape_playlist(parsed.playlist_id)
        return result.model_dump()
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=501,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="NOT_IMPLEMENTED",
                    message=str(exc),
                )
            ).model_dump(),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="PLAYLIST_NOT_FOUND",
                    message=str(exc),
                )
            ).model_dump(),
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=403,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="ACCESS_DENIED",
                    message=str(exc),
                )
            ).model_dump(),
        )
    except RuntimeError as exc:
        msg = str(exc)
        if "rate limit" in msg.lower():
            raise HTTPException(
                status_code=429,
                detail=ErrorResponse(
                    error=ErrorDetail(
                        code="RATE_LIMITED",
                        message=msg,
                    )
                ).model_dump(),
            )
        raise HTTPException(
            status_code=502,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="SCRAPE_FAILED",
                    message=msg,
                )
            ).model_dump(),
        )
    except Exception as exc:
        logger.exception("Unexpected scraping error")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error=ErrorDetail(
                    code="INTERNAL_ERROR",
                    message="An unexpected error occurred during scraping.",
                    details=str(exc),
                )
            ).model_dump(),
        )
