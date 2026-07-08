# Demo

## Install

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Run Tests

```bash
black --check .
isort --check-only .
ruff check .
mypy app
pytest --cov=app --cov-report=term-missing
```

## Run API

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Run CLI Import

```bash
python -m app.cli import-csv examples/csv/demo_venue_rows.csv
```

## Call `/parse`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/row-progression/parse \
  -H 'content-type: application/json' \
  -d '{"code":"AA:DD,A:C,8:19!,13=13W"}'
```

## Call `/import-rows`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/row-progression/import-rows \
  -H 'content-type: application/json' \
  -d '{
    "rows": [
      {"section": "101", "row": "AA", "position": 1},
      {"section": "101", "row": "BB", "position": 2},
      {"section": "101", "row": "13", "position": 20},
      {"section": "101", "row": "13W", "position": 20}
    ]
  }'
```

## Call `/venue-diff`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/row-progression/venue-diff \
  -H 'content-type: application/json' \
  -d '{
    "a": {"name": "Old Demo", "sections": {"101": "A:C"}},
    "b": {"name": "New Demo", "sections": {"101": "A:B,D"}}
  }'
```

## Call `/agent/analyze`

```bash
curl -X POST http://127.0.0.1:8000/api/v1/row-progression/agent/analyze \
  -H 'content-type: application/json' \
  -d '{
    "venue_id": "demo-arena",
    "section_id": "101",
    "code": "AA:DD,A:C,8:19!,13=13W",
    "question": "What should review focus on?"
  }'
```
