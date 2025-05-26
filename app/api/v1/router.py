from fastapi import APIRouter
from .endpoints.comparison import router as comparison_router
from .endpoints.generation import router as generation_router
from .endpoints.parsing import router as parsing_router
from .endpoints.query import router as query_router
from .endpoints.slice_info import router as slice_info_router
from .endpoints.stats import router as stats_router
from .endpoints.venue import router as venue_router
from app.core.config import settings

api_v1_router = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
)

# Extract constant for router configurations
ROUTERS = [
    (parsing_router, "/parsing", ["Parsing", settings.ROW_PROGRESSION_TAG]),
    (generation_router, "/generation", ["generation", settings.ROW_PROGRESSION_TAG]),
    (venue_router, "/venue", ["venue", settings.ROW_PROGRESSION_TAG]),
    (stats_router, "/stats", ["stats", "Statistics"]),
    (query_router, "/query", ["query", settings.ROW_PROGRESSION_TAG, "Query"]),
    (comparison_router, "/comparison", ["comparison", settings.ROW_PROGRESSION_TAG]),
    (slice_info_router, "/slice-info", ["slice_info", settings.ROW_PROGRESSION_TAG, "Slices"]),
]

# Register all routers using a loop
for router, prefix, tags in ROUTERS:
    api_v1_router.include_router(router, prefix=prefix, tags=tags)