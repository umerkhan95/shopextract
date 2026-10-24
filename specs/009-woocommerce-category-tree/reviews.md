# Independent planning review — 2026-10-24

Reviewer: `/root/woo_plan_reviewer`, separate from planning author. Scope: PLAN and scenario/task coverage only. Read actual planning artifacts, development workflow, constitution, Woo product adapter and category mapping/config contracts. No network, tests, implementation or live observation performed.

## Reviewed artifact digests (SHA-256)
- spec.md: `124dcde37b47c68cc108e5003edaa00672520dd065a29bf0382f0288e1ef0f22`
- test-design.md: `637f1efa94b488bef469ef2050788ce030f1e6229126a6efb0067dc0bc930d3c`
- tasks.md: `b36a720c51698e9dea54e749ace97a6895b33b96250a9ae952d2ba6f8be7f820`
- plan.md: `b1b2a92ced772ee340942f406bcc4f28ae93c01cf7b908e5b60befb48c920e79`
- research.md: `979f72715987c62c2f3cf68b139953988765f65dcdcafc305bc284d5ab1b3753`

## Findings and dispositions

1. **Blocking for G1/implementation, open:** research correctly identifies unresolved terminal coverage and guarded-transport guarantees. Before G1, establish current official endpoint parent-field availability, pagination/total-header behavior and headerless policy; inspect the real transport's connected-peer/DNS rebinding guard, redirect accounting and streaming decoded-body/deadline enforcement. A DNS check before an independently resolving fetch is insufficient. Record exact same-origin/credential URL policy, reuse seam, constants and outcome semantics. Do not imply these guarantees are already implemented. Public endpoint availability alone does not establish parent-edge support.
2. **Medium, fixed in planning:** W11 previously depended on W09 although mapping was expressly optional. Changed dependencies to selected-slice verification, with bridge cases deferred explicitly for acquisition-only delivery. Later bridge work needs affected gates and its own evidence; no silent all-24-cases claim.
3. **Low, fixed in planning:** clarified reorder invariance as semantic graph/facet projection, preserving order-specific source pointers/timestamps/ledger; identical duplicate facts are distinct from repeated/nonadvancing pagination. This removes an oracle ambiguity without changing scope.
4. **Implementation prerequisite, open:** G2 must specify accounting before retention and deterministic status precedence for mixed malformed/partial results. Define a retained fact/category count that duplicates and conflicts cannot bypass, exact serialized evidence overhead, and terminal-fit rules. Root depth zero versus zero resource budget must be explicit. These are already raised in research; no signatures are prescribed by this review.

## Coverage assessment

FR01–08 each map to named SC cases and tasks. Designed cases distinguish merchant tree facts from product membership and prevent partial coverage becoming absence. Missing parents, self edges, cycles/depth, totals drift and duplicate conflicts have distinct risks. Scoped/versioned exact mapping reuses existing evidence checks and the 1,000-target/config-byte caps; no full-taxonomy registration is proposed.

Deterministic fixtures, fixed provenance/seed, real-path parser/topology/mapping/persistence execution, a mutation-sensitivity assertion and bounded stress/live smoke are meaningful planning evidence. Stress counts are proposals, not executed results. At fixture authoring, controlled transport must simulate safe DNS/connected-peer behavior without bypassing the guard under test; `.example` provenance is synthetic. Name one selected public store before live execution and retain actual response field/header limitations. Live mutation may remain inconclusive while designed real-path mechanism checks run independently.

## Verdict

**PLAN: pass as a bounded approach proposal, with the open prerequisites above carried forward. W01 planning traceability review complete. W02 unresolved; formal G1 not passed.** No G2/G3/final verdict or runtime correctness claim is made. No implementation, probe, test, push or PR is authorized or reported by this review. Meaningful contract changes require affected review again.

# G1 implementation-slice review — 2026-10-24

Reviewer: `/root/woo_reviewer`, independent of W02 author. Reviewed updated behavior,
acceptance design, task dependencies, research and plan against workflow/constitution
and actual `tools/security.py`, `tools/context.py` and category identity helpers.
Bounded code/document reads only; no production edits, network or test execution.

