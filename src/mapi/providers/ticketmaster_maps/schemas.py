from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class TicketmasterPlaceDetailRaw(BaseModel):
    legacy_event_id: str
    payload: dict[str, Any] = Field(default_factory=dict)


class TicketmasterPlaceDetailSummary(BaseModel):
    legacy_event_id: str
    source: Literal["ticketmaster_maps"] = "ticketmaster_maps"
    has_payload: bool
    top_level_keys: list[str] = Field(default_factory=list)
    venue_name: str | None = None
    event_name: str | None = None
    section_count: int | None = None
    place_count: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
