from pathlib import Path

from mapi.events.ingestion import EventIngestionService, classify_source, parse_sitemap
from mapi.events.repository import EventRepository


def test_parse_sitemap_returns_event_urls() -> None:
    xml = "<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'><url><loc>https://x.test/event/42</loc></url></urlset>"
    assert parse_sitemap(xml) == ["https://x.test/event/42"]


def test_unknown_source_is_reviewable() -> None:
    result = classify_source({"name": "Mystery"}, source_name="SH")
    assert result.event_type == "Event"
    assert result.review_required is True


def test_ingestion_normalizes_and_persists_source_record(tmp_path: Path) -> None:
    service = EventIngestionService(EventRepository(tmp_path / "events.db"))
    event = service.ingest(
        {
            "event_d": "show-42",
            "name": "Comedy Night",
            "startDate": "2026-09-01T19:00:00+00:00",
            "@type": "ComedyEvent",
            "offers": [{"sku": "offer-1", "price": 25, "currency": "USD"}],
        },
        source_name="SH",
        source_event_id="42",
    )
    assert event.event_key == "SH:42"
    assert event.event_type == "ComedyEvent"
    assert event.offers[0].product_id == "offer-1"
