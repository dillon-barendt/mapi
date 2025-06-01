# File: app/core/constants.py

APP_NAME: str = "Mapi Suite"
DEBUG_DEFAULT: bool = True

SUPPORT_EMAIL: str = "dillon.barendt@ticket-vision.com"

CORS_DEFAULT_ORIGINS: list[str] = [
    "https://localhost:3000",
    "http://localhost:8000",
    "https://ticketvision.com",
    "http://0.0.0.0:8000",
    "https://connect.ticket-vision.com",
    "https://connect.ticket-vision.com:8000",
]
CORS_ALLOW_CREDENTIALS: bool = True

# FastAPI route / docs locations
DOCS_REDIRECT_URL: None | str = None
DOCS_URL: str = "/v1/docs"
REDOC_URL: str = "/v1/redoc"
OPENAPI_URL: str = "/v1/openapi.json"
API_PREFIX: str = "/v1"

APP_HEALTH_MESSAGE: dict[str, str] = {"message": "Were doing wonderful!"}


APP_DESCRIPTION = """### What is this API?  
A toolkit for **parsing**, **generating**, and **diffing** row‑progression codes  
used in ticket‑marketplace seat maps.

* 🔍 Parse single codes or entire venues  
* 🆚 Diff partner updates before they break prod  
* 🛠️ Generate DSL strings from raw rows
"""
APP_DEFAULT_CORS_METHODS: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]

# OpenAPI metadata constants
API_TITLE = "Row‑Progression Suite"
API_VERSION = "1.0.0"
API_DESCRIPTION = """
### What is this API?
A toolkit for **parsing**, **generating**, and **diffing** row‑progression codes
used in ticket‑marketplace seat maps.
- 🔍 Parse single codes or entire venues
- 🆚 Diff partner updates before they break prod
- 🛠️ Generate DSL strings from raw rows
"""

########################################################################################################################

VENUE_TAG_DESCRIPTION = (
    "Endpoints that build, diff, or compress entire venues.  \n"
    "Think of these as bulk counterparts to the `/parse` endpoint."
)
