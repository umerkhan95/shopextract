# P4 independent reviews

## G1 — 2026-10-25

Reviewer: `/root/cli_p4_delivery/p4_reviewer`, separate from author. Reviewed
AGENTS.md, development workflow, constitution, the five design artifacts below,
and actual native category/config/codec/portable/policy/tree and CLI catalog/export
seams. No production edits, network, models, installs or Git operations.

Verdict: **changes required**. Findings are design gaps, not claims of defects in
unwritten P4 production code. Resolve and return changed artifacts for G1 review.

| ID | Severity | Finding and required disposition |
|---|---|---|
| G1-1 | Blocking | F2/F5 envelopes contain both `products` and `categorized_products`, but the authority/consistency contract is unspecified. Existing `catalog_from_value` routes every `data` envelope straight to the ordinary portable decoder; an unchanged or ambiguous dispatch could silently discard companions or analyze a different product projection. Specify categorized-key precedence, mandatory rejection of invalid companions rather than fallback, and treatment of missing/mismatched/reordered ordinary products. Add distinct acceptance cases for envelope mismatch, mixed ordinary/category arrays, and tampered companions through a real P2 consumer and export. Expected output must preserve one defined product ordering and exact bindings. |
| G1-2 | Blocking | F6 promises retained/response byte caps, exact numeric behavior and boundary coverage, but C11 only specifies input 1MiB/1000 records and broad labels. Native CLI `atomic_json` and `output` currently do not enforce P4 aggregate output caps; native companion serialization measures canonical UTF-8 while `atomic_json` uses a different JSON serialization. Define whether the output cap measures actual serialized UTF-8 artifact/response bytes, and define behavior when valid small inputs expand into oversized dual projections. Predesign at/above-limit output, native companion/config caps, record/node/depth edge cases, with no artifact replacement on failure. Clarify `WooTreeLimits.seconds`: native validation permits int or float, while proposed `_codec.typed(WooTreeLimits, ...)` permits float only. Preserve native acceptance or explicitly document a narrower CLI wire contract and test integer/float/bool/NaN separately. |
| G1-3 | Blocking | C9/C10 do not yet pin the crossphase export matrix required by F5. Specify all JSON/CSV/feed/parquet formats (dependency-unavailable outcome allowed), missing category destination, category-only and category+evidence exports, companion identity after reload, and a failure on the final third replacement with all prior files restored. Define behavior for payload stdout plus category-file output, since existing publisher emits payload stdout and returns early. Exercise aliases between every output pair as well as input/output; tests should fail before exporter/network effects. |
| G1-4 | Nonblocking | F4 review should explicitly state whether foreign record scope is rejected even when its valid binding contains a matching options digest; native `category_review_reasons` checks digest but not scope. A digest is not trusted scope authorization. Add a forged-but-codec-valid digest/scope interaction case if review requires trusted config scope, consistent with F2. |

The native-algorithm reuse, survivor identity handling, status preservation,
separate policy/options digests, deterministic mechanism/live distinction and
sequential limits are sound. The tasks identify ownership broadly; expand their
FR/SC and red-test dependencies while resolving the findings rather than starting
implementation against ambiguous contracts.

Reviewed SHA-256 digests:

```text
spec.md        efded12ca79705991e56dde7d4cb9300226951868f630c2752f097b00607cad0
test-design.md a81953d4fce7ffce20b0e8db92b1e9068bacf455efd92527b1df063f8f2ae6db
tasks.md       fb882ee774ff5d8607c5151bcadb5cdef1631135f451007e66499198857084b0
research.md    2bf16dbbb71401e739b4a28b6e8316a34cf8a391b6a4334bc30a300eba818916
plan.md        3862d2e2d5135458c19dd9f5f27f7843bd0c8dca71b776e1d2ecfb76ff074c65
```

## G2 — 2026-10-25

Reviewer: `/root/cli_p4_delivery/p4_reviewer`, author idle. Reviewed skeleton,
actual acceptance harness, saved final red log and verification command, plus
native tree HTTP-client construction and CLI registration seams.
Verdict: **changes required**. The document skeleton correctly preserves lazy
domain imports, additive catalog/export contracts and a category-specific bounded
publisher; the saved 13 failures are genuine command/option failures after native
fixture construction, not import failures.

