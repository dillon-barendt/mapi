from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from mapi.events.models import Event, EventClassification, Offer


def test_schema_org_event_serializes_normalized_fields() -> None:
    event = Event(
        event_key="tm:abc",
        name="The Show",
        start_date=datetime(2026, 9, 1, 19, tzinfo=UTC),
        event_type="MusicEvent",
        source_name="TM",
        source_event_id="abc",
        offers=[Offer(offer_key="tm:abc:offer", price=45.0, currency="USD")],
    )

    payload = event.model_dump(by_alias=True, mode="json")

    assert payload["@type"] == "MusicEvent"
    assert payload["startDate"].startswith("2026-09-01T19:00:00")
    assert payload["offers"][0]["@type"] == "Offer"


def test_unknown_classification_requires_review() -> None:
    classification = EventClassification(event_type="Event", confidence=0.4)
    assert classification.review_required is True


def test_offer_rejects_negative_price() -> None:
    with pytest.raises(ValidationError):
        Offer(offer_key="x", price=-1, currency="USD")
