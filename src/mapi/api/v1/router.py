from enum import Enum

from fastapi import APIRouter

from ...core.config import settings
from .endpoints.events import router as events_router
from .endpoints.gametime_enrichment import router as gametime_enrichment_router
from .endpoints.progression import router as progression_router
from .endpoints.ticketmaster_discovery import router as ticketmaster_discovery_router
from .endpoints.ticketmaster_enrichment import router as ticketmaster_enrichment_router
from .endpoints.ticketmaster_maps import router as ticketmaster_maps_router

api_v1_router = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},
)

venue_dsl_tags: list[str | Enum] = [settings.venue_dsl_tag]
ticketmaster_discovery_tags: list[str | Enum] = [settings.ticketmaster_discovery_tag]
ticketmaster_maps_tags: list[str | Enum] = [settings.ticketmaster_maps_tag]
ticketmaster_enrichment_tags: list[str | Enum] = [settings.ticketmaster_enrichment_tag]
gametime_enrichment_tags: list[str | Enum] = [settings.gametime_enrichment_tag]

api_v1_router.include_router(
    events_router,
    prefix="/events",
    tags=["Events"],
)
api_v1_router.include_router(
    progression_router,
    prefix="/dsl",
    tags=venue_dsl_tags,
)
# Legacy aliases remain available while clients migrate to the compact surface.
api_v1_router.include_router(
    progression_router,
    prefix="/row-progression",
    tags=venue_dsl_tags,
)
api_v1_router.include_router(
    ticketmaster_discovery_router,
    prefix="/TM",
    tags=ticketmaster_discovery_tags,
)
api_v1_router.include_router(
    ticketmaster_maps_router,
    prefix="/TM/maps",
    tags=ticketmaster_maps_tags,
)
api_v1_router.include_router(
    ticketmaster_enrichment_router,
    prefix="/TM/enrichment",
    tags=ticketmaster_enrichment_tags,
)
api_v1_router.include_router(
    gametime_enrichment_router,
    prefix="/GT",
    tags=gametime_enrichment_tags,
)

# Legacy provider aliases remain available during migration.
api_v1_router.include_router(
    ticketmaster_discovery_router,
    prefix="/ticketmaster-discovery",
    tags=ticketmaster_discovery_tags,
)
api_v1_router.include_router(
    ticketmaster_maps_router,
    prefix="/ticketmaster-maps",
    tags=ticketmaster_maps_tags,
)
api_v1_router.include_router(
    ticketmaster_enrichment_router,
    prefix="/ticketmaster-enrichment",
    tags=ticketmaster_enrichment_tags,
)
api_v1_router.include_router(
    gametime_enrichment_router,
    prefix="/gametime-enrichment",
    tags=gametime_enrichment_tags,
)
