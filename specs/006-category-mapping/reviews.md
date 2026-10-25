# Independent category reviews

## G1 — 2026-10-17 — pass

Reviewer: `category_reviewer`, independent of the category artifact authors. Reviewed
AGENTS.md, development workflow, constitution, all six platform findings, the two
minimal official-schema resolutions, and the actual behavior/test/task/research/plan
package. Bounded source inspection covered Normalizer/capture/evidence, portable
Product validation, scope, maintenance profiles/cache and native transport guards.
No implementation, tests, storefront requests, inference or Git changes by reviewer.

Reviewed SHA-256 revisions:

| Artifact | SHA-256 |
| --- | --- |
| spec.md | 2cc0ad5688c5aa5a5cb5a8a6f06141ca4f6e3032e353531f717bd48506c9c1ee |
| test-design.md | 213d5d8fb80cdc3945e279ca8b05f4e45459ccfd57690cd6dd877c95e3c92fcf |
| tasks.md | 2bdf51f9365cdfa4d52b4b8171d5c97957a215a2b0dfbec4a4488ba6128b1a47 |
| research.md | de8edadb2d530ef43d6f1250e5c260371107576873e9da124e72c1fef105508b |
| plan.md | 6d6a483f4709d16101dd519a87dab5334d58767ae0445b1b36669abf1c49cc77 |
| status.md | 55ba4e93b1662e549fd913d66ff65312c5fdda4e17536a873809c98fbf940ede |
| BigCommerce minimal schema | d17a2f1d0036199372c477903957c9bbbf9c4264dfd50aa6b109459cde6df8f5 |
| Magento minimal schema | f67e7b51652a44df619bc8397328fef271f8df54cdffcea5140f052fc41a7ece |

Findings and disposition:

- **P1, resolved before pass:** GraphQL partial errors, category rejection and
  missing/malformed connection completion metadata lacked exact native behavior
  and acceptance expectations. The authored native error contract and bounded
  C03a/b, C06a/b, C10a/b variants now preserve valid products and supported leaves,
  distinguish partial/unavailable/unknown from complete empty, and prohibit hidden
  retry/fallback. Real native parser/guard paths are mandatory, within the existing
  24-mechanism/100-invocation/120s envelope.
- Preliminary rule-overlap ambiguity is resolved by exact target-set equality,
  retaining candidate union on disagreement. Distinct memberships may map to
  different targets without inventing a conflict.
- Preliminary stale companion concern is resolved by an immutable original full
  Product/scope binding checked at encoding and decoding; recomputing a digest
  cannot bless mutated facts. Category-mode maintenance review restrictions are
  explicitly separated from unchanged legacy jobs.

The package sufficiently specifies source relations and namespace/store/basepath
scope, explicit public/auth capability limits, native BigCommerce/Magento acquisition
through fixed bounded queries, legacy compatibility, supported-source versus derived
mapping provenance, strict opt-in serialization and maintenance/cache policy binding.
Schema capability is correctly separated from actual live source observation.

**Verdict: G1 pass.** No unresolved blocking G1 finding. This permits skeleton and
red acceptance work only. G2 must verify exact wrapper/config/error/codec signatures,
native query producer/guard mode gating, child-process envelope integration and evidence
ownership. G3 must verify concrete reuse and component boundaries; neither gate is
approved here. The fixture author must count fixed variants before execution; passing
design review does not constitute mechanism, stress or live verification. Actual
session token counters are unavailable; no usage or quota estimate inferred.

## G2 — 2026-10-17 — pass after author repairs

Reviewer: `category_reviewer`. Inspected actual category contracts, API/evidence/
mapping/codec/maintenance stubs, native declarations, adapter contract, engine opt-in
stub, acceptance source and saved red results; no reviewer test execution or network.

