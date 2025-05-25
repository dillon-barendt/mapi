from fastapi import APIRouter
from .endpoints.comparison import router as comparison_router
from .endpoints.slice_info import router as slice_info_router
from .endpoints.parsing import router as parsing_router
from .endpoints.generation import router as generation_router
from .endpoints.venue import router as venue_router
from .endpoints.stats import router as stats_router
from .endpoints.query import router as query_router


API_V1_ROUTER = APIRouter(
    prefix="/api/v1",
    tags=["v1"],
)

API_V1_ROUTER.include_router(parsing_router, prefix="/parsing", tags=["Parsing", "Row Progression"])
API_V1_ROUTER.include_router(generation_router, prefix="/generation", tags=["generation", "Row Progression"])
API_V1_ROUTER.include_router(venue_router, prefix="/venue", tags=["venue", "Row Progression"])
API_V1_ROUTER.include_router(stats_router, prefix="/stats", tags=["stats", "Statistics"])
API_V1_ROUTER.include_router(query_router, prefix="/query", tags=["query, Row Progression"])
API_V1_ROUTER.include_router(comparison_router, prefix="/comparison", tags=["comparison", "Row Progression"])
API_V1_ROUTER.include_router(slice_info_router, prefix="/slice-info", tags=["slice_info", "Row Progression"])