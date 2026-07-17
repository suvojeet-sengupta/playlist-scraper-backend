"""Abstract base scraper.

Every platform-specific scraper inherits from ``BaseScraper`` and implements
the three abstract methods.  This guarantees a uniform interface for the
scraper factory and route layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.base import PlaylistResponse


class BaseScraper(ABC):
    """Base class for all platform scrapers."""

    platform_name: str = ""

    @abstractmethod
    async def scrape_playlist(self, playlist_id: str) -> PlaylistResponse:
        """Scrape a playlist and return normalised data.

        Args:
            playlist_id: Platform-specific identifier for the playlist.

        Returns:
            A fully populated ``PlaylistResponse``.
        """

    @abstractmethod
    def extract_playlist_id(self, url: str) -> str:
        """Extract the playlist ID from a raw URL.

        Args:
            url: The user-supplied playlist URL.

        Returns:
            The platform-specific playlist ID string.
        """

    @classmethod
    @abstractmethod
    def can_handle(cls, url: str) -> bool:
        """Return ``True`` if this scraper can process *url*."""