## Reviewed SHA-256 digests
- spec.md: `b7ce7a93cac3895f326bb526f8483273afff4e04b6846bcfbc9a70fae0e1824a`
- test-design.md: `a248406e648978229f13b669e5b7441a01670c1e2ceb52b4d5569ec58fc57141`
- tasks.md: `2eeea1665e9d7a1559f5d2f831519dabb35bebfa32d892bc457590a89aa29ecd`
- research.md: `83003b3e11e78d1fa3e4ef270359bb32f17dd64204c80d9864e14551a7226a50`
- plan.md: `5924feed5200713caf95068ff234b1b5efbefec0ef9d148ca0203c7ef3882743`
- development-workflow.md: `027f4147359719b99236daf723c41c0e26ffd13a9aed5eeed260c3dc64f430a0`
- constitution.md: `6be0e440e2f89d5f2570fb43907fc8929897c2155f4f86b791c0a7c1fb8f2df6`
- tools/security.py: `f8d84b3febf83633f66123c96d63abd872fb293d5b151f2d130c9a50583964c0`

## Findings and dispositions
1. **Previous blocking source/transport finding: resolved for design.** Saved current
   official schema/route findings establish parent support and first-short-page
   header suppression. Actual guarded transport checks initial/redirect origins,
   rejects mixed/nonpublic DNS, pins the connector to checked numeric IP, charges
   each wire attempt and rejects nonidentity encoding before raw streaming. The
   acquisition owner explicitly supplies missing whole-fetch timeout/cancellation
   and cleanup; these are planned requirements, not existing runtime guarantees.
2. **G1 clarification required:** research allows any headerless first page a
   confirmation; spec/test design allow only short/empty first pages. Align the
   exact eligibility and expected full-headerless result before the gate passes.
   This matters to count/terminal assertions and request budget behavior.
3. **G2 prerequisite, carried forward:** specify bounded URL/header/error metadata,
   exact canonical envelope bytes including derived facts, page-atomic refusal,
   duplicate/raw-record accounting, trusted receipt clocks and strict reload
   validation. A separately bounded ledger cannot store arbitrarily long URLs or
   messages under a fixed-size claim. Test envelope overhead crossing a cap even
   when the raw body fits. Existing W02 design correctly reserves these details
   for skeleton review; no production code before G2/G3.
4. **Coverage accepted at design level:** distinct malformed facets, topology,
   count/header drift, cap boundaries, real pinned-connector behavior, blocked-body
   cancellation/cleanup, partial replay and membership/scope interactions have
   independent expected outcomes. Acceptance authoring must exercise these real
   seams; mocked guard success alone cannot satisfy security coverage. Optional
   bridge SC09/10 is deferred explicitly and cannot be counted as implemented.

## Verdict
**G1: changes required solely for item 2; narrow document repair and digest
recheck suffice.** Other findings are resolved or explicit next-gate requirements.
The 24-case stress/live plans remain unexecuted. Token counters unavailable to
this reviewer; no quota estimate inferred. Unrelated dirty work is preserved.

### G1 narrow repair recheck
The author aligned research and plan: only short/empty headerless first pages
receive page-two confirmation; full headerless first pages stop partial without
another request. This matches the reviewed spec/test design. Item 2 is resolved.
Rechecked SHA-256: research.md
`c1db8bcf8f861db37e122928760a72a48bba501aa2bf9776d96f5c29e6939953`;
plan.md `204a0fce17a19ea67be89138d1af4b2b1c2cba99b2bad2a04da2fa3b10a9f0ff`.
Other reviewed artifact digests above are unchanged.

**Final G1 verdict: pass for acquisition and captured-membership lookup only.**
Proceed to skeleton/red tests and G2; accounting/codec/metadata obligations in
item 3 remain mandatory G2 checks. No G2/G3/runtime/live approval is implied.

# G2 skeleton review — 2026-10-24
Reviewer `/root/woo_reviewer`, independent of author. Reviewed declarations,
skeleton, actual acceptance tests/red log and verification; compared existing
Woo adapter and mapping support boundary. No production edits or test reruns.

