from __future__ import annotations

from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status

from mapi.api.deps import get_ticketmaster_enrichment_service
from mapi.providers.ticketmaster_discovery import TicketmasterDiscoveryProviderError
from mapi.providers.ticketmaster_maps import (
    TicketmasterMapsProviderError,
    TicketmasterPlaceDetailSummary,
)
from mapi.services.ticketmaster_enrichment import (
    MAX_ENRICHMENT_SAMPLE_LIMIT,
    TicketmasterEnrichedEventMapSummary,
    TicketmasterEnrichmentService,
)

router = APIRouter()


def _provider_error(error: Exception) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=str(error),
    )


@router.get(
    "/events/{legacy_event_id}/map-summary",
    response_model=TicketmasterPlaceDetailSummary,
    summary="Enrich one Ticketmaster event with map metadata",
)
async def get_event_map_summary(
    legacy_event_id: str,
    service: Annotated[
        TicketmasterEnrichmentService,
        Depends(get_ticketmaster_enrichment_service),
    ],
) -> TicketmasterPlaceDetailSummary:
    try:
        return await service.enrich_event_by_legacy_id(legacy_event_id)
    except TicketmasterMapsProviderError as error:
        raise _provider_error(error) from error


@router.get(
    "/discovery-feed/sample-map-summaries",
    response_model=list[TicketmasterEnrichedEventMapSummary],
    summary="Enrich a limited Discovery Feed sample with map summaries",
)
async def get_sample_map_summaries(
    service: Annotated[
        TicketmasterEnrichmentService,
        Depends(get_ticketmaster_enrichment_service),
    ],
    country_code: Annotated[str, Query(min_length=2, max_length=2)] = "US",
    limit: Annotated[int, Query(ge=1, le=MAX_ENRICHMENT_SAMPLE_LIMIT)] = 10,
) -> list[TicketmasterEnrichedEventMapSummary]:
    try:
        return cast(
            "list[TicketmasterEnrichedEventMapSummary]",
            await service.enrich_discovery_feed_sample(country_code, limit),
        )
    except (TicketmasterDiscoveryProviderError, ValueError) as error:
        raise _provider_error(error) from error
