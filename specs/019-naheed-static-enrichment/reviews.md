# Independent review record

## G1 — behavior, tests, tasks and research
Reviewer: /root/naheed_fix/reviewer. Date: 2026-10-31.
Reviewed SHA-256 digests:
- spec.md: 6ed00f5b76117c418ec9866148a0153b8eb3d7208d041341f6c875275add5cae
- test-design.md: a948f6dd74b4acab41eb498af23e13e8e2e44ca669ecb88708db87aef75241df
- tasks.md: 261a5e31256f5c5f87edaf46ad354aba60752e5266f74f24e78d159da0505803
- research.md: 9072076f90a133ebd7398449bdec070786612023a539017e575732e62f200a84

Verdict: **pass**. FR1–FR4 have separate observable positive and adverse scenarios SC1–SC6; default compatibility, immutable capture, field-source attribution, no GTIN/variant invention, and positive-only listing membership are explicit. The saved sitemap's 757 entries are correctly distinguished from listing evidence. Tasks require red production-path checks before implementation, sequential independent gates, bounded stress and actual full-driver execution; denied live access remains blocked.

Nonblocking design decisions to resolve explicitly in plan/skeleton before G2:
1. Define concrete URL/page/byte/membership bounds and timeout ownership, and validation of imported index record version, scope and capture consistency. Avoid a total-time promise enforced only by CLI when library calls remain unbounded.
2. Specify URL-only membership when heading is absent (native URL supported; absent label stays absent), and index acquisition completeness versus per-product category completeness. No observed positive membership implies exhaustive taxonomy or nonmembership elsewhere.
3. Specify image reindexing source overrides and the OG-only normalization path for DOM brand/SKU/additional images. A DOM fix visible only in raw JSON but lost in normalized Product would miss the intended behavior.
4. Define main listing container selectors and explicit recommendation exclusion. Generic `.product-item` anywhere on the page is insufficient for FR3.

Disposition: author must record these existing-scope choices in plan/skeleton; G2 reviews them. No blocking finding at behavior stage. Future gates remain pending.

## G2 — interface skeleton
Reviewer: /root/naheed_fix/reviewer. Date: 2026-10-31.
Reviewed SHA-256 digests:
- skeleton.md: ffcec3116964041b005a82fb1e1991056968c10b0b7b575b9a3f34186b6a5a88
- plan.md: 9e0f23655fd33353d524249541d3cfff1776866932f5c136889380b1c369fe3f

Verdict: **pass**. The document-only skeleton exposes no incomplete runtime API. Signatures separate pure product parsing, scoped bounded listing acquisition, imported-artifact validation, raw attachment and category observation. The generic/native category API remains the integration seam; constructors and default command behavior remain unchanged.

G1 decisions resolved: request count/size/membership bounds and per-request timeout are concrete; CLI owns its explicit operation timeout. URL-only category identity retains absent label; observed positive membership remains unknown in exhaustiveness. Original capture and filtered-image source positions are preserved through `_field_sources`; OG brand/SKU/gallery normalization is explicit. Main listing selectors plus recommendation/navigation ancestor exclusions are specified. Partial remote acquisition and invalid caller artifacts have distinct return/exception paths.

Implementation checks required by these contracts: validate bool-versus-int/version and capture time/URL/value consistency; test injected final cross-origin response as well as next links; prove both browser and HTTP parsing consume the shared helper. These clarify existing SC2/SC5/SC6 obligations and do not change scope. G3 and executable red checks remain pending.

## G3 — reusable component model
Reviewer: /root/naheed_fix/reviewer. Date: 2026-10-31.
Reviewed SHA-256: components.md 11bad8ad9bba92c7967129ce1923b930e2959399dd3b798b63e4da4794b1feb1; skeleton.md remains G2 digest. Also inspected authored tests/test_naheed_static.py (no production implementation yet).

Verdict: **pass**. Product DOM selection/placeholder recognition is shared by HTTP and browser consumers; capture and normalizer retain their existing ownership rather than a duplicate provenance engine. The listing module is justified by the explicit index CLI and normalize-with-index consumers and terminates at ordinary category observations. Existing exact mapper, scope helpers, portable validation, atomic CLI output and execution limits remain shared infrastructure. No speculative registration/lifecycle abstraction or new dependency is proposed.

Authored static tests independently assert early-return enrichment, original-capture retention, normalized HTML evidence, filtered-list reindex support, valid structured fields, multi-product isolation, browser OG behavior and blocked-API detection. Listing/CLI acceptance and bounded stress tests are still required by SC4–SC6, followed by recorded red evidence before production implementation. No component-stage blockers; final verification/review remain pending.

## Final review — first implementation, changes required
Reviewer: /root/naheed_fix/reviewer. Date: 2026-10-31.
Inspected tracked diff and untracked implementation/tests. Key SHA-256 digests:
- categories/listings.py: 3db861a931cda6aa3f7b5da5b365a9885d8b03c530a31d0d03ef22361270946d
- extractors/_product_html.py: daec005f7b21109361f26714fe85e6428d5ecb146a4ea25717a391eaa6804c39
- tests/test_listing_categories.py: 2b13f0940862c270a8afb279364a2f67a9d9718e78ead55da79f525371935e32

Verdict: **changes required**; full-driver/live evidence still pending. Existing red.log records 22 failed/4 passed before production changes; adversarial-red.log records hash/empty-gallery failures before repair; focused-green.log records 105 passed. These establish exercised mechanisms, not live Naheed observations.

