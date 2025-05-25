from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.v1.router import API_V1_ROUTER
from .core.config import settings

app = FastAPI(**settings.fastapi_kwargs)
app.include_router(API_V1_ROUTER)


def add_venue_tag_description(openapi_schema: dict) -> None:
    """
    Enhances the OpenAPI schema by adding a custom description
    to the "Venue" tag if it exists.
    :param openapi_schema: The OpenAPI schema dictionary to modify.
    """
    for tag in openapi_schema.get("tags", []):
        if tag["name"] == "Venue":
            tag["description"] = VENUE_TAG_DESCRIPTION


def custom_openapi():
    """
    Returns the OpenAPI schema for the application if it is not already set,
    otherwise retrieves it from the application's state. Customizes
    the schema by adding detailed descriptions for specific API tags.
    :rtype: dict
    :return: The OpenAPI schema for the application.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema: dict[str, Any] = get_openapi(
        title="Row‑Progression Suite",
        version="1.0.0",
        description="""
### What is this API?  
A toolkit for **parsing**, **generating**, and **diffing** row‑progression codes  
used in ticket‑marketplace seat maps.
* 🔍 Parse single codes or entire venues  
* 🆚 Diff partner updates before they break prod  
* 🛠️ Generate DSL strings from raw rows
        """,
        routes=app.routes,
    )

    # Add custom description to the "Venue" tag
    add_venue_tag_description(openapi_schema)

    app.openapi_schema = openapi_schema
    return openapi_schema
app.openapi = custom_openapi





@app.get("/")
async def root():
    """
    Handles HTTP GET requests to the root endpoint.

    This is an asynchronous function that responds to GET requests targeting
    the root path `/`. It returns a JSON object containing a welcome message.

    :returns: A dictionary object with a greeting message.
    :rtype: dict
    """
    return {"message": "Hello World"}

VENUE_TAG_DESCRIPTION = (
    "Endpoints that build, diff, or compress entire venues.  \n"
    "Think of these as bulk counterparts to the `/parse` endpoint."
)