## Reviewed SHA-256
- skeleton.md: `98fa72e481d345285fda15c0f599ac4c20ae0a8b38ee2935e22a4863caa601a2`
- woo_tree.py: `7063ebcb7eef2cf71a2243a38041b72224c6f5115b9831aced98230d331faac6`
- test_woo_tree_acceptance.py: `16038603932c5f73c3335d67ee5923f09ecf15af1d611cc153656108ce9b0a84`
- verification.md: `fc286f9ae97a513d0eb695c1fbb6ba277ae370ffa602bab1cab50d9f892cd0a0`
- evidence/acceptance-red.log: `bea7f0ab701ed9320a54b409ef6419f5bcdb521904c3a51529263468a0939060`

## Findings / disposition
1. **Blocking:** membership inputs are caller-constructible observations. Matching
   reference/scope alone does not establish captured membership. Require a
   native_id fact bound to the same term, OBSERVED support, accepted normalized ID
   equal to the reference, and retained source evidence, consistent with existing
   mapping support checks. Missing/rejected/mismatched/unsupported native-ID
   evidence must yield unsupported, never linked. Add explicit design and red
   acceptance cases before implementation; a label fact alone cannot support ID.
2. **Resolved G1 prerequisites at interface level:** the dedicated envelope
   includes raw pages and derived facts, fixed hash and limits; canonical total
   bytes and conservative terminal/ledger reservation govern atomic admission.
   Zero/small caps explicitly allow an unserializable diagnostic, without falsely
   claiming portable retention. Ledger hashes URL and stores fixed local codes;
   URL/header caps prevent unbounded remote metadata. Strict re-derivation on
   reload rejects digest-only tampering and invented derived coverage.
3. **Accepted skeleton/testability:** async ownership separates explicit event
   cancellation from Task.cancel; request budgets charge redirects/failures;
   controlled resolver/wire hooks do not replace parser/topology. Default APIs
   are untouched. All 40 saved failures are intended operation stubs, including
   independently reached codec/link operations. Additional predesigned transport,
   byte accounting, receipt-time variation, replay with recomputed digest and
   evidence-boundary tests remain required before final verification.

**G2: changes required for item 1 only.** A bounded design/test repair plus saved
red/hash recheck suffices. Components/G3 and business implementation remain next
stages; no correctness/live claim. Actual token counters unavailable.

### G2 narrow repair recheck
Skeleton and direct lookup docstring now require the supported native-ID fact;
foreign scope precedence is explicit. Six direct red tests independently remove
ID support, reject conversion, alter normalized ID, remove evidence, set unknown
support or change term binding. Existing valid membership test supplies the
positive counterpart. Saved revised log ends **46 failed**, all explicit intended
operation-stub failures; no fixture failure or business logic added. Item 1 resolved.

Rechecked SHA-256:
- skeleton.md: `5f32f1e40b4810ade65b2e509d6e0817ef277ece66d93a5043fa38151193718c`
- test-design.md: `61cfc2f7388f06c54be915e5fb28a85e8965ce1333aee4e2bd66fb7b67778e19`
- woo_tree.py: `184359660a2980704cb62b07681c2a792cba3ab4920f0a19dfd1ebe851db3222`
- test_woo_tree_acceptance.py: `3646d9862d52514df590152451c79351ad88a00aebf03fb3c0f143fb6a2b56e9`
- verification.md: `0a5a3b7f7910f997aef98be09319206df4967316e155d831a6dc3859acf39ce9`
- evidence/acceptance-red-g2-revision.log: `e4d307d3e49c0e099324195841a43d7c1e33f0285528ea4e93795784cacc7bc8`

**Final G2 verdict: pass.** Public seams, strict accounting/evidence contracts and
intended red results permit component design/G3. Additional declared mechanism,
resource and replay checks remain required; G3/implementation/green/live results
are not implied.

# G3 component review — 2026-10-24
Reviewer `/root/woo_reviewer`, independent of author. Read actual component model,
G2 skeleton, task/status update, reusable codec, support predicate, transport and
resolver lifecycle seams. No business code changed or tests executed for G3.

