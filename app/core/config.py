from functools import lru_cache
from typing import Any

from pydantic import Field
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
    row_progression_tag: str = "Row Progression"

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
            "contact": {"name": "Mapi maintainers", "email": self.support_email},
        }


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""

    return Settings()


settings = get_settings()
