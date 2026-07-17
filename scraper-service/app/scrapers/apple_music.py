"""Apple Music playlist scraper (placeholder).

This module registers the Apple Music platform so that URLs are recognised,
but the actual scraping logic is not yet implemented.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

from app.models.base import PlaylistResponse
from app.scrapers.base import BaseScraper

_APPLE_MUSIC_PLAYLIST_RE = re.compile(
    r"music\.apple\.com/.+/playlist/.+?/(pl\.[A-Za-z0-9\-]+)"
)


class AppleMusicScraper(BaseScraper):
    """Scraper for Apple Music playlists (not yet implemented)."""

    platform_name = "apple_music"

    @classmethod
    def can_handle(cls, url: str) -> bool:
        parsed = urlparse(url if url.startswith("http") else f"https://{url}")
        hostname = parsed.hostname or ""
        return "music.apple.com" in hostname and "/playlist/" in parsed.path

    def extract_playlist_id(self, url: str) -> str:
        m = _APPLE_MUSIC_PLAYLIST_RE.search(url)
        if not m:
            raise ValueError(f"Cannot extract Apple Music playlist ID from: {url}")
        return m.group(1)

    async def scrape_playlist(self, playlist_id: str) -> PlaylistResponse:
        raise NotImplementedError(
            "Apple Music scraping is not yet implemented. "
            "This platform will be supported in a future release."
        )
