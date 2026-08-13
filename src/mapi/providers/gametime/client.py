from __future__ import annotations

from typing import Any, cast

import httpx

from mapi.core.config import Settings, get_settings

from .exceptions import GametimeProviderError


class GametimeClient:
    """Async HTTP client for the Gametime mobile API (https://mobile.gametime.co)."""

    def __init__(
        self,
        settings: Settings | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self._http_client = http_client

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
        params = {
            "page": str(page),
            "per_page": str(per_page or self.settings.gametime_events_per_page),
        }
        optional = {
            "category_group": category_group,
            "category": category,
            "q": q,
            "performer_id": performer_id,
            "venue_id": venue_id,
        }
        params.update({key: value for key, value in optional.items() if value})

        payload = await self._request_json("/v1/events", params=params)
        events = payload if isinstance(payload, list) else payload.get("events")
        if not isinstance(events, list):
            raise GametimeProviderError(
                "Gametime events response did not contain an event list."
            )
        return [cast(dict[str, Any], item) for item in events if isinstance(item, dict)]

    async def get_event_listings(
        self,
        event_id: str,
        *,
        quantity: int | None = None,
        all_in_pricing: bool | None = None,
        jitter_cheapest: int | None = None,
    ) -> dict[str, Any]:
        if not event_id.strip():
            raise GametimeProviderError("Gametime event id cannot be empty.")

        resolved_pricing = (
            all_in_pricing
            if all_in_pricing is not None
            else self.settings.gametime_listings_all_in_pricing
        )
        resolved_jitter = (
            jitter_cheapest
            if jitter_cheapest is not None
            else self.settings.gametime_listings_jitter_cheapest
        )
        params = {
            "all_in_pricing": "true" if resolved_pricing else "false",
            "quantity": str(
                quantity or self.settings.gametime_listings_default_quantity
            ),
            "jitter_cheapest": str(resolved_jitter),
        }

        payload = await self._request_json(f"/v2/listings/{event_id}", params=params)
        if not isinstance(payload, dict):
            raise GametimeProviderError(
                "Gametime listings response was not a JSON object."
            )
        return cast(dict[str, Any], payload)

    def _build_url(self, path: str) -> str:
        return f"{self.settings.gametime_base_url.rstrip('/')}{path}"

    def _params(self, params: dict[str, str]) -> dict[str, str]:
        if not self.settings.gametime_enabled:
            raise GametimeProviderError("Gametime provider is disabled.")
        return params

    async def _request_json(self, path: str, *, params: dict[str, str]) -> Any:
        response = await self._get(path, params=params)
        try:
            return response.json()
        except ValueError as error:
            raise GametimeProviderError(
                "Gametime provider returned invalid JSON."
            ) from error

    async def _get(self, path: str, *, params: dict[str, str]) -> httpx.Response:
        try:
            if self._http_client is not None:
                response = await self._http_client.get(
                    self._build_url(path),
                    params=self._params(params),
                    timeout=self.settings.gametime_timeout_seconds,
                )
            else:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        self._build_url(path),
                        params=self._params(params),
                        timeout=self.settings.gametime_timeout_seconds,
                    )
        except httpx.TimeoutException as error:
            raise GametimeProviderError(
                "Gametime provider request timed out."
            ) from error
        except httpx.HTTPError as error:
            raise GametimeProviderError("Gametime provider request failed.") from error

        if response.status_code < 200 or response.status_code >= 300:
            raise GametimeProviderError(
                f"Gametime provider returned HTTP {response.status_code}."
            )
        return response
