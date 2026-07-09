from __future__ import annotations

import httpx
import pytest

from app.core.config import Settings
from app.providers.ticketmaster_discovery import (
    TicketmasterDiscoveryClient,
    TicketmasterDiscoveryProviderError,
)


@pytest.mark.anyio
async def test_discovery_client_builds_json_csv_and_metadata_urls() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path.endswith("/events.csv"):
            return httpx.Response(200, text="eventId,legacyEventId\nx,ABC123\n")
        if request.url.path.endswith("/events"):
            return httpx.Response(200, json={"lastUpdated": "2026-07-08T00:00:00Z"})
        return httpx.Response(200, json=[{"eventId": "x", "legacyEventId": "ABC123"}])

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler),
        base_url="https://unused.test",
    ) as http_client:
        client = TicketmasterDiscoveryClient(
            settings=Settings(
                ticketmaster_api_key="test-key",
                ticketmaster_discovery_base_url="https://feed.test/v2",
            ),
            http_client=http_client,
        )
        assert await client.get_events_json("us") == [
            {"eventId": "x", "legacyEventId": "ABC123"}
        ]
        assert "ABC123" in await client.get_events_csv("US")
        assert await client.get_feed_metadata() == {
            "lastUpdated": "2026-07-08T00:00:00Z"
        }

    urls = [str(request.url) for request in seen]
    assert "https://feed.test/v2/events.json?apikey=test-key&countryCode=US" in urls
    assert "https://feed.test/v2/events.csv?apikey=test-key&countryCode=US" in urls
    assert "https://feed.test/v2/events?apikey=test-key" in urls


@pytest.mark.anyio
async def test_discovery_client_requires_api_key() -> None:
    client = TicketmasterDiscoveryClient(settings=Settings(ticketmaster_api_key=None))

    with pytest.raises(TicketmasterDiscoveryProviderError):
        await client.get_events_json()


@pytest.mark.anyio
async def test_discovery_client_raises_on_provider_failures() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(500)),
    ) as http_client:
        client = TicketmasterDiscoveryClient(
            settings=Settings(ticketmaster_api_key="test-key"),
            http_client=http_client,
        )
        with pytest.raises(TicketmasterDiscoveryProviderError):
            await client.get_events_json()


@pytest.mark.anyio
async def test_discovery_client_raises_on_invalid_json() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(200, text="{")),
    ) as http_client:
        client = TicketmasterDiscoveryClient(
            settings=Settings(ticketmaster_api_key="test-key"),
            http_client=http_client,
        )
        with pytest.raises(TicketmasterDiscoveryProviderError):
            await client.get_events_json()


@pytest.mark.anyio
async def test_discovery_client_raises_on_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timeout", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = TicketmasterDiscoveryClient(
            settings=Settings(ticketmaster_api_key="test-key"),
            http_client=http_client,
        )
        with pytest.raises(TicketmasterDiscoveryProviderError):
            await client.get_events_json()
