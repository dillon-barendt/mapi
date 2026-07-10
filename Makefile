PYTHON ?= .venv/bin/python

install:
	uv sync --all-groups

dev:
	uv run fastapi dev src/mapi/main.py

test:
	uv run pytest --cov=mapi --cov-report=term-missing

quality:
	uv run ruff format . --check
	uv run ruff check --fix --unsafe-fixes
	uv run mypy src tools
	uv run pytest --cov=mapi --cov-report=term-missing

demo-cli:
	uv run python -m mapi.cli import-csv examples/csv/demo_venue_rows.csv