## Reviewed SHA-256
- components.md: `041d72cdce101846c7c13d42c546142f1de51c081bbb23a7646836dc5a511137`
- skeleton.md: `5f32f1e40b4810ade65b2e509d6e0817ef277ece66d93a5043fa38151193718c`
- tasks.md: `e5f13b14821c8f402e1da86c18da4633bf79f71c1a5295a6c0daadd1369aa13a`
- status.md: `733837e15d958a6b2ccf1575da0f26a2d94c9f798a88f5ca8284609e62ac32a7`
- woo_tree.py: `184359660a2980704cb62b07681c2a792cba3ab4920f0a19dfd1ebe851db3222`

## Findings / dispositions
- **No blocking design findings.** The transport wrapper owns only category
  policy, whole-fetch cancellation/deadline and result accounting. Existing
  SourceGuard/GuardedTransport/PinnedBackend own URL/IP/origin/pinning and stream
  bounds. Shared dirty transport/runtime files remain untouched; direct context
  construction avoids inappropriate job/session framework and zero-limit rules.
- Tree-specific receipt/fact/envelope types are justified by independent store
  lifetime, slug/parent semantics and 8 MiB budget; product companion codec/schema
  and default extraction stay unchanged. Reusing canonical/typed primitives plus
  one pure projection builder prevents duplicate graph/parser implementations.
  Strict semantic checks still belong to the tree codec, beyond typed decoding.
- Membership linking consumes existing observations and existing support-predicate
  semantics; it neither acquires data nor runs mappings. Importing the small
  existing helper or narrowly sharing it is acceptable; weakening/copying the
  semantics into ref-only matching is not. No taxonomy registry or future plugin
  abstraction is introduced.
- One acquisition owns client, transport, context, fetch/watcher tasks and resolver.
  Remaining-time cancellation and awaited/reaped cleanup cover body stalls and
  external Task.cancel. Sequential pages share the same budget/deadline. Actual
  cleanup, callback accounting, pinning and portable boundary correctness still
  require the already designed mechanism tests, not this design verdict.

**G3: pass.** Proceed with bounded implementation against reviewed contracts and
saved failing tests. Optional Shopify bridge remains deferred. No green, stress,
live or final runtime verdict is implied. Token counters unavailable; no inference
or parallel work launched by this reviewer.

# W10 independent fixture/design revision review — 2026-10-24
Reviewer `/root/woo_reviewer`. Read production seams narrowly for testability,
acceptance/mechanism suites, unexecuted 24-case driver, fixture manifest, live
plan/driver and revised test design. No test, stress or live execution performed.

## Reviewed SHA-256
- spec.md: `b7ce7a93cac3895f326bb526f8483273afff4e04b6846bcfbc9a70fae0e1824a`
- test-design.md: `cdd7eef4e5c10c3d3c07a0a889856f935a91b9a17393c55f879c47bc18fccf32`
- skeleton.md: `5f32f1e40b4810ade65b2e509d6e0817ef277ece66d93a5043fa38151193718c`
- components.md: `041d72cdce101846c7c13d42c546142f1de51c081bbb23a7646836dc5a511137`
- research.md: `c1db8bcf8f861db37e122928760a72a48bba501aa2bf9776d96f5c29e6939953`
- plan.md: `204a0fce17a19ea67be89138d1af4b2b1c2cba99b2bad2a04da2fa3b10a9f0ff`
- verification.md: `61d80f8b057001faf99c42d4ccd120a32a296a25c833b017b6276fae076d46f0`
- woo_tree.py: `a96fa36db62bc8fb9ff566a14bdb567e86842f0e0b8e362569896943d601ba73`
- test_woo_tree_acceptance.py: `3646d9862d52514df590152451c79351ad88a00aebf03fb3c0f143fb6a2b56e9`
- test_woo_tree_mechanisms.py: `06f20d7a30d72e75df6d7c830a7ebe341eefaec30c6507870a775cae89e84da8`
- woo_tree_stress_driver.py: `6f88d097f870b3aa657bc723cf9b3d4ea351e49aabc259d22da13dfefd4f436a`
- woo_tree_live_driver.py: `117158dfc4c99c54c3c2706d9eeb2a004c87464cf69c9a58299f023140a12829`
- fixture-manifest.json: `08004850a7d71f47923c0acf2da8cd3f70a1e428bd8f9e08a7c51da7e9174c57`
- live-plan.json: `0e9efccb5cc1b5e1c139638a9b36892f68f119f6e9a3030aef7ac0c992d7c116`

