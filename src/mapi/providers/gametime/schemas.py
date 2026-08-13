"""Minimal Gametime models.

Only the fields a server-side DataGrid needs later are kept: the event id (to
fetch detail on demand), display columns, and an aggregated listing summary.
Raw upstream payloads are intentionally not stored.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class GametimeListingSummary(BaseModel):
    """Aggregated listing data for one event; individual listings are dropped."""

    listing_count: int = 0
    min_price: float | None = None
    max_price: float | None = None


class GametimeEventGridRow(BaseModel):
    """One flattened DataGrid row derived from a Gametime event record."""

    event_id: str = Field(min_length=1)
    event_name: str | None = None
    event_datetime_local: str | None = None
    event_datetime_utc: str | None = None
    category_group: str | None = None
    category: str | None = None
    performer_name: str | None = None
    venue_id: str | None = None
    venue_name: str | None = None
    venue_city: str | None = None
    venue_state: str | None = None
    listings: GametimeListingSummary | None = None
