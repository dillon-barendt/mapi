from typing import Any, cast

from fastapi.applications import FastAPI
from fastapi.openapi.utils import get_openapi

from app.core.constants import (
    API_DESCRIPTION,
    API_TITLE,
    API_VERSION,
    ROW_PROGRESSION_TAG_DESCRIPTION,
)


def update_row_progression_tag(openapi_schema: dict[str, Any]) -> None:
    for tag in openapi_schema.get("tags", []):
        if tag.get("name") == "Row Progression":
            tag["description"] = ROW_PROGRESSION_TAG_DESCRIPTION


def generate_custom_openapi_schema(fastapi_app: FastAPI) -> dict[str, Any]:
    custom_schema = get_openapi(
        title=API_TITLE,
        version=API_VERSION,
        description=API_DESCRIPTION,
        routes=fastapi_app.routes,
    )
    update_row_progression_tag(custom_schema)
    return custom_schema


def custom_openapi(fastapi_app: FastAPI) -> dict[str, Any]:
    if (
        hasattr(fastapi_app.state, "openapi_schema")
        and fastapi_app.state.openapi_schema is not None
    ):
        return cast("dict[str, Any]", fastapi_app.state.openapi_schema)

    custom_schema = generate_custom_openapi_schema(fastapi_app)
    fastapi_app.state.openapi_schema = custom_schema
    return custom_schema