| Revised artifact | SHA-256 |
| --- | --- |
| skeleton.md | 34abd9dafb7f3741e367095a53d09fafe26b97fa6b8b3d0290c96318f7d28cd4 |
| categories/contracts.py | 266c54fe000118be21b8c28cb3b3797688f8ce32dfe9759c16bb48ab7141875c |
| categories/evidence.py | 5bf56eaaa472406f3c6fb811a150fefe56342232c7ed49f4cc1e621917781e9f |
| categories/native.py | e55d4355153e992ded62976181da4d4a307fe5ab4157a250bf411584135826c1 |
| maintenance/engine.py | 257501ae7b8b3f09dfd0a087979345768f10e12a16e861c202ccccb9dc3aebc5 |
| tests/test_category_skeleton.py | 5afefb92c35a48cc8cee049d39a325402229b07d4f88b2cb5160cd7d906a5f74 |
| red-g2-revision.log | 1bef9acfaeea30dbc825d4b1c9286b80677d6fcce7c9aa8372e5880cf9296783 |

Blocking findings raised during review and resolved by authored revision:

- **P1:** Unbound fact tuples could borrow ID support for an unsupported label and
  lose transformation history. Required CategoryFactBinding now identifies exact
  facet/term/edge, and required existing ConversionOutcome retains source values,
  normalized result, acceptance and transformations. Skeleton explicitly requires
  facet-specific support checks and edge endpoint provenance; new C11 reds exercise
  mutation and support isolation.
- **P1:** Operation-global GraphQL error paths had no per-product origin seam.
  Shared localization now takes the actual product path, excludes sibling errors,
  strips descendant prefixes and propagates global/ancestor failures conservatively.
  Nonzero index1/index2 acceptance red distinguishes the affected product.
- **P2:** Agreed T04 C19 integration red was absent. Revised C19 uses real existing
  maintenance/store/source/cache paths with external transport controlled, requires
  same-policy cache reuse and new HTTP after rule change. Typed category_config
  opt-in now fails explicitly at the intended engine stub; None retains prior flow.

Saved revised evidence is 17 intended NotImplementedError failures in 0.48s after
the saved C19 smoke. Stub failures honestly establish missing behavior; they do not
prove native guard/error handling, cache correctness, codec integrity or stress.
The remaining designed real-path checks must precede their relevant implementation.

**Verdict: G2 pass.** Public opt-in contracts and declared integration seams can
express the G1 behavior; stubs do not fabricate success. Components design may now
proceed. G3 remains required before business implementation and must examine the
CategoryFact/FieldObservation boundary, reuse of capture/Normalizer/evidence validation,
full-product binding with nested mutable values, producer-owned query constants and
mode guard, and actual child-process/cache ownership. Those are concrete component
review obligations, not preapproved implementation choices. No expanded cases,
parallel execution, storefront observation or quota estimate is authorized by this pass.


## G3 author disposition — durable creation policy (review pending)

Author category_bigcommerce addressed reviewer lifecycle blocker in components.md,
skeleton.md, contracts/Store constructor+category_policy explicit stubs and C19 tests.
Store, not runtime engine, owns full validated immutable canonical config snapshot at
atomic create(goal). Persisted mode is authoritative across recovery; old missing rows
legacy, same-job mode/digest mismatch rejected before state/dispatch, new-job changed
policy cache miss. Engine optional config is expected identity only. No activation of
old jobs from current Store defaults. Exact migration/snapshot ownership documented.
Actual creation smoke1 intended NI failure0.36s then20 intended NI failures0.76s saved;
no business algorithm, passing lifecycle claim or reviewer verdict authored here.

## G3 — 2026-10-17 — pass after lifecycle repair

Reviewer: `category_reviewer`. Independently reviewed the actual component reuse
matrix, refined skeleton/contracts, Store creation boundary, C19 fixture source and
saved revised red evidence. No reviewer code execution, source research or network.

| Revised artifact | SHA-256 |
| --- | --- |
| components.md | 4f7b2376c47c68631ccdd22ceb6394b59370a641f5e9ae315c008fa015c7be19 |
| skeleton.md | 1c61414e67df77374be56c231bf94f3ab67aaec67507cb2093eb6150b31f04f7 |
| categories/contracts.py | 67ff20be078bb986038f120f43be58815e2542a59bc05fce305e1abc943b49d2 |
| maintenance/store.py | 1812f2eda3f796dd4cebf482cdc6047fdcdff55801c2177ce22d774771dd8baa |
| tests/test_category_skeleton.py | 0af920bf01919ff651fbaa8d7964122bece1bc2d3be790dcf09f17c3b7683d6e |
| red-g3-policy.log | 3fa1aaa635a933b5be7e738a75e94c92eb6c1b51f558da1469c45687a7aa2838 |

