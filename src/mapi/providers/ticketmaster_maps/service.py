from __future__ import annotations

from typing import Any, Protocol

from ...core.constants import TM_LEGACY_EVENT_REGEX
from .exceptions import TicketmasterMapsProviderError
from .schemas import TicketmasterPlaceDetailRaw, TicketmasterPlaceDetailSummary


def normalize_legacy_event_id(value: str) -> str:
    normalized = value.strip().upper()
    if not normalized:
        raise TicketmasterMapsProviderError("Legacy Event ID is required.")
    if "://" in normalized or "/" in normalized or "\\" in normalized:
        raise TicketmasterMapsProviderError(
            "Legacy Event ID must not be a URL or path."
        )
    if not TM_LEGACY_EVENT_REGEX.fullmatch(normalized):
        raise TicketmasterMapsProviderError(
            "Legacy Event ID must be 6-40 alphanumeric characters."
        )
    return normalized


def _first_string(payload: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def _count_collection(payload: dict[str, Any], keys: tuple[str, ...]) -> int | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return len(value)
        if isinstance(value, dict):
            return len(value)
    return None


def summarize_place_detail_payload(
    legacy_event_id: str,
    payload: dict[str, Any],
) -> TicketmasterPlaceDetailSummary:
    normalized_id = normalize_legacy_event_id(legacy_event_id)
    top_level_keys = sorted(payload)
    return TicketmasterPlaceDetailSummary(
        legacy_event_id=normalized_id,
        has_payload=bool(payload),
        top_level_keys=top_level_keys,
        venue_name=_first_string(payload, ("venueName", "venue_name", "name")),
        event_name=_first_string(payload, ("eventName", "event_name")),
        section_count=_count_collection(payload, ("sections", "sectionGroups")),
        place_count=_count_collection(payload, ("places", "seats")),
        metadata={
            "payload_top_level_key_count": len(top_level_keys),
            "normalization_level": "conservative",
        },
    )


class PlaceDetailClient(Protocol):
    async def get_place_detail(
        self,
        legacy_event_id: str,
    ) -> TicketmasterPlaceDetailRaw: ...


class TicketmasterMapsService:
    def __init__(self, client: PlaceDetailClient | None = None) -> None:
        self.client: PlaceDetailClient
        if client is None:
            from .client import TicketmasterMapsClient

            self.client = TicketmasterMapsClient()
        else:
            self.client = client

    async def fetch_place_detail_summary(
        self,
        legacy_event_id: str,
    ) -> TicketmasterPlaceDetailSummary:
        normalized_id = normalize_legacy_event_id(legacy_event_id)
        raw = await self.client.get_place_detail(normalized_id)
        return summarize_place_detail_payload(raw.legacy_event_id, raw.payload)
