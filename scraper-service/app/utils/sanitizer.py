"""Data sanitization utilities.

Provides helpers for cleaning strings coming from external APIs before
they are stored or returned to clients.
"""

from __future__ import annotations

import html
import re
import unicodedata


class Sanitizer:
    """Collection of static sanitization helpers."""

    @staticmethod
    def clean_text(text: str | None) -> str | None:
        """Clean and normalise a text string.

        * Strips leading/trailing whitespace
        * Decodes HTML entities (``&amp;`` → ``&``)
        * Normalises Unicode to NFC form
        * Collapses internal runs of whitespace to a single space
        """
        if text is None:
            return None
        text = html.unescape(text)
        text = unicodedata.normalize("NFC", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text if text else None

    @staticmethod
    def format_duration(ms: int) -> str:
        """Convert milliseconds to ``M:SS`` or ``H:MM:SS`` format.

        Args:
            ms: Duration in milliseconds (must be >= 0).

        Returns:
            Formatted duration string, e.g. ``"3:45"`` or ``"1:02:30"``.
        """
        if ms < 0:
            ms = 0
        total_seconds = ms // 1000
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}:{minutes:02d}:{seconds:02d}"
        return f"{minutes}:{seconds:02d}"

    @staticmethod
    def clean_url(url: str | None) -> str | None:
        """Return a trimmed URL or ``None`` if empty."""
        if not url:
            return None
        url = url.strip()
        return url if url else None

    @staticmethod
    def truncate(text: str | None, max_length: int = 500) -> str | None:
        """Truncate *text* to *max_length* characters, adding ``…`` if cut."""
        if text is None:
            return None
        if len(text) <= max_length:
            return text
        return text[: max_length - 1] + "…"
