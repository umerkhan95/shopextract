# Category verification evidence — 2026-10-17

## Actual live observations (after offline pass)

The independently reviewed first Shopify smoke was saved before expansion. Seven
actual read requests total, all HTTP200: Shopify1, Woo1, Magento2, Shopware2, generic1,
BigCommerce0. No other retries, credentials, browser, provider or model calls.
All per-platform2 / total12 / request10s / byte2MiB caps held. Final saved budget
charge61.468s includes conservative full-timeout reservations on resumed drivers;
it is not actual network elapsed time. Files: `artifacts/category-mapping/live/`.

| Platform | Actual observation |
|---|---|
| Shopify | Two products, each one supported custom `product_type` label; standard category/collections missing, never invented. |
| WooCommerce | Two products with independently supported category ID/name memberships. |
| Magento | HTTP products returned, but companion size rejected. One separately reviewed final diagnostic saved161080B original captured raw data BEFORE offline replay; ordinary Product records447771B/454858B already exceed the262144B companion cap. Both replay rejections are exactly `Category companion byte cap exceeded`. This is a legitimate configured boundary, not a source/parser success claim. Live companion verification remains limited. |
| Shopware | Two products, returned category membership/index fields null; no supported membership claimed. |
| BigCommerce | Blocked: saved published endpoint/access configuration unavailable; zero requests and no credential acquisition. |
| Generic | Public product page returned, but the chosen structured-data parser yielded no products; inconclusive structured-category observation. |

Magento diagnostic command initially lacked repository root in PYTHONPATH and failed
before main/import, marker or network. One invocation-environment repair to
`PYTHONPATH=src:.` succeeded; this did not consume an HTTP attempt. Diagnostic script
and supplement were independently reviewed before execution. Original inconclusive
Magento row remains unchanged; diagnostic/offline replay are separately identified.
No production source changed after the1054-test pass. Controlled C01–24 mechanism
proof covers the other source/error/guard/persistence cases independently; it does
not establish live complete category catalogs or commercial change frequency.

## Final verification checkpoint

All 75 exact planned invocations across C01–24 are now covered by passing saved
evidence, seed26, with source/evidence hashes independently checked before reuse.
This is split evidence, not a clean 75-case run within 120 seconds:
first attempt reached its aggregate deadline at 120.019s (41 passes, one interrupted);
single-session repair took 21.453s (18 more passes, one byte-fixture failure);
fixture-only deepcopy repair preserved Product trust attachments and the exact byte
assertions (three targeted passes, pytest0.37s); approved fixed completion ran only
13 remaining nodes (13 passes, pytest9.92s / driver15.164s).
Combined driver wall156.636s, plus separately recorded targeted pytest0.37s;
77 cumulative invocation starts including interrupted/failed invocations and targeted
byte checks, below100. Each driver attempt stayed within its120s bound; the extra
attempts were separately reviewed diagnosed repairs. No passing cases were restarted
by the completion driver. Original attempts/logs remain archived, source hash validation
passed, and exclusive markers prohibit automatic restarts. See mechanism-status.json,
mechanism-attempt1/, mechanism-attempt2/, byte-fixture-repair.json and completion manifest.