**P1 resolved:** The initial model required durable policy at job creation while
only Engine received category config; Store.create owns the insertion transaction.
Revised Store constructor snapshots future-job configuration; create atomically
persists authoritative mode/full canonical JSON/schema/digest. Engine config is
expected identity only. Missing historical policy remains legacy permanently;
saved snapshot reconstruction needs no original caller object. Mode/digest mismatch
rejects before state/reservation/wire/recovery, whereas changed policy on a new job
produces a different cache identity. Schema2 explicitly protects enabled databases
from old readers. C19 now configures Store and includes creation/reopen and legacy/
changed-policy mismatch variants. Revised 20 intended NI reds (0.76s) remain evidence
of missing implementation, not passing lifecycle verification.

Reuse is concrete and cohesive: one extracted _capture support-for-outcome helper
serves ordinary attach_contract and category source_fact; existing Normalizer,
ConversionOutcome, Evidence, SupportState and primitive codecs retain their roles.
CategoryFact supplies native facet/edge binding that Product FieldObservation does
not represent; it is not an independent trust engine. The shared mapper, explicit
companion codec, producer-owned fixed query constants/mode gate and existing process/
cache/store boundaries have named consumers and common ownership. The original
binding now covers nested category/evidence/outcome/mapping state as well as Product
and scope; no frozen-dataclass assumption substitutes for revalidation. Digest
integrity is explicitly separated from source authority.

**Verdict: G3 pass.** Implementation may proceed in bounded dependency order with
relevant acceptance reds first. Every platform owner must acknowledge all five
peer findings and final shared contracts before its source edits; this review does
not claim those future acknowledgments already exist. Shared-support extraction
must retain focused ordinary provenance regression coverage. Native error/guard,
codec mutation, Store migration/recovery/cache and remaining C01–24 mechanisms
still require actual green evidence, independent coverage review and the separately
bounded live plan. No final verification or production-readiness verdict is implied.

## Interim source and mechanism-driver review — changes required

Reviewer: `category_reviewer`, 2026-10-17. Bounded source/test/driver inspection only;
no reviewer tests, network or model execution. Reviewed source-checkpoint.json, all six
final peer acknowledgments, shared capture/normalization bridge, API/adapters/mapper/
validation/codec, native errors/queries/guard, Store policy/engine/cache/worker flow and
prepared C01–24 mechanism map. Existing saved green groups are author evidence, not
independently rerun results. G1/G2/G3 remain historical approved design gates; this is
an implementation/verification finding, not a final pass.

Reviewed SHA-256:

| Artifact | SHA-256 |
| --- | --- |
| tests/category_mechanism_driver.py | a1cafaf1121daa31b70c3f16bff3eab0ab5e78775f882bbbf80c7f432a567276 |
| tests/test_category_shared_contract.py | 7e45cbd7e662c2dd6906f73d9103473ebc6ab94c7584e50fdeb4b24cb67c8372 |
| mechanism-plan.json | f3ead34dfcd49b53c6a7dba55ea08f9de1c0ad7195772801297e1367884e28ed |
| categories/adapters/magento.py | 8ef656f99087a2a59af52350dba1b808f1adc5b9baf72e24d94e7a7ad85ad28d |
| categories/validation.py | c8f92701681a8b608d3924512d67fee0bd45ec1360a6496fceb6a117e937d16a |

Blocking findings, in priority order:

1. **P1 — Failed Magento facets remain usable facts.**
   `categories/adapters/magento.py:observe_categories` calls source_fact normally for
   UID/name, then only downgrades relation completeness when native errors exist.
   A captured nonnull failed UID/name therefore remains OBSERVED and can match a
   canonical rule. BigCommerce correctly rejects the affected facet. Existing Magento
   error test uses name=null and therefore misses the faulty nonnull case. Reject
   support for exactly affected local facets/global errors while retaining unaffected
   facets/siblings. Add fixed C06/C11 nonnull failed UID and name variants; a rule on
   the failed facet must not map, and the unaffected ID/label must retain support.

