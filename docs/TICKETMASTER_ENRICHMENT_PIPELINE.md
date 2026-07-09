# Ticketmaster Enrichment Pipeline

```text
Discovery Feed 2.0
        ↓
Event record
        ↓
legacyEventId
        ↓
Maps placeDetail provider
        ↓
Raw map payload
        ↓
Normalized Mapi summary
        ↓
Redis/cache/review workflows
```

Mapi now has an optional provider-backed enrichment layer. Discovery Feed events
provide `legacyEventId` values, and those IDs can be used to request
Ticketmaster Maps `placeDetail` payloads. Mapi stores the raw provider payload
separately from a conservative normalized summary that is safer to expose to API,
Redis, and agent review workflows.

Production considerations:

- Daily Discovery Feed refresh by country.
- Feed metadata checksum or timestamp tracking.
- Cache invalidation when feed metadata changes.
- Rate-limited `placeDetail` fetches.
- Queue-backed enrichment jobs for large country feeds.
- Resume/retry support for interrupted jobs.
- Per-event error recording instead of all-or-nothing batch failure.
- Redis keys for raw provider payloads and normalized summaries.
- Agent review triggers for missing maps, changed section counts, or suspicious
  venue metadata drift.

Redis examples:

```text
SET ticketmaster:discovery:US:last_updated "2026-07-08T00:00:00Z"

SADD ticketmaster:discovery:US:legacy_event_ids "3B00633EA89923F8"

SET venue:tm:event:{legacy_event_id}:place_detail:raw "{...}"

HSET venue:tm:event:{legacy_event_id}:place_detail:summary \
  source "ticketmaster_maps" \
  parser_version "0.1.0" \
  has_payload "true"
```

The sample enrichment endpoint requires an explicit small limit and caps sample
size at 100 events. Full country-feed enrichment should be implemented as a
background worker with provider-aware rate limits and resumable state.