| ID | Severity | Finding and disposition |
|---|---|---|
| G2-1 | Blocking | `install_transport` globally replaces `httpx.AsyncClient` and unconditionally overwrites its explicit `transport` with the product transport. Native Woo tree fetch deliberately passes its `GuardedTransport` to `AsyncClient` (`woo_tree.py:465`), so this fixture discards the actual guarded mechanism and its separately supplied tree wire transport. Correct the harness to preserve explicit transports (e.g. only supply product transport when absent), then save a small direct native-fixture proof that tree fetch returns category7 with real request accounting. Preserve the existing intentional command red run or rerun it if the harness changes its inputs. |
| G2-2 | Nonblocking | The family-binding test accepts any of 0/3/4 and merely non-null data. This proves registration only; it cannot serve as completed C1-C12 behavior evidence. Before implementation verification add the already designed exact status/content assertions: ordinary valid load/map/validate/inspect/export should be0, policy rejection4 needs a reason, and partial3 needs actual incompleteness. |

Reviewed SHA-256:

```text
skeleton.md                 37a8011fedb82d2064543fa3a5a19a2edc1492fbcbc082fb987ba980070d7c30
tests/test_cli_categories.py 3dd621ad6ae07eb73f619ab3d23cb4af2224fc9d83b363c878f1e5c762a835bf
evidence/red.log            096cb2ee576395001e248ec331fd94626c9891d769147290a305766b14f35f59
```

Actual session token counters unavailable. Review used bounded local reads only.

## G1 re-review — 2026-10-25

Same independent reviewer; author idle. Read the changed spec, test design and
tasks and compared them with G1 findings and the already inspected native seams.
Verdict: **PASS** for behavior/test/task/research design; no implementation or
test-execution approval is implied.

G1-1 resolved by explicit category-key authority, strict companion decoding,
exact ordered product projection equality and C9a rejection cases. G1-2 resolved
by actual compact UTF-8 measurement before output/replacement, dual-projection
overflow coverage, explicit bounds and native integer/float seconds acceptance.
G1-3 resolved by format/companion matrix, rejected categorized stdout, every
output-pair alias and final-third-replacement/recovery tests. G1-4 resolved by
independent policy-review scope equality and a codec-valid foreign-scope test.
Tasks now map affected contracts/scenarios and enforce red/gate dependencies.

The planned reduced-cap boundary tests must execute the production path and
include the stated real 1MiB oversized dual projection; later coverage review
will inspect these, the export matrix and exact fixture assertions. This is an
execution obligation, not an unresolved design blocker.

Reviewed SHA-256 digests:

```text
spec.md        46129d5bf0e2deeed398737ee028e74f1e92212e3463602a59a8a08bbf6ff1f5
test-design.md 608ad7dc06bef87df97da378391d0c9ceecd22a043dd3694cd91dc41b71ebeb7
tasks.md       9a6c0f855b6900668039f389b2ab5c115e77c9dc5912a599e1d4036d28c30f7d
research.md    2bf16dbbb71401e739b4a28b6e8316a34cf8a391b6a4334bc30a300eba818916
plan.md        3862d2e2d5135458c19dd9f5f27f7843bd0c8dca71b776e1d2ecfb76ff074c65
```

## G2 re-review — 2026-10-25

Same independent reviewer; author idle. Verdict: **PASS** for skeleton and genuine
red gate. G2-1 resolved: the test client uses `setdefault`, preserving explicitly
supplied GuardedTransport while ordinary extraction receives controlled product
transport. Reviewed saved tree-fixture-proof.json and independently executed the
patched fixture through native `fetch_woocommerce_category_tree` with requests=1:
asserted complete, exactly one node and exactly one transport attempt; exit0.
No network was used. The existing command red remains applicable because the
repair only preserves the native transport seam that the missing commands have
not yet reached. G2-2 remains a later coverage obligation, not a skeleton blocker.

Reviewed SHA-256:

```text
skeleton.md                 37a8011fedb82d2064543fa3a5a19a2edc1492fbcbc082fb987ba980070d7c30
tests/test_cli_categories.py ae3f08b74813bec326e0e181e6253814d6a453ca3904de3bfe9dcb835ca88323
evidence/red.log            096cb2ee576395001e248ec331fd94626c9891d769147290a305766b14f35f59
evidence/tree-fixture-proof.json 9aff9ed7623f5e0c9f85841ce9b2802da90c8b129de3a898c56801ca2c4973e5
```

## G3 — 2026-10-25

