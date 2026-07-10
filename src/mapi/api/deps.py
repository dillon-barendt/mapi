from mapi.providers.ticketmaster_discovery import TicketmasterDiscoveryService
from mapi.providers.ticketmaster_maps import TicketmasterMapsService
from mapi.services.ticketmaster_enrichment import TicketmasterEnrichmentService


def get_ticketmaster_discovery_service() -> TicketmasterDiscoveryService:
    return TicketmasterDiscoveryService()


def get_ticketmaster_maps_service() -> TicketmasterMapsService:
    return TicketmasterMapsService()


def get_ticketmaster_enrichment_service() -> TicketmasterEnrichmentService:
    return TicketmasterEnrichmentService()
