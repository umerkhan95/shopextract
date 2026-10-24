# G2 skeleton — 2026-10-24

Author `/root/woo_author`; follows recorded G1 pass. No business logic.
Declarations and explicit `NotImplementedError` operations are in
`src/shopextract/categories/woo_tree.py`. This opt-in module is not re-exported
from default extraction or category APIs during skeleton work.

## Public contracts
`fetch_woocommerce_category_tree(CategoryScope, *, limits=WooTreeLimits(),
cancelled=None, resolver=None, wire_transport=None, utc_now=None)` is async and
returns `WooCategoryTree`. Scope must be WooCommerce. Preserve supplied merchant
catalog/channel/locale dimensions and installation base path. Default clock is
UTC now at successful receipt of each bounded response. Injected clock is a
trusted deterministic test boundary; reject naive/non-UTC timestamps. Resolver
and wire hooks replace unavailable external boundaries, never graph/parser logic.
Production uses checked numeric-IP connections with existing transport.

`WooTreeLimits` fixes the reviewed ceilings; validate before DNS/I/O. Limits may
lower to zero; depth zero permits roots. Invalid types/configuration raise
`CategoryError`. Denied URL is an unavailable result without DNS/wire calls.
Transport/cancellation failures return retained bounded result/reasons; external
Task.cancel propagates CancelledError after cleanup, while the explicit event
returns unavailable/partial with `cancelled`. No retries or restart/merge.

`WooCategoryTree` owns scope, immutable limits, outcome/reasons, receipt pages,
node declarations, rejected entries, supported edges, integrity issues and attempt
ledger. Tree facts carry their own actual JSON pointer, source URL/time, raw value,
normalized value and observed/missing/null/malformed state. Missing raw values
use None distinguished by state. Root parent 0 normalizes to string `0`; absent/
null parent has no normalized value. IDs reuse opaque existing Woo semantics;
labels/slugs remain verbatim nonblank text. No universal taxonomy or membership
observation is created. A separate tree fact shape accommodates slug and parent
root without changing existing product fact contracts.

Each raw array entry creates one declaration, including malformed entries.
Usable IDs group into nodes, invalid IDs stay in `rejected`. Equal normalized
facet/state declarations may coalesce semantically, but every raw declaration
remains inspectable/countable. Conflicting facets flag the node, retaining all
competing facts; no edge is selected for a conflicting child or conflicting
parent. Parent zero declares root, no edge; unknown/malformed parent creates no
edge. Orphan/self/cycle/depth diagnostics are explicit. Edges involving cycle
nodes or descendants beyond bounded ancestry are withheld; depth 8 edges are
accepted, root depth is zero. Graph integrity issues do not by themselves erase
otherwise complete traversal; consumers inspect both fields. Malformed facets,
duplicate IDs/count inconsistency/conflicts do prevent complete coverage.

`link_tree_memberships(tree, observations)` returns one `TreeMembershipLink` per
captured membership term. Match exact Woo namespace plus complete CategoryScope
and merchant_scope identity. Category observations with other relations produce
no links. Unsupported namespace or missing native ID is unsupported; foreign
scope is scope_mismatch; absent tree ID is missing; conflicted node conflicting;
otherwise linked. Matching a ref alone is insufficient: a bound `native_id`
fact must match the exact term ref, have `SupportState.OBSERVED`, an accepted
conversion whose normalized value equals the native ID, and nonempty source
evidence, reusing `mapping._supported` semantics. Missing/rejected/mismatched or
evidenceless native-ID facts return unsupported even when the ref names a tree
node. Scope mismatch takes precedence over evidence validation. A partial tree can link a positively observed unconflicted ID,
while missing remains unresolved, not proof of absence. No source object mutates;
no ancestor/category guess, mapping or product creation occurs.

`woo_tree_to_record` / `woo_tree_from_record` own a strict version-1 tree envelope.
Invalid tree/record raises CategoryError, never silently trims or repairs.
A plain record round-trip is supported independently of product/maintenance
portable envelopes, which remain unchanged.

## Canonical accounting and portable validation
Envelope exactly `{"schema_version":1,"payload":<wire WooCategoryTree>,
"sha256":<SHA256 canonical payload>}`. Canonical JSON is existing sorted-key,
compact, ensure_ascii=False, allow_nan=False UTF-8 via category codec primitives.
`payload` includes all dataclass fields (including schema_version, limits,
scope, raw page body text, page URLs/times/header strings, duplicate declarations,
normalized facts, derived nodes/edges/issues, reasons and bounded attempts).
Complete envelope bytes, including digest and all derived metadata, must fit
`limits.retained_bytes` (maximum 8 MiB). This is a serialized retention ceiling,
not an assertion about total interpreter memory. Pending response body allocation
is separately bounded at 2 MiB; graph work at 1,000 raw retained declarations.