Reviewer: `/root/cli_p4_delivery/p4_reviewer`, separate from author, author idle.
Reviewed components.md, refined skeleton/plan and existing response, atomic JSON,
execution policy and destination-check contracts. Verdict: **PASS**.

The shared decoder belongs in `_cli_data`: both category commands and existing
catalog consumers need the same strict category-key authority and native product
projection. Native imports stay local, preserving lazy help. Category business
rules remain in existing native codecs/adapters/mapping/policy/tree modules.
The concrete third category artifact extends the existing staged publisher and
recovery contract rather than introducing a competing transaction abstraction.
Native code does not depend on CLI code.

Optional keyword-only `compact=False` parameters preserve existing emitter and
atomic-file defaults. Category callers can consistently measure and publish
compact UTF-8, including the stdout newline. All response/artifact byte checks
must precede replacement; the existing native limits remain independently
applicable. The small `compact_json_bytes` shared serializer is justified by
actual response/file consumers. The refined shared decoder naming supersedes
the original local skeleton name. No new G2 incompatibility or blocking finding.

Reviewed SHA-256:

```text
components.md 7cdfde18d78907840d08564132c9bfd44dc5b3b0792077e2f5106be9c9b0e09f
skeleton.md   34c0854f54bd5c90a3e6353fac19897849675c6eb2cda0231355096ee4195c2e
plan.md       2c3423eba8c2396c65de543bd0431ba33451fdea12396184b84f775b8541e9c8
```

## G1/G2/G3 policy metadata amendment — 2026-10-25

Reviewer: `/root/cli_p4_delivery/p4_reviewer`; author idle. Reviewed appended
behavior/test/interface/component contracts and existing category dispatch seam.
Verdict: **PASS** for the amendment at G1/G2/G3, subject to actual implementation
and C8b/C9c execution at the coverage/final gates.

The amendment closes a distinct crossphase metadata-loss risk: the native runtime
policy identity includes profile bindings beyond a companion's options digest.
A narrowly typed additive CatalogInput field and a shared native-validated decoder
are appropriate concrete reuse. Policy-bearing export uses an explicitly versioned
reloadable envelope; ordinary category files remain bare records. Requiring both
runtime claims and independently checking native runtime digest, options identity
and every scope avoids accepting a digest as scope authorization. Rejecting record
transformations that would discard/rebind runtime metadata is an explicit error
contract rather than silent loss. Fresh review requires matching trusted runtime
configuration. New tests target missing-half/tampered metadata, crossphase retention
and transformation rejection before effects, distinct from existing binding tests.
No new native business algorithm or dependency cycle is introduced.

Implementation must preserve policy metadata or explicitly reject it on every
companion-returning path (including tree link), consistent with the shared
categorized_file rejection contract. This is an application of the amended
no-silent-discard invariant, not an additional feature requirement.

Reviewed SHA-256:

```text
spec.md        29f9158e41504f7d6f1f498a4cd4fb520385fb2ccc9485e63c0ec497e724d6df
test-design.md d037067fb454355c8ba21ac215189c61a3176faba6c082f2f77bfa92a56559e5
skeleton.md    da1dec6ac29d4fbdd2ba7eba50417639e436565c87feabd04e6426263bfd099a
components.md  6561baee95fde29fd9e73be25bdd597f6b74a67513b6196c698cb543518e00c4
```

## G1/G2/G3 native extraction controls amendment — 2026-10-25

Reviewer: `/root/cli_p4_delivery/p4_reviewer`; author idle. Verdict: **PASS** for
amended behavior/test/interface/component contracts. Reviewed appended artifacts,
actual P1 `storefront_options` validator and native category extraction kwargs.

Reusing the existing bounded storefront decoder preserves exact protocol/auth
validation without duplicate configuration logic. Explicit enrichment/restoration
flags map to supported native parameters, default false; no ambient model/browser
controls are added. Storefront config joins one-stdin and alias preflight. Operator
endpoint/token values must stay out of diagnostics and any exported config; use
the existing execution-policy secret handling when passing credentials. The six
planned wire fixtures exercise actual parsers/capture/adapters; malformed config
and alias cases require zero transport effects. This adds relevant real extraction
coverage rather than mocking the native API. No new coupling or blocking finding.

Reviewed SHA-256:

