from mapi.core.config import settings
from mapi.events.repository import EventRepository
from mapi.providers.ticketmaster_discovery import TicketmasterDiscoveryService
from mapi.providers.ticketmaster_maps import TicketmasterMapsService
from mapi.services.gametime_enrichment import GametimeEnrichmentService
from mapi.services.ticketmaster_enrichment import TicketmasterEnrichmentService

_event_repository: EventRepository | None = None


def get_ticketmaster_discovery_service() -> TicketmasterDiscoveryService:
    return TicketmasterDiscoveryService()


def get_ticketmaster_maps_service() -> TicketmasterMapsService:
    return TicketmasterMapsService()


def get_ticketmaster_enrichment_service() -> TicketmasterEnrichmentService:
    return TicketmasterEnrichmentService()


def get_gametime_enrichment_service() -> GametimeEnrichmentService:
    return GametimeEnrichmentService()


def get_event_repository(path: str | None = None) -> EventRepository:
    global _event_repository
    if path is not None:
        return EventRepository(path)
    if _event_repository is None:
        _event_repository = EventRepository(settings.events_db_path)
    return _event_repository
