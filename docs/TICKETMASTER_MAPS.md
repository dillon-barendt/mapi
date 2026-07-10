# Ticketmaster Maps Provider

Mapi can optionally fetch Ticketmaster-served place-detail metadata by
Ticketmaster Legacy Event ID.

The provider is intended for venue-map enrichment, broker review workflows, and
future section/place/seat metadata normalization.

Example request shape:

```bash
curl 'https://mapsapi.tmol.io/maps/geometry/3/event/3B00633EA89923F8/placeDetail?systemId=HOST' \
  -H 'Referer: https://cims.ticketmaster.com/' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36'
```

Browser-like provider headers are isolated inside
`src/mapi/providers/ticketmaster_maps/client.py`. Domain services and API routes do
not know about those headers.

Mapi keeps raw and normalized provider data separate:

- `TicketmasterPlaceDetailRaw` wraps the original provider payload.
- `TicketmasterPlaceDetailSummary` exposes conservative broker-useful metadata
  such as top-level keys, venue name, event name, section count, and place count.

The current summarizer intentionally avoids deep assumptions about the full
Ticketmaster geometry schema until stable captured fixtures are available.
