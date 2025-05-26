"""Application entry point for Mapi API (Mapi).

This module initializes the FastAPI application, sets up middleware, includes routers, the application's OpenAPI schema
and provides health-check endpoints.
"""
from fastapi import FastAPI, status
from fastapi.requests import Request

from app.api.v1.router import api_v1_router
from .core.config import settings
from .core.constants import APP_HEALTH_MESSAGE
from .core.state import lifespan
from .core.middleware import ResponseTimeMiddleware
from .utils.openapi_custom import custom_openapi

app: FastAPI = FastAPI(**settings.fastapi_kwargs, lifespan=lifespan)  # type: ignore[arg-type]
app.add_middleware(ResponseTimeMiddleware)  # type: ignore[arg-type]
app.include_router(api_v1_router)
app.openapi = custom_openapi
if not app.openapi:
    app.openapi = custom_openapi

@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_json() -> dict:
    """
    Custom OpenAPI JSON endpoint.
    Returns the OpenAPI schema for the application.
    """
    if app.openapi_schema:
        return app.openapi_schema
    return {"error": "OpenAPI schema is not available."}
@app.get("/", response_model=dict[str, str], status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Simple health-check endpoint confirming the service is alive"""
    if not app.state.openapi_schema:
        return {"message": "OpenAPI schema is not cached."}
    return APP_HEALTH_MESSAGE

@app.get(
    "/cache-status",
    response_model=dict[str, bool],
    status_code=status.HTTP_200_OK
)
async def cache_status(request: Request) -> dict[str, bool]:
    """
    Reports whether the OpenAPI schema is stored in the application's state.
    """
    schema_cached: bool = request.app.state.openapi_schema is not None
    return {"schema_cached": schema_cached}