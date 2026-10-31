# G1 review — CLI product discovery repair

Verdict: PASS

Reviewed the behavior contract, test design, task breakdown, research, and plan for spec 018. The requested work stays within the existing CLI and caps discovery at the requested URL sample. It preserves product/result schemas and partial-coverage semantics, addresses the observed index-parser/seeder/category-crawl failure, and does not propose a new driver or whole-store crawl.

The acceptance design is appropriately layered: real CLI/parser/normalizer path behind controlled HTTP, a small 3-page red/smoke before bounded adversarial cases, and a distinct live 3-then-50 sequence. Risks include index cycles/duplicates, category-only maps, cross-origin and path escapes, robots denials, XML hazards, byte/request/time caps, cancellation, legacy fallback behavior, and truthful timeout/output handling. Fixtures and limits are bounded and deterministic.

No blocking contract or coverage gap found. During implementation, include response-body reads in the byte and deadline accounting, and ensure a depleted enclosing deadline cannot launch a legacy fallback; these follow the written contracts and are implementation checks, not design blockers.

Reviewed artifact SHA-256 (concatenated sha256sum manifest): `524680326fb31c79af0f3c777e6ae2b6a7b5f775ff86feebdba74cbda510fbb9`.

G1 does not authorize implementation beyond the reviewed scope and does not certify runtime or live behavior.

## G2 skeleton review

Verdict: PASS

Reviewed the private sitemap interface and stub, the two controlled acceptance tests, and the saved acceptance-red log. The seam returns ordered URL candidates plus an explicit fallback decision, accepts an optional caller-owned HTTP client, and keeps public discovery output unchanged. The integration contract routes the requested cap and remaining deadline into discovery, permits the legacy path only when appropriate, and propagates cancellation/deadline exhaustion without launching a browser after expiry. The tests exercise public discovery and the actual CLI/extractor/normalizer/output path; only HTTP and browser/seeder boundaries are controlled. The saved red shows both tests failing on the old seeder/browser path in 0.29s, so it demonstrates the missing mechanism without broad crawling.

No blocking interface or test gap found for G2. During implementation, keep `stop_fallback` limited to authoritative stop conditions; unsupported or absent native sources must retain the documented compatibility fallback, while cancellation and exhausted deadlines escape. The focused red does not itself exercise cancellation or resource limits; those remain required by the broader SC02–SC04 verification matrix, not claims established at G2.

Reviewed G2 artifact SHA-256 (concatenated sha256sum manifest): `9a272b75274df940f71bb9eb1943066f4dd73006395db8dc027e204db07cea72`.


## G3 component review

Verdict: PASS

Reviewed `components.md` against the approved skeleton and test design. Ownership is coherent: public discovery remains shared, API precedence and output contracts stay in existing code, while one private component owns HTTP sitemap traversal, robots/XML handling, URL scope, deduplication, resource accounting, and deadline-aware body reading. The caller retains shared-client ownership; an internally created client closes on all exit paths. Requested `max_urls` is propagated through private fallbacks, and the legacy seeder is capped.

Fallback behavior is compatible and safety-aware: missing or unsupported native sources may use the existing fallback; authoritative robots/resource stops suppress fallback; cancellation or exhausted outer deadlines escape and cannot launch another crawler. The 12 physical-request cap includes redirects, decoded body limits are stated, and redirects remain bounded and same-origin. Product extraction, normalization, capture, and CLI publication stay with existing components. No blocking ownership, dependency, cancellation, or compatibility gap found.

Implementation must retain per-candidate robots filtering and avoid treating a single excluded candidate as evidence that the overall native source is unusable; ensure the specified authoritative stop behavior applies to sources/conditions that actually block safe fallback. The broader test matrix remains responsible for proving these boundaries.

Reviewed G3 artifact SHA-256 (concatenated sha256sum manifest): `81783034c2b4b577c3e2a86fd56eb436f4d11518b9b4c93caad1762298b993d5`.


## Implementation and host-disposition review

Verdict: HOLD for verification-plan consistency; no source blocker found in this review.

The native walker and integration preserve the approved boundaries: requested max propagation, bounded source traversal, existing platform API ordering, and safe client ownership. The robots fix sorts each stdlib rule group by descending UTF-8 path length and allows win equal-length ties, matching the recorded specificity red. The new tests cover longer-disallow precedence and allow/tie cases. The existing Shopify CLI transport mock now answers the added robots and root-sitemap requests and asserts the expected fallback call order. The recorded affected suite result is 159 passed (8.32s).

Two records need reconciliation before treating verification as complete. `tasks.md` T12 requires offline and full-gate success before live execution, while the new host disposition in `plan.md` permits the explicitly requested read-only live check after a failed but classified full-driver result. Align T12 and the plan, then preserve the required distinction between a passed feature check and an incomplete repository gate. Also update `verification.md`: it still says the specificity red needs a diagnosed fix and rerun, while the implementation contains the fix and the affected suite log now reports 159 passing tests. Full-driver evidence and the live result remain pending and are outside this review.

Reviewed artifact SHA-256 (concatenated sha256sum manifest): `08fb86fcff4ef709088a7649a5759a6e320f3bff003d30a05b144db79c8a8103`.


## Implementation review update

Verdict: PASS for implementation and host-disposition consistency; full-driver and live verification remain pending.

Rechecked the two requested document corrections. The plan now sequences live testing after affected offline success and the required full-driver result is recorded and classified, matching T12 and the host disposition. The prior robots-specificity red is explicitly described as a milestone finding resolved by the later configured rerun, which records 159 affected tests passing.

No implementation blocker found in the reviewed diff. The rule ordering fix and its specificity/tie tests are appropriately narrow, and the Shopify transport fixture explicitly handles the new robots/root-sitemap requests while retaining its product/count assertions. This verdict does not certify the pending full repository driver or Naheed live runs.

Reviewed artifact SHA-256 (concatenated sha256sum manifest): `3e497336805d1c0daa1a4fa9809c8928e544d76c8af41d5b42363485dab1407c`.

## Final evidence review

Verdict: PASS for the feature and evidence record; the required full-repository gate remains incomplete.

The saved full-driver report records exit 1 after its main group: 1745 passed, 16 failed, 1 skipped in 214.325 seconds; the later reliable-oracle and maintenance groups did not run. All 16 failing cases are in the existing Google production owned-process/worker supervision tests. The log directly records the macOS Linux-only `_subreaper` RuntimeError; downstream worker-report cases fail on missing process metadata or expected status. The evidence does not justify marking the full gate passed. `status.md` and T11 leave it incomplete.

The retained CLI receipts and `live-summary.json` report exit 0 for both runs: 3/3 in the smoke and 50/50 for max 50. The 50-run summary records 50 unique captures, JSON-LD extraction, nonempty titles, PKR prices matching captured offers, zero overlap with the 757 saved category URLs, and `catalog_complete: null` with `crawl_coverage_unverified`. All 50 source images are placeholders. Both stderr files retain the existing Playwright pending-task/TargetClosedError warning. These limitations are represented in the status and verification record.

T12 and T13 are checked; T11 remains unchecked because the full driver failed on this host and its later groups did not run. The result is a successful requested live sample and feature verification with an explicitly incomplete whole-repository gate. No further test or network run was performed for this review.

Reviewed artifact SHA-256 (concatenated sha256sum manifest): `1c06d8023c6585b9ccf0b3d7e11df6009bc385248c77bafe28ac328cf8e25680`.
