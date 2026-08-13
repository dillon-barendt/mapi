from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field

EventType = Literal[
    "Event",
    "ComedyEvent",
    "SportsEvent",
    "TheatreEvent",
    "MusicEvent",
    "Festival",
]


class Offer(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    offer_key: str = Field(min_length=1)
    product_id: str | None = Field(default=None, alias="sku")
    name: str | None = None
    price: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    availability: str | None = None
    url: str | None = None

    @computed_field(alias="@type")  # type: ignore[prop-decorator]
    @property
    def schema_type(self) -> Literal["Offer"]:
        return "Offer"


class EventClassification(BaseModel):
    event_type: EventType
    confidence: float = Field(ge=0, le=1)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def review_required(self) -> bool:
        return self.confidence < 0.8 or self.event_type == "Event"


class Event(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    event_key: str = Field(min_length=1)
    name: str = Field(min_length=1)
    start_date: datetime | None = Field(default=None, alias="startDate")
    end_date: datetime | None = Field(default=None, alias="endDate")
    event_d: str | None = Field(default=None, alias="eventD")
    event_type: EventType = Field(default="Event", alias="@type")
    description: str | None = None
    url: str | None = None
    image: str | None = None
    venue_name: str | None = None
    source_name: str = Field(min_length=1)
    source_event_id: str = Field(min_length=1)
    classification_confidence: float = Field(default=1.0, ge=0, le=1)
    review_required: bool = False
    offers: list[Offer] = Field(default_factory=list)


class ComedyEvent(Event):
    event_type: Literal["ComedyEvent"] = "ComedyEvent"


class SportsEvent(Event):
    event_type: Literal["SportsEvent"] = "SportsEvent"


class TheatreEvent(Event):
    event_type: Literal["TheatreEvent"] = "TheatreEvent"


class MusicEvent(Event):
    event_type: Literal["MusicEvent"] = "MusicEvent"


class Festival(Event):
    event_type: Literal["Festival"] = "Festival"


SchemaOrgEvent = Annotated[
    Event | ComedyEvent | SportsEvent | TheatreEvent | MusicEvent | Festival,
    Field(discriminator="event_type"),
]
