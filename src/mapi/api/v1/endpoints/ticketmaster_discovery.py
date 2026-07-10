from __future__ import annotations

from typing import Annotated, Literal, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status

from mapi.api.deps import get_ticketmaster_discovery_service
from mapi.providers.ticketmaster_discovery import (
    TicketmasterDiscoveryFeedSummary,
    TicketmasterDiscoveryProviderError,
    TicketmasterDiscoveryService,
    TicketmasterLegacyIdsResponse,
    extract_legacy_event_ids,
)

router = APIRouter()


def _provider_error(error: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=str(error),
    )


def _limit_summary(
    summary: TicketmasterDiscoveryFeedSummary,
    limit: int,
) -> TicketmasterDiscoveryFeedSummary:
    events = summary.events[:limit]
    return TicketmasterDiscoveryFeedSummary(
        country_code=summary.country_code,
        format=summary.format,
        event_count=len(events),
        legacy_event_ids=extract_legacy_event_ids(events),
        events=events,
    )


@router.get(
    "/events",
    response_model=TicketmasterDiscoveryFeedSummary,
    summary="Fetch Ticketmaster Discovery Feed events",
)
async def get_events(
    service: Annotated[
        TicketmasterDiscoveryService,
        Depends(get_ticketmaster_discovery_service),
    ],
    country_code: Annotated[str, Query(min_length=2, max_length=2)] = "US",
    format: Literal["json", "csv"] = "json",
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> TicketmasterDiscoveryFeedSummary:
    try:
        summary = (
            await service.fetch_events_json(country_code)
            if format == "json"
            else await service.fetch_events_csv(country_code)
        )
    except TicketmasterDiscoveryProviderError as error:
        raise _provider_error(error) from error
    return _limit_summary(summary, limit)


@router.get(
    "/events/legacy-ids",
    response_model=TicketmasterLegacyIdsResponse,
    summary="Fetch Ticketmaster legacy event IDs",
)
async def get_legacy_event_ids(
    service: Annotated[
        TicketmasterDiscoveryService,
        Depends(get_ticketmaster_discovery_service),
    ],
    country_code: Annotated[str, Query(min_length=2, max_length=2)] = "US",
    format: Literal["json", "csv"] = "json",
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
) -> TicketmasterLegacyIdsResponse:
    summary = await get_events(service, country_code, format, limit)
    return TicketmasterLegacyIdsResponse(
        country_code=summary.country_code,
        format=summary.format,
        legacy_event_ids=summary.legacy_event_ids,
    )


@router.get(
    "/metadata",
    response_model=dict[str, object],
    summary="Fetch Ticketmaster Discovery Feed metadata",
)
async def get_metadata(
    service: Annotated[
        TicketmasterDiscoveryService,
        Depends(get_ticketmaster_discovery_service),
    ],
) -> dict[str, object]:
    try:
        return cast("dict[str, object]", await service.fetch_feed_metadata())
    except TicketmasterDiscoveryProviderError as error:
        raise _provider_error(error) from error
