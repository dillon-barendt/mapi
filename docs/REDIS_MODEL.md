# Redis Model

Mapi treats the row progression string as the compact source representation and
expanded rows as a cacheable derivative. The examples below are synthetic.

## Redis String

Store the compact section code directly when the section is the lookup unit.

```redis
SET venue:demo-arena:section:101:row_progression "AA:DD,A:C,1:12,13=13W"
```

Good for:

- Fast section lookup
- Small memory footprint
- Change detection by comparing compact strings

## Redis Hash

Use a hash when a section has several related fields.

```redis
HSET venue:demo-arena:section:101 \
  row_progression "AA:DD,A:C,1:12,13=13W" \
  row_count "20" \
  updated_by "synthetic-import" \
  parser_version "0.1.0"
```

Good for:

- Keeping parser metadata next to the compact code
- Updating one field without rewriting the whole document
- Fetching all section metadata in one call

## Redis JSON

Cache expanded rows as a JSON derivative. The compact code remains the source
value; the expanded rows can be regenerated when parser logic changes.

```redis
JSON.SET venue:demo-arena:section:101:expanded $ '{
  "venue_id": "demo-arena",
  "section_id": "101",
  "row_progression": "AA:DD,A:C,1:12,13=13W",
  "rows": [
    {"name": "AA", "position": 1},
    {"name": "BB", "position": 2},
    {"name": "CC", "position": 3},
    {"name": "DD", "position": 4},
    {"name": "13", "position": 20},
    {"name": "13W", "position": 20}
  ]
}'
```

Good for:

- Agent tools that need row-level context without reparsing
- UI preview endpoints
- Diff workflows that compare expanded rows across venue revisions

## Queryable Representation

With Redis Query Engine, store compact and derived fields that support section
search and review workflows.

Example index shape:

```redis
FT.CREATE idx:venue_sections ON JSON PREFIX 1 venue: \
  SCHEMA \
    $.venue_id AS venue_id TAG \
    $.section_id AS section_id TAG \
    $.row_progression AS row_progression TEXT \
    $.row_count AS row_count NUMERIC \
    $.has_equivalents AS has_equivalents TAG \
    $.has_gaps AS has_gaps TAG
```

Example document:

```redis
JSON.SET venue:demo-arena:section:101:index $ '{
  "venue_id": "demo-arena",
  "section_id": "101",
  "row_progression": "AA:DD,A:C,1:12,13=13W",
  "row_count": 20,
  "has_equivalents": "true",
  "has_gaps": "false"
}'
```

Queries:

```redis
FT.SEARCH idx:venue_sections '@venue_id:{demo-arena} @has_equivalents:{true}'
FT.SEARCH idx:venue_sections '@venue_id:{demo-arena} @row_count:[10 50]'
```

## Agent Workflow Relevance

Venue changes can trigger downstream review without exposing customer data.

1. Import a new compact venue map.
2. Parse and validate each section.
3. Store compact strings and expanded row caches in Redis.
4. Diff the new compact map against the previous revision.
5. Publish changed sections to a review queue.
6. Let an agent summarize affected inventory, suspicious gaps, aliases, or row
   count changes for a human operator.

Synthetic event payload:

```json
{
  "event": "venue.section.changed",
  "venue_id": "demo-arena",
  "section_id": "101",
  "old_row_progression": "AA:DD,A:C,1:12",
  "new_row_progression": "AA:DD,A:C,1:12,13=13W",
  "review_reason": "equivalent-row-added"
}
```

This keeps the workflow auditable: the compact code is the input, expanded rows
are deterministic, and diffs explain why a downstream marketplace or inventory
review was requested.
