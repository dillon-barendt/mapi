from datetime import UTC, datetime
from pathlib import Path

from fastapi.testclient import TestClient

from mapi.api.deps import get_event_repository
from mapi.events.models import Event
from mapi.main import app


def test_events_endpoint_returns_datagrid_page(tmp_path: Path) -> None:
    repository = get_event_repository(str(tmp_path / "events.db"))
    repository.upsert(
        Event(
            event_key="x:1",
            name="A",
            source_name="x",
            source_event_id="1",
            start_date=datetime(2026, 1, 1, tzinfo=UTC),
        )
    )
    app.dependency_overrides[get_event_repository] = lambda: repository
    try:
        response = TestClient(app).get("/api/v1/events?limit=10")
    finally:
        app.dependency_overrides.pop(get_event_repository, None)
    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["name"] == "A"