2. **P1 — Driver does not enforce reviewed timeout/cleanup contract.**
   `tests/category_mechanism_driver.py:main` gives one pytest process an aggregate
   timeout but does not enforce 15s per invocation. subprocess.run timeout kills its
   direct child, not auxiliary/domain descendants. Use bounded per-test enforcement
   and process-group/session cleanup with kill and wait for collection and execution,
   save timeout/failure state and stop at first failure. Bound log retention as well.
   Do not run the current driver. Collection count <=100 and single sequential process
   intent are appropriate; aggregate120s and worker/thread caps must remain intact.

3. **P2 — Edge endpoint semantic validation is incomplete.**
   `categories/validation.py:validate_observations` checks an edge binding exists and
   evidence equals raw_value, but never checks an OBSERVED parent_id/child_id outcome
   against binding.edge[0/1].native_id. Accepted history saying source parent7 may
   therefore be bound to edge(parent99,child) and survive validation/binding/codec.
   Validate each observed endpoint conversion and bound ref exactly; keep unsupported
   raw edges inspectable without representing them as proven ancestry. Add a C13
   adversarial endpoint-mismatch rejection through the real validator/mapper/codec
   boundary. Do not repair a malformed binding by changing asserted expected values.

4. **P2 — Mechanism map overstates designed coverage.**
   C20 currently selects only category_review_reasons, not the required real category-
   enabled maintenance/matcher safeguard interaction. C24 selects legacy projection/
   default-error checks, not category encode/checkpoint failure + same-policy retry
   atomicity. C13/C22 select a cycle and member/byte/ref bounds, but omit the designed
   explicit ancestry depth7/8/9 and missing-parent cases. Extend these existing families
   with exact predeclared inputs/outcomes, or cite equivalent actual saved runs.
   For Shopware `parent_by_child` traversal, supported explicit edges remain source
   facts, absent parent means partial/category_parent_unavailable with no fabricated
   root/path; a chain continuing beyond depth8 is partial/category_ancestry_depth_reached;
   valid shorter/at-boundary chains stay complete only where source membership/parent
   evidence warrants it. Execute expected edge/root/depth semantics against the real
   adapter/validation path. Keep <=24 mechanisms/100 fixed invocations/120s; replace
   redundant variants rather than expand the approved envelope.

Positive findings: six acknowledgments explicitly cover all five peers/final contract;
one common support helper serves Product and category facts; one shared mapper and
producer-owned query constants are present. Store schema2 policy snapshot/legacy mode,
expected-only Engine config, cache policy identity/origin authorization, explicit worker
codec and existing matcher/field checks have concrete integration paths. Native added
fields are actually dispatched by producers, rather than being adapter-only fixtures.
These findings do not waive the blocking cases or prove every platform live.

**Verdict: changes required; bounded driver not approved yet.** Approved next work is
only the diagnosed source/driver repairs and missing fixed variants above, followed by
focused affected checks and bounded independent rereview. No broad sweep, full suite,
live source requests, model call or final completion is approved by this interim review.

## Documentation and bounded live plan — static pass, execution conditional

Reviewer: `category_reviewer`, 2026-10-17. Reviewed only docs/category-mapping.md,
README category addition and tests/category_live_driver.py; no test, driver or network
execution. Independent AST inspection confirmed all four saved-JSON newline constants
are actual one-character newlines; an earlier display-escaping concern was withdrawn.

| Artifact | SHA-256 |
| --- | --- |
| docs/category-mapping.md | dfc0c56df6885cd1f753cd2365e9c6a367259b6a089d0b9252cc59d0c2139e8d |
| README.md | 16b52698159b18aa28a97e3b715ccee8f30490f37af2e5aaadf46d26f8a137c5 |
| tests/category_live_driver.py | 33c99f5bcc226ed663168d4f7a3e8e36fbfddd11cbbfacc1012521c6265f253f |

