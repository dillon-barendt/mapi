from functools import lru_cache
from typing import Any

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    API_DESCRIPTION,
    API_VERSION,
    APP_NAME,
    CORS_ALLOW_CREDENTIALS,
    CORS_ALLOW_METHODS,
    CORS_DEFAULT_ORIGINS,
    DEBUG_DEFAULT,
    DOCS_URL,
    OPENAPI_URL,
    REDOC_URL,
    SUPPORT_EMAIL,
)


class Settings(BaseSettings):
    """Application settings configuration."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
        populate_by_name=True,
    )

    app_name: str = APP_NAME
    description: str = API_DESCRIPTION
    debug: bool = DEBUG_DEFAULT
    version: str = API_VERSION
    support_email: str = Field(
        default=SUPPORT_EMAIL,
        description="Public support email for generated OpenAPI contact metadata.",
    )
    cors_origins: list[str] = Field(
        default=CORS_DEFAULT_ORIGINS,
        description="Allowed CORS origins.",
    )
    cors_allow_credentials: bool = CORS_ALLOW_CREDENTIALS
    cors_allow_methods: list[str] = Field(
        default_factory=lambda: CORS_ALLOW_METHODS.copy(),
        description="Allowed CORS HTTP methods.",
    )
    venue_dsl_tag: str = "Venue DSL"
    row_progression_tag: str = "Venue DSL"
    ticketmaster_discovery_tag: str = "Ticketmaster Discovery"
    ticketmaster_maps_tag: str = "Ticketmaster Maps"
    ticketmaster_enrichment_tag: str = "Ticketmaster Enrichment"
    gametime_enrichment_tag: str = "Gametime Enrichment"
    events_db_path: str = "data/events.db"

    ticketmaster_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "TICKETMASTER_API_KEY",
            "APP_TICKETMASTER_API_KEY",
        ),
        description="Ticketmaster Discovery Feed API key. Never commit this value.",
    )
    ticketmaster_discovery_base_url: str = (
        "https://app.ticketmaster.com/discovery-feed/v2"
    )
    ticketmaster_discovery_default_country_code: str = "US"
    ticketmaster_discovery_timeout_seconds: float = 30.0
    ticketmaster_discovery_enabled: bool = True

    ticketmaster_maps_base_url: str = "https://mapsapi.tmol.io"
    ticketmaster_maps_geometry_version: int = 3
    ticketmaster_maps_system_id: str = "HOST"
    ticketmaster_maps_referer: str = "https://cims.ticketmaster.com/"
    ticketmaster_maps_user_agent: str | None = None
    ticketmaster_maps_timeout_seconds: float = 15.0
    ticketmaster_maps_enabled: bool = True

    gametime_base_url: str = "https://mobile.gametime.co"
    gametime_timeout_seconds: float = 30.0
    gametime_enabled: bool = True
    gametime_events_per_page: int = Field(
        default=10_000,
        description=(
            "Events fetched per /v1/events page. The published spec caps per_page "
            "at 6000, but the API accepts up to 10000 items per request."
        ),
    )
    gametime_max_event_pages: int = Field(
        default=10,
        description="Safety cap on event pagination during enrichment jobs.",
    )
    gametime_listings_default_quantity: int = 2
    gametime_listings_all_in_pricing: bool = True
    gametime_listings_jitter_cheapest: int = 0

    @property
    def build_fastapi_kwargs(self) -> dict[str, Any]:
        return {
            "title": self.app_name,
            "description": self.description,
            "version": self.version,
            "debug": self.debug,
            "docs_url": DOCS_URL,
            "redoc_url": REDOC_URL,
            "openapi_url": OPENAPI_URL,
            "openapi_tags": [
                {
                    "name": self.venue_dsl_tag,
                    "description": (
                        "Map venue selections to row attributes using the compact "
                        "venue DSL."
                    ),
                },
                {"name": self.ticketmaster_discovery_tag},
                {"name": self.ticketmaster_maps_tag},
                {"name": self.ticketmaster_enrichment_tag},
                {"name": self.gametime_enrichment_tag},
                {"name": "Events"},
            ],
            "contact": {"name": "Mapi maintainers", "email": self.support_email},
        }


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""

    return Settings()


settings = get_settings()
