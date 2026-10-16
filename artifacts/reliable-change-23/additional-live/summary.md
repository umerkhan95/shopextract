# Additional live verification result — 2026-10-16

PASS: four sequential requests, no retries or redirects; both native sources
completed initial smoke before repeat and the next platform. Each capture retained
two products; Magento retained four variants per product, Woo none.

| Source | Requests | Response bytes/capture | Qualified evidence checks | Result |
| --- | --- | --- | --- | --- |
| Magento native GraphQL | 2 | 28,843 | 132 + 132 | PASS |
| Woo Store API | 2 | 11,789 | 27 + 27 | PASS |

Price, currency and stock had observed source support for all captured products.
Shared anchored product IDs remained stable. Source URL/time/pointer round-trips
passed 318 evidence checks. Both live comparisons produced zero events and their
replays zero new events. Missing-field diagnostics remained explicit (two per
comparison). Separately labelled offline-derived partial omissions confirmed zero
removals. No source values were mutated.

Actual commercial-change verification is inconclusive: repeat captures had no
tracked differences. No blocked platform or execution error. Raw responses, report
and SQLite databases remain under ignored raw/; compact exact results summary.json.
