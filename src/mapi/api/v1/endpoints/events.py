from typing import Annotated

from fastapi import APIRouter, Depends, Query

from mapi.api.deps import get_event_repository
from mapi.events.repository import EventPage, EventRepository

router = APIRouter()


@router.get("", response_model=EventPage, summary="List normalized events")
def list_events(
    repository: Annotated[EventRepository, Depends(get_event_repository)],
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
    q: Annotated[str | None, Query(min_length=1)] = None,
) -> EventPage:
    return repository.list_events(limit=limit, offset=offset, query=q)
