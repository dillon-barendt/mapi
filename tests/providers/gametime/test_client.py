from __future__ import annotations

import httpx
import pytest

from mapi.core.config import Settings
from mapi.providers.gametime import GametimeClient, GametimeProviderError


@pytest.mark.anyio
async def test_gametime_client_builds_events_and_listings_urls() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.path.startswith("/v2/listings/"):
            return httpx.Response(200, json={"listings": []})
        return httpx.Response(200, json={"events": [{"event": {"id": "evt-1"}}]})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = GametimeClient(
            settings=Settings(gametime_base_url="https://gametime.test"),
            http_client=http_client,
        )
        events = await client.get_events(
            page=2,
            per_page=500,
            category_group="sport",
            category="nba",
        )
        assert events == [{"event": {"id": "evt-1"}}]
        assert await client.get_event_listings(
            "evt-1", quantity=10, jitter_cheapest=4
        ) == {"listings": []}

    urls = [str(request.url) for request in seen]
    assert (
        "https://gametime.test/v1/events"
        "?page=2&per_page=500&category_group=sport&category=nba"
    ) in urls
    assert (
        "https://gametime.test/v2/listings/evt-1"
        "?all_in_pricing=true&quantity=10&jitter_cheapest=4"
    ) in urls


@pytest.mark.anyio
async def test_gametime_client_accepts_top_level_event_list() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(200, json=[{"event": {"id": "evt-1"}}])
        )
    ) as http_client:
        client = GametimeClient(settings=Settings(), http_client=http_client)

        assert await client.get_events() == [{"event": {"id": "evt-1"}}]


@pytest.mark.anyio
async def test_gametime_client_rejects_payload_without_event_list() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda _request: httpx.Response(200, json={"unexpected": True})
        )
    ) as http_client:
        client = GametimeClient(settings=Settings(), http_client=http_client)

        with pytest.raises(GametimeProviderError):
            await client.get_events()


@pytest.mark.anyio
async def test_gametime_client_rejects_empty_event_id() -> None:
    client = GametimeClient(settings=Settings())

    with pytest.raises(GametimeProviderError):
        await client.get_event_listings("  ")


@pytest.mark.anyio
async def test_gametime_client_raises_when_disabled() -> None:
    client = GametimeClient(settings=Settings(gametime_enabled=False))

    with pytest.raises(GametimeProviderError):
        await client.get_events()


@pytest.mark.anyio
async def test_gametime_client_raises_on_provider_failures() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(500))
    ) as http_client:
        client = GametimeClient(settings=Settings(), http_client=http_client)

        with pytest.raises(GametimeProviderError):
            await client.get_events()


@pytest.mark.anyio
async def test_gametime_client_raises_on_invalid_json() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(200, text="{"))
    ) as http_client:
        client = GametimeClient(settings=Settings(), http_client=http_client)

        with pytest.raises(GametimeProviderError):
            await client.get_events()


@pytest.mark.anyio
async def test_gametime_client_raises_on_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timeout", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = GametimeClient(settings=Settings(), http_client=http_client)

        with pytest.raises(GametimeProviderError):
            await client.get_events()