Required offline regression passed: **1054 tests /377.35s pytest**, driver380.575s,
Python3.10.11, exit0, no timeout or truncated log. One sequential pytest session with
`-q --tb=short --maxfail=1`, capped at480s (the existing CI groups' aggregate cap),
512KiB retained logs and existing CPU/thread limits. Source is frozen. This checks the
whole current workspace, including preexisting maintenance work. Saved offline-status.json
and offline-suite.log. Optional-SDK-absent import compatibility passed with8 schemas;
installed MCP1.30.0, sdk-compatibility.json. Local Python3.11/3.12 CI matrix has not run.
The environment emits its existing requests dependency warning; tests still pass.
No inference/model/provider calls. Actual live results under the separately reviewed request/byte/deadline plan are
recorded above.

## Baseline (coordinator, before category skeleton)
Existing normalize smoke44 passed/0.15s; saved
`artifacts/category-mapping/baseline-normalize.log`. This is compatibility baseline only.

## Intended red acceptance (G1 passed; G2 pending)
Environment: repository .venv Python3.10, PYTHONPATH=src; OPENBLAS_NUM_THREADS=1,
OMP_NUM_THREADS=2,MKL_NUM_THREADS=1,TOKENIZERS_PARALLELISM=false. One test process at a
time; no inference/model/provider, installation, storefront, Git or issue operation.
The first smoke invocation lacked PYTHONPATH and could not import shopextract from
conftest. Diagnosed once and repaired invocation environment only; not a red acceptance
result. Final saved smoke/full logs below contain no collection/import/syntax failures.

Smoke command:
```sh
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 MKL_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false .venv/bin/python -m pytest tests/test_category_skeleton.py::test_c01_normalize_preserves_custom_label -q --tb=short
```
Result:1 collected,1 intended NotImplementedError failure,0.25s. Saved before full file:
`artifacts/category-mapping/red-smoke.log`.

Bounded red command (after saving smoke):
```sh
PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 MKL_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false .venv/bin/python -m pytest tests/test_category_skeleton.py -q --tb=short
```
Result:13 collected,13 intended NotImplementedError failures,0.35s; six separate platform
adapter stubs, normalization/extraction wrappers, shared mapper, config validation,
encoder/decoder, maintenance review. Saved `artifacts/category-mapping/red.log`.
No passing/implemented category mechanism claimed; exceptions are intended missing
business behavior, not deliberately weakened assertions or fabricated success reports.
Native extraction test uses HTTPX MockTransport boundary; current wrapper fails before
network/production algorithm, so this is a seam red, not native guard/error verification.

C19 real cache/checkpoint red and remaining C01–24 native/error/guard/stress fixtures are
pending; relevant red cases must precede their implementation. No complete synthetic,
stress or live verification exists. G2 signatures/ownership review pending; components
stage/G3 must pass before business code. Actual session counters unavailable; no quota
estimate. Red runs are14 total fixed invocations including smoke repetition, far below
reviewed100 parameter invocations/120s; later green driver budget remains separately saved.


## G2 revision reds
Changes: typed fact facet/term/edge binding with retained existing ConversionOutcome;
per-product native error localization stub; typed opt-in engine constructor integration
stub; required C19 real cache scenario. No business implementation. Existing legacy
constructor behavior unchanged when category_config=None.

First saved revised smoke (same capped env/PYTHONPATH as above):
```sh
.venv/bin/python -m pytest tests/test_category_skeleton.py::test_c19_real_source_cache_reuse_and_rule_change -q --tb=short
```
Result1 collected/1 intended NI failure0.39s at real MaintenanceEngine opt-in source/cache
constructor stub; artifacts/category-mapping/red-cache-smoke.log. Cache test sets up real
store/engine/source harness; no HTTP occurs while constructor is intentionally unimplemented.

Then bounded rerun:
```sh
.venv/bin/python -m pytest tests/test_category_skeleton.py -q --tb=short
```
Result17 collected/17 intended NI failures0.48s; no import/syntax/collection errors.
Saved artifacts/category-mapping/red-g2-revision.log. C11 facet bridge/mapping and C03
nonzero-index localization reds fail at corresponding explicit stubs. This establishes
correct missing-behavior red seams, not passing mechanism/cache/native verification.
Total skeleton red invocations32 (old smoke1+old full13+new smoke1+new full17); no fullsuite,
actual storefront/model/provider calls or broad research. G2 rereview pending.


## G3 durable policy repair reds
Fixed C19 variants now configure MaintenanceStore (creation owner), verify canonical full
policy snapshot/reopen, and reject legacy/same-job changed policy before wire/state.
All implementation seams remain explicit NI; None default constructor paths unchanged.
Same capped PYTHONPATH/thread environment; one process sequentially:
```sh
.venv/bin/python -m pytest tests/test_category_skeleton.py::test_c19_store_creation_persists_canonical_policy -q --tb=short
.venv/bin/python -m pytest tests/test_category_skeleton.py -q --tb=short
```
First smoke1 intended NI failure0.36s saved red-policy-smoke.log; then20 collected/20
intended NI failures0.76s saved red-g3-policy.log (under artifacts/category-mapping/).
No import/syntax/collection failures or actual storefront/model/network calls. Lifecycle
variants are within C19, not extra mechanisms. Total skeleton invocations53 across all
historical runs; no passing cache/native/mechanism/live proof claimed. G3 review pending.

Initial green source smoke:1 passed0.08s saved green-smoke.log. First focused core file:19 passed/1 failed4.62s saved focused-core.log. Diagnosed fixture blocker C20 constructed a default GENERIC Product with Shopify scope and fake binding/digest; strict codec correctly rejected it before review. Replaced ONLY fixture construction with actual captured normalize_with_categories missing-type path; assertion category_unavailable unchanged. One fixture repair, no trust/codec relaxation.

First five-platform focused file set:67 passed/3 failed0.97s, focused-platforms.log. Root-authorized one fixture-only repair: three generic C08 feed wrappers had original XML/CSV sources with title+category but no valid Product identity/price/image, so normalize correctly returnedNone. Added real fixture ID D1 in ORIGINAL feed source before parser/capture (not after-capture enrichment); category assertions/normalization validity unchanged. Targeted rerun follows.

BigCommerce focused native/schema/error/guard set initial7 passed/1 assertion API fixture failure0.78s, focused-bigcommerce.log. ToolError string is its code; detailed reason is .message. One test-only correction asserts both exact .code and .message (same denial requirement, no guard relaxation), reruns only failed C21. Generic original-source identifier fixture repair targeted3 passed0.21s, focused-generic-repair.log.

## Source-stage checkpoint (independent source/driver review pending)
No full suite/stress/live execution. All focused tests ran sequentially with the saved capped environment.
- Core seams: first focused19pass/1 invalid-fixture failure4.62s; unchanged assertion repaired with real missing-type wrapper, targeted1pass0.12s. Core native extraction and actual Store/cache/recovery paths execute, no stubs remain.
- Five dedicated adapters: first67pass/3 invalid-feed-fixture failures0.97s; original-source IDs added before capture per root authorization, targeted3pass0.21s.
- BigCommerce schema/native/error/guard: first7pass/1 ToolError API assertion failure0.78s; exact code/message assertion repair, targeted1pass0.21s.
- Existing capture provenance + BigCommerce authentication/default compatibility:93pass1.61s, focused-default-compat.log. This rerun is justified by shared capture helper extraction/native optional query changes; no unrelated fullsuite repeated.
Commands: `python -m pytest tests/test_category_skeleton.py -q --tb=short`; five named platform files; tests/test_category_bigcommerce.py; tests/test_capture_provenance.py tests/test_bigcommerce_auth.py, each with PYTHONPATH/thread environment recorded above. Per-repair targeted commands named logs hold exact assertions/failure reasons.

`tests/category_mechanism_driver.py` and `artifacts/category-mapping/mechanism-plan.json`
provide C01–24 -> actual test-node mapping, fixed seed26, <=100 fixed parameter invocations,
120s total including collection, one sequential process, explicit fixture/oversize limits,
stop first failure and saved progress/logs. Additional shared boundary/roundtrip/cache
fixtures in test_category_shared_contract.py are PREPARED NOT RUN. Driver/stress requires
independent review before execution; no claim all C01–24 passed. Existing passing checks
may be reused where source hashes remain applicable. Source hashes/status saved in
source-checkpoint.json. Actual session token counters unavailable; no quota estimates.

## Interim reviewer repairs — bounded focused evidence, 2026-10-17
Design first: test-design.md interim repair cases. Saved `review-repair-red.log`:6 intended failures (four nonnull failed Magento facet/global variants, two parent/child edge mismatch bindings),4 passing depth7/8/9/orphan checks,0.51s. One diagnosed source repair: shared `native_source_fact` rejects exactly GraphQL-affected facets for Magento and BigCommerce through the existing Normalizer/source_fact support bridge; validator now checks observed edge endpoints against exact raw/outcome/bound native ID. `review-source-green.log`:31 passed1.09s across repair cases + affected Magento/BigCommerce files.

`review-interaction-first.log`:2 fixture failures/5 passes15.33s. Real category-enabled hardware tests used source Shoes, so existing Shoes->footwear veto masked matcher risk. One diagnosed fixture-only repair: neutral source label Declared mapped by explicit trusted rule; no assertion weakening or matcher changes. `review-matcher-green.log`:4 C20 engine/matcher cases passed6.69s, proving RAM/boot variant/identity review under agreeing category mapping and explicit profile conflict veto.

C24 codec/checkpoint atomic retry variants passed in first interaction run: actual controlled worker/parser/result, real codec rejects injected damaged binding before source checkpoint; separate before_checkpoint crash. Neither creates committed source/cache success. Same saved policy resume marks unknown then explicit retry commits exactly one valid companion/finding. Fault injection wraps existing source-result boundary and invokes the real codec; it does not stub parsing, mapping, encoding, Store or checkpoint algorithm.

Driver helper controlled check passed in first interaction run: timeout kills child session + auxiliary descendant (delayed escape marker absent), retained output exactly1024B despite20000B production. Revised runner drains bounded logs, caps retained64KiB/invocation/1MiB aggregate, one child session per exact collected node, timeout15s/invocation and120s shared collection+execution deadline, killpg+wait cleanup (Linux adopted-child reap where available). Driver itself NOT RUN and awaits independent approval. `review-plan-collection.log`:75 exact parameterized invocations collected0.29s across24 mechanisms, below100 cap; collection only, not verification pass.

Same capped environment as earlier (.venv Python3.10/PYTHONPATH=src/BLAS1/OMP2/MKL1/tokenizerparallelismfalse). No live/model/fullsuite run; actual session token counters unavailable. One sequential test process per command. Source/checkpoint digests refreshed after these repairs; G1/G2/G3 remain historical, interim rereview pending.

## Parent-boundary C24 correction — 2026-10-17
Independent rereview correctly found the prior C24 injection raised before returning a fresh result, masking acceptance ordering. That earlier codec-boundary claim is superseded. Updated fixture corrupts actual OwnedProcess worker reply original_binding and returns it WITHOUT invoking any codec in the injector. `parent-child-reply-red.log`:1 intended failure2.30s, source step already committed despite late CategoryError (initial source-return corruption also reproduced same defect in parent-boundary-red.log1.96s).

One diagnosed repair: `categories.portable.validate_categorized_products` reuses strict companion decoder and verifies trusted expected config digest AND assignment scope; GuardedSources calls it immediately after fresh child JSON decode, before result acceptance. Maintenance cache consumes that same category validator instead of its prior inline check; legacy fresh/cache paths unchanged. Actual corrupted child reply now rejects before source checkpoint/cache, leaves an unknown source attempt, and same-policy explicit retry commits exactly one valid companion/finding. `parent-boundary-green.log`:4 passed16.21s (both C24 codec-reply/checkpoint variants, C19 source cache/rule change and corrupt-cache miss). No driver/fullsuite/live run. Updated source digests saved; independent rereview pending.

## First bounded mechanism attempt / prepared single-session runner repair
Root-approved original driver stopped at120.019s,42 invocations started:41passed, final lightweight C16 interrupted with2.4s aggregate remaining. It did not fail a mechanism assertion. Original status reason incorrectly says invocation_timeout; preserved original unchanged, corrected classification aggregate_timeout in archive manifest. Archive `mechanism-attempt1/` retains original status/plan/collection/sourcecheckpoint and SHA256 file/log manifest; original42 node logs stay unchanged.

One diagnosed runner-only repair authored after design addendum: single pytest session, progress-only plugin, independent parent collection/node15s watchdog and aggregate120s with group kill+wait; one64KiB log, bounded progress. Exact source/test hashes matched saved approved checkpoint and complete source snapshot. Reuse41passes, select only34remaining exact nodes including interrupted C16; upper bound cumulative42+34=76invocations. Repaired attempt reserves an exclusive marker and refuses automatic restart. Archive/status/log/source hashes revalidated before execution. Full75-node/24-mechanism plan retained. Combined elapsed across failed attempt+repair will be reported honestly, not as75passing in one120srun. No repaired driver/helper/test executed; independent reapproval pending. No production source changes, fullsuite/live/model work by repair author.

## Diagnosed C22 byte fixture repair — no production change
Single-session repaired attempt failed at first byte variant after18additional passes/19started21.453s. Original evidence archived under mechanism-attempt2 (status/progress/log/plan/checkpoint hashes); first41+18=59 unique successful nodes retained. Combined prior attempt wall141.472s/61starts, not a clean single120srun.

Diagnosis: baseline serialized Product retains dynamic evidence_contract, dataclasses.replace discarded it, causing padded result252377B rather than262143B. Designed repair deep-copies Product and changes description only; all exact262143/262144/262145 assertions/cap checks unchanged. `byte-fixture-green.log`:3passed0.37s. `byte-fixture-only.diff` and byte-fixture-repair.json prove reverse patch matches prior whole-file approved hash; only failed fixture function+deepcopy import changed, production unchanged.

Arithmetic from actual node sets:59prior unique passes+3targeted byte passes=62unique;13original nodes remain.64invocations started across attempts+targeted cases; prospective remaining13=>77total<=100. No further driver invocation authorized/executed here. Main failed status remains untouched, exclusive prior repair marker remains; any bounded remaining completion requires independent/root approval and honest split evidence, never automatic restart.

Exact13 completion path prepared only after root authorization. Frozen mechanism-completion-manifest.json holds original75nodes/62completed/13remaining,64priorstarts/proposed77total; source hashes and archived metadata/log/diff hashes rechecked. Same reviewed outer watchdog/plugin/session cleanup unchanged; only fixed manifest/counts/output path/new exclusive completion marker changed. Prior attempts remain archived and no automatic restart option exists. Prior driver wall sum141.472s; targeted byte pytest duration0.37s reported separately, not represented as full subprocess wall. No completion execution/tests here; independent manifest/path review pending before root invocation.

Final independent review PASS (reviews.md):60 checkpoint hashes verified,0 source
deltas after testing, no unresolved blockers. Only authorized T16/status bookkeeping
followed; no source/test/network changes. Local Python3.11/3.12 matrix remains unrun.