```text
spec.md        50444bc17cf277ee2dfac195361a7205364a1605920d13cca47ffdd00b2b42cd
test-design.md fb0edafe2988e3c08125d8177eb9bb2d0c4a8b6680f0e2fa3120f6c1dd18c4f9
skeleton.md    3b3c506d99922f6770d32bd0fb630f5b8d5bf8615c4cf1b80dd610b2fb528eae
components.md  0112d40e7439c20ec8e34c6b9ea64ca1d2295271d4223ca571d2fbc081c30171
```

## Diagnosed mechanism amendments — 2026-10-25

Reviewer: `/root/cli_p4_delivery/p4_reviewer`; author idle. Reviewed changed
contracts, initial failure summary and actual native projection/trace/tree seams.
Verdict: **changes required** for one precise native-repair contract detail.

The tree/Shopify expectation corrections are justified by native-authority
requirements: traversal completeness is independent of retained cycle/orphan
issues; capped Shopify extraction stays partial. Preserve graph issues and add
an actually partial malformed-facet fixture rather than weakening that assertion.
Shared strict load_products dispatch closes the promised P3 interaction while
keeping products_from_value portable-only. Explicit unsupported-Parquet failure
with all files preserved, plus a compatible successful fixture, is appropriate.

Blocking finding G-MECH-1: A non-list->[] projection guard alone can mark false or
object category input as accepted ordinary category_path evidence. Actual
`_record_items` unconditionally calls `trace.record(..., accepted=True)` and
Normalizer.record accepts usable scalar/object sources. Consequently the category
adapter may correctly report malformed while ordinary product evidence claims an
observed empty path, violating the amendment's no-known-empty contract. Specify
and implement a rejected conversion outcome for non-list malformed category input
(e.g. trace.record accepted=False with a bounded reason) while preserving actual
raw source/evidence. Predesign tests for false and object (not only null), requiring
empty compatibility projection AND no accepted observed category_path support;
valid [] must remain distinguishable as explicit empty. No adapter rewrite needed.

Reviewed SHA-256:

```text
spec.md        3cac7e8b9d16f2fba89ae681f63d62ebf6ece82445e567db3c986b0357067b98
test-design.md 65cebf3fb1306d889f3d258a4d4b14758febbcf160337c04ea0484711fd56f32
skeleton.md    09f0127001f5f319eccc4448b3eccfae793d7808411221b1e5ba27937a4f4123
components.md  12205eee4bed8990baf863c135894acf1d435cb060b3fbe7fccd491b7dea0609
```

## G1/G2/G3 mechanism repair and Parquet refinement — 2026-10-25

Reviewer: `/root/cli_p4_delivery/p4_reviewer`; author idle. Reviewed amended
spec/test/skeleton/components. Verdict: **PASS** for amended contracts.
G-MECH-1 resolved in design: malformed non-list Woo collection uses native
Normalizer.record accepted=False with retained source values; valid [] keeps the
existing accepted explicit-empty conversion. Tests require both ordinary rejected
support and native adapter state, not just category_path=[] equality.

Parent-reported user authorization covers the categorized-only Parquet projection.
The declared evidence-json-v1 column encoding is concrete and inspectable: sorted
union of structured top-level columns, every cell in those columns compactly
encoded via the existing evidence codec, native table writer unchanged. Converting
scalar/null cells in the same columns avoids a mixed Arrow type failure and
preserves null/empty distinctions. Required companion retains full native bindings.
Reported encoding/columns and Arrow readback expectations make the new format
observable. Ordinary Parquet behavior stays unchanged. This supersedes earlier
unsupported-empty-struct fallback expectations for normal categorized products;
other genuinely unsupported native shapes may still fail explicitly with no
replacement. Gate approval does not substitute for the required readback test.

Reviewed SHA-256:

```text
spec.md        b4a027bae80baca1de66fe00250867cfe37ba01559f504f888564f1a54530ff7
test-design.md e16d7b557fbd20a9240945a39a346c36fea1becc568dff076c0867226701dee6
skeleton.md    f04aa4aa46872e41d1f48982f13309a03d809458e7f76f2986555ccfadd698ee
components.md  b8fc16ca90c989e924bb6870ffd83e0ea43506c7a1625ed4c646c71358de35a1
```

## Independent coverage gate before stress — 2026-10-25

Reviewer: `/root/cli_p4_delivery/p4_reviewer`; author idle. Inspected all category
production glue, actual mechanism tests and 12-group driver, not only author map.
Reviewed saved75PASS result and genuine native negative-support/Arrow assertions.
Verdict: **changes required** before stress.

