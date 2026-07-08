# Ticketmaster Discovery Feed Provider

Mapi can optionally fetch Ticketmaster Discovery Feed 2.0 event metadata by
country.

The feed provides event-level data and includes `legacyEventId`, which can be
used as the bridge into Ticketmaster Maps `placeDetail` metadata.

Official docs:

```text
https://developer.ticketmaster.com/products-and-docs/apis/discovery-feed/
```

Endpoint shapes:

```text
https://app.ticketmaster.com/discovery-feed/v2/events.csv?apikey={TICKETMASTER_API_KEY}&countryCode=US
https://app.ticketmaster.com/discovery-feed/v2/events.json?apikey={TICKETMASTER_API_KEY}&countryCode=US
https://app.ticketmaster.com/discovery-feed/v2/events?apikey={TICKETMASTER_API_KEY}
```

Mapi reads the API key from `TICKETMASTER_API_KEY` or
`APP_TICKETMASTER_API_KEY`. The key is never hardcoded in source, tests, docs, or
fixtures.

Downloaded production feed files should not be committed. Feed payloads can be
large, time-sensitive, and provider-owned. Production ingestion should cache feed
metadata, track checksums or timestamps, and store only data needed for broker
review workflows.

Pipeline:

```text
Discovery Feed 2.0 event
        ↓
legacyEventId
        ↓
Ticketmaster Maps placeDetail lookup
        ↓
Mapi normalized map summary
```
