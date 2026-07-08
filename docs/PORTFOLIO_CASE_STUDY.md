# Portfolio Case Study

## Summary

Mapi turns spreadsheet-shaped venue section-row maps into compact, validated,
diffable, cacheable infrastructure values. It is a FastAPI/Python portfolio
project focused on a real ticketing operations problem, using synthetic data.

## The Ticketing Problem

Broker operations teams often maintain section-row maps manually. A section can
contain numeric rows, repeated-letter rows, gaps, and aliases that refer to the
same physical position. If those maps stay as ad hoc spreadsheet rows, every
downstream system has to rediscover the same rules.

## Why Manual Spreadsheet Entry Breaks Down

- Row labels are domain-specific and not always naturally sortable.
- Gaps matter because they preserve physical section alignment.
- Aliases such as `13=13W` need one shared position.
- Small data changes can affect inventory review and marketplace publishing.
- Manual spreadsheet edits are hard to diff, audit, and validate.

## Domain Model

The core model is `RowOut(name, position)`. Compact DSL strings are source
values. Expanded rows, stats, diffs, Redis records, and review triggers are
deterministic derivatives.

## DSL Design

The DSL supports:

- Numeric ranges: `1:12`
- Repeated-letter ranges: `AA:DD`
- Descending ranges: `DD:AA`
- Gaps: `8:19!`
- Aliases: `13=13W`
- Mixed atomic rows: `21WC`

## API Design

The API is versioned under `/api/v1/row-progression`. It exposes parsing,
compression, stats, venue building, venue diffing, spreadsheet-shaped import,
and deterministic Pydantic AI analysis.

## Parser Correctness Strategy

Parser behavior is tested with unit examples and property-based round-trip
checks. Compression is canonical: it preserves row names and positions, not the
exact original source string.

## Spreadsheet Import Workflow

CSV or API records shaped like `section,row,position` are grouped by section,
validated, converted to typed rows, and compressed with the same canonical
compressor used by the rest of the system.

## Redis and Indexing Model

The compact DSL can be stored as a Redis string or hash field. Expanded rows can
be cached as JSON. Derived flags such as row count, gaps, and aliases can become
queryable index fields for review workflows.

## Agent-Assisted Review

The Pydantic AI agent returns parser-grounded guidance: why the row map matters,
which Redis keys to use, and which review triggers are present. The default
agent uses a local function model and does not require external credentials.

## Testing Strategy

The test suite covers parser edge cases, spreadsheet import validation, API
contracts, CLI behavior, and the deterministic agent endpoint.

## What Is Synthetic

All venues, sections, rows, Redis keys, and workflow events in this repository
are synthetic examples. The project does not include broker, customer,
marketplace, provider, or production inventory data.

## Production Extensions

Real deployment work would add authenticated ingestion, venue-map revision
history, review queues, provider adapters, audit logging, and operational
monitoring. Those are documented as extensions, not claimed as implemented.
