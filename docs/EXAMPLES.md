# Examples

Run the API locally:

```bash
uvicorn app.main:app --reload
```

The OpenAPI UI is available at:

```text
http://127.0.0.1:8000/docs
```

## Parse One Section

Request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/row-progression/parse \
  -H 'content-type: application/json' \
  -d '{"code":"AA:DD,A:C,1:12,13=13W"}'
```

Response excerpt:

```json
{
  "code": "AA:DD,A:C,1:12,13=13W",
  "rows": [
    {"name": "AA", "position": 1},
    {"name": "BB", "position": 2},
    {"name": "CC", "position": 3},
    {"name": "DD", "position": 4},
    {"name": "13", "position": 20},
    {"name": "13W", "position": 20}
  ]
}
```

## Parse Gaps

```text
A,B:C!,D
```

Result:

```json
[
  {"name": "A", "position": 1},
  {"name": "D", "position": 4}
]
```

Rows `B` and `C` are gap markers. They consume positions 2 and 3 without being
returned as rows in this section.

## Compress Expanded Rows

Request:

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

The generated gap labels are canonical position placeholders. Parsing the
compressed code returns the same row names and positions.

## Build a Venue

```bash
curl -X POST http://127.0.0.1:8000/api/v1/row-progression/build-venue \
  -H 'content-type: application/json' \
  -d '{
    "venue_name": "Demo Arena",
    "sections": [
      {"name": "101", "code": "AA:DD,A:C,1:12,13=13W"},
      {"name": "102", "code": "A,B:C!,D"}
    ]
  }'
```

## Diff Venues

```bash
curl -X POST http://127.0.0.1:8000/api/v1/row-progression/venue-diff \
  -H 'content-type: application/json' \
  -d '{
    "a": {"name": "Old Demo", "sections": {"101": "A:C"}},
    "b": {"name": "New Demo", "sections": {"101": "A:B,D"}}
  }'
```

Response:

```json
{
  "venue_diff": {
    "101": {
      "C": {"a": 3, "b": null},
      "D": {"a": null, "b": 3}
    }
  }
}
```

## Stats

```bash
curl -X POST http://127.0.0.1:8000/api/v1/row-progression/stats \
  -H 'content-type: application/json' \
  -d '{"code":"AA:CC,1=1W"}'
```

Response excerpt:

```json
{
  "code_type": "mixed",
  "total_rows": 5,
  "unique_row_count": 5,
  "unique_position_count": 4,
  "unique_names": ["1", "1W", "AA", "BB", "CC"],
  "segment_count": 2
}
```

## Agent Analysis

The Mapi agent is backed by Pydantic AI. By default it uses a local function
model, so this works without an external API key.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/row-progression/agent/analyze \
  -H 'content-type: application/json' \
  -d '{
    "venue_id": "demo-arena",
    "section_id": "101",
    "code": "AA:CC,1=1W",
    "question": "What should a broker review?"
  }'
```

Response excerpt:

```json
{
  "analysis": {
    "friendly_name": "Mapi is a friendly name for a mapping API...",
    "parser_confidence": "valid",
    "review_triggers": [
      "Equivalent row alias detected; verify shared-position rows.",
      "Range expansion used; validate start/end row family semantics."
    ],
    "redis": {
      "string_key": "venue:demo-arena:section:101:row_progression",
      "hash_key": "venue:demo-arena:section:101",
      "json_key": "venue:demo-arena:section:101:expanded",
      "index_document_key": "venue:demo-arena:section:101:index"
    }
  },
  "agent_model": "function:mapi-local"
}
```
