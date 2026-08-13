from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from mapi.api.deps import get_gametime_enrichment_service
from mapi.core.config import Settings
from mapi.main import app
from mapi.providers.gametime import GametimeService
from mapi.services.gametime_enrichment import (
    GametimeEnrichmentRequest,
    GametimeEnrichmentService,
    GametimeEnrichmentStore,
)

BASE = "/api/v1/gametime-enrichment"


class FakeGametimeClient:
    async def get_events(
        self,
        *,
        page: int = 1,
        per_page: int | None = None,
        category_group: str | None = None,
        category: str | None = None,
        q: str | None = None,
        performer_id: str | None = None,
        venue_id: str | None = None,
    ) -> list[dict[str, Any]]:
        if page > 1:
            return []
        return [
            {
                "event": {"id": "evt-1", "name": "Warriors vs Lakers"},
                "venue": {"id": "ven-1", "name": "Chase Center"},
            },
            {"event": {"id": "evt-2", "name": "Giants vs Dodgers"}},
        ]

    async def get_event_listings(
        self,
        event_id: str,
        *,
        quantity: int | None = None,
        all_in_pricing: bool | None = None,
        jitter_cheapest: int | None = None,
    ) -> dict[str, Any]:
        return {"listings": [{"price": 75}]}


@pytest.fixture
def enrichment_service() -> Iterator[GametimeEnrichmentService]:
    service = GametimeEnrichmentService(
        gametime_service=GametimeService(
            client=FakeGametimeClient(),
            settings=Settings(),
        ),
        store=GametimeEnrichmentStore(),
    )
    app.dependency_overrides[get_gametime_enrichment_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


def test_job_lifecycle_queues_runs_and_serves_grid_rows(
    enrichment_service: GametimeEnrichmentService,
) -> None:
    with TestClient(app) as client:
        created = client.post(f"{BASE}/jobs", json={"include_listings": True})
        assert created.status_code == 202
        job_id = created.json()["job_id"]

        polled = client.get(f"{BASE}/jobs/{job_id}")
        assert polled.status_code == 200
        job = polled.json()
        assert job["status"] == "succeeded"
        assert job["total_rows"] == 2
        assert job["listings_enriched"] == 2

        rows = client.get(
            f"{BASE}/jobs/{job_id}/rows",
            params={"start_row": 0, "end_row": 1},
        )

    assert rows.status_code == 200
    page = rows.json()
    assert page["total_rows"] == 2
    assert len(page["rows"]) == 1
    assert page["rows"][0]["event_id"] == "evt-1"
    assert page["rows"][0]["listings"]["min_price"] == 75.0


def test_unknown_job_returns_404(
    enrichment_service: GametimeEnrichmentService,
) -> None:
    with TestClient(app) as client:
        response = client.get(f"{BASE}/jobs/does-not-exist")

    assert response.status_code == 404


def test_rows_before_job_finishes_returns_409(
    enrichment_service: GametimeEnrichmentService,
) -> None:
    job = enrichment_service.start_job(GametimeEnrichmentRequest())

    with TestClient(app) as client:
        response = client.get(f"{BASE}/jobs/{job.job_id}/rows")

    assert response.status_code == 409
    assert "queued" in response.json()["detail"]


def test_invalid_listings_limit_is_rejected(
    enrichment_service: GametimeEnrichmentService,
) -> None:
    with TestClient(app) as client:
        response = client.post(f"{BASE}/jobs", json={"listings_limit": 5000})

    assert response.status_code == 422
