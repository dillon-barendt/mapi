from __future__ import annotations

import json
from pathlib import Path

import pytest

from mapi.providers.ticketmaster_discovery import (
    TicketmasterDiscoveryProviderError,
    extract_legacy_event_ids,
    parse_discovery_csv_events,
    parse_discovery_json_events,
)
from mapi.providers.ticketmaster_maps import (
    TicketmasterMapsProviderError,
    normalize_legacy_event_id,
    summarize_place_detail_payload,
)

DISCOVERY_FIXTURES = Path(__file__).parents[2] / "fixtures" / "ticketmaster_discovery"
MAPS_FIXTURES = Path(__file__).parents[2] / "fixtures" / "ticketmaster_maps"


def test_parse_discovery_json_events_maps_fields_and_preserves_raw() -> None:
    events = json.loads((DISCOVERY_FIXTURES / "events_minimal.json").read_text())
    summary = parse_discovery_json_events("us", events)

    assert summary.country_code == "US"
    assert summary.format == "json"
    assert summary.event_count == 2
    assert summary.legacy_event_ids == ["3B00633EA89923F8", "1A00222BBBBCCCCD"]
    assert summary.events[0].event_name == "Demo Arena Basketball"
    assert summary.events[0].venue is not None
    assert summary.events[0].venue.venue_city == "Phoenix"
    assert summary.events[0].raw["legacyEventId"] == "3B00633EA89923F8"
    assert summary.events[1].event_start_local_time is None


def test_parse_discovery_csv_events_maps_fields() -> None:
    csv_text = (DISCOVERY_FIXTURES / "events_minimal.csv").read_text()
    summary = parse_discovery_csv_events("US", csv_text)

    assert summary.event_count == 2
    assert summary.format == "csv"
    assert summary.events[0].official_seller is True
    assert summary.events[1].transactable is False
    assert summary.events[0].venue is not None
    assert summary.events[0].venue.venue_id == "KovZpZA6taIA"


def test_extract_legacy_event_ids_deduplicates_in_order() -> None:
    events = parse_discovery_csv_events(
        "US",
        (DISCOVERY_FIXTURES / "events_minimal.csv").read_text(),
    ).events

    assert extract_legacy_event_ids([events[0], events[1], events[0]]) == [
        "3B00633EA89923F8",
        "1A00222BBBBCCCCD",
    ]


def test_parse_discovery_json_events_rejects_missing_legacy_event_id() -> None:
    with pytest.raises(TicketmasterDiscoveryProviderError):
        parse_discovery_json_events("US", [{"eventId": "missing"}])


def test_normalize_legacy_event_id_trims_and_uppercases() -> None:
    assert normalize_legacy_event_id(" 3b00633ea89923f8 ") == "3B00633EA89923F8"


@pytest.mark.parametrize("value", ["", "../secret", "https://example.com/x", "abc!"])
def test_normalize_legacy_event_id_rejects_unsafe_values(value: str) -> None:
    with pytest.raises(TicketmasterMapsProviderError):
        normalize_legacy_event_id(value)


def test_summarize_place_detail_payload_is_conservative() -> None:
    payload = json.loads((MAPS_FIXTURES / "place_detail_minimal.json").read_text())
    summary = summarize_place_detail_payload("3b00633ea89923f8", payload)

    assert summary.legacy_event_id == "3B00633EA89923F8"
    assert summary.source == "ticketmaster_maps"
    assert summary.has_payload is True
    assert summary.venue_name == "Demo Arena"
    assert summary.event_name == "Demo Arena Basketball"
    assert summary.section_count == 2
    assert summary.place_count == 3
    assert "sections" in summary.top_level_keys