## Affected G1/G2 clarification verdict
**Pass for design clarifications:** raw integer parent zero is the root sentinel;
opaque text `0` is a category reference under existing adapter semantics. Keeping
that distinction in conflict/replay projection prevents invented roots. Constraining
same-origin redirects to the fixed route/query, permitting its trailing slash,
and retaining actual guarded-hop URL plus successful-attempt provenance tightens
the read-only evidence boundary. Invalid scope scalar types are caller errors
before I/O. These are consistent refinements of the selected slice, not Shopify
bridge expansion. Existing recomputed-digest path/query/status tests meaningfully
challenge portable provenance. Runtime correctness awaits final review.

## Findings / dispositions
1. **W10 blocking coverage gap:** fixed 8,192-byte fitting/overhead-rejected
   fixtures do not exercise the exact canonical admission threshold mandated by
   G2. Predesign a bounded below/at/above test with public operations and an
   independent threshold oracle or bounded black-box boundary search; do not
   calculate expected size by calling `_reserved_bytes`. Retain current 24-case
   count and add focused acceptance coverage separately if useful.
2. **Required additional direct mechanism coverage:** altered same-origin redirect
   path/query must stop before destination wire access; accepted trailing-slash
   redirect must retain its actual URL/time/fact provenance and survive replay.
   Also exercise mixed public/private resolver answers, an explicit earlier risk
   absent from the current tests. Pinning test already checks actual backend
   connector receives numeric checked IP and rejects later private rebinding.
3. **Live oracle gap:** current driver asserts positive ID/parent pointers and
   partial-not-empty, but does not independently check coverage against observed
   total headers, page lengths and budget reasons. Add that declared live oracle
   before execution. Existing actual target, no credentials, attempt/time/body
   caps and blocked/inconclusive reporting are appropriate.
4. **Accepted realism/limits:** fixtures use documented category shape with
   explicitly malformed cases, synthetic URLs/clocks, and actual guard/parser/
   topology/codec/lookup. The 24 slots map to six topology, six pagination, eight
   limits and four interactions. Terminal-fit combines item+request limits;
   requests-fit isolates multi-page request completion, so the overlap is useful.
   Lowered item cap isolates page-atomic refusal from request exhaustion. Memory
   is honestly an observed after-case RSS stop, not OS isolation. Check elapsed
   time after each case too, since synchronous work cannot be interrupted by an
   asyncio timer until yielding. Save a small smoke before stress expansion.
5. Partial-to-complete fault sensitivity, complete affected regressions and actual
   live observations remain separate required execution evidence; none is
   credited as executed by this review. Optional bridge remains deferred.

**W10 coverage verdict: changes required for 1–3 before stress/live execution.**
The fixture architecture and affected G1/G2 clarifications pass; no final code or
runtime verdict is made. Bounded review only; actual token counters unavailable.

### W10 narrow coverage repair recheck — 2026-10-24
Reviewer `/root/woo_reviewer`; read repaired tests/driver/design and manifest.
No tests/stress/live executed by this review; coordinator's unrelated regression
process remains owner of execution scheduling.

Rechecked SHA-256:
- test-design.md: `185b177b89c745d50580b1f184e0b8850b82d09e2107717f57df9d29f186cf45`
- test_woo_tree_mechanisms.py: `55e76b02abb95728718ab46f2a51685baf499374e4cad11ae008709dbaaebd58`
- woo_tree_stress_driver.py: `4efe27dd0f7cd963ca1ec968641f6f318614a7bc759a3710a7ff559ffeaef841`
- woo_tree_live_driver.py: `93ca9ce3502ee8988f06eb96173e2e8fa4622f976f4b696adb318d9872d53e8b`
- test_woo_tree_live_oracle.py: `fefbe674ebb543aca12bfa8391f9e25f7537676b1f3330f7e52c1f5dd83e3516`
- fixture-manifest.json: `f9102def648c5b87d207ddcd622ad65d56f848857921282c9c815aeeec8ee6b1`
- live-plan.json: `0e9efccb5cc1b5e1c139638a9b36892f68f119f6e9a3030aef7ac0c992d7c116`
- woo_tree.py unchanged: `a96fa36db62bc8fb9ff566a14bdb567e86842f0e0b8e362569896943d601ba73`

