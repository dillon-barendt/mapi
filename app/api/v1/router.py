from enum import Enum

from fastapi import APIRouter

from ...core.config import settings
from .endpoints.progression import router as progression_router

api_v1_router = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},
)

row_progression_tags: list[str | Enum] = [settings.row_progression_tag]

api_v1_router.include_router(
    progression_router,
    prefix="/row-progression",
    tags=row_progression_tags,
)