| ID | Severity | Actual finding and required coverage |
|---|---|---|
| COV-1 | Blocking | Extract's scope guard compares lexical path prefixes. Independently executed controlled real extraction with `https://supplier.test/shop/../other` under trusted `/shop` scope: exit0 and actual MockTransport URL `https://supplier.test/other/wp-json/wc/store/v1/products?per_page=100&page=1`. Thus the required basepath restriction is bypassed after HTTP normalization. Predesign raw/percent-encoded dot-segment cases and reject or safely canonicalize before network; include valid nested paths. Do not replace the native extractor in this check. |
| COV-2 | Blocking | `test_category_to_p3_snapshot_projection` only asserts snapshot-save exit0 and that the original input still has a digest. It never loads persisted products or checks any saved field. This does not prove P3 product projection fidelity and contradicts the appended test-design claim of reloading the snapshot. Reload the actual snapshot through CLI/native DB API and compare native portable product projections, including identity, money and retained source support; cover policy-bearing category input as well. |
| COV-3 | Blocking | The new extraction flag tests only assert command acceptance and one product. Their data has no short GTIN/enrichment-dependent values, so they pass if either flag is ignored. The declared C1 control forwarding requires fixtures whose expected normalized/enriched facts differ when flags are enabled vs defaults, through real extractors/normalization; add this distinct coverage. |
| COV-4 | Nonblocking | The staged exporter checks the category companion byte cap but does not check actual payload/evidence staged sizes before replacement. F6 currently says all file artifacts fit1MiB. Enforce the declared cap for categorized exports or explicitly narrow/review that contract; add staged-size boundary proof if enforced. |

Other coverage is substantive: actual six-platform parsers/adapters, no algorithm
mocks, source evidence distinctions, strict decoder authority, foreign scope with
valid native binding, independent runtime/options digest checks, native tree
status/graph issues, actual Arrow readback, final-third replacement and failed
recovery, aliases, exact UTF-8/node/depth/record caps. Existing native suites can
supply underlying version-selector/tree edge coverage with actual regression-run
references. New fixture expectations are generally independent of implementation.

The driver is sequential with thread caps,30s/group,300stotal and512MiB summed
RSS, saved group status and stop-on-failure. Distinct selectors map to reviewed
risks. An orphan failure should also kill surviving owned processes before return;
currently it records the violation only (driver cleanup follow-up). No stress or
live run was executed during this review. Session token counters unavailable.

Reviewed SHA-256:

```text
_cli_categories.py 67eec709c938301b5a93bc937a4a5896f4d8b79b5e8f14fff3be7227ffae71ea
_cli_data.py f52a11499d01f320802ebb654a2292d602a688639ac4b0dac960af0db0332ef4
_cli_analysis.py 9650b475b2c514fe2f027d5d4fda5182d698a48a56d842cd3c9eb1d4be65c926
_cli_core.py 416e37b00ff42785fc395c5c5f17ede0699c351ae9db66a57b22589265919ef8
_normalize.py fd9abacb2b3ada75a650ae75ce573ceacf3567b88199950cd5afb0b7f1e2e724
cli.py 197f04a01ed3ae7412cb38aff3ca43b282bf628aee24299bcd8bb23895e88bcb
test_cli_categories.py cd50132d5b3f74a1f43f98fd24e50c4dfca6876112d25d513039e1b37870b155
test_cli_categories_mechanisms.py b75dcec8fe2fb5c2395386785aaa37745877a9566bb0886caa667dffbb537c12
cli_categories_stress_driver.py 67e4a0e045593418d012137f28514638e2f56319d214b31bcb025a075608f35c
coverage-review.md 5856dc6b56ec3d58f8a3aadbe6adc2338c2e3199e9d1eda5888cf82759da96f8
```

## G1/G2/G3 coverage repairs design — 2026-10-25

Reviewer: `/root/cli_p4_delivery/p4_reviewer`; author idle. Verdict: **PASS** for
predesigned repair contracts; coverage verdict remains pending execution/review.