Documentation reflects the explicit API, source semantics, constructor policy owner,
schema migration and remaining verification limitations. The revised live driver
requires a saved Shopify smoke before expansion; pins six public sources and exact
saved-public native endpoint origins; permits no new credentials/model/browser/write;
caps actual attempts12 total/2 per platform, retained products2, request10s, aggregate120s
and response2MiB. It reserves attempts durably before wire and charges full request
timeouts conservatively on resume. Interrupted reserved cases become inconclusive
without repeat; cases interrupted before any reservation may start safely. Request
and response encoding are identity-only, with rejection before raw byte streaming.
Safe reason codes distinguish caps/rate limiting/timeout without logging headers,
tokens or query strings. Category observation requires an OBSERVED fact in the
expected namespace/relation, rather than merely an ordinary Product companion;
unavailable source/category remains blocked/inconclusive. Catalog completeness is
recorded separately and no complete taxonomy claim follows from a sample.

**Verdict: static live-plan/docs pass.** Only after the separate source/mechanism
repairs receive independent approval and required offline checks pass may root run
the saved Shopify smoke, inspect/save it, then expand within the same cumulative
budget. This approval does not supersede the outstanding source/mechanism-driver
changes-required verdict or claim any actual live observation or final completion.

## Interim repair rereview — fresh child boundary changes required

Reviewer: `category_reviewer`, 2026-10-17. Reviewed authored design-before-test repair
cases, actual changed source/test/driver, refreshed checkpoint and saved targeted
evidence; no reviewer test/network execution. Earlier four findings are resolved:
shared native_source_fact rejects the affected nonnull Magento/BigCommerce facets;
observed edge endpoints match exact raw/outcome/bound IDs; C20 uses real category-
enabled Store/Engine/matcher with independent RAM/boot/identity/profile veto outcomes;
C13/C22 cover7/8/9-edge and orphan semantics. Driver now runs exact collected nodes
sequentially with15s limits,120s shared deadline, bounded logs and session kill/wait,
including production multiprocessing children that inherit the process group. Saved
helper evidence checks a timeout auxiliary descendant and bounded retained output.

| Reviewed repair artifact | SHA-256 |
| --- | --- |
| source-checkpoint.json | 279ecd7c3c857330c863460305a619094f6c3c3dd16345899ea809e97b0ca074 |
| test-design.md | 60fd04b8d85c9943cc782a7b94e05f2242705dca695ad49e7c24458a5bb28f42 |
| tests/category_mechanism_driver.py | d0d6e9641d1c92cff8af657949304599048462cf02f1ae37dc4dedfcc5c2437e |
| tests/test_category_review_repairs.py | dc6fccf76c69e8ca7b383aaa3b6411345eeeac195ede0884a328b2c455c22c9b |
| categories/validation.py | 092199930af26416640444ebc7457df060a07b376c1c2bb464a7f2f08f7cd9b0 |
| categories/adapters/magento.py | 0fb92acd81971297ab5e6978d3d3cc61e157ec891f24f3485d8958e7d5299b36 |

**P1 — Fresh child envelope is checkpointed before parent validation.**
`tools/sources.py:GuardedSources.execute` parses auxiliary JSON and returns records
without strict companion decoding/policy validation. `maintenance/engine.py:_source`
validates cached companions, but sends fresh source result directly to checkpoint/
cache; `_reconcile` decodes afterward. A malformed child companion can thus become
a committed/cached source success before rejection. The current C24 damaged-binding
test calls the real encoder itself and raises before source return; that proves
exception atomicity but hides this missing untrusted-result validation.

Required bounded repair: validate fresh auxiliary companion records and exact policy
digest before returning/accepting the source result, using the existing strict codec
(prefer the shared guarded source boundary so nonmaintenance consumers are covered).
Extend C24 with a malformed fresh child result that returns a damaged binding without
a preemptive encoder call; parent must reject before successful source/checkpoint/cache,
and same-policy explicit retry must produce one valid committed companion. Keep the
reviewed24 mechanisms/100-invocation/120s limits; no broad sweeps or live requests.

