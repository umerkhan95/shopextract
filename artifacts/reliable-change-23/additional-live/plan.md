# Additional native storefront live verification — 2026-10-16

Predeclared before execution. User authorized additional live tests before merge.
Sequential platforms, one process and one HTTP connection, no retries/redirect
following. Four requests maximum: two Magento native GraphQL then two Woo Store
API. Each whole request <=20 seconds, body <=1 MiB, <=2 retained products and
<=4 variants/product. Total network ceiling 80 seconds; no discovery or expansion.

Targets:
- https://magento2-demo.magebit.com/graphql using the repository extractor's
  read-only Catalog query, size=2/page=1.
- https://demo.athemes.com/botiga/wp-json/wc/store/v1/products?per_page=2&page=1

Per platform first capture->normalize->partial-snapshot->load smoke is saved
before repeat and before the next platform. Assert qualified retained evidence
lookup source URL, exact capture time and pointer values; inspect support for
price/currency/stock and report unsupported honestly. Assert anchored identities
stable across shared records, report source references valid, partial snapshots
never confirm removals, replay emits zero new events. Actual commercial changes
are inconclusive if captures have no difference; never invent an expected change.

Separately labelled offline-derived partial sample drops one captured product;
assert no removal event. No synthetic price or stock changes and no live mutation.
Any HTTP/schema/access failure is blocked, no blind repair; continue independent
platform. Save raw response/SQLite/report only under ignored raw/. Driver, plan
and compact summary are reviewable. No dependencies installed or source edits.
