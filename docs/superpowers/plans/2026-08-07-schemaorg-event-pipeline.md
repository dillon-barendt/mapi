# Schema.org Event Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the in-memory marketplace aggregation shape with a durable, Schema.org-compatible event and offer pipeline suitable for a React Server Component and MUI DataGrid.

**Architecture:** Source adapters emit raw records from sitemaps, Page Object Models, or Scrapy spiders. A bounded classifier maps those records to validated `Event`/subtype and `Offer` models, which are persisted in SQLite through a small repository. The API exposes normalized, paginated event rows and keeps marketplace identifiers as internal source mappings.

**Tech Stack:** Python 3.13, FastAPI, Pydantic v2, SQLite (`sqlite3`), pytest.

## Global Constraints

- Schema.org names and JSON-LD field aliases remain the public domain contract.
- The database stores only fields required for event discovery and ticket/product lookup.
- Classification may be agent-assisted, but Pydantic validation and confidence/review state are authoritative.
- No provider API keys are required for tests.
- Existing row DSL and legacy provider routes remain untouched in this slice.

### Task 1: Schema.org event and offer models

**Files:** Create `src/mapi/events/models.py`; modify `src/mapi/events/__init__.py`; test `tests/events/test_models.py`.

- [ ] Add a discriminated union for `Event`, `ComedyEvent`, `SportsEvent`, `TheatreEvent`, `MusicEvent`, and `Festival` with stable source metadata and optional `event_d`/date fields.
- [ ] Add an `Offer` model linked by event key and marketplace product identifier.
- [ ] Verify JSON output uses Schema.org-compatible names and rejects unsupported event types.

### Task 2: Durable SQLite repository

**Files:** Create `src/mapi/events/repository.py`; modify `src/mapi/core/config.py`; test `tests/events/test_repository.py`.

- [ ] Create events, offers, and source mappings tables with upsert semantics.
- [ ] Persist normalized events and offers across repository instances.
- [ ] Add paginated filtering ordered by start date and stable event key.

### Task 3: Sitemap and classification contracts

**Files:** Create `src/mapi/events/ingestion.py`; test `tests/events/test_ingestion.py`.

- [ ] Parse sitemap XML loc entries without requiring network access.
- [ ] Define a classifier protocol returning validated classification, confidence, and review state.
- [ ] Implement a deterministic fallback classifier for known Schema.org types and a safe review state for unknown data.

### Task 4: Structured event API

**Files:** Create `src/mapi/api/v1/endpoints/events.py`; modify `src/mapi/api/v1/router.py`, `src/mapi/api/deps.py`; test `tests/integration/test_events_api.py`.

- [ ] Add `GET /api/v1/events` with pagination and optional type/search filters.
- [ ] Return DataGrid-ready rows containing normalized event data and offers.
- [ ] Ensure the endpoint reads from the durable repository rather than the Gametime in-memory store.

### Task 5: Documentation and verification

**Files:** Modify `docs/ARCHITECTURE.md`, `docs/DOMAIN.md`, and `README.md` only where claims conflict with the new behavior.

- [ ] Remove claims that the in-memory aggregation store is the production event store.
- [ ] Document sitemap/POM/Scrapy input boundaries and Schema.org output types.
- [ ] Run focused tests, full tests, Ruff, mypy, and `git diff --check`.
