from __future__ import annotations

import csv
from collections.abc import Iterable
from io import StringIO
from typing import Any

from .client import TicketmasterDiscoveryClient
from .exceptions import TicketmasterDiscoveryProviderError
from .schemas import (
    TicketmasterDiscoveryEvent,
    TicketmasterDiscoveryFeedSummary,
    TicketmasterVenueSummary,
)


def _first(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return None


def _as_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y"}:
            return True
        if lowered in {"false", "0", "no", "n"}:
            return False
    return None


def _as_float(value: Any) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _venue_from_record(record: dict[str, Any]) -> TicketmasterVenueSummary | None:
    raw_venue = record.get("venue")
    venue = raw_venue if isinstance(raw_venue, dict) else record
    venue_name = _first(venue, "venueName", "name")
    if venue is record and venue_name is None:
        return None
    return TicketmasterVenueSummary(
        venue_name=venue_name,
        venue_id=_first(venue, "venueId", "id"),
        legacy_venue_id=_first(venue, "legacyVenueId"),
        venue_timezone=_first(venue, "venueTimezone", "timezone"),
        venue_city=_first(venue, "venueCity", "city"),
        venue_state_code=_first(venue, "venueStateCode", "stateCode"),
        venue_country_code=_first(venue, "venueCountryCode", "countryCode"),
        venue_zip_code=_first(venue, "venueZipCode", "postalCode", "zipCode"),
        venue_latitude=_as_float(_first(venue, "venueLatitude", "latitude")),
        venue_longitude=_as_float(_first(venue, "venueLongitude", "longitude")),
        raw=dict(venue),
    )


def _event_from_record(
    record: dict[str, Any],
    *,
    source_format: str,
) -> TicketmasterDiscoveryEvent:
    legacy_event_id = str(
        _first(record, "legacyEventId", "legacy_event_id") or ""
    ).strip()
    if not legacy_event_id:
        raise TicketmasterDiscoveryProviderError(
            f"Discovery {source_format} event is missing legacyEventId."
        )
    return TicketmasterDiscoveryEvent(
        event_id=_first(record, "eventId", "event_id"),
        legacy_event_id=legacy_event_id,
        event_name=_first(record, "eventName", "event_name"),
        event_status=_first(record, "eventStatus", "event_status"),
        event_start_date_time=_first(
            record,
            "eventStartDateTime",
            "event_start_date_time",
        ),
        event_start_local_date=_first(
            record,
            "eventStartLocalDate",
            "event_start_local_date",
        ),
        event_start_local_time=_first(
            record,
            "eventStartLocalTime",
            "event_start_local_time",
        ),
        source=_first(record, "source"),
        brand_name=_first(record, "brandName", "brand_name"),
        official_seller=_as_bool(_first(record, "officialSeller", "official_seller")),
        transactable=_as_bool(_first(record, "transactable")),
        classification_segment=_first(
            record,
            "classificationSegment",
            "classification_segment",
        ),
        classification_genre=_first(
            record,
            "classificationGenre",
            "classification_genre",
        ),
        classification_sub_genre=_first(
            record,
            "classificationSubGenre",
            "classification_sub_genre",
        ),
        venue=_venue_from_record(record),
        raw=dict(record),
    )


def extract_legacy_event_ids(events: Iterable[TicketmasterDiscoveryEvent]) -> list[str]:
    seen: set[str] = set()
    ids: list[str] = []
    for event in events:
        if event.legacy_event_id not in seen:
            seen.add(event.legacy_event_id)
            ids.append(event.legacy_event_id)
    return ids


def parse_discovery_json_events(
    country_code: str,
    events: list[dict[str, Any]],
) -> TicketmasterDiscoveryFeedSummary:
    parsed = [_event_from_record(event, source_format="json") for event in events]
    if not parsed:
        raise TicketmasterDiscoveryProviderError("Discovery JSON feed was empty.")
    return TicketmasterDiscoveryFeedSummary(
        country_code=country_code.upper(),
        format="json",
        event_count=len(parsed),
        legacy_event_ids=extract_legacy_event_ids(parsed),
        events=parsed,
    )


def parse_discovery_csv_events(
    country_code: str,
    csv_text: str,
) -> TicketmasterDiscoveryFeedSummary:
    if not csv_text.strip():
        raise TicketmasterDiscoveryProviderError("Discovery CSV feed was empty.")
    try:
        rows = list(csv.DictReader(StringIO(csv_text)))
    except csv.Error as error:
        raise TicketmasterDiscoveryProviderError(
            "Discovery CSV feed could not be parsed."
        ) from error
    if not rows:
        raise TicketmasterDiscoveryProviderError("Discovery CSV feed had no rows.")
    parsed = [_event_from_record(dict(row), source_format="csv") for row in rows]
    return TicketmasterDiscoveryFeedSummary(
        country_code=country_code.upper(),
        format="csv",
        event_count=len(parsed),
        legacy_event_ids=extract_legacy_event_ids(parsed),
        events=parsed,
    )


class TicketmasterDiscoveryService:
    def __init__(self, client: TicketmasterDiscoveryClient | None = None) -> None:
        self.client = client or TicketmasterDiscoveryClient()

    async def fetch_events_json(
        self,
        country_code: str = "US",
    ) -> TicketmasterDiscoveryFeedSummary:
        events = await self.client.get_events_json(country_code)
        return parse_discovery_json_events(country_code, events)

    async def fetch_events_csv(
        self,
        country_code: str = "US",
    ) -> TicketmasterDiscoveryFeedSummary:
        csv_text = await self.client.get_events_csv(country_code)
        return parse_discovery_csv_events(country_code, csv_text)

    async def fetch_feed_metadata(self) -> dict[str, Any]:
        return await self.client.get_feed_metadata()
