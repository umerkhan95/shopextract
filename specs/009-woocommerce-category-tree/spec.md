# WooCommerce per-store category tree — behavior design

## Outcomes and requirements
- FR01: Add explicit opt-in, read-only category-index acquisition for one WooCommerce store through `/wp-json/wc/store/v1/products/categories`, with `hide_empty=false`. This is a merchant tree, not a universal Woo taxonomy.
- FR02: Retain observed category ID, label, slug and parent ID with exact response pointers, source URL, per-page capture time and merchant scope. Parent `0` is a root declaration; missing/null parent is unknown. Category presence never establishes product membership.
- FR03: Resolve supported parent edges after acquisition; flag missing parents, self-parent, cycles, conflicts and truncated depth without inventing edges or silently selecting one conflicting declaration. Keep supported raw facts inspectable.
- FR04: Return explicit acquisition outcome, coverage and reasons. Successful traversal means only a bounded traversal of responses requested with `hide_empty=false`; never an atomic snapshot or proof of private/unpublished categories. Distinguish confirmed empty, partial, unavailable and malformed.
- FR05: Bound all transport, body retention and graph work in one sequential run. Ceilings: 10 HTTP attempts including redirects/failures, `per_page=100`, 1,000 retained categories, 2 MiB identity response; reject nonidentity encoding, 8 MiB aggregate retained payload, graph depth 8, 30 seconds elapsed; no retries or LLMs. W02 resolves constants; G1 review remains required.
- FR06: Use guarded transport for initial URL and every redirect, with DNS/IP and origin protections; do not forward credentials cross-origin. Reject unsafe targets before network access. Cancellation/deadline prevents further calls and returns bounded retained evidence with reason.
- FR07: Optional mapping bridge uses existing exact rule engine only on supported product membership evidence, scoped to merchant and pinned target version. Tree lookup may enrich context but does not create membership or mapped ancestors. Unknown, ambiguous and unavailable stay distinct.
- FR08: Keep existing Product/Variant constructors, default extraction, category observations, feeds and maintenance behavior compatible. New index/edge data cannot create false removals or automatic store writes. Per-product companion limits remain separate from traversal limits.

## Acceptance scenarios
- SC01 (FR01/02): Given a two-page tree with root and child, acquisition retains three scoped nodes and the declared child edge, with page-specific evidence; existing product membership is unchanged.
- SC02 (FR01/04): Given a verified first successful page containing `[]`, known consistent total zero and `hide_empty=false`, report confirmed empty; `[]` without reliable traversal coverage is unknown/partial, not confirmed empty.
- SC03 (FR02/03): Given absent/null/zero/false/string/negative parent and malformed IDs, retain only independently valid facts; zero is root, booleans/negative/malformed IDs are rejected, and absent/null is unknown. Numeric IDs canonicalize consistently with the existing Woo adapter.
- SC04 (FR03): Given orphan, self-parent, cycle and depth-9 chain fixtures, mark affected relations unresolved/conflicting/truncated; no fabricated root, ancestry or membership.
- SC05 (FR03/04): Given repeated pages, identical duplicate IDs, conflicting IDs and changing totals, terminate within budget; duplicate identical facts may coalesce with evidence, conflicts remain inspectable and coverage is partial. Reordering alone does not change semantic output.
- SC06 (FR04): Given 403/404, timeout, invalid JSON, invalid shape, or later-page failure, distinguish unavailable from empty and retain valid prior pages as partial. Do not infer category deletion or membership absence.
- SC07 (FR05): Given every resource boundary below/at/above its ceiling or configured zero, never exceed it; exact last-page fit may complete only with independent terminal evidence. Exhaustion with further work is partial; zero transport budget performs no call.
- SC08 (FR06): Given unsafe initial/redirect URL, DNS rebinding, cross-origin redirect or cancellation between pages, no unsafe follow-up request occurs and the attempt ledger/deadline is respected.
- SC09 (FR07): Given explicit exact scoped rule and evidenced membership, emit existing mapped decision; label similarity, category-index presence or ancestor relation alone cannot map a product. Changed taxonomy version or stale rule is rejected/unavailable, never silently migrated.
- SC10 (FR07/08): Given same category ID at two stores, unknown version rules, ambiguous targets and oversized target set, preserve scope isolation and existing rule validation. Shopify bridge registers only referenced valid targets within the existing 1,000-target cap.
- SC11 (FR08): Given feature disabled or acquisition partial with product companion enabled, legacy output stays identical; per-product caps still apply and maintenance cannot mistake partial tree coverage for confirmed absence.

## Boundaries and compatibility
No fuzzy/AI classification, credentials discovery, authenticated admin API, category writes, universal taxonomy, product crawl or automatic full-tree-to-Shopify mapping. Category tree acquisition is independently usable; the optional bridge is a later slice under the same reviewed contracts.
W02 decisions: same-origin redirects only; consistent total headers plus count/identity coverage are required. A headerless first short/empty page may use one page-two confirmation; otherwise headerless/malformed/drifting totals are partial. Graph integrity is separate from traversal coverage. Zero depth permits roots. Exact result shapes/accounting await G2. Captured memberships link by scoped native ID without mutation; optional Shopify mapping SC09/10 is deferred.

## Workflow
User authorized implementation; independent G1 checks behavior/tests/tasks/research; G2 skeleton and G3 components precede implementation and saved red evidence. Planned synthetic/live checks are not execution evidence.