**Verdict: changes required on this one boundary.** Revised mechanism driver and the
other repaired mechanisms are acceptable for their stated scope, but driver execution
remains conditional on the fresh-child repair, focused green evidence and bounded
independent rereview. Static live-plan/docs pass remains unchanged. No final pass,
full-suite execution or actual live observation is implied.

## Source/driver repair checkpoint — pass for bounded execution

Reviewer: `category_reviewer`, 2026-10-17. Bounded inspection of the frozen fresh-child
repair, exact C24 injector, shared cache validator and saved red/green evidence; no
reviewer test, driver or network execution. Earlier native facet/edge/depth/matcher and
driver findings remain resolved at their reviewed revisions.

| Artifact | SHA-256 |
| --- | --- |
| categories/portable.py | 2e3a0bbcf9e1214e09fff008ed7168320b9af99e0a6614481c74293c261e93fa |
| tools/sources.py | 64b0f0c3c1896102a11e9355694ce12780c81bd25525a8045983886823bd99aa |
| maintenance/engine.py | 7ff9befb3991442030106c837448d83e81fa643a419536963183b1ce6d32e1e4 |
| tests/test_category_review_repairs.py | 07b54a1ca9d3ee901c66e480ef8e4db28741dfbc51810f134d44cca0a074c179 |
| tests/category_mechanism_driver.py | d0d6e9641d1c92cff8af657949304599048462cf02f1ae37dc4dedfcc5c2437e |
| source-checkpoint.json | fd416592c0127e2d6361ed323d746abb34806b8d1bcd482e3fc6d95c409f3d35 |
| mechanism-plan.json | 368a1d3fe627d8aff33d82782836c56a7091cd89cc8c9fbcdf9e5e3fe6bb7b01 |

**P1 fresh-child boundary resolved.** C24 now corrupts an actual OwnedProcess parse
reply and returns bytes without invoking a codec in the injector. Saved intended red
demonstrated premature committed source success. GuardedSources now immediately runs
the shared strict companion collection validator after JSON decode, checking count,
envelope/binding and expected options digest AND exact scope before result acceptance.
Maintenance cache reuse consumes the same helper; ordinary legacy paths are preserved.
Saved four targeted green cases cover both C24 failures/retry and C19 policy/cache
reuse/corruption. The fixture exercises the actual untrusted parent/child boundary;
it no longer manufactures early rejection that masks checkpoint ordering.

**Verdict: source/driver checkpoint pass; bounded execution approved.** Root may run
the reviewed75 exact parameterized invocations across24 mechanism families with seed26,
one sequential driver,15s per node,120s shared deadline, bounded logs and process-group
cleanup. Save result and stop on first failure; use the diagnosed repair policy, not
an expanded sweep. Then run required affected offline/repository checks, reusing still-
valid saved evidence. Only after these pass may the separately approved live plan run
its saved Shopify smoke and then bounded expansion. This is approval to execute the
reviewed checks, not a claim that the mechanism driver, required offline checks or
live observations have passed. Final independent evidence review remains mandatory.

## Runner-only diagnosed repair — pass for one remaining-node attempt

Reviewer: `category_reviewer`, 2026-10-17. Static review of revised runner, progress-only
pytest plugin, archive manifest and design/verification addendum. Read-only hash and
saved-status comparison found no mismatches across archived metadata, original logs or
source/test snapshot; saved41 successful nodes exactly match manifest passed_nodes.
No test, repaired runner or network execution by reviewer.

| Artifact | SHA-256 |
| --- | --- |
| tests/category_mechanism_driver.py | 7b283bcf015c3d2644e6bf1b60eb243afce028787e8541b0834b389d3d8ac46a |
| tests/category_mechanism_plugin.py | 544abc25f091a5dae0e5c4a3a7c55d3effcca0aa19130fd8de07a25f9e891308 |
| mechanism-attempt1/manifest.json | dc4c610aa08440cf77d4228e3f29ce25c78a21d68652e69778d828d3ef5df2dd |

