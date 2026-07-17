"""Base Pydantic v2 models for playlist scraping.

These models represent the universal data structures shared across all
music platforms.  Every platform scraper maps its raw data into these
common models so that downstream consumers never need to know which
platform the data came from.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Artist(BaseModel):
    """A music artist / creator."""

    name: str = Field(..., description="Artist display name")
    id: str | None = Field(default=None, description="Platform-specific artist ID")
    url: str | None = Field(default=None, description="Link to the artist page")
    image_url: str | None = Field(default=None, description="Artist avatar / image URL")


class Album(BaseModel):
    """An album or single release."""

    name: str = Field(..., description="Album title")
    id: str | None = Field(default=None, description="Platform-specific album ID")
    url: str | None = Field(default=None, description="Link to the album page")
    image_url: str | None = Field(default=None, description="Album cover art URL")
    release_date: str | None = Field(default=None, description="Release date (ISO or partial)")
    total_tracks: int | None = Field(default=None, description="Total tracks in the album")


class Track(BaseModel):
    """A single track / song."""

    title: str = Field(..., description="Track title")
    artists: list[Artist] = Field(default_factory=list, description="List of track artists")
    album: Album | None = Field(default=None, description="Album the track belongs to")
    duration_ms: int = Field(..., description="Track duration in milliseconds")
    duration_formatted: str = Field(..., description="Human-readable duration (M:SS)")
    isrc: str | None = Field(
        default=None,
        description="International Standard Recording Code – crucial for cross-platform matching",
    )
    track_number: int | None = Field(default=None, description="Track position on the album")
    explicit: bool = Field(default=False, description="Whether the track is marked explicit")
    preview_url: str | None = Field(default=None, description="30-second preview audio URL")
    external_url: str | None = Field(default=None, description="Link to the track on the platform")
    platform_id: str = Field(..., description="Platform-specific track ID")
    platform: str = Field(..., description='Source platform (e.g. "spotify")')


class PlaylistInfo(BaseModel):
    """Metadata about a playlist (without the tracks)."""

    name: str = Field(..., description="Playlist name")
    description: str | None = Field(default=None, description="Playlist description")
    owner: str | None = Field(default=None, description="Playlist owner / creator name")
    platform: str = Field(..., description="Source platform identifier")
    platform_id: str = Field(..., description="Platform-specific playlist ID")
    url: str = Field(..., description="Canonical URL of the playlist")
    image_url: str | None = Field(default=None, description="Playlist cover image URL")
    total_tracks: int = Field(..., description="Total number of tracks")
    followers: int | None = Field(default=None, description="Number of followers / subscribers")


class PlaylistResponse(BaseModel):
    """Full scrape result containing playlist metadata and tracks."""

    success: bool = Field(default=True, description="Whether the scrape succeeded")
    platform: str = Field(..., description="Source platform identifier")
    playlist: PlaylistInfo = Field(..., description="Playlist metadata")
    tracks: list[Track] = Field(default_factory=list, description="List of scraped tracks")
    scraped_at: str = Field(..., description="ISO-8601 timestamp of when the scrape finished")
    scrape_duration_ms: int = Field(..., description="Total scrape wall-clock time in milliseconds")
