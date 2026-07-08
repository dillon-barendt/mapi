# Mapi

Mapi is a FastAPI/Python case study for a ticketing infrastructure problem:
representing venue section-row maps as compact atomic progression strings that
can be parsed, validated, diffed, compressed, cached, and indexed.

The examples in this repository are synthetic. The project is intended as a
public engineering portfolio artifact, not a claim of production deployment.

## Problem

Ticket inventory systems need a shared understanding of section-row layout. A
single venue section can contain numeric rows, alphabetic rows, repeated-letter
rows, skipped physical positions, and equivalent accessible-row labels. Storing
every expanded row everywhere is noisy; storing only unvalidated strings is
risky.

Mapi keeps the compact string as the source value and derives typed rows,
statistics, venue diffs, and Redis-friendly cache/index records from it.

## Why Ticketing Venue Maps Are Hard

- Brokers, exchanges, and internal tools often use different row naming
  conventions for the same physical place.
- `AA:DD` means `AA`, `BB`, `CC`, `DD` in this domain, not Excel-style column
  labels.
- A row can exist physically but not belong to a section, so gaps must advance
  position without returning a row.
- Two row labels can point to one physical position, such as `13=13W`.
- Small section-map changes can affect inventory matching, marketplace quality
  checks, and review workflows.

## DSL Examples

```text
1:4                         -> 1, 2, 3, 4
5:1                         -> 5, 4, 3, 2, 1
A:D                         -> A, B, C, D
AA:DD                       -> AA, BB, CC, DD
A,B:C!,D                    -> A at position 1, D at position 4
1:2,3=3W                    -> 3 and 3W share position 3
DD:AA,A:C,1:4,5!,6:10:2    -> mixed descending, alpha, numeric, gap, stepped
```

See [docs/DOMAIN.md](docs/DOMAIN.md) for the parser rules.

## API Examples

Run locally:

```bash
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Parse one section:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/row-progression/parse \
  -H 'content-type: application/json' \
  -d '{"code":"AA:DD,A:C,1:12,13=13W"}'
```

Compress typed rows:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/row-progression/compress \
  -H 'content-type: application/json' \
  -d '{
    "code": "manual",
    "rows": [
      {"name": "A", "position": 3},
      {"name": "B", "position": 5},
      {"name": "BW", "position": 5}
    ]
  }'
```

Response:

```json
{"code": "1:2!,A,4!,B=BW"}
```

All domain endpoints live under `/api/v1/row-progression`. OpenAPI docs are
available at `/docs` when the app is running.

## Redis Usage

The compact code can be stored as a Redis string:

```redis
SET venue:demo-arena:section:101:row_progression "AA:DD,A:C,1:12,13=13W"
```

It can also live in a section hash:

```redis
HSET venue:demo-arena:section:101 \
  row_progression "AA:DD,A:C,1:12,13=13W" \
  parser_version "0.1.0" \
  row_count "20"
```

Expanded rows can be cached as Redis JSON for agent workflows:

```json
{
  "venue_id": "demo-arena",
  "section_id": "101",
  "row_progression": "AA:DD,A:C,1:12,13=13W",
  "rows": [
    {"name": "AA", "position": 1},
    {"name": "BB", "position": 2},
    {"name": "13", "position": 20},
    {"name": "13W", "position": 20}
  ]
}
```

Venue diffs can trigger downstream marketplace or inventory review workflows:
row-count changes, new aliases, removed rows, or suspicious gaps become auditable
review events. See [docs/REDIS_MODEL.md](docs/REDIS_MODEL.md).

## Architecture

```mermaid
flowchart LR
    A["Input venue DSL"] --> B["Parser"]
    B --> C["Typed row model"]
    C --> D["FastAPI response"]
    D --> E["Redis cache/index"]
    E --> F["Agent review workflow"]
```

Key files:

- `app/schemas/validators.py`: parser, compressor, stats, venue build, venue
  diff
- `app/schemas/*.py`: Pydantic request and response models
- `app/api/v1/endpoints/progression.py`: versioned FastAPI endpoints
- `docs/ARCHITECTURE.md`: architecture notes and parser flow

## Testing Strategy

The suite covers:

- Numeric, single-letter, and multi-letter repeated-letter ranges
- Ascending, descending, and stepped ranges
- Mixed atomic row codes
- Equivalent rows with `=`
- Gap rows with `!`
- Duplicate row detection
- `parse -> compress -> parse` round trips
- API response contracts

Run:

```bash
black --check .
isort --check-only .
ruff check .
mypy app
pytest --cov=app --cov-report=term-missing
```

## Local Development

Python 3.13 is retained because the current FastAPI and Pydantic dependency set
supports it.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

## Recruiter-Facing Summary

Mapi demonstrates domain modeling, parser correctness, typed FastAPI contracts,
property-based testing, and cache/index design around a real class of ticketing
data problem. The value is not the number of endpoints; it is that compact venue
DSL strings become deterministic, validated infrastructure objects that can
drive search, diffing, and human-in-the-loop review workflows.

## More Documentation

- [docs/DOMAIN.md](docs/DOMAIN.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/REDIS_MODEL.md](docs/REDIS_MODEL.md)
- [docs/EXAMPLES.md](docs/EXAMPLES.md)
