from __future__ import annotations

import httpx
import pytest

from mapi.core.config import Settings
from mapi.providers.ticketmaster_maps import TicketmasterMapsClient, TicketmasterMapsProviderError


@pytest.mark.anyio
async def test_maps_client_builds_place_detail_url_and_headers() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"venueName": "Demo Arena"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = TicketmasterMapsClient(
            settings=Settings(ticketmaster_maps_base_url="https://maps.test"),
            http_client=http_client,
        )
        raw = await client.get_place_detail("3b00633ea89923f8")

    assert raw.legacy_event_id == "3B00633EA89923F8"
    assert str(seen[0].url) == (
        "https://maps.test/maps/geometry/3/event/"
        "3B00633EA89923F8/placeDetail?systemId=HOST"
    )
    assert seen[0].headers["referer"] == "https://cims.ticketmaster.com/"
    assert "Mozilla/5.0" in seen[0].headers["user-agent"]
    assert seen[0].headers["sec-ch-ua-mobile"] == "?0"


@pytest.mark.anyio
async def test_maps_client_raises_on_non_2xx() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(404)),
    ) as http_client:
        client = TicketmasterMapsClient(http_client=http_client)
        with pytest.raises(TicketmasterMapsProviderError):
            await client.get_place_detail("3B00633EA89923F8")


@pytest.mark.anyio
async def test_maps_client_raises_on_invalid_json() -> None:
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(lambda _request: httpx.Response(200, text="{")),
    ) as http_client:
        client = TicketmasterMapsClient(http_client=http_client)
        with pytest.raises(TicketmasterMapsProviderError):
            await client.get_place_detail("3B00633EA89923F8")


@pytest.mark.anyio
async def test_maps_client_raises_on_timeout() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timeout", request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = TicketmasterMapsClient(http_client=http_client)
        with pytest.raises(TicketmasterMapsProviderError):
            await client.get_place_detail("3B00633EA89923F8")
