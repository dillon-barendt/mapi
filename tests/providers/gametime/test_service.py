from __future__ import annotations

from typing import Any

import pytest

from mapi.core.config import Settings
from mapi.providers.gametime import (
    GametimeService,
    grid_row_from_event_record,
    grid_rows_from_event_records,
    summarize_listings_payload,
)

EVENT_RECORD: dict[str, Any] = {
    "event": {
        "id": "evt-1",
        "name": "Warriors vs Lakers",
        "datetime_local": "2026-08-10T19:30:00",
        "datetime_utc": "2026-08-11T02:30:00Z",
        "category_group": "sport",
        "category": "nba",
    },
    "venue": {"id": "ven-1", "name": "Chase Center", "city": "SF", "state": "CA"},
    "performers": [{"name": "Golden State Warriors"}],
}


class FakeGametimeClient:
    def __init__(
        self,
        pages: list[list[dict[str, Any]]],
        listings: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        self.pages = pages
        self.listings = listings or {}
        self.event_calls: list[int] = []

    async def get_events(
        self,
        *,
        page: int = 1,
        per_page: int | None = None,
        category_group: str | None = None,
        category: str | None = None,
        q: str | None = None,
        performer_id: str | None = None,
        venue_id: str | None = None,
    ) -> list[dict[str, Any]]:
        self.event_calls.append(page)
        if page - 1 < len(self.pages):
            return self.pages[page - 1]
        return []

    async def get_event_listings(
        self,
        event_id: str,
        *,
        quantity: int | None = None,
        all_in_pricing: bool | None = None,
        jitter_cheapest: int | None = None,
    ) -> dict[str, Any]:
        return self.listings.get(event_id, {})


def test_grid_row_flattens_nested_event_venue_and_performer() -> None:
    row = grid_row_from_event_record(EVENT_RECORD)

    assert row.event_id == "evt-1"
    assert row.event_name == "Warriors vs Lakers"
    assert row.event_datetime_local == "2026-08-10T19:30:00"
    assert row.category_group == "sport"
    assert row.category == "nba"
    assert row.performer_name == "Golden State Warriors"
    assert row.venue_id == "ven-1"
    assert row.venue_name == "Chase Center"
    assert row.venue_city == "SF"
    assert row.venue_state == "CA"
    assert row.listings is None


def test_grid_row_accepts_flat_records() -> None:
    row = grid_row_from_event_record(
        {"id": "evt-2", "name": "Flat Event", "category": "nfl"}
    )

    assert row.event_id == "evt-2"
    assert row.event_name == "Flat Event"
    assert row.venue_name is None


def test_grid_rows_skip_records_without_an_id() -> None:
    rows, skipped = grid_rows_from_event_records(
        [EVENT_RECORD, {"event": {"name": "no id"}}, {"id": "evt-3"}]
    )

    assert [row.event_id for row in rows] == ["evt-1", "evt-3"]
    assert skipped == 1


def test_summarize_listings_extracts_count_and_price_bounds() -> None:
    summary = summarize_listings_payload(
        {
            "listings": [
                {"price": {"total": 120.5}},
                {"price": 80},
                {"price": "not-a-number"},
            ]
        }
    )

    assert summary.listing_count == 3
    assert summary.min_price == 80.0
    assert summary.max_price == 120.5


def test_summarize_listings_reads_nested_data_container() -> None:
    summary = summarize_listings_payload({"data": {"listings": [{"price": 55}]}})

    assert summary.listing_count == 1
    assert summary.min_price == 55.0


def test_summarize_listings_handles_empty_payload() -> None:
    summary = summarize_listings_payload({})

    assert summary.listing_count == 0
    assert summary.min_price is None
    assert summary.max_price is None


@pytest.mark.anyio
async def test_fetch_all_event_records_paginates_until_short_page() -> None:
    client = FakeGametimeClient(
        pages=[[EVENT_RECORD, EVENT_RECORD], [EVENT_RECORD]],
    )
    service = GametimeService(
        client=client,
        settings=Settings(gametime_events_per_page=2),
    )

    records = await service.fetch_all_event_records()

    assert len(records) == 3
    assert client.event_calls == [1, 2]


@pytest.mark.anyio
async def test_fetch_all_event_records_respects_page_safety_cap() -> None:
    client = FakeGametimeClient(pages=[[EVENT_RECORD]] * 50)
    service = GametimeService(
        client=client,
        settings=Settings(gametime_events_per_page=1, gametime_max_event_pages=3),
    )

    records = await service.fetch_all_event_records()

    assert len(records) == 3
    assert client.event_calls == [1, 2, 3]


@pytest.mark.anyio
async def test_fetch_listing_summary_uses_client_payload() -> None:
    client = FakeGametimeClient(
        pages=[],
        listings={"evt-1": {"listings": [{"price": 42}]}},
    )
    service = GametimeService(client=client, settings=Settings())

    summary = await service.fetch_listing_summary("evt-1")

    assert summary.listing_count == 1
    assert summary.min_price == 42.0
