from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TicketmasterVenueSummary(BaseModel):
    venue_name: str | None = None
    venue_id: str | None = None
    legacy_venue_id: str | None = None
    venue_timezone: str | None = None
    venue_city: str | None = None
    venue_state_code: str | None = None
    venue_country_code: str | None = None
    venue_zip_code: str | None = None
    venue_latitude: float | None = None
    venue_longitude: float | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class TicketmasterDiscoveryEvent(BaseModel):
    event_id: str | None = None
    legacy_event_id: str
    event_name: str | None = None
    event_status: str | None = None
    event_start_date_time: str | None = None
    event_start_local_date: str | None = None
    event_start_local_time: str | None = None
    source: str | None = None
    brand_name: str | None = None
    official_seller: bool | None = None
    transactable: bool | None = None
    classification_segment: str | None = None
    classification_genre: str | None = None
    classification_sub_genre: str | None = None
    venue: TicketmasterVenueSummary | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class TicketmasterDiscoveryFeedSummary(BaseModel):
    country_code: str
    format: Literal["json", "csv"]
    event_count: int
    legacy_event_ids: list[str]
    events: list[TicketmasterDiscoveryEvent]


class TicketmasterLegacyIdsResponse(BaseModel):
    country_code: str
    format: Literal["json", "csv"]
    legacy_event_ids: list[str]
