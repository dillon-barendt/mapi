from __future__ import annotations

from typing import Any

import pytest

from mapi.core.config import Settings
from mapi.providers.gametime import GametimeProviderError, GametimeService
from mapi.services.gametime_enrichment import (
    GametimeEnrichmentRequest,
    GametimeEnrichmentService,
    GametimeEnrichmentStore,
)


def event_record(event_id: str, name: str, category: str | None = None) -> dict:
    return {"event": {"id": event_id, "name": name, "category": category}}


class FakeGametimeClient:
    def __init__(
        self,
        pages: list[list[dict[str, Any]]],
        listings: dict[str, dict[str, Any]] | None = None,
        failing_listing_ids: set[str] | None = None,
        fail_events: bool = False,
    ) -> None:
        self.pages = pages
        self.listings = listings or {}
        self.failing_listing_ids = failing_listing_ids or set()
        self.fail_events = fail_events

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
        if self.fail_events:
            raise GametimeProviderError("events feed unavailable")
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
        if event_id in self.failing_listing_ids:
            raise GametimeProviderError(f"no listings for {event_id}")
        return self.listings.get(event_id, {})


def build_service(client: FakeGametimeClient) -> GametimeEnrichmentService:
    return GametimeEnrichmentService(
        gametime_service=GametimeService(client=client, settings=Settings()),
        store=GametimeEnrichmentStore(),
    )


@pytest.mark.anyio
async def test_run_job_aggregates_events_and_counts_skipped_records() -> None:
    service = build_service(
        FakeGametimeClient(
            pages=[
                [
                    event_record("evt-1", "One"),
                    {"event": {"name": "missing id"}},
                    event_record("evt-2", "Two"),
                ]
            ]
        )
    )

    job = service.start_job(GametimeEnrichmentRequest())
    assert job.status == "queued"

    await service.run_job(job.job_id)

    finished = service.fetch_job(job.job_id)
    assert finished.status == "succeeded"
    assert finished.total_rows == 2
    assert finished.skipped_records == 1
    assert finished.finished_at is not None


@pytest.mark.anyio
async def test_run_job_enriches_listings_and_skips_per_event_failures() -> None:
    service = build_service(
        FakeGametimeClient(
            pages=[[event_record("evt-1", "One"), event_record("evt-2", "Two")]],
            listings={"evt-2": {"listings": [{"price": 60}, {"price": 90}]}},
            failing_listing_ids={"evt-1"},
        )
    )

    job = service.start_job(GametimeEnrichmentRequest(include_listings=True))
    await service.run_job(job.job_id)

    finished = service.fetch_job(job.job_id)
    assert finished.status == "succeeded"
    assert finished.listings_enriched == 1

    page = service.fetch_rows_page(job.job_id, start_row=0, end_row=10)
    by_id = {row.event_id: row for row in page.rows}
    assert by_id["evt-1"].listings is None
    assert by_id["evt-2"].listings is not None
    assert by_id["evt-2"].listings.min_price == 60.0
    assert by_id["evt-2"].listings.listing_count == 2


@pytest.mark.anyio
async def test_run_job_records_failures_instead_of_raising() -> None:
    service = build_service(FakeGametimeClient(pages=[], fail_events=True))

    job = service.start_job(GametimeEnrichmentRequest())
    await service.run_job(job.job_id)

    finished = service.fetch_job(job.job_id)
    assert finished.status == "failed"
    assert finished.error == "events feed unavailable"


@pytest.mark.anyio
async def test_fetch_rows_page_slices_and_reports_totals() -> None:
    service = build_service(
        FakeGametimeClient(
            pages=[[event_record(f"evt-{i}", f"Event {i}") for i in range(5)]]
        )
    )
    job = service.start_job(GametimeEnrichmentRequest())
    await service.run_job(job.job_id)

    page = service.fetch_rows_page(job.job_id, start_row=1, end_row=3)

    assert page.total_rows == 5
    assert page.start_row == 1
    assert page.end_row == 3
    assert [row.event_id for row in page.rows] == ["evt-1", "evt-2"]


@pytest.mark.anyio
async def test_fetch_rows_page_sorts_with_missing_values_last() -> None:
    service = build_service(
        FakeGametimeClient(
            pages=[
                [
                    event_record("evt-1", "Bravo", category="nba"),
                    event_record("evt-2", "Alpha", category=None),
                    event_record("evt-3", "Charlie", category="mlb"),
                ]
            ]
        )
    )
    job = service.start_job(GametimeEnrichmentRequest())
    await service.run_job(job.job_id)

    ascending = service.fetch_rows_page(
        job.job_id, start_row=0, end_row=10, sort_field="category"
    )
    descending = service.fetch_rows_page(
        job.job_id, start_row=0, end_row=10, sort_field="category", sort_order="desc"
    )

    assert [row.event_id for row in ascending.rows] == ["evt-3", "evt-1", "evt-2"]
    assert [row.event_id for row in descending.rows] == ["evt-1", "evt-3", "evt-2"]


@pytest.mark.anyio
async def test_fetch_rows_page_sorts_by_min_price_from_listings() -> None:
    service = build_service(
        FakeGametimeClient(
            pages=[[event_record("evt-1", "One"), event_record("evt-2", "Two")]],
            listings={
                "evt-1": {"listings": [{"price": 90}]},
                "evt-2": {"listings": [{"price": 40}]},
            },
        )
    )
    job = service.start_job(GametimeEnrichmentRequest(include_listings=True))
    await service.run_job(job.job_id)

    page = service.fetch_rows_page(
        job.job_id, start_row=0, end_row=10, sort_field="min_price"
    )

    assert [row.event_id for row in page.rows] == ["evt-2", "evt-1"]


@pytest.mark.anyio
async def test_fetch_rows_page_validates_job_state_and_arguments() -> None:
    service = build_service(FakeGametimeClient(pages=[[event_record("evt-1", "One")]]))
    job = service.start_job(GametimeEnrichmentRequest())

    with pytest.raises(ValueError, match="status 'queued'"):
        service.fetch_rows_page(job.job_id)

    await service.run_job(job.job_id)

    with pytest.raises(LookupError, match="Unknown enrichment job"):
        service.fetch_rows_page("does-not-exist")
    with pytest.raises(ValueError, match="greater than start_row"):
        service.fetch_rows_page(job.job_id, start_row=5, end_row=5)
    with pytest.raises(ValueError, match="sort_field must be one of"):
        service.fetch_rows_page(job.job_id, sort_field="raw")
