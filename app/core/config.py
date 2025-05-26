from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

description = """### What is this API?  
A toolkit for **parsing**, **generating**, and **diffing** row‑progression codes  
used in ticket‑marketplace seat maps.

* 🔍 Parse single codes or entire venues  
* 🆚 Diff partner updates before they break prod  
* 🛠️ Generate DSL strings from raw rows
"""

__author__ = "Dillon Barendt"


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        use_enum_values=True,
    )
    # Application settings
    app_name: str = "Mapi Suite"
    description: str = description
    debug: bool = True
    version: str = "1.0.0"
    USERNAME: str = "dillon.barendt@ticket-vision.com"


    CORS_ORIGINS: list[AnyHttpUrl] = Field(
        default=[
            "https://localhost:3000",
            "http://localhost:8000",
            "https://ticketvision.com",
            "http://0.0.0.0:8000",
            "https://connect.ticket-vision.com",
            "https://connect.ticket-vision.com:8000",
        ]
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    @property
    def fastapi_kwargs(self, **kwargs):
        return {
            "title": self.app_name,
            "description": description,
            "version": self.version,
            "debug": self.debug,
            "docs_redirect_url": None,
            "docs_url": "/v1/docs",
            "redoc_url": "/v1/redoc",
            "openapi_url": "/v1/openapi.json",
            "support_email": self.USERNAME,
            "support_url": lambda x: f"mailto:{self.USERNAME}",
            "prefix": "/v1",
            **kwargs,
        }

    ROW_PROGRESSION_TAG: str = Field(default="Row Progression", description="Tag for row progression related endpoints")


@lru_cache()
def get_settings() -> Settings:
    """Get the application settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
