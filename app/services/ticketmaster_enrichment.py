from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.providers.ticketmaster_discovery import (
    TicketmasterDiscoveryEvent,
    TicketmasterDiscoveryService,
)
from app.providers.ticketmaster_maps import (
    TicketmasterMapsProviderError,
    TicketmasterMapsService,
    TicketmasterPlaceDetailSummary,
    normalize_legacy_event_id,
)

MAX_ENRICHMENT_SAMPLE_LIMIT = 100


class TicketmasterEnrichedEventMapSummary(BaseModel):
    event: TicketmasterDiscoveryEvent
    place_detail: TicketmasterPlaceDetailSummary | None = None
    enrichment_status: Literal["enriched", "place_detail_unavailable", "skipped"]
    errors: list[str] = Field(default_factory=list)


class TicketmasterEnrichmentService:
    def __init__(
        self,
        discovery_service: TicketmasterDiscoveryService | None = None,
        maps_service: TicketmasterMapsService | None = None,
    ) -> None:
        self.discovery_service = discovery_service or TicketmasterDiscoveryService()
        self.maps_service = maps_service or TicketmasterMapsService()

    async def enrich_event_by_legacy_id(
        self,
        legacy_event_id: str,
    ) -> TicketmasterPlaceDetailSummary:
        return await self.maps_service.fetch_place_detail_summary(
            normalize_legacy_event_id(legacy_event_id)
        )

    async def enrich_discovery_feed_sample(
        self,
        country_code: str = "US",
        limit: int = 10,
    ) -> list[TicketmasterEnrichedEventMapSummary]:
        if limit < 1:
            raise ValueError("limit must be at least 1.")
        if limit > MAX_ENRICHMENT_SAMPLE_LIMIT:
            raise ValueError(f"limit must be <= {MAX_ENRICHMENT_SAMPLE_LIMIT}.")

        feed = await self.discovery_service.fetch_events_json(country_code)
        enriched: list[TicketmasterEnrichedEventMapSummary] = []
        for event in feed.events[:limit]:
            try:
                place_detail = await self.maps_service.fetch_place_detail_summary(
                    event.legacy_event_id
                )
            except TicketmasterMapsProviderError as error:
                enriched.append(
                    TicketmasterEnrichedEventMapSummary(
                        event=event,
                        place_detail=None,
                        enrichment_status="place_detail_unavailable",
                        errors=[str(error)],
                    )
                )
                continue
            enriched.append(
                TicketmasterEnrichedEventMapSummary(
                    event=event,
                    place_detail=place_detail,
                    enrichment_status="enriched",
                )
            )
        return enriched
