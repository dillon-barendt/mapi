"""Application entry point for the Mapi FastAPI service."""

from typing import Any, cast

from fastapi import FastAPI, status
from fastapi.requests import Request

from mapi.core.openapi_custom import custom_openapi

from .api.v1.router import api_v1_router
from .core.config import settings
from .core.constants import APP_HEALTH_MESSAGE
from .core.middleware import ResponseTimeMiddleware
from .core.state import lifespan

app = FastAPI(**settings.build_fastapi_kwargs, lifespan=lifespan)
app.add_middleware(ResponseTimeMiddleware)
app.include_router(api_v1_router)


def openapi() -> dict[str, Any]:
    return cast("dict[str, Any]", custom_openapi(fastapi_app=app))


app.openapi = openapi  # type: ignore[method-assign]


@app.get("/", response_model=dict[str, str], status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Simple health-check endpoint confirming the service is alive."""

    return APP_HEALTH_MESSAGE


@app.get(
    "/cache-status",
    response_model=dict[str, bool],
    status_code=status.HTTP_200_OK,
)
async def cache_status(request: Request) -> dict[str, bool]:
    """Return whether the OpenAPI schema has been cached."""

    schema_cached = getattr(request.app.state, "openapi_schema", None) is not None
    return {"schema_cached": schema_cached}
