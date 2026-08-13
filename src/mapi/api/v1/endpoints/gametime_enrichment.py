"""Gametime enrichment job API.

Aggregation runs as a FastAPI ``BackgroundTasks`` job instead of one
passthrough endpoint per upstream Gametime call, so the surface is three
routes: queue a job, poll it, and read DataGrid row blocks back.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from mapi.api.deps import get_gametime_enrichment_service
from mapi.services.gametime_enrichment import (
    GametimeEnrichmentJob,
    GametimeEnrichmentRequest,
    GametimeEnrichmentService,
    GametimeGridRowsPage,
    SortOrder,
)

router = APIRouter()

ServiceDep = Annotated[
    GametimeEnrichmentService,
    Depends(get_gametime_enrichment_service),
]


def _not_found(error: LookupError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.post(
    "/jobs",
    response_model=GametimeEnrichmentJob,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Queue a Gametime aggregation job",
)
async def create_enrichment_job(
    request: GametimeEnrichmentRequest,
    background_tasks: BackgroundTasks,
    service: ServiceDep,
) -> GametimeEnrichmentJob:
    job = service.start_job(request)
    background_tasks.add_task(service.run_job, job.job_id)
    return job


@router.get(
    "/jobs/{job_id}",
    response_model=GametimeEnrichmentJob,
    summary="Get the status of a Gametime aggregation job",
)
async def get_enrichment_job(
    job_id: str,
    service: ServiceDep,
) -> GametimeEnrichmentJob:
    try:
        return service.fetch_job(job_id)
    except LookupError as error:
        raise _not_found(error) from error


@router.get(
    "/jobs/{job_id}/rows",
    response_model=GametimeGridRowsPage,
    summary="Read a server-side DataGrid row block from a finished job",
)
async def get_enrichment_job_rows(
    job_id: str,
    service: ServiceDep,
    start_row: Annotated[int, Query(ge=0)] = 0,
    end_row: Annotated[int, Query(gt=0)] = 100,
    sort_field: Annotated[str | None, Query()] = None,
    sort_order: Annotated[SortOrder, Query()] = "asc",
) -> GametimeGridRowsPage:
    try:
        return service.fetch_rows_page(
            job_id,
            start_row=start_row,
            end_row=end_row,
            sort_field=sort_field,
            sort_order=sort_order,
        )
    except LookupError as error:
        raise _not_found(error) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