1. **Item 1 resolved:** independent black-box retention search has an explicit
   maximum of 17 public acquisitions, no private reservation-helper oracle,
   threshold-1/threshold/threshold+1 outcomes, page-atomic refusal and actual
   encoded-envelope fit checks. The raw body fits below the discovered threshold,
   so this targets canonical metadata overhead, not the response cap.
2. **Item 2 resolved:** path/query redirect rejection checks exactly one wire
   attempt; valid trailing slash checks actual final page/fact URL, last-hop hash
   and portable replay. Mixed public/private answers assert no wire/ledger entry.
   These exercise different guard/evidence seams from reload-only tampering.
3. **Item 3 resolved:** live coverage oracle independently interprets retained
   header pairs, page/query sequence, lengths, raw native IDs and exhausted
   request/item budgets; graph outcome is compared to that result. Two controlled
   oracle tests include deliberate partial-to-complete/empty state injection and
   inconsistent totals. Its execution must pass before actual live observation.
4. **Elapsed-bound note resolved:** stress checks monotonic elapsed time after
   every case, alongside observed peak RSS, before crediting the case. Original
   24-case manifest/count remains unchanged. Save the small smoke before stress.

**Final W10 coverage/design verdict: pass for execution.** This approves fixtures,
oracles, bounds and affected G1/G2 clarifications, not unexecuted results. Execute
focused repair tests/oracle sensitivity, then saved bounded stress and required
regressions before live. Any failure keeps verification incomplete; final code/
coverage review and honest blocked/inconclusive live reporting remain required.

# W14 independent final review — 2026-10-24
Reviewer `/root/woo_reviewer`. Read actual acquisition/projection/coverage/codec/
lookup implementation, tests/drivers, user docs, status/verification, manifests
and saved execution summaries/log tails. Existing successful verification is
credited for its stated cases, not as proof of uncovered invariants. Ran only
three small controlled probes (mock HTTP/public resolver; no production mutation,
commercial network, inference, parallel agent or broad repeated test suite).

## Reviewed SHA-256
- woo_tree.py: `a96fa36db62bc8fb9ff566a14bdb567e86842f0e0b8e362569896943d601ba73`
- test_woo_tree_acceptance.py: `4748e7e066979aaa32f387ff4d49b6aab8d792048d7f68caf5079e2f386ce985`
- test_woo_tree_mechanisms.py: `55e76b02abb95728718ab46f2a51685baf499374e4cad11ae008709dbaaebd58`
- woo_tree_stress_driver.py: `4efe27dd0f7cd963ca1ec968641f6f318614a7bc759a3710a7ff559ffeaef841`
- woo_tree_live_driver.py: `93ca9ce3502ee8988f06eb96173e2e8fa4622f976f4b696adb318d9872d53e8b`
- test_woo_tree_live_oracle.py: `391f1e5849c0b0ab2f895de2bf19462378984a82176433382c279f68bfcc914c`
- docs/woocommerce-category-tree.md: `ba4817b9c7ec1d1c933cae59c92a08e3556db0a470aa19a0a49806b39d845952`
- status.md: `b4f31c4cb0b9d86b3f9e1ed84c926065bb04ac945bbffafbe81c2c1e6b456da7`
- verification.md: `80c04bd89b4659be2c60bcaeca34fcd0e139dd9858227191f13c8095d8c1c2eb`
- evidence/stress-results.json: `d375ec90b6386171aef0c560451a759aaa22c522a7f8b6342459ac40da52889a`
- evidence/live-smoke.json: `4e6bf16313e01e0371c65866d0ef29ead70fa0bab875b87838482a5ee27af0fe`
- evidence/regression-results.json: `e22d7ee0827836e9d0d7c36fc38b6c402ad6616fe9d622c203b3f596ef0aaf79`
- evidence/final-review-probe.json: `c126dbeebcf8e76da5161eecc6c09ce004749f16dd934ce29dd259bb114a28d1`