The first run exhausted aggregate120.019s after41 passes and one interrupted node.
The archived original timeout label is preserved with explicit aggregate-timeout
correction; no mechanism assertion failure is inferred. Reusing the unchanged41
passes is appropriate. The repair selects only the34 remaining exact IDs in one
pytest session; plugin verifies exact collection and saves atomic start/report/end
state. Independent parent enforces15s collection/node and120s repair aggregate,
retains64KiB session log, and kills/waits the session group. Exclusive start marker
prevents automatic repeat. No source, fixture, assertion or planned family changed.

**Verdict: approve exactly one repaired remaining34-node attempt.** Total started
invocations are bounded42+34=76, within100. Save split evidence and combined elapsed;
do not claim75 passed in one120s run. If the repair fails, preserve results and report
the limitation rather than restart or enlarge the sweep. Existing source/live-plan
approvals remain conditional on actual offline completion and final evidence review.

## C22 fixture repair and exact13 completion — pass for one attempt

Reviewer: `category_reviewer`, 2026-10-17. Reviewed the byte fixture diff, targeted
saved result, attempt2 archive, frozen completion manifest and runner-only path/count
changes. Independently hashed current source/test/archive/log records: no mismatches.
Reversing the fixture-only change reconstructs the exact previously approved shared
test file digest7e45cbd7e662c2dd6906f73d9103473ebc6ab94c7584e50fdeb4b24cb67c8372.
No reviewer tests, driver or network execution.

| Artifact | SHA-256 |
| --- | --- |
| tests/test_category_shared_contract.py | af6ea53fc450a02baf74e8e0d26007e7c7297dd8cd51eaaff0af866548387ca9 |
| byte-fixture-repair.json | 05352820569d673bc8fcac21b8d73173d4414aadc377a9860f638d08c72b1f35 |
| tests/category_mechanism_driver.py | dd404cd86082ef68b9e15d60beebd8b6d0667ca7ff7b2dfb0e835143573713c9 |
| tests/category_mechanism_plugin.py | 544abc25f091a5dae0e5c4a3a7c55d3effcca0aa19130fd8de07a25f9e891308 |
| mechanism-completion-manifest.json | 34b82dd8d8f95ba5414f2e7ab5e89d5abbb1fbcc4ffb97d2795bc67648853017 |

The second attempt stopped on the first real assertion failure after18 additional
passes. dataclasses.replace discarded dynamic Product trust attachments that the
measured baseline included; deepcopy preserves them before description padding.
All exact262143/262144/262145 byte expectations are unchanged, and targeted3 passed.
This is an independently verified fixture repair, distinct from the earlier runner
aggregate timeout and earlier production support/parent-boundary defects.

Frozen evidence covers62 unique original nodes (41+18+3 targeted),64 invocations
started, and13 unseen nodes. Completion revalidates hashes, fixes exact collection,
uses a fresh exclusive marker/progress/log path and retains existing independent15s
watchdog/session cleanup/120s-attempt bounds. Previous failed evidence is preserved.

**Verdict: approve exactly one remaining13-node completion attempt, maximum77 total
started invocations.** Do not rerun62 completed cases. Preserve/report any failure
without automatic restart. Report split evidence across attempts: prior wall141.472s,
targeted pytest0.37s separately, plus actual completion time; no single120s/full75-run
claim. Production source remains unchanged. Required offline checks, bounded live
observations and final independent handoff review are still pending.

## One-shot Magento diagnostic — static pass for one remaining request

Reviewer: `category_reviewer`, 2026-10-17. Inspected saved live status and the exact
diagnostic script; no reviewer test/network execution. Existing status has6 actual
requests including1 Magento request; Shopify/Woo category observations and other
blocked/inconclusive outcomes remain preserved.

| Artifact | SHA-256 |
| --- | --- |
| tests/category_magento_live_diagnostic.py | 5c285543c9dea6997ab3ebc69fd8a74fe394cf176a71945e514e42330ddae1ca |
| reused tests/category_live_driver.py | 33c99f5bcc226ed663168d4f7a3e8e36fbfddd11cbbfacc1012521c6265f253f |

