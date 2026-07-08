PYTHON ?= .venv/bin/python

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

dev:
	$(PYTHON) -m uvicorn app.main:app --reload

test:
	$(PYTHON) -m pytest --cov=app --cov-report=term-missing

quality:
	$(PYTHON) -m black --check .
	$(PYTHON) -m isort --check-only .
	$(PYTHON) -m ruff check .
	$(PYTHON) -m mypy app
	$(PYTHON) -m pytest --cov=app --cov-report=term-missing

demo-cli:
	$(PYTHON) -m app.cli import-csv examples/csv/demo_venue_rows.csv
