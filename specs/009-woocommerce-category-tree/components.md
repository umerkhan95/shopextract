# Reusable component model — 2026-10-24

Author `/root/woo_author`; follows recorded G2 pass. W06 documents ownership and
reuse; operation stubs remain unimplemented. Independent G3 is next.

## Existing reusable components

| Component | Responsibility reused | Boundary / concrete consumer |
| --- | --- | --- |
| `tools.security.normalized`, `public`, `SourceGuard` | Canonical URL, exact origin allowlist, bounded DNS and public-address policy | Woo acquisition builds one fixed endpoint and one-origin ToolConfig; no copied URL/IP policy |
| `tools.security.GuardedTransport`, `PinnedBackend` | Pinned checked numeric IP, sequential no-retry connections, per-hop authorization/accounting, identity encoding and bounded body reads | Acquisition owns client/context and wraps the entire fetch in remaining deadline + cancellation; transport never owns category semantics |
| `tools.context.OperationContext`, `OperationBudget`; `tools.runtime.Limits`, `ToolConfig` | Shared request/redirect/body limits and operation deadline/cancel/accounting data | Construct directly after WooTreeLimits validation; avoid ToolRuntime job/session/config APIs, whose positive-only validation would reject reviewed zero work capacities |
| `tools.execution.OwnedProcess` | One bounded resolver process, cancellation and reaping | Owned by one acquisition; no inference, extraction worker or separate session runtime launched |
| `categories.helpers.native_id`, `nonblank_text`, `merchant_scope` | Existing Woo opaque ID/text normalization and scoped merchant identity | Tree facts and membership lookup use identical ID semantics; parent integer zero handled explicitly by Woo-specific parser |
| `categories._codec.wire`, `typed`, `canonical`, `digest` and existing primitive value codecs | Strict dataclass shape/type conversion, canonical JSON, timestamps and hashes | Standalone tree envelope adds its own version/cap/semantic validation; does not loosen product companion codec |
| `categories.mapping._supported` semantics | Bound observed native-ID fact, accepted matching conversion and nonempty source evidence | Explicit tree membership lookup must preserve this exact support predicate; reuse helper if stable enough or a narrowly shared predicate with both consumers, no weaker ref-only path |
| `categories.contracts.CategoryScope`, `CategoryObservation`, `CategoryTermRef`, `CategoryError` | Existing source scope, captured product memberships and common validation errors | Tree lookup consumes these immutable value objects; no Product/Variant, observation, feed or maintenance changes |

`source_fact` is useful precedent for independent facet states and capture support,
but its CategoryFactBinding cannot express slug and its existing per-product
portable limits cannot contain a full store index. Therefore tree-specific facts
and receipt pages are justified, without changing shared product schemas or
manufacturing a product capture around a category response. Source URLs/times and
raw page bodies remain independently inspectable. No generic evidence framework
or global taxonomy registry is introduced.

## New single-module responsibilities

`categories/woo_tree.py` is one cohesive opt-in module with the public declarations
in skeleton.md. Concrete consumers are callers acquiring/exporting one merchant
tree and callers resolving their already captured Woo product membership IDs.
Private helpers may separate these five bounded jobs without a plugin framework:

1. Validate scope/limits and construct the fixed installation-relative endpoint.
   Own guard/context/client/auxiliary lifecycle and fixed-size attempt accounting.
2. Parse accepted pages into raw declarations and independent facet states;
   enforce headers, pagination/terminal rules and page-atomic retention admission.
3. Group same-ID declarations, preserve conflicts, resolve supported parent edges
   and diagnose orphan/self/cycle/depth with bounded iterative work.
4. Encode/decode the strict canonical tree envelope. Reuse the exact same pure
   projection builder for live acquisition and replay validation, so there is
   one topology/facet implementation rather than a second validator algorithm.
5. Resolve positively supported captured membership terms against scoped retained
   nodes. This path cannot acquire data, change observations or invoke mapping.

Tree types are new because their lifecycle/size/completeness differs from a
per-product companion. Raw receipts plus derived graph permit replay and audit;
repeated declarations consume input and retention budgets. Topology and codec
remain private implementation components, not separately extensible public APIs.
Existing default extraction/imports remain unchanged. Shopify bridge is deferred.

## Lifecycle and error ownership

One acquisition owns one monotonic deadline, cancellation event, mutable shared
request budget, resolver owner, transport and AsyncClient. Page fetches are
strictly sequential; temporary fetch and cancel-watcher tasks are ownership
mechanisms, not parallel page work. A single fetch task includes DNS through
response-body completion. Cancellation/deadline cancels and awaits it; finally
closes client/transport and reaps the resolver. The same context/deadline is never
reset by redirects or nested work. Cleanup uses the existing resolver owner's
bounded cleanup policy; no detached task survives an invocation.

Initial argument/type/limit errors raise CategoryError before I/O. URL denial,
transport error, unsupported encoding, HTTP failure, resource exhaustion or
explicit-event cancellation produces the reviewed terminal result with retained
prior pages and fixed local reason codes. External task cancellation propagates
after cleanup. Invalid JSON/collection on the first response is malformed;
subsequent failure is partial when a valid page was retained. Guard/transport
ToolError codes are translated by a small fixed local mapping, never remote text.
No hidden retries, automatic repair, cached partial merge or store write occurs.

Only the guarded transport charges actual attempted wire requests. Its optional
accounting callback records bounded hash/status metadata and enforces redirect
URL length before the next wire attempt. Preflight checks do not double-charge.
Same-origin guard rejects cross-origin destinations before connection. Raw body
and canonical retained envelope caps are separate. Candidate page admission
checks all raw entries and reserved full-envelope overhead before committing
any page data. Codec rejects unencodable/tampered state rather than silently
trimming it. Scope and observed evidence remain authoritative for membership.

## Review/verification seams

Existing transport remains unchanged, preserving unrelated dirty work. Controlled
wire fixtures exercise real guarded fetch + parser + graph + codec + lookup.
A separate PinnedBackend connector fixture verifies the actual checked numeric-IP
connect seam, because mocked wire injection bypasses real sockets. Blocked stream
fixtures verify cancellation/deadline closes resources. Canonical size tests
cross the envelope cap while raw bodies fit, and replay tests challenge altered
facts/edges/coverage. The reviewed deterministic 24-case stress uses these real
entry points and records actual selected-scope case count. Required offline and
bounded live checks remain pending; component design itself claims no runtime
correctness. Actual token counters unavailable; no inference or parallel agents.
