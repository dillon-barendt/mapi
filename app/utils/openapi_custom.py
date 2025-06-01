from typing import Any
from fastapi.applications import FastAPI
from fastapi.openapi.utils import get_openapi
from app.core.constants import (
    VENUE_TAG_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    API_DESCRIPTION,
)


def update_venue_tag_description(openapi_schema: dict) -> None:
    """
    Updates the 'Venue' tag in an OpenAPI schema with a custom description.

    :param openapi_schema: The OpenAPI schema dictionary to modify.
    """
    for tag in openapi_schema.get("tags", []):
        if tag.get("name") == "Venue":
            tag["description"] = VENUE_TAG_DESCRIPTION


def generate_custom_openapi_schema(fastapi_app: FastAPI) -> dict[str, Any]:
    """
    Generates a customized OpenAPI schema for the FastAPI application
    and enhances it with additional descriptions.

    :param fastapi_app: The FastAPI application instance.
    :return: A customized OpenAPI schema dictionary.
    """
    custom_schema: dict[str, Any] = get_openapi(
        title=API_TITLE,
        version=API_VERSION,
        description=API_DESCRIPTION,
        routes=fastapi_app.routes,
    )
    update_venue_tag_description(
        custom_schema
    )  # Update the schema with the "Venue" tag description
    return custom_schema


def custom_openapi(fastapi_app: FastAPI) -> dict[str, Any] | None:
    """
    Retrieves or generates a custom OpenAPI schema for the FastAPI application.
    If the OpenAPI schema has already been generated and cached in the app's state,
    it returns the cached version. Otherwise, it generates a new schema, caches it, and returns it.

    :param fastapi_app: The FastAPI application instance.
    :return: A dictionary representing the OpenAPI schema of the specified app, or None if not applicable.
    """
    if (
        hasattr(fastapi_app.state, "openapi_schema")
        and fastapi_app.state.openapi_schema is not None
    ):
        return fastapi_app.state.openapi_schema  # Return cached schema
    custom_schema = generate_custom_openapi_schema(fastapi_app)  # Generate schema
    fastapi_app.state.openapi_schema = custom_schema  # Cache the generated schema
    return custom_schema
