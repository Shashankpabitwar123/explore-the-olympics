# Understand the data

The source folder holds five related CSV tables. Counts describe this saved snapshot.

| File | One row represents | Rows | Key and relationship |
|---|---|---:|---|
| `editions.csv` | One Olympic edition | 55 | `id`; includes year, season, city, host, dates and source URL |
| `events.csv` | One event within an edition | 7,098 | `id`; `edition` links to editions |
| `awards.csv` | One recorded medal award | 21,821 | `id`; `event_id` links to events; `noc` links to countries |
| `countries.csv` | One delegation/NOC code | 233 | `noc`; includes historical and special delegations |
| `roster_members.csv` | One recorded member of an award roster | 31,194 | `award_id` links to awards; `member_order` preserves order |

## Counting rules

- Medal codes are **1 = gold, 2 = silver, 3 = bronze**.
- Count distinct award IDs for medal awards. A team award remains one award regardless of roster size.
- Roster rows are appearances in recorded award rosters, not a count of unique people. The same person can appear more than once.
- Country codes describe delegations, not necessarily present-day sovereign countries. Historical delegations are retained separately.
- An edition is not the same as a gallery destination. Melbourne and the separately hosted Stockholm equestrian events produce two host destinations for the 1956 Summer edition.
- Event totals come from distinct event IDs. The source includes historical disciplines and art competitions.
- Missing facts such as performance, venue or event date may be recorded as `Not recorded`; they are not zero values.
- `is_team` distinguishes team awards. `roster_source` records supplemental roster provenance where available.

## Published extract

The Hyper extract has **117,468 presentation rows**, including awards, result text and control geometry. This is not an athlete count. For example, each event control has four vertices, so 28,392 event-control rows represent 7,098 events.

Filter `RowType = Award` before counting awards in the extract. Use distinct `EventID` for events. The [checking script](../scripts/check_and_export.py) applies these rules and reconciles them with the source tables.

Twenty-two historical hurdle labels are clarified for display as 80 m or 100 m. One blank winner label falls back to its recorded country. Original source values remain unchanged in the CSVs.

## Summary exports

`data/summary/editions.csv` counts events, distinct sports and medal awards within each edition. Ties and events with multiple bronze awards can make medal counts differ from a simple three-times-events calculation.

`data/summary/paris-2024-womens-100m.csv` reproduces the opening podium directly from the published extract.
