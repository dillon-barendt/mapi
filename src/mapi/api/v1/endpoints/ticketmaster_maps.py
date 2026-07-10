from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from mapi.api.deps import get_ticketmaster_maps_service
from mapi.providers.ticketmaster_maps import (
    TicketmasterMapsProviderError,
    TicketmasterMapsService,
    TicketmasterPlaceDetailSummary,
)

router = APIRouter()


@router.get(
    "/events/{legacy_event_id}/place-detail",
    response_model=TicketmasterPlaceDetailSummary,
    summary="Fetch Ticketmaster Maps place-detail summary",
)
async def get_place_detail(
    legacy_event_id: str,
    service: Annotated[TicketmasterMapsService, Depends(get_ticketmaster_maps_service)],
) -> TicketmasterPlaceDetailSummary:
    try:
        return await service.fetch_place_detail_summary(legacy_event_id)
    except TicketmasterMapsProviderError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(error),
        ) from error
