"""URL parsing and platform detection utilities.

Centralises all logic for recognising which music platform a URL belongs to
and extracting the playlist identifier from it.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ParsedURL:
    """Result of parsing a playlist URL."""

    platform: str
    playlist_id: str
    original_url: str


class URLParser:
    """Detect platform and extract playlist ID from a URL."""

    # Compiled patterns mapping a platform name to a regex that captures the
    # playlist ID.  Each regex is applied against the *path* portion of the
    # URL (for Spotify / Apple Music) or the *query* string (YouTube Music).
    _PLATFORM_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
        # Spotify – e.g. /playlist/37i9dQZF1DXcBWIGoYBM5M
        ("spotify", re.compile(r"open\.spotify\.com/playlist/(?P<id>[A-Za-z0-9]+)")),
        # Apple Music – e.g. /us/playlist/todays-hits/pl.12345
        ("apple_music", re.compile(r"music\.apple\.com/.+/playlist/.+?/(?P<id>pl\.[A-Za-z0-9\-]+)")),
        # YouTube Music – e.g. /playlist?list=PLxxxxxx
        ("youtube_music", re.compile(r"music\.youtube\.com/playlist")),
    ]

    @classmethod
    def parse(cls, url: str) -> ParsedURL:
        """Parse a playlist URL and return a ``ParsedURL`` instance.

        Args:
            url: The raw playlist URL provided by the user.

        Returns:
            A ``ParsedURL`` containing the detected platform and playlist ID.

        Raises:
            ValueError: If the URL is invalid or the platform cannot be detected.
        """
        url = url.strip()
        if not url:
            raise ValueError("URL must not be empty")

        # Ensure we have a scheme so urlparse behaves correctly.
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        parsed = urlparse(url)
        if not parsed.hostname:
            raise ValueError(f"Unable to extract hostname from URL: {url}")

        full_url = parsed.geturl()

        for platform, pattern in cls._PLATFORM_PATTERNS:
            match = pattern.search(full_url)
            if match:
                playlist_id = cls._extract_id(platform, match, parsed)
                logger.info("Detected platform=%s playlist_id=%s", platform, playlist_id)
                return ParsedURL(platform=platform, playlist_id=playlist_id, original_url=url)

        raise ValueError(
            f"Unsupported or unrecognised playlist URL: {url}. "
            "Supported platforms: Spotify, Apple Music, YouTube Music."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _extract_id(cls, platform: str, match: re.Match, parsed: object) -> str:
        """Extract the playlist ID using platform-specific logic."""
        if platform == "youtube_music":
            # YouTube Music stores the playlist ID in the `list` query param.
            qs = parse_qs(parsed.query)  # type: ignore[arg-type]
            list_ids = qs.get("list", [])
            if not list_ids:
                raise ValueError("YouTube Music URL is missing the 'list' query parameter")
            return list_ids[0]

        # For Spotify and Apple Music the ID is captured by the regex.
        try:
            return match.group("id")
        except IndexError:
            raise ValueError(f"Could not extract playlist ID for platform {platform}")

    @classmethod
    def is_supported_url(cls, url: str) -> bool:
        """Return ``True`` if *url* matches any known platform pattern."""
        try:
            cls.parse(url)
            return True
        except ValueError:
            return False

    @classmethod
    def detect_platform(cls, url: str) -> str | None:
        """Return the platform name for *url*, or ``None`` if unrecognised."""
        try:
            return cls.parse(url).platform
        except ValueError:
            return None
