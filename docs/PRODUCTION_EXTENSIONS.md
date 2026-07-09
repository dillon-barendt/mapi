# Production Extensions

Mapi is a portfolio-ready case study, not a production deployment claim. These
are realistic next steps for turning the architecture into an operational
system.

## Ticketmaster Provider Enrichment

- Ticketmaster Discovery Feed daily ingestion.
- Feed metadata checksum and timestamp tracking.
- Event-to-map matching through `legacyEventId`.
- Venue metadata enrichment from provider records.
- Section/place normalization from `placeDetail` payloads.
- Seat/row geometry enrichment once stable fixtures exist.
- Broker review triggers for missing maps, aliases, gaps, and geometry drift.
- Redis cache invalidation when feed or map metadata changes.
- Diffing provider metadata over time.
- Agent-assisted anomaly review.
- Background queue processing for large country feeds.
- Rate-limited provider fetches with retry and resume support.

## Spreadsheet Ingestion

- Accept authenticated uploads.
- Validate file size and content type.
- Store original uploads in an audit-safe object store.
- Track import status and validation errors by upload ID.

## Broker-Facing Review UI

- Show compact DSL beside expanded rows.
- Highlight gaps, aliases, and row-count changes.
- Let operators approve, reject, or annotate section changes.
- Keep examples and tests synthetic in public code.

## Redis Indexing

- Store compact DSL strings as source values.
- Cache expanded rows as JSON.
- Index derived fields such as row count, gap presence, alias presence, and
  revision ID.
- Use index queries to route high-risk sections to review queues.

## Review Queues

- Emit events for venue-map changes.
- Route sections with aliases, gaps, or large row-count deltas to manual review.
- Record review decisions with actor, timestamp, and reason.

## Inventory Impact Analysis

- Compare row map revisions against active inventory.
- Identify listings whose row labels moved, disappeared, or became aliases.
- Block marketplace publishing when map changes invalidate inventory assumptions.

## Marketplace Publishing Validation

- Validate each outbound payload against the current venue map revision.
- Reject ambiguous row labels before provider submission.
- Keep provider-specific transformations isolated behind adapters.

## Versioned Venue Map Revisions

- Persist immutable venue-map versions.
- Diff revisions at section and row granularity.
- Support rollback when an import is rejected.

## Provider-Specific Adapters

- Normalize provider naming differences at the edge.
- Keep Mapi's core DSL provider-neutral.
- Test adapters with synthetic fixtures.

## Audit Log

- Record imports, parser results, review decisions, and publish attempts.
- Keep original compact source values and derived rows available for inspection.

## Confidence Scoring

- Score imports based on gaps, aliases, row-count deltas, and parser warnings.
- Use scores for routing decisions, not as a substitute for required review.
