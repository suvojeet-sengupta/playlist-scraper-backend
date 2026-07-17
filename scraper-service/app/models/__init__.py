"""Data models for the playlist scraper service."""

from app.models.base import Album, Artist, PlaylistInfo, PlaylistResponse, Track
from app.models.responses import ErrorDetail, ErrorResponse, PlatformInfo, PlatformsResponse

__all__ = [
    "Artist",
    "Album",
    "Track",
    "PlaylistInfo",
    "PlaylistResponse",
    "ErrorDetail",
    "ErrorResponse",
    "PlatformInfo",
    "PlatformsResponse",
]
