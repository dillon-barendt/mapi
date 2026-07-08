install:
	python -m pip install --upgrade pip
	python -m pip install -e ".[dev]"

dev:
	uvicorn app.main:app --reload

test:
	pytest --cov=app --cov-report=term-missing

quality:
	black --check .
	isort --check-only .
	ruff check .
	mypy app
	pytest --cov=app --cov-report=term-missing

demo-cli:
	python -m app.cli import-csv examples/csv/demo_venue_rows.csv