For each new page, build a bounded candidate page + graph and terminal record,
measure the complete canonical envelope before committing it. A refused page
retains none of that page's facts/body; previous accepted pages survive with
partial/resource reason. Reserve finalization bytes up front: admission measures
all terminal states/reasons permitted by the state machine, fixed-length SHA256,
and ten maximum-size attempt slots. This conservative reservation can refuse
before the nominal cap; final output must always fit. If even minimal terminal
envelope plus bounded reservation cannot fit, return a minimal unavailable result
with no pages; `to_record` raises if caller's lowered cap cannot encode it. Thus
zero/small caps can still return an in-memory diagnostic without pretending a
serializable capture exists. Exact-cap tests derive size from this admission
reservation, not only raw bodies. Error metadata never contains arbitrary remote
text. Page-atomic refusal also applies when raw entry count exceeds remaining
category capacity; attempts remain charged.

Fixed local reason/issue vocabulary: `cancelled`, `deadline`, `request_limit`,
`category_limit`, `response_limit`, `retention_limit`, `zero_budget`, `unsafe_url`,
`url_limit`, `transport_error`, `http_status`, `unsupported_content_encoding`,
`malformed_json`, `malformed_collection`, `malformed_facet`, `missing_headers`,
`malformed_headers`, `totals_changed`, `count_mismatch`, `repeated_page`,
`duplicate_id`, `conflicting_id`, `missing_parent`, `self_parent`, `cycle`,
`depth_limit`, `unknown_parent`. New local codes require affected test/design
review. Remote strings never become codes.

Metadata ceilings before retention: normalized initial/page/redirect URLs 4,096
UTF-8 bytes; total headers 20 ASCII decimal characters; per-page body bounded
UTF-8 (invalid UTF-8 is malformed); at most ten TreeAttempt entries. Ledger stores
only ordinal, SHA256 of actual wire URL, HTTP integer status or None, and a fixed
allowlisted local reason code or None. No unbounded Location/body/header/error
messages enter the ledger. The same URL ceiling is enforced on redirect targets
before the next wire call. Canonical outcome/reason/issue codes come from fixed
local sets; node_ids reference retained IDs and count against the envelope.

Reload first checks encoded tree node/depth limits and absolute 8 MiB ceiling,
strict exact fields/types/version, limits and declared cap, aware UTC timestamps,
URL origin/base endpoint/query validity, page sequence/request budgets and header
format, pointers, native ID and declaration references, SHA256 and canonical
size. Rebuild derived nodes/edges/facts from retained raw pages, compare with
stored projection, and recompute whether complete/confirmed_empty is possible.
Reject fabricated evidence/edges, inconsistent coverage and altered scope; do
not trust the digest as authentication. A fully forged consistent capture is not
cryptographic proof of a store response; provenance remains caller trust.

## Ownership, deadlines and cleanup
One acquisition owns context/budget, guarded client/transport, resolver process,
fetch task and optional cancellation watcher. Guarded callbacks collect fixed
attempt metadata before/after the actual wire operation. Each redirect/failure
uses that same request budget. Same-origin-only allowlist remains authoritative.
Per-request remaining-time wait covers DNS, connect, headers and body. Explicit
cancel watcher cancels/awaits blocked fetch; all exit paths close response/client/
transport and cancel/reap auxiliary work. Parsing/topology are bounded iterative
work and check event/deadline between bounded units. No concurrent page fetch or
inference. Guarded pinned backend tests separately exercise actual numeric-IP
connection seam; mocked wire tests alone cannot establish pinning correctness.

## Red acceptance seam and next gate
`tests/test_woo_tree_acceptance.py` exercises these signatures against controlled
public-address resolver/wire fixtures and fixed receipt clock. Expected assertions
are from G1 behavior/design. Initial run must fail at explicit operation stubs,
not import or fixture errors; log and counts belong in verification.md. Additional
security/stress/codec tamper cases remain predesigned in test-design.md and must
be authored before corresponding logic changes. G2 review precedes components.md;
G3 and saved red evidence precede production implementation.
