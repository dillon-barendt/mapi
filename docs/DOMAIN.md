# Domain: Events, Offers, and Venue Maps

The production domain is a normalized event catalog. Events use Schema.org
structures: `Event`, `ComedyEvent`, `SportsEvent`, `TheatreEvent`, `MusicEvent`,
and `Festival`. Ticket products are represented as `Offer` records linked to an
event and retain marketplace identifiers for downstream product lookup.

Source ingestion accepts sitemap URLs, marketplace Page Object Models, and
Scrapy spider records. A bounded classifier can assign the Schema.org subtype;
unknown or low-confidence records remain reviewable rather than being silently
promoted to a specialized type. The normalized records are persisted in the
production event store and served through `GET /api/v1/events` for a React Server
Component and MUI DataGrid.

Ticketing venue maps look simple until brokers, marketplaces, and inventory
systems need to agree on the same section-row shape. A section might contain
numeric rows, alphabetic rows, repeated-letter rows, row aliases, and physical
gaps where neighboring sections own the skipped positions.

Mapi models that problem with a compact row progression DSL. The DSL stores a
section as one string that can be parsed, validated, compressed, diffed, and
indexed for automated review workflows.

## Row Progression Codes

A row progression code is a comma-delimited list of atomic row codes, ranges,
gap ranges, and equivalent rows.

```text
DD:AA,A:C,1:4,5!,6:10:2,12=12W,ZZZ
```

This expands to:

| Row | Position |
| --- | -------: |
| DD  |        1 |
| CC  |        2 |
| BB  |        3 |
| AA  |        4 |
| A   |        5 |
| B   |        6 |
| C   |        7 |
| 1   |        8 |
| 2   |        9 |
| 3   |       10 |
| 4   |       11 |
| 6   |       13 |
| 8   |       14 |
| 10  |       15 |
| 12  |       16 |
| 12W |       16 |
| ZZZ |       17 |

Position 12 is consumed by `5!`, but no row named `5` is returned.

## Atomic Rows

Atomic rows are single row names:

- Numeric: `1`, `2`, `12`
- Repeated-letter families: `A`, `B`, `AA`, `BB`, `CCC`
- Mixed rows: `12W`, `A1`, `21WC`

Mixed rows are valid as single rows and equivalent aliases, but they are not
rangeable because `A1:B1` has no reliable venue-independent ordering.

## Ranges

Ranges are inclusive and can ascend or descend.

| Code      | Rows                              |
| --------- | --------------------------------- |
| `1:4`     | `1`, `2`, `3`, `4`                |
| `5:1`     | `5`, `4`, `3`, `2`, `1`           |
| `1:6:2`   | `1`, `3`, `5`                     |
| `A:D`     | `A`, `B`, `C`, `D`                |
| `D:A`     | `D`, `C`, `B`, `A`                |
| `AA:DD`   | `AA`, `BB`, `CC`, `DD`            |
| `HHH:DDD` | `HHH`, `GGG`, `FFF`, `EEE`, `DDD` |

Repeated-letter ranges stay inside one family. `AA:DD` does not mean Excel-style
labels `AA`, `AB`, `AC`, `AD`; it means row labels `AA`, `BB`, `CC`, `DD`.

## Equivalent Rows

Equivalent rows use `=` and share one physical position.

```text
1:2,3=3W
```

This returns `1` at position 1, `2` at position 2, and both `3` and `3W` at
position 3.

## Gap Rows

Gap rows use `!`. They consume physical position while returning no row.

```text
A,B!,C
```

This returns `A` at position 1 and `C` at position 3. Position 2 exists in the
section alignment but belongs somewhere else or is intentionally skipped.

## Guardrails

Mapi rejects:

- Empty segments such as `A,,B`
- Mixed ranges such as `A1:B1`
- Unequal repeated-letter families such as `A:AA`
- Zero or negative range steps
- Duplicate returned row names

Gaps do not create returned rows, so a gap label cannot collide with an actual
row name.
