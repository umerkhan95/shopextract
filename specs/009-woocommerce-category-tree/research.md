# Bounded production research — 2026-10-24

Author: `/root/woo_author`. W02 only; production implementation and executable
skeleton wait for independent G1. Existing dirty files are preserved.

## Official source findings
Consulted the following current primary sources via browser on 2026-10-24.
These are upstream documentation/trunk observations, not proof of any deployed
store version. No commercial-store probe was made.

- [Category API reference](https://developer.woocommerce.com/docs/apis/store-api/resources-endpoints/product-categories/)
  documents the public category list, pagination, `hide_empty` and parent.
- [TermSchema](https://raw.githubusercontent.com/woocommerce/woocommerce/trunk/plugins/woocommerce/src/StoreApi/Schemas/V1/TermSchema.php)
  exposes ID/name/slug/parent and serializes actual term parent as integer.
- [ProductCategorySchema](https://raw.githubusercontent.com/woocommerce/woocommerce/trunk/plugins/woocommerce/src/StoreApi/Schemas/V1/ProductCategorySchema.php)
  inherits the term schema. Thus parent support exists upstream; missing/null
  deployed fields still remain unknown and cannot be synthesized.
- [AbstractTermsRoute](https://raw.githubusercontent.com/woocommerce/woocommerce/trunk/plugins/woocommerce/src/StoreApi/Routes/V1/AbstractTermsRoute.php)
  uses offset pagination. Crucially it emits totals only when a positive page
  size returns a full page OR the requested page is greater than one. First
  short/empty pages normally lack headers. Supported order keys include slug;
  ID ordering is not supported. Use `orderby=slug&order=asc`, never invented ID ordering.
- [Pagination](https://raw.githubusercontent.com/woocommerce/woocommerce/trunk/plugins/woocommerce/src/StoreApi/Utilities/Pagination.php)
  sets `X-WP-Total` and `X-WP-TotalPages`; links are navigation hints. Traversal
  constructs its own next numbered query and does not trust Link destinations.

## Guarded transport audit and reuse decision
`tools/security.py` normalizes HTTP(S), rejects URL credentials/fragments,
checks an exact origin allowlist and requires all DNS answers public. Its
`PinnedBackend.connect_tcp` resolves/checks again and connects to the checked
numeric IP; HTTP Host/TLS retains the original origin. The network backend does
not perform an uncontrolled second hostname lookup. This closes DNS rebinding
through independently resolving fetches; a separate post-connect peer query is
unnecessary for this pinned socket path. Test the actual pinned backend with a
controlled connector, not merely mocked SourceGuard calls.

`GuardedTransport` uses one connection, no keepalive, HTTP-core `retries=0`,
checks redirects with the same guard, charges requests before wire calls, and
closes response streams in finally. It forces identity transfer encoding and
rejects any other content encoding before decoding. Its streamed identity
response cap also bounds decoded bytes. Compressed sources are unsupported,
not a decompression path. Redirect bodies are not retained. No automatic retry
will be added despite ToolError's generic `retryable` metadata.

Gaps owned by the acquisition wrapper: there is no whole-fetch deadline or
cancellation polling while an existing response body blocks. Wrap the complete
fetch (DNS/connect/headers/body) in a remaining-deadline wait and race it with an
external cancellation event; cancel and await the owned fetch task, close client
and transport, and reap the owned resolver process. Check deadline/cancel between
pages and during bounded parsing/graph work. SourceGuard's existing resolver
cap is two seconds. Reuse `OperationContext`, `OperationBudget`, `Limits`,
`ToolConfig`, `SourceGuard`, `GuardedTransport`, `OwnedProcess`; do not alter the
unrelated dirty shared transport/runtime files or use ToolRuntime's stricter
positive-only configuration validation for zero-cap acquisition.

Only the normalized store origin is allowlisted. This yields same-origin-only
redirects; scheme, port and host changes are denied before the destination wire
call. URL credentials and fragments reject before DNS. No caller credential or
cookie API is exposed. Endpoint construction preserves a supplied installation
base path, rejects a store URL query, and appends the fixed Store API route.

## Ratified behavior decisions for G1
- Ceilings: 10 HTTP attempts (redirects/failures included), 100/page, 1,000 input
  category records accepted for retention (including malformed/duplicate/conflicting
  entries), 2 MiB identity body/page, 8 MiB aggregate retained evidence, depth 8,
  30 seconds overall. One sequential worker, no retries or inference.
- Integers must be real integers, excluding bool; seconds may be finite numeric.
  Values may only lower ceilings. Zero request/item/page/body/retention/time caps
  perform no network work and return unavailable with the applicable reason;
  zero depth permits roots and flags every nonroot expansion. Invalid configuration
  raises before I/O. Exact category/body/retention caps can complete only with
  independent terminal coverage; never request extra categories to test the cap.
- Header policy: both totals must be decimal nonnegative integers, pages must
  equal ceil(total/page_size), and every observed pair must agree. First page
  with neither header may continue once only when short/empty, because upstream
  deliberately suppresses those headers in that case. A full headerless first
  page stops partial immediately; it does not receive a confirmation request. Page two must provide valid totals;
  absent/malformed/one-sided headers then stop partial. A malformed header pair
  on any page stops partial immediately. Valid earlier facts remain retained.
- Completion requires all expected numbered pages (or the special page-two
  confirmation of a headerless short/empty first page), consistent page lengths,
  total raw entry count AND distinct usable IDs equal to total, no malformed
  records/facets or conflicting IDs, no repeated nonempty page, and no exhausted
  resource with remaining work. An empty page with consistent totals zero
  confirms empty only when no records were observed. A page-two confirmation
  must be empty when total fits in page one. This is bounded observed traversal,
  not an atomic snapshot or private/unpublished coverage proof.
- Missing/null parent is unknown; malformed ID/name/slug/parent facets remain
  inspectable alongside valid siblings and prevent complete data coverage.
  Orphans/cycles/depth are graph diagnostics independent of transport completion;
  report graph integrity separately. Never invent roots or product memberships.
- Status precedence: complete only on proven coverage; otherwise partial if any
  valid page was retained, malformed if the first response has malformed JSON/
  collection shape, unavailable if no valid page exists due to denial/failure/
  zero budget/cancellation. Reasons preserve all encountered distinctions. A
  valid empty first page followed by failure is partial, never confirmed empty.
- Item accounting happens per raw array entry before semantic deduplication.
  Retention accounting must include raw values, pointers, timestamps, page URLs,
  headers needed for coverage, facts and conflicting declarations. G2 defines
  exact wire representation; account canonical UTF-8 serialized retained page
  evidence plus derived result records before accepting a page/entry. If a page
  cannot fit, retain prior pages only and mark partial; attempt ledger remains
  separately bounded to ten fixed-size metadata entries, not arbitrary headers.
- Product linking is a separate explicit lookup of existing captured Woo
  memberships against same-merchant tree IDs. Return linked/missing/conflicting/
  scope-mismatch outcomes without mutating companion observations. Index presence
  never creates membership. Optional Shopify bridge SC09/10 is deferred; existing
  exact mapping remains unchanged and its regression boundary is still tested.

## Existing category seams and compatibility
Reuse `categories/helpers.py` merchant scope and opaque positive-int-to-text /
nonblank-text native ID conversion. Booleans/nonpositive integer IDs are invalid;
nonblank string IDs stay opaque, including numeric strings, exactly as the
existing Woo product adapter. Parent integer zero is a root marker, not an ID.
Do not rewrite label HTML or guess IDs from slugs. Reuse `source_fact` and captured
source evidence where compatible. `CategoryFactBinding` lacks a slug facet, and
existing product portable envelopes have a 256 KiB cap: a bounded tree needs its
own envelope/codec, not insertion of the whole index into every product record.
G2 specifies evidence types and strict round-trip seam. Existing index/parent
observations are excluded by `mapping.py`; preserve those boundaries. No tree
enters maintenance snapshots or removal inference in this slice.

## Research execution / limits
Five small official pages plus bounded existing-code reads; no inference,
commercial-store probes, tests, parallel agents or production edits. Actual
session token counters unavailable to this author; no quota estimate inferred.
All W02 decisions are proposals awaiting independent G1 approval, not gate passes.