Diagnostic requires exactly1 prior Magento attempt and reserves an exclusive marker.
It reuses the same status/BudgetTransport, HTTPS endpoint, identity/raw-byte cap,
10s request timeout, per-platform2/total12 budget and conservative resumed time charge.
Only Magento page_size2/max_pages1 is dispatched, with no retry or other platform.
Captured raw products retain actual URL/time and are saved <=2MiB before normalization;
the later local replay is explicitly offline. Original inconclusive case is retained,
diagnostic results are separate, and only fixed safe CategoryError reasons are shown.
Unknown errors stay unclassified rather than exposing arbitrary exception content.

**Verdict: approve exactly one remaining Magento attempt, then offline diagnosis
from its saved fixture.** This may establish a legitimate configured record limit or
a reproducible defect; do not assume either before the replay. No new production
change, other source retry, model or broader sweep is approved. If the attempt fails,
preserve limitation/evidence without another request. Final evidence review remains.

## Final independent evidence and handoff review — pass with recorded limits

Reviewer: `category_reviewer`, 2026-10-17. Reviewed final checkpoint, current status/
tasks/docs, actual saved offline/SDK/mechanism/live results and Magento diagnostic.
Read-only hash comparison verified all60 checkpoint files and zero production-source
deltas from the approved tested source checkpoint. No reviewer tests, network,
source changes, commits or publication. This final entry itself follows that snapshot.

| Final evidence | SHA-256 |
| --- | --- |
| final-checkpoint.json | 5f4e4c5988e40eec3f3eb15b0b7077b08d22c88b8cd2d7808bdea789e991fe2b |
| offline-status.json | bead7c4bb5afb7cd3aa5ecda15bb39d079cc021f6d5a305e04b942f032bcebe6 |
| mechanism-status.json | 40ef878605c2f9bdeb150d590aae089eb64dbd5e6a22ff843bebf735a8fe3a82 |
| live/status.json | 3dc28d6648b9851d2f168569837bd3e6938feb0ae4f7bf5290bc39c3464c9922 |
| verification.md | f8f404e46c02de68fa3556e775f85fb19ee3b3661385e3c239f8b8ec2a6e0905 |

Offline evidence is consistent: whole workspace1054 tests passed377.35s on Python
3.10.11, driver380.575s within480s, exit0 with no timeout/truncated log; optional-SDK-
absent import/8 schemas and installed MCP1.30.0 checks passed. Python3.11/3.12 matrix
was not run locally and remains explicitly unclaimed. Existing dependency warning
and preexisting maintenance work are identified rather than hidden.

Mechanism result covers75 unique exact planned checks across C01–24,77 total starts.
Saved split evidence preserves the aggregate timeout and fixture failure, reviewed
fixture-only correction and exact13-node completion. Combined driver wall156.636s
plus targeted pytest0.37s is reported separately; there is no false single120s/full75
run claim. Source hashes support reuse; diagnosed production fixes have real-path
failure/green evidence, including facet support, edge bindings, native guards,
child-process validation, cache/policy recovery and matcher/persistence interactions.

Live result is deliberately narrower:7 actual HTTP200 requests within2/source and12
total; only Shopify custom labels and Woo memberships have supported category facts.
Shopware null category fields and generic no structured product are inconclusive;
BigCommerce access configuration is blocked with0 requests. Magento2 requests returned
products but companion normalization hit the configured256KiB record cap. The reviewed
diagnostic saved161080B original captured raw before offline replay; ordinary Product
records447771/454858B already exceed that cap. Both exact safe replay reasons establish
the expected boundary, not a successful live companion. Docs disclose this practical
limit without dropping evidence or raising caps. Conservative61.468s reservation
charge is correctly distinguished from actual network time. No credential acquisition,
model/browser fallback, storefront writes or unsupported live completeness is claimed.

**Final verdict: pass for the implemented and documented slice, with those explicit
live/platform/runtime limitations.** No unresolved blocking finding remains. Root may
complete T16/status bookkeeping and hand off the result; no further test sweep or live
retry is needed. This is not universal taxonomy coverage, successful live verification
of every platform companion, or deployment/merge/publication approval. Actual session
token counters remain unavailable; no quota estimate inferred.
