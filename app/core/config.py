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
    app_name: str = "Row‑Progression Suite"
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
        ]
    )
    CORS_ALLOW_CREDENTIALS: bool = True

    @property
    def fastapi_kwargs(self, **kwargs):
        return {
            "title": self.app_name,
            "description":  description,
            "docs_url": "/v1/docs",
            "redoc_url": "/v1/redoc",
            "openapi_url": "/v1/openapi.json",
            "support_email": self.USERNAME,
            "support_url": lambda x: f"mailto:{self.USERNAME}",
            "prefix": "/v1",
            "servers": [
                {
                    "url": "https://connect.ticket-vision.com",
                    "description": "Production Server",
                },
                {
                    "url": "http://localhost:8000",
                    "description": "Development Server",
                },
            ],
            **kwargs,
        }

@lru_cache()
def get_settings() -> Settings:
    """Get the application settings instance."""
    return Settings()



#Global settings instance
settings = get_settings()
