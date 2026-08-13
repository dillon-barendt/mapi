from __future__ import annotations

from typing import Any, Protocol

from mapi.core.config import Settings, get_settings

from .client import GametimeClient
from .exceptions import GametimeProviderError
from .schemas import GametimeEventGridRow, GametimeListingSummary


class GametimeFeedClient(Protocol):
    """Structural client contract so tests can inject fakes without inheritance."""

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
    ) -> list[dict[str, Any]]: ...

    async def get_event_listings(
        self,
        event_id: str,
        *,
        quantity: int | None = None,
        all_in_pricing: bool | None = None,
        jitter_cheapest: int | None = None,
    ) -> dict[str, Any]: ...


def _first(record: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return None


def _as_str(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)


def _as_float(value: Any) -> float | None:
    try:
        return float(value) if value not in (None, "", True, False) else None
    except (TypeError, ValueError):
        return None


def _nested_dict(record: dict[str, Any], key: str) -> dict[str, Any]:
    value = record.get(key)
    return value if isinstance(value, dict) else {}


def _performer_name(record: dict[str, Any], event: dict[str, Any]) -> str | None:
    for source in (record, event):
        performers = source.get("performers")
        if isinstance(performers, list):
            for performer in performers:
                if isinstance(performer, dict):
                    name = _as_str(_first(performer, "name", "short_name"))
                    if name:
                        return name
    return None


def grid_row_from_event_record(record: dict[str, Any]) -> GametimeEventGridRow:
    """Flatten one Gametime event record into the minimal DataGrid row."""

    event = _nested_dict(record, "event") or record
    venue = _nested_dict(record, "venue") or _nested_dict(event, "venue")

    event_id = str(_first(event, "id", "event_id") or "").strip()
    if not event_id:
        raise GametimeProviderError("Gametime event record is missing an id.")

    return GametimeEventGridRow(
        event_id=event_id,
        event_name=_as_str(_first(event, "name", "event_name")),
        event_datetime_local=_as_str(
            _first(event, "datetime_local", "datetimeLocal", "local_datetime")
        ),
        event_datetime_utc=_as_str(_first(event, "datetime_utc", "datetimeUtc")),
        category_group=_as_str(_first(event, "category_group", "categoryGroup")),
        category=_as_str(_first(event, "category")),
        performer_name=_performer_name(record, event),
        venue_id=_as_str(_first(venue, "id", "venue_id")),
        venue_name=_as_str(_first(venue, "name", "venue_name")),
        venue_city=_as_str(_first(venue, "city")),
        venue_state=_as_str(_first(venue, "state", "state_code")),
    )


def grid_rows_from_event_records(
    records: list[dict[str, Any]],
) -> tuple[list[GametimeEventGridRow], int]:
    """Flatten records, returning parsed rows and the count of skipped records."""

    rows: list[GametimeEventGridRow] = []
    skipped = 0
    for record in records:
        try:
            rows.append(grid_row_from_event_record(record))
        except GametimeProviderError:
            skipped += 1
    return rows, skipped


def _listing_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for container in (payload, _nested_dict(payload, "data")):
        listings = container.get("listings")
        if isinstance(listings, list):
            return [item for item in listings if isinstance(item, dict)]
    return []


def _listing_price(listing: dict[str, Any]) -> float | None:
    price = _first(listing, "price", "total_price", "price_total")
    if isinstance(price, dict):
        price = _first(price, "total", "amount", "value")
    return _as_float(price)


def summarize_listings_payload(payload: dict[str, Any]) -> GametimeListingSummary:
    """Reduce a listings payload to the aggregate the DataGrid needs."""

    listings = _listing_records(payload)
    prices = [
        price
        for price in (_listing_price(listing) for listing in listings)
        if price is not None
    ]
    return GametimeListingSummary(
        listing_count=len(listings),
        min_price=min(prices) if prices else None,
        max_price=max(prices) if prices else None,
    )


class GametimeService:
    """Fetch and flatten Gametime data into DataGrid-ready rows."""

    def __init__(
        self,
        client: GametimeFeedClient | None = None,
        settings: Settings | None = None,
    ) -> None:
        self.client: GametimeFeedClient = client or GametimeClient()
        self.settings = settings or get_settings()

    async def fetch_all_event_records(
        self,
        *,
        category_group: str | None = None,
        category: str | None = None,
        q: str | None = None,
        performer_id: str | None = None,
        venue_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Page through /v1/events until a short page signals the end."""

        per_page = self.settings.gametime_events_per_page
        records: list[dict[str, Any]] = []
        for page in range(1, self.settings.gametime_max_event_pages + 1):
            batch = await self.client.get_events(
                page=page,
                per_page=per_page,
                category_group=category_group,
                category=category,
                q=q,
                performer_id=performer_id,
                venue_id=venue_id,
            )
            records.extend(batch)
            if len(batch) < per_page:
                break
        return records

    async def fetch_event_grid_rows(
        self,
        *,
        category_group: str | None = None,
        category: str | None = None,
        q: str | None = None,
        performer_id: str | None = None,
        venue_id: str | None = None,
    ) -> tuple[list[GametimeEventGridRow], int]:
        records = await self.fetch_all_event_records(
            category_group=category_group,
            category=category,
            q=q,
            performer_id=performer_id,
            venue_id=venue_id,
        )
        return grid_rows_from_event_records(records)

    async def fetch_listing_summary(self, event_id: str) -> GametimeListingSummary:
        payload = await self.client.get_event_listings(event_id)
        return summarize_listings_payload(payload)