COV-1 now specifies bounded source/scope path decoding, traversal/backslash and
remaining ambiguous-encoding rejection before transport, plus valid nested-path
acceptance. This directly addresses the independently reproduced HTTP path escape.
COV-2 requires actual saved-ID snapshot load and exact native portable projection
comparison for bare and runtime-policy inputs. COV-3 uses observable native Shopify
detail-fetch/GTIN differences and restored UPC plus note, with no algorithm mocks.
COV-4 now enforces actual sizes for every categorized staged artifact before any
backup/replacement; controlled post-native padding targets exact publisher edges.
Orphan cleanup preserves the violation receipt while terminating owned children.
These are narrow applications of existing scope/fidelity/budget requirements,
with clear shared-component ownership and no new native business algorithms.

Reviewed SHA-256:

```text
spec.md        844ad7340951b852c4bf7ecd0d34f392a07adec49aa30ec3c148d817f29f1653
test-design.md 79a3a1a6b64de8fb0371f346344477726dd913b8747c681cd8d797c6056349f7
skeleton.md    ed71a2047e871b7e4ce26ca023d205ba542650c7b20e440a949bf8e2e81267ce
components.md  4121e383526fdd42a53e28becc62e7dbe371676eea3b4c00adcc18f3c231831e
```

## Independent coverage re-review — 2026-10-25

Reviewer: `/root/cli_p4_delivery/p4_reviewer`; author idle. Verdict: **PASS** to
proceed with the declared bounded sequential stress/fault proof. Reviewed actual
repair code, tests, saved red/green summary and updated group selectors.

COV-1 resolved: source and configured paths undergo bounded decoding and reject
dot/backslash traversal before native extraction; raw/encoded/double-encoded cases
assert zero HTTP, legitimate nested scope succeeds. COV-2 resolved: actual bare
and policy-bearing saved snapshots reload and compare native portable products.
Canonicalizing only evidence/observation collection order by stable identity is
consistent with native DB ordering; all content/IDs/support remain compared.
COV-3 resolved: actual native Shopify wire fixtures prove default vs enabled
barcode detail acquisition and valid short-UPC restoration with normalization
policy, without extractor/normalizer substitution. COV-4 resolved: actual sizes of
all categorized staged files are checked before backups/replacement; native CSV
and evidence stages exercise real1MiB-1/at/+1 publication behavior and preservation.
Driver now terminates discovered orphan PIDs/group before failure and includes new
cases in the fixed12groups.

