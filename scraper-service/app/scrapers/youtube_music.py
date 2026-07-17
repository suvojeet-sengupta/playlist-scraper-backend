"""YouTube Music playlist scraper (placeholder).

This module registers the YouTube Music platform so that URLs are recognised,
but the actual scraping logic is not yet implemented.
"""

from __future__ import annotations

from urllib.parse import parse_qs, urlparse

from app.models.base import PlaylistResponse
from app.scrapers.base import BaseScraper


class YouTubeMusicScraper(BaseScraper):
    """Scraper for YouTube Music playlists (not yet implemented)."""

    platform_name = "youtube_music"

    @classmethod
    def can_handle(cls, url: str) -> bool:
        parsed = urlparse(url if url.startswith("http") else f"https://{url}")
        hostname = parsed.hostname or ""
        return "music.youtube.com" in hostname and "/playlist" in parsed.path

    def extract_playlist_id(self, url: str) -> str:
        parsed = urlparse(url if url.startswith("http") else f"https://{url}")
        qs = parse_qs(parsed.query)
        list_ids = qs.get("list", [])
        if not list_ids:
            raise ValueError(
                "YouTube Music URL is missing the 'list' query parameter."
            )
        return list_ids[0]

    async def scrape_playlist(self, playlist_id: str) -> PlaylistResponse:
        raise NotImplementedError(
            "YouTube Music scraping is not yet implemented. "
            "This platform will be supported in a future release."
        )
