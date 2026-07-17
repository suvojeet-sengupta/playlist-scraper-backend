"""Spotify playlist scraper (Unofficial Web Scraping).

Extracts playlist data directly from the public Spotify web player HTML
payload (initialState) without requiring any official API keys or SDKs.
"""

from __future__ import annotations

import base64
import json
import logging
import re
import time
from datetime import datetime, timezone

import httpx

from app.models.base import (
    Album,
    Artist,
    PlaylistInfo,
    PlaylistResponse,
    Track,
)
from app.scrapers.base import BaseScraper
from app.utils.sanitizer import Sanitizer

logger = logging.getLogger(__name__)

_SPOTIFY_PLAYLIST_RE = re.compile(
    r"open\.spotify\.com/playlist/([A-Za-z0-9]+)"
)


class SpotifyScraper(BaseScraper):
    """Unofficial scraper for Spotify public playlists."""

    platform_name = "spotify"

    def __init__(self) -> None:
        pass

    # ── Interface ─────────────────────────────────────────────────────

    @classmethod
    def can_handle(cls, url: str) -> bool:
        return "open.spotify.com/playlist/" in url

    def extract_playlist_id(self, url: str) -> str:
        m = _SPOTIFY_PLAYLIST_RE.search(url)
        if not m:
            raise ValueError(f"Cannot extract Spotify playlist ID from: {url}")
        return m.group(1)

    async def scrape_playlist(self, playlist_id: str) -> PlaylistResponse:
        """Fetch full playlist data by scraping Spotify public pages."""
        start = time.perf_counter()
        logger.info("Scraping Spotify playlist %s (Unofficial Embed)", playlist_id)

        url = f"https://open.spotify.com/embed/playlist/{playlist_id}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 404:
                raise ValueError(f"Spotify playlist '{playlist_id}' not found.")
            if response.status_code != 200:
                raise RuntimeError(f"Spotify returned status {response.status_code}")

            html = response.text

        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
        if not match:
            raise RuntimeError("Failed to extract Spotify payload. The page structure might have changed.")

        try:
            payload = json.loads(match.group(1))
        except Exception as e:
            raise RuntimeError(f"Failed to decode Spotify payload: {e}")

        entity = payload.get("props", {}).get("pageProps", {}).get("state", {}).get("data", {}).get("entity", {})
        if not entity:
            raise ValueError(f"Playlist data missing in payload for ID: {playlist_id}")

        raw_playlist = entity
        
        # ── Playlist metadata ────────────────────────────────────────
        playlist_info = self._build_playlist_info(raw_playlist, playlist_id)

        # ── Tracks ───────────────────────────────────────────────────
        tracks: list[Track] = []
        track_list = raw_playlist.get("trackList", [])
        
        for i, item in enumerate(track_list):
            try:
                tracks.append(self._build_track(item, i + 1))
            except Exception:
                logger.warning("Skipping malformed track in payload", exc_info=True)

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            "Scraped %d tracks from '%s' in %d ms (Unofficial Embed)",
            len(tracks),
            playlist_info.name,
            elapsed_ms,
        )

        return PlaylistResponse(
            success=True,
            platform=self.platform_name,
            playlist=playlist_info,
            tracks=tracks,
            scraped_at=datetime.now(timezone.utc).isoformat(),
            scrape_duration_ms=elapsed_ms,
        )

    # ── Private helpers ───────────────────────────────────────────────

    @staticmethod
    def _build_playlist_info(raw: dict, playlist_id: str) -> PlaylistInfo:
        images = raw.get("coverArt", {}).get("sources", [])
        image_url = images[0].get("url") if images else None
        
        return PlaylistInfo(
            name=Sanitizer.clean_text(raw.get("title", "")) or "Untitled",
            description=Sanitizer.clean_text(raw.get("subtitle")),
            owner="Spotify" if "Spotify" in str(raw.get("subtitle", "")) else None,
            platform="spotify",
            platform_id=playlist_id,
            url=f"https://open.spotify.com/playlist/{playlist_id}",
            image_url=image_url,
            total_tracks=len(raw.get("trackList", [])),
            followers=None,
        )

    @staticmethod
    def _build_track(raw: dict, track_number: int) -> Track:
        # Artists
        artists: list[Artist] = []
        subtitle = raw.get("subtitle", "")
        if subtitle:
            artist_names = [a.strip() for a in re.split(r',|\u00a0', subtitle) if a.strip()]
            for name in artist_names:
                artists.append(
                    Artist(
                        name=Sanitizer.clean_text(name),
                        id=None,
                        url=None,
                        image_url=None,
                    )
                )

        duration_ms = raw.get("duration", 0)
        
        uri = raw.get("uri", "")
        track_id = uri.split(":")[-1] if uri else ""

        return Track(
            title=Sanitizer.clean_text(raw.get("title", "")) or "Untitled",
            artists=artists,
            album=None,
            duration_ms=duration_ms,
            duration_formatted=Sanitizer.format_duration(duration_ms),
            isrc=None,
            track_number=track_number,
            explicit=raw.get("isExplicit", False),
            preview_url=raw.get("audioPreview", {}).get("url") if raw.get("audioPreview") else None,
            external_url=f"https://open.spotify.com/track/{track_id}" if track_id else None,
            platform_id=track_id,
            platform="spotify",
        )
