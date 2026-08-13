from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Protocol, cast
from xml.etree import ElementTree

from .models import Event, EventClassification, EventType, Offer
from .repository import EventRepository


class EventClassifier(Protocol):
    def classify(self, source: Mapping[str, object]) -> EventClassification: ...


class DefaultEventClassifier:
    def classify(self, source: Mapping[str, object]) -> EventClassification:
        return classify_source(source, source_name="unknown")


def parse_sitemap(xml: str) -> list[str]:
    root = ElementTree.fromstring(xml)
    return [
        loc.text.strip()
        for loc in root.findall(".//{*}loc")
        if loc.text and loc.text.strip()
    ]


def classify_source(
    source: Mapping[str, object], *, source_name: str
) -> EventClassification:
    raw_type = str(source.get("@type") or source.get("type") or "Event")
    valid_types = {
        "Event",
        "ComedyEvent",
        "SportsEvent",
        "TheatreEvent",
        "MusicEvent",
        "Festival",
    }
    event_type = cast(
        "EventType",
        raw_type if raw_type in valid_types else "Event",
    )
    confidence = 0.95 if event_type != "Event" else 0.4
    return EventClassification(event_type=event_type, confidence=confidence)


class EventIngestionService:
    def __init__(
        self,
        repository: EventRepository,
        classifier: EventClassifier | None = None,
    ) -> None:
        self.repository = repository
        self.classifier = classifier or DefaultEventClassifier()

    def ingest(
        self,
        source: Mapping[str, object],
        *,
        source_name: str,
        source_event_id: str,
    ) -> Event:
        classification = self.classifier.classify(source)
        event = Event(
            event_key=f"{source_name}:{source_event_id}",
            name=str(source.get("name") or source.get("event_d") or source_event_id),
            startDate=_parse_datetime(source.get("startDate")),
            endDate=_parse_datetime(source.get("endDate")),
            eventD=_string_or_none(source.get("event_d") or source.get("eventD")),
            **{"@type": classification.event_type},
            description=_string_or_none(source.get("description")),
            url=_string_or_none(source.get("url")),
            image=_string_or_none(source.get("image")),
            venue_name=_string_or_none(source.get("venue_name")),
            source_name=source_name,
            source_event_id=source_event_id,
            classification_confidence=classification.confidence,
            review_required=classification.review_required,
            offers=_normalize_offers(
                source.get("offers"), source_name, source_event_id
            ),
        )
        self.repository.upsert(event)
        return event


def _string_or_none(value: object) -> str | None:
    return str(value) if value is not None and str(value).strip() else None


def _parse_datetime(value: object) -> datetime | None:
    text = _string_or_none(value)
    return datetime.fromisoformat(text) if text else None


def _normalize_offers(
    value: object, source_name: str, source_event_id: str
) -> list[Offer]:
    if not isinstance(value, list):
        return []
    return [
        _normalize_offer(offer, source_name, source_event_id, index)
        for index, offer in enumerate(value)
        if isinstance(offer, Mapping)
    ]


def _normalize_offer(
    offer: Mapping[str, object], source_name: str, source_event_id: str, index: int
) -> Offer:
    normalized = dict(offer)
    normalized.setdefault("offer_key", f"{source_name}:{source_event_id}:offer:{index}")
    return Offer.model_validate(normalized)
