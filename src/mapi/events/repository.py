from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from pydantic import BaseModel

from .models import Event


class EventPage(BaseModel):
    items: list[Event]
    total: int
    limit: int
    offset: int


class EventRepository:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS events (
                    event_key TEXT PRIMARY KEY,
                    event_type TEXT NOT NULL,
                    start_date TEXT,
                    payload TEXT NOT NULL
                )"""
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def upsert(self, event: Event) -> None:
        payload = event.model_dump_json(by_alias=True)
        start_date = event.start_date.isoformat() if event.start_date else None
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO events(event_key, event_type, start_date, payload)
                   VALUES (?, ?, ?, ?)
                   ON CONFLICT(event_key) DO UPDATE SET
                     event_type=excluded.event_type,
                     start_date=excluded.start_date,
                     payload=excluded.payload""",
                (event.event_key, event.event_type, start_date, payload),
            )

    def list_events(
        self, *, limit: int = 100, offset: int = 0, query: str | None = None
    ) -> EventPage:
        clauses: list[str] = []
        params: list[str | int] = []
        if query:
            clauses.append("json_extract(payload, '$.name') LIKE ?")
            params.append(f"%{query}%")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._connect() as connection:
            total = connection.execute(
                f"SELECT COUNT(*) FROM events {where}", params
            ).fetchone()[0]
            rows = connection.execute(
                f"SELECT payload FROM events {where} "
                "ORDER BY start_date IS NULL, start_date, event_key LIMIT ? OFFSET ?",
                [*params, limit, offset],
            ).fetchall()
        return EventPage(
            items=[Event.model_validate(json.loads(row["payload"])) for row in rows],
            total=total,
            limit=limit,
            offset=offset,
        )
