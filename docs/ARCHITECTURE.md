# Architecture

Mapi has two bounded domains: the venue DSL remains a deterministic mapping
utility, while the production event pipeline normalizes marketplace data into
Schema.org-compatible events and offers.

Source sitemaps, marketplace Page Object Models, and Scrapy spiders feed raw
records into a bounded classifier. The classifier may use Pydantic AI, but
validated Pydantic models and review state remain authoritative.

```mermaid
flowchart LR
    A["Sitemap / POM / Scrapy source"]
    H["Schema.org Event subtype + Offer"]
    I["SQLite production event store"]
    J["/api/v1/events"]
    K["React Server Component + MUI DataGrid"]
    B["Source adapter"]
    C["Pydantic validation"]

    A --> B --> C --> H --> I --> J --> K
```

## Runtime Modules

| Module                                     | Responsibility                                                                  |
| ------------------------------------------ | ------------------------------------------------------------------------------- |
| `src/mapi/schemas/validators.py`           | Parse, compress, inspect, build, and diff row progression codes.                |
| `src/mapi/agents/mapi.py`                  | Pydantic AI agent that explains mapping value, Redis keys, and review triggers. |
| `src/mapi/schemas/*.py`                    | Pydantic request and response models for API contracts.                         |
| `src/mapi/events/models.py`                | Schema.org-compatible Event subtypes, classifications, and Offers.              |
| `src/mapi/events/repository.py`            | Durable SQLite event/offer persistence and DataGrid pagination.                 |
| `src/mapi/events/ingestion.py`             | Sitemap extraction and bounded source classification contracts.                 |
| `src/mapi/api/v1/endpoints/progression.py` | Versioned FastAPI endpoints under `/api/v1/row-progression`.                    |
| `src/mapi/main.py`                         | FastAPI app construction, middleware, and health/cache endpoints.               |
| `docs/*.md`                                | Domain, architecture, Redis, and example documentation.                         |

## Endpoint Surface

Normalized production events are served from `/api/v1/events`; the venue DSL
compatibility surface remains under `/api/v1/dsl`.

| Method | Path             | Purpose                                                          |
| ------ | ---------------- | ---------------------------------------------------------------- |
| `POST` | `/parse`         | Expand one compact code into typed rows.                         |
| `POST` | `/bulk-parse`    | Parse several compact codes independently.                       |
| `POST` | `/compress`      | Canonicalize expanded rows back into a compact code.             |
| `POST` | `/stats`         | Return row counts, unique positions, entropy, and segment count. |
| `POST` | `/build-venue`   | Expand a venue made of compact section definitions.              |
| `POST` | `/venue-diff`    | Compare compact venue maps by section and row position.          |
| `POST` | `/agent/analyze` | Run the Mapi Pydantic AI agent on one compact section code.      |

| `GET` | `/api/v1/events` | Paginated normalized Schema.org events and offers for the DataGrid. |

## Parser Flow

1. Split the code on commas and reject empty segments.
2. Detect and remove trailing `!` gap markers.
3. Parse `=` aliases as multiple row names sharing one position.
4. Parse `:` ranges only when both ends are numeric or repeated-letter codes in
   the same family.
5. Advance physical position for every atomic, alias, range member, and gap.
6. Return only non-gap rows and reject duplicate returned row names.

## Compression Flow

Compression is canonical rather than lossless. It preserves the parsed meaning,
not the exact source text.

For example:

```text
DD:AA,A:C,1:4,5!,6:10:2,12=12W,ZZZ
```

compresses to:

```text
DD:AA,A:C,1:4,12!,6:10:2,12=12W,ZZZ
```

Both parse to the same typed rows. The gap label changes because gaps are
position-only in the returned model.

## Why FastAPI

FastAPI keeps the project easy to inspect:

- Pydantic schemas become OpenAPI request and response models.
- Endpoint behavior can be tested with `TestClient`.
- The parser remains framework-independent and property-testable.
- The API can be embedded behind other marketplace, broker, or data-quality
  systems without changing the DSL.

## Why Pydantic AI

The Pydantic AI agent gives the project an explicit agent workflow without
making tests depend on a live model provider. The default model is a local
`FunctionModel` that returns deterministic, parser-grounded analysis.

This keeps the agent honest:

- Parser output remains the evidence source.
- The agent explains mapping value, Redis key shape, and review triggers.
- External model credentials are not required for local development or CI.
- A future real model can use the same typed request/response contract.
