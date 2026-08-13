from __future__ import annotations

from typing import Any, cast

import httpx

from mapi.core.config import Settings, get_settings

from .exceptions import TicketmasterDiscoveryProviderError


class TicketmasterDiscoveryClient:
    """Async HTTP client for Ticketmaster Discovery Feed 2.0."""

    def __init__(
        self,
        settings: Settings | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._http_client = http_client

    async def get_events_json(self, country_code: str = "US") -> list[dict[str, Any]]:
        payload = await self._request_json(
            "/events.json",
            params={"countryCode": country_code.upper()},
        )
        events = payload if isinstance(payload, list) else payload.get("events")
        if not isinstance(events, list):
            raise TicketmasterDiscoveryProviderError(
                "Discovery JSON response did not contain an event list."
            )
        return [cast(dict[str, Any], item) for item in events if isinstance(item, dict)]

    async def get_events_csv(self, country_code: str = "US") -> str:
        return await self._request_text(
            "/events.csv",
            params={"countryCode": country_code.upper()},
        )

    async def get_feed_metadata(self) -> dict[str, Any]:
        payload = await self._request_json("/events", params={})
        if not isinstance(payload, dict) or not payload:
            raise TicketmasterDiscoveryProviderError(
                "Discovery metadata response was empty or invalid."
            )
        return payload

    def _build_url(self, path: str) -> str:
        return f"{self.settings.ticketmaster_discovery_base_url.rstrip('/')}{path}"

    def _params(self, params: dict[str, str]) -> dict[str, str]:
        if not self.settings.ticketmaster_discovery_enabled:
            raise TicketmasterDiscoveryProviderError(
                "Ticketmaster Discovery is disabled."
            )
        if not self.settings.ticketmaster_api_key:
            raise TicketmasterDiscoveryProviderError(
                "TICKETMASTER_API_KEY is required for Discovery Feed calls."
            )
        return {"apikey": self.settings.ticketmaster_api_key, **params}

    async def _request_json(
        self,
        path: str,
        *,
        params: dict[str, str],
    ) -> Any:
        response = await self._get(path, params=params)
        try:
            return response.json()
        except ValueError as error:
            raise TicketmasterDiscoveryProviderError(
                "Discovery provider returned invalid JSON."
            ) from error

    async def _request_text(
        self,
        path: str,
        *,
        params: dict[str, str],
    ) -> str:
        response = await self._get(path, params=params)
        if not response.text.strip():
            raise TicketmasterDiscoveryProviderError(
                "Discovery provider returned an empty payload."
            )
        return response.text

    async def _get(self, path: str, *, params: dict[str, str]) -> httpx.Response:
        try:
            if self._http_client is not None:
                response = await self._http_client.get(
                    self._build_url(path),
                    params=self._params(params),
                    timeout=self.settings.ticketmaster_discovery_timeout_seconds,
                    follow_redirects=True,
                )
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        self._build_url(path),
                        params=self._params(params),
                        timeout=self.settings.ticketmaster_discovery_timeout_seconds,
                        follow_redirects=True,
                    )
        except httpx.TimeoutException as error:
            raise TicketmasterDiscoveryProviderError(
                "Discovery provider request timed out."
            ) from error
        except httpx.HTTPError as error:
            raise TicketmasterDiscoveryProviderError(
                "Discovery provider request failed."
            ) from error

        if response.status_code < 200 or response.status_code >= 300:
            raise TicketmasterDiscoveryProviderError(
                f"Discovery provider returned HTTP {response.status_code}."
            )
        return response
