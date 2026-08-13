# CLAUDE.md

This file gives Claude Code concise, repository-specific guidance. `AGENTS.md`
is the authoritative agent guide; use `PLANS.md` for complex or multi-milestone
work.

## Working Agreements

- Inspect the worktree before editing and preserve unrelated staged, unstaged,
  and untracked changes.
- Make minimal, localized changes that preserve strict typing, async safety,
  package boundaries, compatibility routes, and existing public contracts.
- Do not stage broadly, commit, push, add production dependencies, or perform
  destructive actions unless the task explicitly authorizes them.
- Keep documentation conservative and verify claims against runtime code.

## Commands

```bash
uv sync --all-groups
uv run fastapi dev src/mapi/main.py
UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run pytest \
  tests/unit/test_validators.py::test_name -q --no-cov
make demo-cli
docker-compose up
```

Use the following non-mutating full gate before claiming completion:

```bash
UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv lock --check
UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run ruff check . --no-cache
UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run ruff format . --check --no-cache
UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run mypy src --show-error-codes
UV_CACHE_DIR=/private/tmp/mapi-uv-cache uv run pytest -q --no-cov
git diff --check
```

Do not use `make quality` for validation. It mutates files with
`ruff check --fix --unsafe-fixes` and passes the nonexistent `tools` path to
mypy. Pre-commit hooks may also rewrite Python, Markdown, YAML, and JSON files.

## Architecture

Mapi is a Python 3.13 FastAPI service with two bounded domains:

- **Venue DSL:** pure parsing, validation, compression, statistics, venue
  building, and diffing in `src/mapi/schemas/validators.py`, with Pydantic v2
  contracts in `src/mapi/schemas/`.
- **Event pipeline:** Schema.org-compatible event and offer normalization,
  ingestion contracts, and durable SQLite persistence in `src/mapi/events/`.

The rest of the repository keeps transport and orchestration separate:

- `src/mapi/services/`: CSV and provider orchestration.
- `src/mapi/providers/<provider>/`: async clients, provider schemas, parsing
  services, and provider-specific exceptions.
- `src/mapi/api/deps.py`: injectable service and repository dependencies.
- `src/mapi/api/v1/`: public routes and HTTP error translation.
- `src/mapi/core/`: `APP_`-prefixed settings, middleware, state, constants, and
  OpenAPI customization.

Canonical routes are `/api/v1/dsl`, `/api/v1/events`, `/api/v1/TM`, and
`/api/v1/GT`. Legacy row-progression and provider route aliases remain for
compatibility.

## Conventions

- Preserve Venue DSL semantics: `!` consumes a position and returns no row;
  names joined by `=` share one position.
- Keep provider payloads internal and expose normalized Pydantic contracts.
- Keep async I/O async, inject client fakes through existing seams, and prefer
  `Protocol` client contracts over inheritance.
- Map invalid input to HTTP 400 and provider failures to HTTP 502 using the
  established endpoint patterns.
- Preserve Schema.org aliases including `@type`, `startDate`, `endDate`, and
  `sku`.
- Read secrets through settings, never commit them, and keep tests keyless.
- Add regression tests at the closest boundary, then run the full gate.
- Use Conventional Commits with a required scope only when a commit is
  explicitly requested.

## Planning

For complex features, significant refactors, migrations, cross-domain changes,
or multi-milestone work, create a living ExecPlan under
`docs/plans/YYYY-MM-DD-<short-slug>.md` and follow `PLANS.md`. Small localized
fixes, tests, and documentation edits may use a short inline plan.
