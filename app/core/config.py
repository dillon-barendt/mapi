from functools import lru_cache
from typing import Any, Dict

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import APP_DESCRIPTION, APP_DEFAULT_CORS_METHODS

__author__ = "Dillon Barendt"

# Extracted constant ----------------------------------------------------------


class Settings(BaseSettings):
    """Application configuration settings."""

    # Environment / model configuration ---------------------------------------
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
    )

    # Application metadata -----------------------------------------------------
    app_name: str = "Mapi Suite"
    description: str = APP_DESCRIPTION
    debug: bool = True
    version: str = "1.0.0"
    support_email: str = Field(
        default="dillon.barendt@ticket-vision.com",
        description="Primary contact e-mail address for support",
    )

    # CORS configuration -------------------------------------------------------
    cors_origins: list[AnyHttpUrl] = Field(
        default=[
            "https://localhost:3000",
            "http://localhost:8000",
            "https://ticketvision.com",
            "http://0.0.0.0:8000",
            "https://connect.ticket-vision.com",
            "https://connect.ticket-vision.com:8000",
        ],
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = Field(
        default_factory=lambda: APP_DEFAULT_CORS_METHODS.copy(),
        description="Allowed CORS HTTP methods",
    )

    # API tags -----------------------------------------------------------------
    ROW_PROGRESSION_TAG: str = Field(
        default="Row Progression",
        description="Tag for row progression related endpoints",
    )

    # FastAPI kwargs builder ---------------------------------------------------
    def build_fastapi_kwargs(self, **extra_kwargs: Any) -> Dict[str, Any]:
        """
        Construct the kwargs dict to initialise FastAPI.

        Extra keyword arguments override the defaults.
        """
        base_kwargs: Dict[str, Any] = {
            "title": self.app_name,
            "description": self.description,
            "version": self.version,
            "debug": self.debug,
            "docs_redirect_url": None,
            "docs_url": "/v1/docs",
            "redoc_url": "/v1/redoc",
            "openapi_url": "/v1/openapi.json",
            "support_email": self.support_email,
            "support_url": lambda _: f"mailto:{self.support_email}",
            "prefix": "/v1",
        }
        base_kwargs.update(extra_kwargs)
        return base_kwargs


@lru_cache()
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""
    return Settings()


# Global settings instance ----------------------------------------------------
settings = get_settings()