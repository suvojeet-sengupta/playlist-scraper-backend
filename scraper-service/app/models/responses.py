"""API response models and error schemas.

These models define the shape of every JSON response returned by the API,
including structured error payloads.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Error responses
# ---------------------------------------------------------------------------

class ErrorDetail(BaseModel):
    """Structured error information."""

    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict | list | str | None = Field(
        default=None,
        description="Optional extra context for debugging",
    )


class ErrorResponse(BaseModel):
    """Envelope returned on any failed request."""

    success: bool = Field(default=False)
    error: ErrorDetail


# ---------------------------------------------------------------------------
# Platform listing
# ---------------------------------------------------------------------------

class PlatformInfo(BaseModel):
    """Information about a supported scraping platform."""

    name: str = Field(..., description='Platform identifier (e.g. "spotify")')
    display_name: str = Field(..., description="User-friendly name")
    supported: bool = Field(..., description="Whether the platform is fully implemented")
    url_patterns: list[str] = Field(
        default_factory=list,
        description="Example URL patterns accepted",
    )


class PlatformsResponse(BaseModel):
    """Response listing all platforms."""

    success: bool = Field(default=True)
    platforms: list[PlatformInfo] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Scrape request body
# ---------------------------------------------------------------------------

class ScrapeRequest(BaseModel):
    """POST body for the scrape endpoint."""

    url: str = Field(..., description="Playlist URL to scrape")
