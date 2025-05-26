from typing import Any
from fastapi.applications import FastAPI
from fastapi.openapi.utils import get_openapi
from app.core.constants import VENUE_TAG_DESCRIPTION

def add_venue_tag_description(openapi_schema: dict) -> None:
    """
    Adds a custom description to the "Venue" tag in an OpenAPI schema, if the tag is present.
    
    :param openapi_schema: The OpenAPI schema dictionary to modify.
    """
    for tag in openapi_schema.get("tags", []):
        if tag["name"] == "Venue":
            tag["description"] = VENUE_TAG_DESCRIPTION

def generate_custom_openapi_schema(app: FastAPI) -> dict[str, Any]:
    """
    Generates a customized OpenAPI schema for the FastAPI application
    and enhances it with additional descriptions.
    
    :param app: The FastAPI application instance.
    :return: A customized OpenAPI schema dictionary.
    """
    schema: dict[str, Any] = get_openapi(
        title="Row‑Progression Suite",
        version="1.0.0",
        description="""
### What is this API?
A toolkit for **parsing**, **generating**, and **diffing** row‑progression codes
used in ticket‑marketplace seat maps.
- 🔍 Parse single codes or entire venues
- 🆚 Diff partner updates before they break prod
- 🛠️ Generate DSL strings from raw rows
        """,
        routes=app.routes,
    )
    add_venue_tag_description(schema)  # Update the schema with the "Venue" tag description
    return schema

def custom_openapi(app: FastAPI) -> dict[str, Any] | None:
    """
    Generates and retrieves a custom OpenAPI schema for the given FastAPI application.
    If the OpenAPI schema has already been generated and cached in the app's state, it
    returns the cached version. Otherwise, it generates a new schema, caches it in
    the app's state, and then returns the newly generated schema.

    :param app: The FastAPI application instance for which the custom OpenAPI schema
                is generated.
    :type app: FastAPI
    :return: A dictionary representing the OpenAPI schema of the specified app, or
             None if schema generation is not applicable.
    :rtype: dict[str, Any] | None
    """
    if hasattr(app.state, "openapi_schema") and app.state.openapi_schema is not None:
        return app.state.openapi_schema  # Return cached schema
    schema = generate_custom_openapi_schema(app)  # Generate schema
    app.state.openapi_schema = schema  # Cache schema for future use
    return schema