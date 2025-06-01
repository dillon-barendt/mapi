"""Modularity for Mapi v1 routers.

This module defines the API v1 router and includes all the necessary endpoints. At the end of the file, it registers each endpoint router with the main API router.

"""

from fastapi import APIRouter
from .endpoints.progression import router as progression_router
from ...core.config import settings

api_v1_router = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},
)

# Extract constant for router configurations
ROUTERS = [
    (progression_router, "/row-progression", [settings.ROW_PROGRESSION_TAG]),
]

for router, prefix, tags in ROUTERS:
    api_v1_router.include_router(router, prefix=prefix, tags=tags)
