from __future__ import annotations

import re

APP_NAME: str = "Mapi"
DEBUG_DEFAULT: bool = False
SUPPORT_EMAIL: str = "opensource@example.com"

CORS_DEFAULT_ORIGINS: list[str] = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS: bool = True
CORS_ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

DOCS_URL: str = "/docs"
REDOC_URL: str = "/redoc"
OPENAPI_URL: str = "/openapi.json"

APP_HEALTH_MESSAGE: dict[str, str] = {"message": "Mapi API is healthy."}

API_TITLE = "Mapi"
API_VERSION = "0.1.0"
API_DESCRIPTION = """
Mapi is a FastAPI reference project for compact ticketing venue row maps.

It parses row progression strings such as `AA:DD,A:C,1:12,13=13W` into typed
row models, validates edge cases, compresses expanded rows, diffs compact venue
maps, and documents Redis indexing patterns for downstream review workflows.
"""

ROW_PROGRESSION_TAG_DESCRIPTION = (
    "Parse, compress, diff, and inspect compact section-row progression codes."
)
TM_LEGACY_EVENT_REGEX = re.compile(r"^[A-Z0-9]{6,40}$")
