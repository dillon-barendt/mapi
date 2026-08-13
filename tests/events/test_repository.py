from datetime import UTC, datetime
from pathlib import Path

from mapi.events.models import Event, Offer
from mapi.events.repository import EventRepository


def test_repository_persists_events_and_offers(tmp_path: Path) -> None:
    path = tmp_path / "events.db"
    event = Event(
        event_key="source:1",
        name="Concert",
        start_date=datetime(2026, 8, 1, tzinfo=UTC),
        source_name="source",
        source_event_id="1",
        offers=[Offer(offer_key="source:1:offer", product_id="p1", price=20)],
    )

    EventRepository(path).upsert(event)
    result = EventRepository(path).list_events(limit=10, offset=0)

    assert result.total == 1
    assert result.items[0].event_key == "source:1"
    assert result.items[0].offers[0].product_id == "p1"
