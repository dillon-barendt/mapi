from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.deps import (
    get_ticketmaster_discovery_service,
    get_ticketmaster_enrichment_service,
    get_ticketmaster_maps_service,
)
from app.main import app
from app.providers.ticketmaster_discovery import (
    TicketmasterDiscoveryProviderError,
    parse_discovery_json_events,
)
from app.providers.ticketmaster_maps import (
    TicketmasterMapsProviderError,
    summarize_place_detail_payload,
)
from app.services.ticketmaster_enrichment import TicketmasterEnrichmentService

DISCOVERY_FIXTURES = Path(__file__).parents[1] / "fixtures" / "ticketmaster_discovery"
MAPS_FIXTURES = Path(__file__).parents[1] / "fixtures" / "ticketmaster_maps"


class FakeDiscoveryService:
    async def fetch_events_json(self, country_code: str = "US"):
        events = json.loads((DISCOVERY_FIXTURES / "events_minimal.json").read_text())
        return parse_discovery_json_events(country_code, events)

    async def fetch_events_csv(self, country_code: str = "US"):
        return await self.fetch_events_json(country_code)

    async def fetch_feed_metadata(self) -> dict[str, object]:
        return {"lastUpdated": "2026-07-08T00:00:00Z", "countryCodes": ["US"]}


class FailingDiscoveryService(FakeDiscoveryService):
    async def fetch_events_json(self, country_code: str = "US"):
        raise TicketmasterDiscoveryProviderError("provider unavailable")


class FakeMapsService:
    async def fetch_place_detail_summary(self, legacy_event_id: str):
        payload = json.loads((MAPS_FIXTURES / "place_detail_minimal.json").read_text())
        return summarize_place_detail_payload(legacy_event_id, payload)


class FailingMapsService:
    async def fetch_place_detail_summary(self, legacy_event_id: str):
        raise TicketmasterMapsProviderError("map unavailable")


def _clear_overrides() -> None:
    app.dependency_overrides.clear()


def test_ticketmaster_discovery_events_route_returns_summary() -> None:
    app.dependency_overrides[get_ticketmaster_discovery_service] = FakeDiscoveryService
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/ticketmaster-discovery/events?country_code=US&limit=1"
            )
    finally:
        _clear_overrides()

    payload = response.json()

    assert response.status_code == 200
    assert payload["country_code"] == "US"
    assert payload["event_count"] == 1
    assert payload["events"][0]["legacy_event_id"] == "3B00633EA89923F8"


def test_ticketmaster_discovery_legacy_ids_route_returns_ids() -> None:
    app.dependency_overrides[get_ticketmaster_discovery_service] = FakeDiscoveryService
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/ticketmaster-discovery/events/legacy-ids")
    finally:
        _clear_overrides()

    assert response.status_code == 200
    assert response.json()["legacy_event_ids"] == [
        "3B00633EA89923F8",
        "1A00222BBBBCCCCD",
    ]


def test_ticketmaster_discovery_metadata_route_returns_payload() -> None:
    app.dependency_overrides[get_ticketmaster_discovery_service] = FakeDiscoveryService
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/ticketmaster-discovery/metadata")
    finally:
        _clear_overrides()

    assert response.status_code == 200
    assert response.json()["countryCodes"] == ["US"]


def test_ticketmaster_maps_place_detail_route_returns_summary() -> None:
    app.dependency_overrides[get_ticketmaster_maps_service] = FakeMapsService
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/ticketmaster-maps/events/3B00633EA89923F8/place-detail"
            )
    finally:
        _clear_overrides()

    assert response.status_code == 200
    assert response.json()["section_count"] == 2


def test_ticketmaster_enrichment_specific_event_route_returns_summary() -> None:
    app.dependency_overrides[get_ticketmaster_enrichment_service] = (
        lambda: TicketmasterEnrichmentService(
            discovery_service=FakeDiscoveryService(),  # type: ignore[arg-type]
            maps_service=FakeMapsService(),  # type: ignore[arg-type]
        )
    )
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/ticketmaster-enrichment/events/" "3B00633EA89923F8/map-summary"
            )
    finally:
        _clear_overrides()

    assert response.status_code == 200
    assert response.json()["venue_name"] == "Demo Arena"


def test_ticketmaster_enrichment_sample_route_returns_combined_summary() -> None:
    app.dependency_overrides[get_ticketmaster_enrichment_service] = (
        lambda: TicketmasterEnrichmentService(
            discovery_service=FakeDiscoveryService(),  # type: ignore[arg-type]
            maps_service=FakeMapsService(),  # type: ignore[arg-type]
        )
    )
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/ticketmaster-enrichment/"
                "discovery-feed/sample-map-summaries?limit=1"
            )
    finally:
        _clear_overrides()

    payload = response.json()

    assert response.status_code == 200
    assert payload[0]["event"]["legacy_event_id"] == "3B00633EA89923F8"
    assert payload[0]["place_detail"]["section_count"] == 2


def test_provider_errors_become_http_errors() -> None:
    app.dependency_overrides[get_ticketmaster_discovery_service] = (
        FailingDiscoveryService
    )
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/ticketmaster-discovery/events")
    finally:
        _clear_overrides()

    assert response.status_code == 502
    assert response.json()["detail"] == "provider unavailable"
