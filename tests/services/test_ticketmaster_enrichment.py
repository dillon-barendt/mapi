from __future__ import annotations

import json
from pathlib import Path

import pytest

from mapi.providers.ticketmaster_discovery import parse_discovery_json_events
from mapi.providers.ticketmaster_discovery.schemas import (
    TicketmasterDiscoveryFeedSummary,
)
from mapi.providers.ticketmaster_maps import (
    TicketmasterMapsProviderError,
    TicketmasterMapsService,
    TicketmasterPlaceDetailSummary,
    summarize_place_detail_payload,
)
from mapi.services.ticketmaster_enrichment import TicketmasterEnrichmentService

DISCOVERY_FIXTURES = Path(__file__).parents[1] / "fixtures" / "ticketmaster_discovery"
MAPS_FIXTURES = Path(__file__).parents[1] / "fixtures" / "ticketmaster_maps"


class FakeDiscoveryService:
    async def fetch_events_json(
        self, country_code: str = "US"
    ) -> TicketmasterDiscoveryFeedSummary:
        events = json.loads((DISCOVERY_FIXTURES / "events_minimal.json").read_text())
        return parse_discovery_json_events(country_code, events)


class FakeMapsService(TicketmasterMapsService):
    async def fetch_place_detail_summary(
        self, legacy_event_id: str
    ) -> TicketmasterPlaceDetailSummary:
        payload = json.loads((MAPS_FIXTURES / "place_detail_minimal.json").read_text())
        return summarize_place_detail_payload(legacy_event_id, payload)


class FailingMapsService(TicketmasterMapsService):
    async def fetch_place_detail_summary(
        self, legacy_event_id: str
    ) -> TicketmasterPlaceDetailSummary:
        raise TicketmasterMapsProviderError(f"no map for {legacy_event_id}")


@pytest.mark.anyio
async def test_enrich_event_by_legacy_id_returns_map_summary() -> None:
    service = TicketmasterEnrichmentService(
        discovery_service=FakeDiscoveryService(),
        maps_service=FakeMapsService(),
    )

    summary = await service.enrich_event_by_legacy_id("3b00633ea89923f8")

    assert summary.legacy_event_id == "3B00633EA89923F8"
    assert summary.section_count == 2


@pytest.mark.anyio
async def test_enrich_discovery_feed_sample_respects_limit() -> None:
    service = TicketmasterEnrichmentService(
        discovery_service=FakeDiscoveryService(),
        maps_service=FakeMapsService(),
    )

    summaries = await service.enrich_discovery_feed_sample("US", limit=1)

    assert len(summaries) == 1
    assert summaries[0].enrichment_status == "enriched"
    assert summaries[0].place_detail is not None


@pytest.mark.anyio
async def test_enrich_discovery_feed_sample_records_per_event_errors() -> None:
    service = TicketmasterEnrichmentService(
        discovery_service=FakeDiscoveryService(),
        maps_service=FailingMapsService(),
    )

    summaries = await service.enrich_discovery_feed_sample("US", limit=2)

    assert len(summaries) == 2
    assert all(
        summary.enrichment_status == "place_detail_unavailable" for summary in summaries
    )
    assert summaries[0].errors


@pytest.mark.anyio
async def test_enrich_discovery_feed_sample_rejects_unbounded_limits() -> None:
    service = TicketmasterEnrichmentService(
        discovery_service=FakeDiscoveryService(),
        maps_service=FakeMapsService(),
    )

    with pytest.raises(ValueError):
        await service.enrich_discovery_feed_sample("US", limit=101)
