"""Gametime enrichment as a background aggregation job.

One POST queues a FastAPI ``BackgroundTasks`` job that pages the Gametime
events feed, optionally aggregates listings, and stores only DataGrid-ready
rows. The grid then reads slices back through the rows endpoint, replacing the
one-passthrough-endpoint-per-upstream-call pattern.

The job store is in-process and single-node. Its interface is deliberately
small so a Redis-backed implementation can replace it without touching the
service or endpoints.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from mapi.providers.gametime import GametimeEventGridRow, GametimeService

JobStatus = Literal["queued", "running", "succeeded", "failed"]
SortOrder = Literal["asc", "desc"]

MAX_LISTINGS_PER_JOB = 100
DEFAULT_LISTINGS_LIMIT = 25

_SCALAR_SORT_FIELDS = frozenset(
    name for name in GametimeEventGridRow.model_fields if name != "listings"
)
SORTABLE_FIELDS = frozenset({*_SCALAR_SORT_FIELDS, "min_price"})


class GametimeEnrichmentRequest(BaseModel):
    """Filters for one aggregation job; mirrors the upstream /v1/events query."""

    category_group: Literal["concert", "sport", "theater"] | None = None
    category: str | None = None
    q: str | None = None
    performer_id: str | None = None
    venue_id: str | None = None
    include_listings: bool = Field(
        default=False,
        description="Aggregate listing counts and price bounds per event.",
    )
    listings_limit: int = Field(
        default=DEFAULT_LISTINGS_LIMIT,
        ge=1,
        le=MAX_LISTINGS_PER_JOB,
        description="Maximum events to enrich with listings (one call each).",
    )


class GametimeEnrichmentJob(BaseModel):
    job_id: str
    status: JobStatus
    request: GametimeEnrichmentRequest
    created_at: str
    finished_at: str | None = None
    total_rows: int = 0
    skipped_records: int = 0
    listings_enriched: int = 0
    error: str | None = None


class GametimeGridRowsPage(BaseModel):
    """One server-side DataGrid block: a row slice plus the total for paging."""

    job_id: str
    total_rows: int
    start_row: int
    end_row: int
    rows: list[GametimeEventGridRow]


def _utc_now() -> str:
    return datetime.now(tz=UTC).isoformat()


class GametimeEnrichmentStore:
    """In-process job store keyed by job id."""

    def __init__(self) -> None:
        self._jobs: dict[str, GametimeEnrichmentJob] = {}
        self._rows: dict[str, list[GametimeEventGridRow]] = {}

    def create(self, request: GametimeEnrichmentRequest) -> GametimeEnrichmentJob:
        job = GametimeEnrichmentJob(
            job_id=uuid4().hex,
            status="queued",
            request=request,
            created_at=_utc_now(),
        )
        self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> GametimeEnrichmentJob:
        try:
            return self._jobs[job_id]
        except KeyError:
            raise LookupError(f"Unknown enrichment job '{job_id}'.") from None

    def mark_running(self, job_id: str) -> None:
        self.get(job_id).status = "running"

    def mark_succeeded(
        self,
        job_id: str,
        *,
        rows: list[GametimeEventGridRow],
        skipped_records: int,
        listings_enriched: int,
    ) -> None:
        job = self.get(job_id)
        job.status = "succeeded"
        job.finished_at = _utc_now()
        job.total_rows = len(rows)
        job.skipped_records = skipped_records
        job.listings_enriched = listings_enriched
        self._rows[job_id] = rows

    def mark_failed(self, job_id: str, error: str) -> None:
        job = self.get(job_id)
        job.status = "failed"
        job.finished_at = _utc_now()
        job.error = error

    def rows(self, job_id: str) -> list[GametimeEventGridRow]:
        return self._rows.get(job_id, [])


_store = GametimeEnrichmentStore()


def get_gametime_enrichment_store() -> GametimeEnrichmentStore:
    """Return the process-wide job store shared across per-request services."""

    return _store


def _sort_value(row: GametimeEventGridRow, field: str) -> str | float | None:
    if field == "min_price":
        price: float | None = row.listings.min_price if row.listings else None
        return price
    value = getattr(row, field, None)
    return value if isinstance(value, str) else None


def _sorted_rows(
    rows: list[GametimeEventGridRow],
    field: str,
    order: SortOrder,
) -> list[GametimeEventGridRow]:
    present = [row for row in rows if _sort_value(row, field) is not None]
    missing = [row for row in rows if _sort_value(row, field) is None]

    def sort_key(row: GametimeEventGridRow) -> str | float:
        value = _sort_value(row, field)
        assert value is not None
        return value

    ordered = sorted(present, key=sort_key, reverse=order == "desc")
    return ordered + missing


class GametimeEnrichmentService:
    """Queue, run, and read back Gametime aggregation jobs."""

    def __init__(
        self,
        gametime_service: GametimeService | None = None,
        store: GametimeEnrichmentStore | None = None,
    ) -> None:
        self.gametime_service = gametime_service or GametimeService()
        self.store = store or get_gametime_enrichment_store()

    def start_job(self, request: GametimeEnrichmentRequest) -> GametimeEnrichmentJob:
        return self.store.create(request)

    async def run_job(self, job_id: str) -> None:
        """Aggregate events (and optionally listings) for a queued job.

        Designed to run inside FastAPI ``BackgroundTasks``: every failure is
        recorded on the job instead of raising into the void.
        """

        request = self.store.get(job_id).request
        self.store.mark_running(job_id)
        try:
            rows, skipped = await self.gametime_service.fetch_event_grid_rows(
                category_group=request.category_group,
                category=request.category,
                q=request.q,
                performer_id=request.performer_id,
                venue_id=request.venue_id,
            )
            listings_enriched = 0
            if request.include_listings:
                listings_enriched = await self._enrich_listings(
                    rows, limit=request.listings_limit
                )
            self.store.mark_succeeded(
                job_id,
                rows=rows,
                skipped_records=skipped,
                listings_enriched=listings_enriched,
            )
        except Exception as error:
            self.store.mark_failed(job_id, str(error))

    async def _enrich_listings(
        self,
        rows: list[GametimeEventGridRow],
        *,
        limit: int,
    ) -> int:
        enriched = 0
        for index, row in enumerate(rows[:limit]):
            try:
                summary = await self.gametime_service.fetch_listing_summary(
                    row.event_id
                )
            except Exception:
                continue
            rows[index] = row.model_copy(update={"listings": summary})
            enriched += 1
        return enriched

    def fetch_job(self, job_id: str) -> GametimeEnrichmentJob:
        return self.store.get(job_id)

    def fetch_rows_page(
        self,
        job_id: str,
        *,
        start_row: int = 0,
        end_row: int = 100,
        sort_field: str | None = None,
        sort_order: SortOrder = "asc",
    ) -> GametimeGridRowsPage:
        """Return one DataGrid block: rows [start_row, end_row) plus the total."""

        job = self.store.get(job_id)
        if job.status != "succeeded":
            raise ValueError(
                f"Job '{job_id}' has status '{job.status}'; rows are only "
                "available once it has succeeded."
            )
        if end_row <= start_row:
            raise ValueError("end_row must be greater than start_row.")
        if sort_field is not None and sort_field not in SORTABLE_FIELDS:
            allowed = ", ".join(sorted(SORTABLE_FIELDS))
            raise ValueError(f"sort_field must be one of: {allowed}.")

        rows = self.store.rows(job_id)
        if sort_field is not None:
            rows = _sorted_rows(rows, sort_field, sort_order)

        return GametimeGridRowsPage(
            job_id=job_id,
            total_rows=len(rows),
            start_row=start_row,
            end_row=end_row,
            rows=rows[start_row:end_row],
        )
