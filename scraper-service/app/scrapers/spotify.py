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
        logger.info("Scraping Spotify playlist %s (Unofficial)", playlist_id)

        url = f"https://open.spotify.com/playlist/{playlist_id}"
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

        match = re.search(r'<script id="initialState" type="text/plain">(.*?)</script>', html)
        if not match:
            raise RuntimeError("Failed to extract Spotify payload. The page structure might have changed.")

        try:
            payload = json.loads(base64.b64decode(match.group(1)).decode("utf-8"))
        except Exception as e:
            raise RuntimeError(f"Failed to decode Spotify payload: {e}")

        entities = payload.get("entities", {}).get("items", {})
        playlist_key = f"spotify:playlist:{playlist_id}"
        if playlist_key not in entities:
            raise ValueError(f"Playlist data missing in payload for ID: {playlist_id}")

        raw_playlist = entities[playlist_key]
        
        # ── Playlist metadata ────────────────────────────────────────
        playlist_info = self._build_playlist_info(raw_playlist, playlist_id)

        # ── Tracks ───────────────────────────────────────────────────
        tracks: list[Track] = []
        content = raw_playlist.get("content", {})
        items = content.get("items", [])
        
        for item in items:
            try:
                track_data = item.get("itemV2", {}).get("data", {})
                if not track_data or track_data.get("__typename") != "Track":
                    continue
                tracks.append(self._build_track(track_data))
            except Exception:
                logger.warning("Skipping malformed track in payload", exc_info=True)

        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.info(
            "Scraped %d tracks from '%s' in %d ms (Unofficial)",
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
        images = raw.get("images", {}).get("items", [])
        image_url = images[0].get("sources", [{}])[0].get("url") if images else None
        
        return PlaylistInfo(
            name=Sanitizer.clean_text(raw.get("name", "")) or "Untitled",
            description=Sanitizer.clean_text(raw.get("description")),
            owner=raw.get("ownerV2", {}).get("data", {}).get("name"),
            platform="spotify",
            platform_id=playlist_id,
            url=f"https://open.spotify.com/playlist/{playlist_id}",
            image_url=image_url,
            total_tracks=raw.get("content", {}).get("totalCount", 0),
            followers=raw.get("followers"),
        )

    @staticmethod
    def _build_track(raw: dict) -> Track:
        # Artists
        artists: list[Artist] = []
        raw_artists = raw.get("artists", {}).get("items", [])
        for a in raw_artists:
            uri = a.get("uri", "")
            artist_id = uri.split(":")[-1] if uri else None
            artists.append(
                Artist(
                    name=Sanitizer.clean_text(a.get("profile", {}).get("name", "")) or "Unknown",
                    id=artist_id,
                    url=f"https://open.spotify.com/artist/{artist_id}" if artist_id else None,
                    image_url=None,
                )
            )

        # Album
        album: Album | None = None
        raw_album = raw.get("albumOfTrack", {})
        if raw_album:
            uri = raw_album.get("uri", "")
            album_id = uri.split(":")[-1] if uri else None
            cover_sources = raw_album.get("coverArt", {}).get("sources", [])
            album = Album(
                name=Sanitizer.clean_text(raw_album.get("name", "")) or "Unknown",
                id=album_id,
                url=f"https://open.spotify.com/album/{album_id}" if album_id else None,
                image_url=cover_sources[0].get("url") if cover_sources else None,
                release_date=None,  # Not reliably available in web payload
                total_tracks=None,
            )

        # Duration
        duration_ms = raw.get("duration", {}).get("totalMilliseconds", 0)
        
        uri = raw.get("uri", "")
        track_id = uri.split(":")[-1] if uri else ""

        return Track(
            title=Sanitizer.clean_text(raw.get("name", "")) or "Untitled",
            artists=artists,
            album=album,
            duration_ms=duration_ms,
            duration_formatted=Sanitizer.format_duration(duration_ms),
            isrc=None, # ISRC not exposed in unauthenticated payload
            track_number=raw.get("trackNumber"),
            explicit=raw.get("contentRating", {}).get("label") == "EXPLICIT",
            preview_url=raw.get("previews", {}).get("audioPreviews", {}).get("items", [{}])[0].get("url"),
            external_url=f"https://open.spotify.com/track/{track_id}" if track_id else None,
            platform_id=track_id,
            platform="spotify",
        )
