"""Scraper factory.

Maintains a registry of all available platform scrapers and provides
a single entry point for obtaining the correct scraper instance from
a playlist URL.
"""

from __future__ import annotations

import logging
from typing import Type

from app.models.responses import PlatformInfo
from app.scrapers.apple_music import AppleMusicScraper
from app.scrapers.base import BaseScraper
from app.scrapers.spotify import SpotifyScraper
from app.scrapers.youtube_music import YouTubeMusicScraper

logger = logging.getLogger(__name__)


class ScraperFactory:
    """Factory that selects the appropriate scraper for a given URL."""

    _scrapers: list[Type[BaseScraper]] = [
        SpotifyScraper,
        AppleMusicScraper,
        YouTubeMusicScraper,
    ]

    @classmethod
    def get_scraper(cls, url: str) -> BaseScraper:
        """Return a scraper instance capable of handling *url*.

        Raises:
            ValueError: If no registered scraper can handle the URL.
        """
        for scraper_cls in cls._scrapers:
            if scraper_cls.can_handle(url):
                logger.info("Selected scraper: %s", scraper_cls.platform_name)
                return scraper_cls()
        raise ValueError(
            f"No scraper available for URL: {url}. "
            "Supported platforms: Spotify, Apple Music (coming soon), "
            "YouTube Music (coming soon)."
        )

    @classmethod
    def get_supported_platforms(cls) -> list[PlatformInfo]:
        """Return metadata about all registered platforms."""
        platform_meta: dict[str, dict] = {
            "spotify": {
                "display_name": "Spotify",
                "supported": True,
                "url_patterns": [
                    "https://open.spotify.com/playlist/{id}",
                ],
            },
            "apple_music": {
                "display_name": "Apple Music",
                "supported": False,
                "url_patterns": [
                    "https://music.apple.com/{country}/playlist/{name}/{id}",
                ],
            },
            "youtube_music": {
                "display_name": "YouTube Music",
                "supported": False,
                "url_patterns": [
                    "https://music.youtube.com/playlist?list={id}",
                ],
            },
        }

        platforms: list[PlatformInfo] = []
        for scraper_cls in cls._scrapers:
            meta = platform_meta.get(scraper_cls.platform_name, {})
            platforms.append(
                PlatformInfo(
                    name=scraper_cls.platform_name,
                    display_name=meta.get("display_name", scraper_cls.platform_name),
                    supported=meta.get("supported", False),
                    url_patterns=meta.get("url_patterns", []),
                )
            )
        return platforms
