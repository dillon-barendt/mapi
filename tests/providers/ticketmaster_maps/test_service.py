from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.providers.ticketmaster_maps import (
    TicketmasterMapsProviderError,
    normalize_legacy_event_id,
    summarize_place_detail_payload,
)

FIXTURES = Path(__file__).parents[2] / "fixtures" / "ticketmaster_maps"


def test_normalize_legacy_event_id_trims_and_uppercases() -> None:
    assert normalize_legacy_event_id(" 3b00633ea89923f8 ") == "3B00633EA89923F8"


@pytest.mark.parametrize("value", ["", "../secret", "https://example.com/x", "abc!"])
def test_normalize_legacy_event_id_rejects_unsafe_values(value: str) -> None:
    with pytest.raises(TicketmasterMapsProviderError):
        normalize_legacy_event_id(value)


def test_summarize_place_detail_payload_is_conservative() -> None:
    payload = json.loads((FIXTURES / "place_detail_minimal.json").read_text())
    summary = summarize_place_detail_payload("3b00633ea89923f8", payload)

    assert summary.legacy_event_id == "3B00633EA89923F8"
    assert summary.source == "ticketmaster_maps"
    assert summary.has_payload is True
    assert summary.venue_name == "Demo Arena"
    assert summary.event_name == "Demo Arena Basketball"
    assert summary.section_count == 2
    assert summary.place_count == 3
    assert "sections" in summary.top_level_keys
