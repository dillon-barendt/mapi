from functools import lru_cache
from typing import Any, Dict

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import (
    APP_DESCRIPTION,
    APP_DEFAULT_CORS_METHODS,
    VENUE_TAG_DESCRIPTION,
    API_VERSION,
    API_PREFIX,
    APP_NAME,
    DEBUG_DEFAULT,
    SUPPORT_EMAIL,
    CORS_DEFAULT_ORIGINS,
    CORS_ALLOW_CREDENTIALS,
    DOCS_REDIRECT_URL,
    DOCS_URL,
    REDOC_URL,
    OPENAPI_URL,
    API_PREFIX,
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
    description: str = APP_DESCRIPTION
    debug: bool = DEBUG_DEFAULT
    version: str = API_VERSION
    api_prefix: str = API_PREFIX
    support_email: str = Field(
        default=SUPPORT_EMAIL,
        description="Primary contact e-mail address for support",
    )

    cors_origins: list[AnyHttpUrl] = Field(
        default=CORS_DEFAULT_ORIGINS,
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = CORS_ALLOW_CREDENTIALS
    cors_allow_methods: list[str] = Field(
        default_factory=lambda: APP_DEFAULT_CORS_METHODS.copy(),
        description="Allowed CORS HTTP methods",
    )

    ROW_PROGRESSION_TAG: str = "Row Progression"

    @property
    def build_fastapi_kwargs(self, **extra_kwargs: Any) -> Dict[str, Any]:
        base_kwargs: Dict[str, Any] = {
            "title": self.app_name,
            "description": self.description,
            "version": self.version,
            "debug": self.debug,
            "docs_redirect_url": DOCS_REDIRECT_URL,
            "docs_url": DOCS_URL,
            "redoc_url": REDOC_URL,
            "openapi_url": OPENAPI_URL,
            "support_email": self.support_email,
            "support_url": lambda _: f"mailto:{self.support_email}",
            "prefix": API_PREFIX,
        }
        base_kwargs.update(extra_kwargs)
        return base_kwargs

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return self.build_fastapi_kwargs


@lru_cache()
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""
    return Settings()


# GLOBAL SETTINGS
settings = get_settings()
