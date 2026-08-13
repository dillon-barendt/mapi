# AGENTS.md

This file is the repository-level operating guide for Codex and other coding
agents. Keep changes small, typed, testable, and faithful to the current tree.

## Working Agreements

- Inspect `git status --short --branch` before editing. This repository may
  contain unrelated staged and unstaged work; preserve it.
- Make the smallest correct change. Do not refactor unrelated code, weaken
  types, or introduce new abstractions without a concrete need.
- Search with `rg` or `rg --files` and follow existing module boundaries.
- Never stage broadly with `git add -A` or `git add .`. If publication is
  requested, confirm the exact file scope and stage explicit paths only.
- Do not commit, push, open a pull request, add a production dependency, or run
  a destructive command unless the task authorizes it.
- Treat documentation as a public contract. Distinguish implemented behavior
  from proposals, prototypes, and production-extension ideas.

## Project Orientation

Mapi is a Python 3.13 FastAPI service with two bounded domains:

1. The **Venue DSL** is a deterministic domain for parsing, validating,
   compressing, inspecting, building, and diffing compact venue row
   progressions such as `DD:AA,A:C,1:4,5!,6:10:2,12=12W`.
2. The **event pipeline** normalizes marketplace data into Schema.org-compatible
   event and offer models and persists them in SQLite for stable querying.

The Venue DSL is pure application logic. The event pipeline is durable; do not
describe the whole service as stateless or in-memory.

### Repository Boundaries

- `src/mapi/schemas/validators.py`: pure Venue DSL functions. Keep framework,
  network, and persistence concerns out of this module.
- `src/mapi/schemas/`: Pydantic v2 API contracts. Preserve strict and frozen
  row-model behavior where already configured.
- `src/mapi/events/`: Schema.org-compatible models, ingestion contracts, and
  SQLite repository behavior.
- `src/mapi/services/`: orchestration across domain and provider boundaries.
- `src/mapi/providers/<provider>/`: async external clients, provider schemas,
  parsing services, and one provider-specific exception boundary.
- `src/mapi/api/deps.py`: FastAPI dependency construction and injectable test
  seams.
- `src/mapi/api/v1/`: versioned endpoint routers and HTTP error translation.
- `src/mapi/core/`: `APP_`-prefixed settings, middleware, application state,
  constants, and OpenAPI customization.
- `tests/`: unit, event, service, provider, and integration coverage mirroring
  the runtime boundaries.

Canonical routes are under `/api/v1/dsl`, `/api/v1/events`, `/api/v1/TM`, and
`/api/v1/GT`. Compatibility aliases under `/api/v1/row-progression` and the
legacy provider route names remain supported while clients migrate.

## Development Commands

Install dependencies and run the local service with:

```bash
uv sync --all-groups
uv run fastapi dev src/mapi/main.py
```

Run the narrowest relevant test first, for example:

```bash
UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run pytest \
  tests/unit/test_validators.py::test_name -q --no-cov
```

Use this non-mutating full gate before claiming a change is complete:

```bash
UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv lock --check
UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run ruff check . --no-cache
UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run ruff format . --check --no-cache
UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run mypy src --show-error-codes
UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run pytest -q --no-cov
git diff --check
```

The explicit cache path avoids local `uv` cache permission failures. Do not
classify a default-cache permission error as a project defect.

Do **not** use `make quality` for validation. It runs
`ruff check --fix --unsafe-fixes`, which rewrites files, and invokes mypy with
the nonexistent `tools` path. Pre-commit is also mutating: its Ruff, Prettier,
and whitespace hooks may rewrite files.

## Implementation Conventions

- Preserve strict mypy compatibility and precise public types. Fix root causes
  instead of adding broad ignores or weakening annotations.
- Keep async I/O async. Reuse the existing `httpx` client and service patterns,
  inject fakes through constructor or FastAPI dependency seams, and prefer
  `Protocol` types over inheritance for client contracts.
- Keep provider payloads behind provider boundaries. Expose normalized domain
  contracts rather than leaking upstream identifiers or response shapes.
- Read configuration through `src/mapi/core/config.py`; never hard-code or
  commit credentials. Tests and default demos must remain keyless.
- Map invalid client/domain input to HTTP 400 and provider failures to HTTP 502
  using the endpoint's established exception pattern.
- Preserve Schema.org public names and aliases, including `@type`, `startDate`,
  `endDate`, and `sku`.
- Preserve Venue DSL semantics: `!` consumes a physical position without
  returning a row, while names joined by `=` share one position.
- Add regression coverage at the closest boundary. Use unit/property tests for
  DSL rules, event tests for normalization and persistence, provider/service
  tests for upstream behavior, and integration tests for public HTTP contracts.
- Use Conventional Commits with a required scope if a commit is explicitly
  requested, for example `fix(mapi): preserve alias positions`.

## ExecPlans

For a complex feature, significant refactor, migration, cross-domain change, or
work spanning multiple independently verifiable milestones, create and maintain
an ExecPlan that follows `PLANS.md`. Store it at
`docs/plans/YYYY-MM-DD-<short-slug>.md`.

Localized bug fixes, focused tests, and small documentation edits may use a
short inline plan. If uncertainty grows into multiple milestones, promote the
work to an ExecPlan before continuing.

## Code Review Rules

- Flag any Venue DSL change that violates gap, alias, range, duplicate-name, or
  parse/compress equivalence behavior without a regression test.
- Flag Schema.org changes that rename public aliases, accept unsupported event
  types, or bypass Pydantic validation and review state.
- Flag blocking network I/O in async paths, unclosed clients, provider payloads
  crossing into public contracts, or provider errors escaping as HTTP 500.
- Flag committed secrets, credentials in fixtures/logs, or tests that require a
  live provider key.
- Flag removal of canonical or compatibility routes unless the change includes
  an explicit migration and compatibility decision.
- Flag documentation that claims unimplemented production behavior or conflicts
  with runtime routes, persistence, configuration, or verification commands.