Independently executed:
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 TOKENIZERS_PARALLELISM=false PYTHONPATH=src .venv/bin/python -m pytest tests/test_cli_categories_mechanisms.py -q --tb=short -k 'decoded_scope or valid_nested or category_to_p3 or native_flags or staged_file_size'`
Actual **16PASS,58deselected,2.68s**, exit0. Controlled transport only, no live work.
Previous reviewed native/Arrow/recovery/boundary coverage remains applicable.
Full regression, fault mutation, bounded stress and declared live observation are
still required and not implied by this coverage verdict.

Reviewed SHA-256:

```text
_cli_categories.py 1fc933a223931e9006069fe53bc61b8ec997935c6e7d3bab8cad876fcd60ff0d
_cli_analysis.py 0357fb62c9488dcd8d4d65a7e2a177df3759a686fd2e2f00465ae0b081336acb
test_cli_categories_mechanisms.py 32c15a41af49966e9acc13c17c5b610183c078f65f44daf219b9a40dd968ec50
cli_categories_stress_driver.py 66baab9adc0bf9a7cccac98540032c97b1dc8ffb31a64eea776b101ed6ba1100
evidence/coverage-repair.log e9c52547a5ffa32bbdb2ab0867ebb0647cfa8ecd1469c8cdbf2da39e314d2532
```

## FINAL — 2026-10-25

Independent reviewer: `/root/cli_p4_delivery/p4_reviewer`; author idle throughout
review. Verdict: **PASS for the P4 slice**, with the live instrumentation limitation
below. No remaining blocking finding. Whole-repository/wheel/P5 delivery is outside
this verdict. All earlier blocking findings have recorded reviewed resolutions.

Reviewed final production/source contracts, actual C1-C12 mechanism tests, mutation
and stress drivers, docs grammar/examples, parent capability rows, verification
receipts and current source digests. Independently recomputed every entry in
final-source-digests.json: **zero mismatches**, including restored mutation source.
No public request, production edit, install, Git operation or model launch during
this final review.

Production compatibility: category parsing/retained policy metadata use strict
native codecs and scope checks; ordinary portable decoder/default command behavior
remains separate. All category export formats require retained native companions;
three-file publication validates actual sizes before replacement and preserves
rollback/recovery. The categorized-only Parquet evidence-json-v1 representation is
explicit, uses native value encoding/writing, has real Arrow readback and full
native companion retention. The narrow Woo non-list projection retains rejected
support/source state; valid empty input remains distinct. Module registration,
parser grammar and native exception handling are covered by affected regressions.
Docs accurately describe options, caps, native traversal versus graph issues,
policy/options identities, metadata preservation and P3 product projection.
Parent capability rows are historical-baseline plus scoped P4 implementation notes;
P5 maintenance/full parity remains pending. Author may now update P4 status and
parent notes from pending-final to this actual verdict.

Actual verification receipts checked:

- Stress: read all12group receipts and matched log pass counts
  `[14,3,2,14,5,1,6,8,3,4,11,3]`, total74selected executions; every exit0,
  maxgroup6.396s, elapsed48.464s, maxRSS199499776bytes,0orphans. Within declared
  30s/group,300stotal,512MiB and sequential limits; no unlimited-scale claim.
- Critical guard mutation: saved failing assertion detects actual wrong exit0
  when guard disabled; mutant1FAIL, restored1PASS, original/restored source SHA
  matches current1fc933a223931e9006069fe53bc61b8ec997935c6e7d3bab8cad876fcd60ff0d.
- Affected native/CLI regression log: **678PASS,74warnings,59.13s**. Earlier
  independent targeted16PASS remains valid. Native tree/security mechanism
  coverage, actual source-support negatives, adverse states and rollback are
  independently reviewed; no live counter exception waives these mechanisms.
- Live: independently loaded saved native tree through woo_tree_from_record:
  complete,2nodes, one native attempt(number1,status200,errorNone), captured page1
  total2/pages1. Saved record hash matches report. One declared read-only smoke
  elapsed3.954s. This establishes current Woo tree availability only, not live
  change frequency or all-six-platform live extraction. Shared receipt3HTTP,
  4products+2nodes=6items,5.629s remains within parent ceilings.

Live counter disposition: the initial auxiliary httpx hook missed direct httpcore
and was not a valid independent counter. Original receipt/source are retained;
corrected report explicitly attributes1GET200 to native guarded request accounting
and its captured successful page. Inspection of actual GuardedTransport shows
accounting immediately around raw submission, retries=0, and per-redirect accounting;
this retained native receipt is adequate to bound the observed smoke. The repaired
original-delegating raw hook has separately saved controlled2send/2attempt proof,
clearly offline. It is not retroactive independent live instrumentation. Parent
explicitly prohibited a second public probe; no rerun is required or authorized.
Do not describe the live count as an independent low-level measurement. Availability
observation passes with this documented measurement limitation.

Reviewed final artifact SHA-256:

```text
evidence/final-source-digests.json f51000fb66529eeec4b423688d3fc3b0b96400dee62062d1accd9815f20f8266
evidence/stress/status.json 1f0c6da8bbdfc6325e3a368dd740d35399277085f747598f9cf50ab4d270c611
evidence/mutation/report.json ad2790dfda9efef925c698ca70e785fc1b039f58fcb18393f0fd27b900fbc0c9
evidence/affected-regressions.log a178fa2ac28c359cdaebc48312ea3bfc4a86a69b0a7a729cdb7832e124a2f7bd
evidence/live/report.json d9fc60fb0e6a0b2214b48aabfd037968ef4d6118c963d3cf7bf64dad8952a739
evidence/live/tree.json 01ebcfac5f9a4b3bf45088ea134037d74f49b19b51231c7efb231d582765e2a9
evidence/live/counter-offline-proof.json 68ba55765a688139104f7cd521e811342be8dfd24230a2457b2a2c1ae41dc236
verification.md 023f4d4a0ecb1ac6b11cf6d2ff6f72b061ac4c766887345af31df1760f5e1dcc
coverage-review.md 1a07f827f2e6bffbea192f829782660dcf5a5bf64616aeaf09fc87a727cb0669
docs/cli.md cd7ef16ff6731b1d77bdc9984b02b25abc2b39abdd22b138e967c3933dcf0517
parent coverage.md 72df18b5579626eef8188dd6e82a1fd12468d6674a9b119c6aa9d692c1438c61
```

Actual session token counters unavailable; review remained bounded and reused
valid earlier inspections/tests. No quota percentage inferred.