Blocking finding F1 (resource bound): build_listing_index checks its 300-second deadline only before each request. httpx read timeout measures inactivity between chunks, so continuous drip-fed response content can exceed the total deadline indefinitely. Reviewer executed a deterministic real-path reproduction using an AsyncByteStream and a patched module monotonic clock: elapsed moved from 0 to 301 before yielding valid listing HTML, yet result was complete=True, reasons=[], memberships=1. Enforce remaining total time across request and complete streamed body consumption, catch expiry as a partial index with time_budget_reached, and add a controlled-stream regression designed before repair. Author acknowledged this finding.

Coverage gaps under existing SC5/SC6: explicitly exercise out-of-scope final response URL in an injected client, configured store base-path rejection, malformed capture timestamp/value shape, and library invalid artifact shape. Current redirect-status/cross-next/root-traversal cases do not prove these distinct contracts. Address before final coverage pass. Static image filtering/reindexing, per-field DOM provenance, Magento blocked-API routing, positive-only listing namespace, CLI opt-in mapping and recommendation exclusion are otherwise consistent with reviewed design on inspected paths.

## Final review — deadline repair and supplemental coverage
Reviewer: /root/naheed_fix/reviewer. Date: 2026-10-31.
Reviewed revised SHA-256 digests:
- categories/listings.py: 7a1a9339fba64dfae432e656bf4198d0f954c278501a7f07043e05ea7d0962da
- tests/test_listing_categories.py: a8a16fba58fac7e6a10602610d3ed9199a89664179e1e6fb723d258e990d5282
- test-design.md: abd0b162ab67b06df391d12eee7e6591fec2f684d71f73fe031b02907fd5eeb0
- docs/static-enrichment-listings.md: de6b2d4d2d72affb3cb6788d3a6dd6eee5b47191660a485621d95b60d32ee62a

F1 disposition: **resolved** on inspected code. `_read_page` includes streamed-body consumption inside `asyncio.wait_for` using remaining total budget; timeout returns partial `time_budget_reached`. stream-red.log proves the drip regression failed before repair; revised focused-green.log records 115 passed. The injected-final-URL, store base-path, malformed timestamp/capture shape, invalid CLI index and external-entity tests exercise distinct reviewed boundaries through production code. Reproducible 100-card/three-page mechanism cases remain bounded and execute real parsing/deduplication, not expected-result stubs.

Affected design gates reaffirmed: supplemental G1 test cases refine FR3/FR4 and SC5/SC6 without changing required behavior; G2 gains a private request/body helper and explicit whole-acquisition cancellation without public signature change; G3 source-parser/capture/category/CLI ownership remains unchanged. No new blocking code finding in this revision. Minor invalid-helper-input exception consistency was sent to author for a bounded correction.

Documentation correctly separates 757 saved URLs from memberships, exposes the opt-in CLI path and unknown membership completeness, and states that live crawling/re-extraction and automatic Google taxonomy assignment have not occurred. Final full-driver gate remains **pending** until the revised complete run and finalized verification/status artifacts are supplied. No live pass is asserted.

Code-review disposition after author response: **pass**, conditional only on final verification evidence. Confirmed `with_listing_categories` guards non-dict raw/index inputs before attribute access; direct None/list/integer index fixtures assert CategoryError. Reviewed implementation and test digests remain those immediately above. No unresolved code blocker. Full repository verification remains pending and live execution remains blocked; code-review passage is not full feature-verification completion.

## Final evidence gate
Reviewer: /root/naheed_fix/reviewer. Date: 2026-10-31.
Inspected revised required driver report and all three per-family logs, verification.md, and finalized status/tasks. Implementation/test digests remain the passed revision immediately above.

Evidence SHA-256:
- final-check/report.json: 2aaf7153aba7907924516b44f285aca1fd751f0e4b1e6b6fbdb970403d40300c
- final-check/main.log: 3dc1d7aef52e728641b12d9e98e1d04fc932f6cc8e1912045ec0bbd3a8077b43
- final-check/reliable-oracle.log: 3961c26bae0b1d2c7cd974df7c2500e68a8768d79843ad1fc1b5d207b17696d9
- final-check/maintenance.log: eefbf274b4fd2da278ffe049dd683d614fb44169e7f3ee4e253ce5105f0f92f0
- verification.md: 565a04cae195bf4de3f7e2b8b26c60b7a0bd17432101b550817a38d8bbf56a5d
- status.md (review completion update): a9f7ed0daa1c0e1d9dbc16a218e36bdac9be06db1146acc4ac209bb50c1da001
- tasks.md (review completion update): d5ad00e5fcc844a48c7c5993c0f98091b3cf3f3e40c2ee5421fa533854f62228

Verdict: **pass for final code, coverage and offline evidence**. Required complete driver passed 1734 tests (main1604, reliable oracle24, maintenance106), exit0, 209.12946 seconds, one worker, within unchanged 240s-family/480s-total ceilings. Logs contain matching counts and no skipped tests. Earlier full run is explicitly diagnostic because source changed; final report is correctly distinguished. Focused115, intended red failures, reviewer-found deadline repair and deterministic real-path stress are recorded with no assertion weakening or synthetic-as-live claim. No unresolved code/review blocker remains.

Live integration status: **blocked**, not passed. Enforced network policy excludes Naheed hosts, so the planned two live GETs and a populated 757-category membership crawl were not executed. The handoff must retain this exact limitation; implementation/offline completion does not prove current live selectors or complete live category mapping. No installed-wheel release, push or PR is claimed. Status/tasks updated to close independent review while preserving live blockage.
