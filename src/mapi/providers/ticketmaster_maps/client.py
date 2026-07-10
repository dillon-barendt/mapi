from __future__ import annotations

from typing import Any, cast

import httpx

from mapi.core.config import Settings, get_settings

from .exceptions import TicketmasterMapsProviderError
from .schemas import TicketmasterPlaceDetailRaw
from .service import normalize_legacy_event_id

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
)


class TicketmasterMapsClient:
    """Async HTTP client for Ticketmaster Maps place-detail payloads."""

    def __init__(
        self,
        settings: Settings | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._http_client = http_client

    async def get_place_detail(
        self,
        legacy_event_id: str,
    ) -> TicketmasterPlaceDetailRaw:
        normalized_id = normalize_legacy_event_id(legacy_event_id)
        response = await self._get(normalized_id)
        try:
            payload = response.json()
        except ValueError as error:
            raise TicketmasterMapsProviderError(
                "Ticketmaster Maps returned invalid JSON."
            ) from error
        if not isinstance(payload, dict) or not payload:
            raise TicketmasterMapsProviderError(
                "Ticketmaster Maps returned an empty or invalid payload."
            )
        return TicketmasterPlaceDetailRaw(
            legacy_event_id=normalized_id,
            payload=cast(dict[str, Any], payload),
        )

    def _build_url(self, legacy_event_id: str) -> str:
        base_url = self.settings.ticketmaster_maps_base_url.rstrip("/")
        version = self.settings.ticketmaster_maps_geometry_version
        return f"{base_url}/maps/geometry/{version}/event/{legacy_event_id}/placeDetail"

    def _headers(self) -> dict[str, str]:
        return {
            "Referer": self.settings.ticketmaster_maps_referer,
            "User-Agent": self.settings.ticketmaster_maps_user_agent
            or DEFAULT_USER_AGENT,
            "sec-ch-ua-platform": '"macOS"',
            "sec-ch-ua": (
                '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"'
            ),
            "sec-ch-ua-mobile": "?0",
        }

    async def _get(self, legacy_event_id: str) -> httpx.Response:
        if not self.settings.ticketmaster_maps_enabled:
            raise TicketmasterMapsProviderError("Ticketmaster Maps is disabled.")
        try:
            if self._http_client is not None:
                response = await self._http_client.get(
                    self._build_url(legacy_event_id),
                    params={"systemId": self.settings.ticketmaster_maps_system_id},
                    headers=self._headers(),
                    timeout=self.settings.ticketmaster_maps_timeout_seconds,
                )
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        self._build_url(legacy_event_id),
                        params={"systemId": self.settings.ticketmaster_maps_system_id},
                        headers=self._headers(),
                        timeout=self.settings.ticketmaster_maps_timeout_seconds,
                    )
        except httpx.TimeoutException as error:
            raise TicketmasterMapsProviderError(
                "Ticketmaster Maps request timed out."
            ) from error
        except httpx.HTTPError as error:
            raise TicketmasterMapsProviderError(
                "Ticketmaster Maps request failed."
            ) from error

        if response.status_code < 200 or response.status_code >= 300:
            raise TicketmasterMapsProviderError(
                f"Ticketmaster Maps returned HTTP {response.status_code}."
            )
        return response