## Blocking findings / exact required repair design
1. **Supported membership evidence alignment:** lookup calls `_supported` without
   the additional `validate_observations` boundary used by map_categories. A
   captured native-ID fact altered to raw_value=99 while retaining normalized
   ID/ref/evidence=1 is reported linked by the controlled probe. Evidence is
   truthy but no longer supports the asserted raw fact. Predesign adverse raw,
   outcome.source_values and evidence.resolve_pointer disagreement cases.
   Validate the candidate native-ID support's inspected source alignment; invalid
   candidates return unsupported, preserving scope mismatch precedence and the
   six already reviewed unsupported cases. Do not globally reject unrelated
   malformed observations or weaken existing assertions to accommodate a repair.
2. **Malformed initial URL escapes result contract:** `_endpoint` calls urlsplit
   before its guarded normalization try. `https://[broken` raises ValueError
   rather than unavailable/unsafe_url. Predesign malformed IPv6 URL and no-I/O
   assertion, including serialization of its diagnostic if within cap.
3. **Remote Unicode escapes escape bounded failure handling:** valid UTF-8 JSON
   containing an escaped unpaired surrogate in a category name reaches canonical
   UTF-8 hashing and raises UnicodeEncodeError. Predesign malformed Unicode on
   first/later page; return malformed_json (or explicitly reviewed facet policy)
   and retain valid prior pages as partial without throwing, fabricating a fact
   or losing resource accounting. No replacement-character normalization.

All three reproduced in 1.437s; compact actual/expected evidence saved in
`evidence/final-review-probe.json`. New tests/design must precede each diagnosed
repair and affected contract review. Focused/affected reruns suffice unless new
failures implicate shared behavior; completed broad checks need not be repeated
solely due to these local fixes.

## Accepted evidence / documentation follow-through
Saved focused 77-pass, distinct-page-clock affected pass, 24/24 stress with observed
RSS/time, general 1,018-pass and maintenance 106-pass results agree with log tails
and structured results. Counts overlap and are correctly distinguished. Saved
public Botiga observation establishes one complete two-root traversal within its
small limits; child edges/natural mutation remain synthetic-only observations.
No expansion is needed against the same already-complete sample. Narrow repairs
need not repeat that valid live observation unless they alter its path/semantics.

Low documentation cleanup: fixture-manifest retains historical pending review/
execution fields; update final dispositions or label those explicitly historical.
Module docstring still describes unimplemented G2 operations. Preserve earlier
stage evidence, deferred Shopify bridge and unrelated dirty work.

**Final W14 verdict: changes required for findings 1–3. W14 not complete.**
No commit/push/PR or final feature-complete claim. Actual token counters unavailable.

### W14 affected repair design/red review — 2026-10-24
Independent reviewer `/root/woo_reviewer` read the new behavior supplement,
`tests/test_woo_tree_final_edges.py` and saved red log before production repair.
SHA-256:
- test-design.md: `3702a774773b7deda8f7d25c1f6a8f9bdd29b89a284cb9346a2e55ecb12b5e61`
- test_woo_tree_final_edges.py: `956ab5dddc144eaf8354172dd3ee7bc3e9ebd015afeb78d73cd271c6c2567f1b`
- evidence/final-edges-red.log: `a49b40e8def68d471c487fcd8e000c08f4d448bd10a39fd08bba5fcdd8311be2`
- production unchanged: `a96fa36db62bc8fb9ff566a14bdb567e86842f0e0b8e362569896943d601ba73`

**Affected design verdict: pass for the three bounded repairs.** Four independent
native-ID source alignment defects require unsupported with unchanged input and
scope-mismatch precedence; valid independent native-ID support survives a damaged
sibling/label. This avoids global validation changing established unsupported
outcomes. Malformed IPv6 produces a no-I/O unavailable diagnostic. Escaped lone
surrogate first/later pages produce malformed/partial with bounded prior evidence,
charged attempts and strict portable replay. Expected results follow inspected
source support and UTF-8 portability contracts, not observed bad outputs.

Saved red is **7 failed / 1 passed in 0.20s**: four incorrect linked outcomes,
one URL ValueError and two UnicodeEncodeErrors reproduce the exact blockers;
valid independent support already passes. These are intended missing-behavior
failures, not import/fixture errors. No new production edit, test execution or
broader verification by this review. Implement one local repair per blocker,
run focused/affected checks, then return for final recheck. W14 remains pending.

### W14 final bounded repair recheck — 2026-10-24
Independent reviewer `/root/woo_reviewer` reviewed actual changed production
helpers, unchanged predesigned eight-case supplement, affected green evidence,
parser stress rerun, updated docs/status/manifest. No additional tests, network,
production edits, agent launches or broad suite repeats by this review.

Reviewed SHA-256:
- woo_tree.py: `56b63c46043c070d7412da5a6bc9a2d519da3da44891b34edd931d8dc62f6ecf`
- test_woo_tree_final_edges.py: `956ab5dddc144eaf8354172dd3ee7bc3e9ebd015afeb78d73cd271c6c2567f1b`
- test-design.md: `3702a774773b7deda8f7d25c1f6a8f9bdd29b89a284cb9346a2e55ecb12b5e61`
- verification.md: `9cb2a08afb9d76f9168ff77b864d60cd5be1de2b02c301788f615f50a836e405`
- evidence/final-repair-focused-affected.log: `a53d243b7331171778e7accb2e606c5a0c5226335033a3581d6407a2c1240bca`
- evidence/stress-results.json: `58f0c76c5cb4101c513c0b3f58f3cea15a30e25c5e2de7319c471c6b424bd01d`
- evidence/fixture-manifest.json: `ffce5bad37bbf56615b410113312224421980ebfba4d6951fb95d9bf92855626`
- reused evidence/live-smoke.json: `4e6bf16313e01e0371c65866d0ef29ead70fa0bab875b87838482a5ee27af0fe`
- final status.md: `019662e802e2e39f4d69fbc45bcf239c5fcba88f9aac704f7c81183501d1d908`
- final tasks.md: `ec106b71316926c8a45e8ba3f838da54f0554d0005e9b8c9c20a0e3109b64443`
Other previously reviewed interfaces, drivers and supported normal behavior remain
within the approved selected slice; no unrelated shared dirty module was edited.

**Blocker 1 resolved:** candidate-only native-ID validation invokes the existing
source-binding validator after checking exactly one conversion source value and
native-ID raw conversion. It inspects retained evidence pointer/value alignment,
returns unsupported for broken candidates, permits a separately valid sibling,
and preserves scope mismatch precedence. Unrelated label corruption cannot erase
valid ID support. Existing shared mapper is unchanged.

**Blocker 2 resolved:** URL splitting/normalization/endpoint encoding are inside
the same guarded boundary. Malformed IPv6 becomes unsafe_url without network;
its no-page diagnostic remains portable under cap.

**Blocker 3 resolved:** decoded JSON strings and object keys are checked for
UTF-8 encodability before hashing/retention. UnicodeEncodeError is contained by
the malformed parser boundary; first/later pages produce malformed/partial and
preserve actual attempt/prior-page evidence. No replacement characters are added.

Saved **130 passed in 20.94s** covers 85 feature/oracle plus 45 existing affected
category checks, including all eight final-edge cases. The reviewed unchanged
24-case driver rerun passes **24/24 in 8.673s**, observed peak RSS **146,325,504
bytes**, within its 60s/256 MiB observed limits. Prior stress evidence is retained.
Earlier general 1,018-pass, maintenance 106-pass and actual complete two-root
Botiga observation remain applicable and are reused; the repairs do not change
those normal source/transport semantics. Counts are overlapping, not additive.

**Final W14 verdict: PASS for opt-in Woo tree acquisition, strict portable result
and supported captured-membership lookup.** No open blocking finding remains in
that selected scope. W14/task/status marked complete by the independent reviewer.
Optional Shopify bridge W09/SC09–10 remains deferred; live child edges and natural
mutation remain unobserved, with synthetic mechanism/stress evidence reported
separately. No claim of universal store coverage, atomicity or unlimited scale.
No commit/push/PR. Actual session token counters unavailable; no quota estimate.
