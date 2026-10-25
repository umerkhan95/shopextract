# Independent reviews
G1/G2/G3/coverage/final pending; no inferred verdicts.

## G1 — 2026-10-25, initial review

Reviewer: independent sequential `cli_p1_delivery/p1_reviewer`; no production
changes, network, installs or inference. Reviewed parent spec/coverage and workflow,
native CLI/extraction/quality/portable seams, and the following SHA256 artifacts:

| Artifact | SHA256 |
|---|---|
| spec.md | 756dbe9171f3564913985c5d06ce27aa414bfab3c07a9b1826f94a32e3f8645d |
| test-design.md | ca1c4882ae8afbb141c9c74a345c6dbddc57fbcb2e26b53357e16011df262186 |
| tasks.md | 89bec2842e7b6c599aed3eb11e18e5c45a731954e20c44c862b380a0d59f411e |
| research.md | 70836420b81ba39da4d3f2bcb7021431ca4ae8bca9f0539083c5bc6840fd7bc0 |
| plan.md | dced7846017cb906ef6595dbca8bf341883cfef8022a07fc0d80c2a78d1573c3 |

Verdict: **changes required**. Scope is additive and the explicit context-local
policy/native codec reuse is reasonable, but the following block G1:

1. **High, open — exact parity mapping missing.** Parent `coverage.md` explicitly
   requires the phase manifest before G1; P1 currently has no exact callable,
   command, flag and input/output schema mapping. Add that mapping, including
   detect payload, storefront allowed values/combinations and new versus legacy
   invocation selection. Reconcile P1 API signatures against it; P0 reserved
   command names alone cannot prove P1 parity.
2. **High, open — acceptance contracts leave material failure/boundary choices
   to implementation.** F5 promises node bounds without a numeric node maximum;
   S4 has only a subset of cap boundaries. Predesign exact outcomes at/below/above
   bytes, depth, nodes, records, finite timeout/temperature and LLM limits;
   malformed tagged values/portable records and mixed arrays; and output-file
   failure preserving an existing file. Specify error code/exit and absence of
   transport/provider side effects where relevant. Also design retained-data
   partial and unknown-catalog-coverage success assertions for F4. These target
   distinct uncovered risks, not additional random variations. They may be
   grouped in a bounded parameter matrix rather than separate large tests.
3. **High, open — live budget is not executable as designed.** S8 requires at most
   five actual HTTP attempts and no retries, while F8 preserves native retries.
   Identify the transport request counter/abort seam that enforces the live
   attempt budget, or amend the live contract with a bounded compatible policy.
   Record the exact smoke command and deadline/cancellation assertions before
   live execution. A post-hoc request count cannot enforce a hard request cap.
4. **Medium, open — task breakdown lacks completion contracts and explicit
   fixture/stress ownership.** D3–D7 aggregate several independent deliverables;
   record dependencies, FR/SC traceability, author/reviewer ownership, check and
   saved evidence for each. In particular separate acceptance-red, synthetic
   fixture authoring, coverage review, stress execution and verification review.
   `D1 [x]` should not imply all design complete while these findings remain.

Nonblocking observation: initial smoke failed from import setup, and the one
saved repair succeeded (52 passed in 0.35s). Update research/status to cite
`evidence/baseline-smoke-repair.log` and stop reporting the smoke as running.
No test or runtime success is inferred beyond that saved baseline.

Task-breaker coverage disposition: F1–F8 map to S1–S8 at a coarse level; the
specific additional cases in finding 2 are required before approving the
dependency-ordered implementation tasks. G2/G3/coverage/final remain pending.

## G1 — first repair review, 2026-10-25

Same independent reviewer. Artifact SHA256: spec
`57c6afb86e9e6d779f0f9bf296f7f1de66bdfeb1c56971e906ea69dc64b53663`;
test-design `f6eff42b0c09f5d4761f4db3241ca2ad39ab911a26d88e5c0e960da88bc4aae7`;
tasks `c685c4ef8609fc6dcdac0759bb1e61f1fa56b6d408fcbc6c50a735c093746333`;
capability-manifest.json
`9ee9f1bc3e34c6311d1b5d0c31c782556b9ef749fbbccc3d349732ee9ceb8d62`.
Research and plan digests unchanged from initial review.

Findings 1, 3 and 4 resolved at design level: the manifest supplies P1 mappings,
the live driver declares an actual transport-send stop seam, and tasks now state
dependencies/ownership/check evidence. Exact enforcement remains subject to
G2/coverage/final verification. Finding 2 partly resolved: numeric node maximum,
byte/item/depth/node edges and atomic preservation are now predeclared. Still
required before implementation: malformed native tags/portable records and mixed
arrays; retained partial versus unknown catalog coverage success; and finite
timeout/temperature/LLM cap boundary outcomes. Verdict: **changes required** for
this remaining acceptance-design gap only.

## G1 — final repair review, 2026-10-25

Same independent reviewer; reread the adverse matrix refinement. Test-design
SHA256 is now
`e80efea27d1ed90f3f45fc8e4683c39ce00bf3ba87fb078ab90ee6e9a7bca28f`;
all five other reviewed artifact digests remain as above (research/plan retain
initial digests). Finding 2 resolved: malformed portable/tagged/mixed inputs,
partial versus unknown coverage, numeric/finite controls and provider failure
outcomes are predeclared. Task-breaker accepts F1–F8/S1–S8 coverage and the stated
dependency/ownership/evidence contracts. **G1 PASS**. G2, G3, independent executed
coverage and final review remain pending; this approves design, not runtime
correctness or actual live observation.

## G2 — initial skeleton review, 2026-10-25

Reviewer: `cli_p1_delivery/p1_reviewer`, independent and sequential. SHA256:
skeleton.md `02cb8231fd63a8af113dac3ddb98f56f08105a8cb293bebd0d6ce8ee0203e6cb`;
tests/test_cli_extract.py
`1a8f0ff516c72004c8a72a8c35313a3c03f0d478f9821e7e3b779dd23ab40230`;
acceptance-red.log
`9d381f5c65917db838e5eb74549fb2c9abc380902150bde72f3bdfbcd8e39ea1`.
Declaration-only skeleton adds no fabricated runtime API. Native-to-private
execution seam, CLI-to-native codec direction and centralized P0 errors are
reasonable. Saved red is genuine: five intended missing-binding/command/cap
failures and one existing unknown-option rejection pass, not an import failure.

**Changes required:** F7 provider timeout and global call-budget contracts need
operation-owned state. Immutable LLMBudget/ExecutionPolicy currently declare no
absolute deadline or consumed-call counter, so repeated bounded_llm invocations
could reset caps, and no interface supplies remaining time to provider requests.
Declare shared state lifecycle, deadline access and reserve-before-await call
accounting, plus a repeated/nested-helper case proving the cap does not reset.
Outer wait_for alone does not specify the required provider timeout parameter.
No production changes during review. Existing red is sufficient to demonstrate
missing CLI behavior; later coverage must assert no side effects directly rather
than infer them only from E_USAGE, and exercise designed HTTP/provider seams.

## G2 — accounting repair review, 2026-10-25

Same independent reviewer. Skeleton SHA256
`149d99eaf46cba5981df529f121f27ecb38f7cd570103c2307eac60603b990a4`;
test-design SHA256
`e8f7c2f9da8dcdf97831f8d74e223de2348e38327157b0f085b9d19db9b0c5e1`.
Acceptance test/red digests unchanged from initial G2 review. Shared mutable
operation state now declares context lifetime, remaining monotonic deadline,
reserve-before-await accounting and failure/cancellation consumption. Predesigned
repeated/nested helper and expired-deadline checks directly address the finding.
**G2 PASS**. No implementation or provider call executed during this review.

## G3 — components review, 2026-10-25

Same independent reviewer, performed after G2 passage. Components SHA256
`23cd409a2b7d0520f9fb629000b4928ad2a443515b3da4530b3809f6495f3e93`;
revised skeleton/test-design digests are those in the G2 repair above. Existing
P0 envelopes/config/error handling, native portable/evidence codecs, extraction
algorithms and quality/normalization remain the shared owners. The three private
modules have concrete P1 consumers and separate execution, transport-data and
binding responsibilities; no speculative registry or exported runtime framework
is introduced. Context cleanup and sanitized error ownership are declared.
**G3 PASS**, with no blocking component finding. Runtime secret-error suppression,
legacy absence-of-policy behavior, direct no-side-effect assertions, shared
budget/deadline enforcement and real native-path fixture execution remain required
coverage checks before final passage. This is a design verdict, not executed
mechanism evidence.

## G1/G2/G3 — P0 invariant clarification review, 2026-10-25

Reviewer: same independent sequential reviewer. Revised spec SHA256
`3b2e845005202c0033e228d9c53c30be8728e661bfbfe2c5d60c8877cf206757`;
test-design SHA256
`8ea3959f5e257d6ae156fc0637002e5d194e6a18d7303a774cab78774bf87e7f`.
Skeleton remains `149d99eaf46cba5981df529f121f27ecb38f7cd570103c2307eac60603b990a4`;
components remains `23cd409a2b7d0520f9fb629000b4928ad2a443515b3da4530b3809f6495f3e93`.
Compared the change with P0 FR envelope invariants and actual make_response:
empty extract-one now correctly fails E_OPERATION/1 with null data/unavailable;
retained products at a native explicit budget remain usable partial data with
E_PARTIAL/3/retryable=false; unknown catalog coverage remains success. Exact
inner portable decimal string `0.10` strengthens codec fidelity acceptance.
Existing binding/error seams can implement the clarification without ownership
changes. **Affected G1 PASS, G2 PASS, G3 PASS**. No production execution or code
edits. Generic partial wording must continue to mean usable retained data as P0
requires; these verdicts do not approve fabricated empty partial payloads.

## Coverage — initial implementation review, 2026-10-25

Independent reviewer `cli_p1_delivery/p1_reviewer`. SHA256:

| Artifact | SHA256 |
|---|---|
| _execution.py | e216b78e9f16c3e0051e54bab6f267c849d41f180e994c2d49b53d78a6313b2a |
| _cli_data.py | b20e5c6687f1c06817bfa5e5541386e6f5967896faf547eee7e7ab60bfe67097 |
| _cli_extract.py | 355013f67bac4c1991ebd76fa3700d69027b59c10d4161a54407972ee7a8a17d |
| test_cli_extract.py | b68f57007f1288e4bbe7f704e9cd712195558e223be86987d14125204cc6e7e8 |
| test_cli_extract_limits.py | 0012d7c5dfea4915861a4aebbfb245ff75db35b734721147be2b9498990db8d6 |
| cli_extract_stress_driver.py | 834f8f864ad1c48fcf14a6ea5b2de95e2e9ec3011e5d20da1b231ccede55303e |
| coverage-final-ready.log | 79c44c1945399f8a85fec3cd53542ffb3dec4e74c9ca0c1ae9f6e90c4c7fe669 |

Read shared modules, focused fixtures/tests, native seams and sequential driver.
Saved 112-pass evidence is real. Shopify eleven-record fixture exercises actual
transport/parser/normalizer/portable evidence and exact decimal values; feed CSV/
XML and JSON-LD also exercise real native algorithms. No model/network activity
is needed. **Changes required before stress**:

1. **High:** no-usable-product errors still produce fabricated partial feed data.
   Reviewer controlled probe, real parser with MockTransport returning empty CSV
   `id,title,price\n`: exit3/E_PARTIAL/completeness partial/product_count0. P0
   requires failure unavailable/null when no usable partial work exists. Add
   predesigned empty native-error feed/store cases and consistent handling.
2. **High:** shared-call/deadline test uses consecutive helper calls only; no
   child task overlaps. Add a bounded overlapping helper case proving shared
   lock serialization/common cap, and provider-await cancellation/failure checks
   proving consumed accounting and cleanup. Existing timeout test replaces the
   entire extract_one API, so it does not verify provider cancellation.
3. **Medium:** temperature NaN test lacks --allow-llm and can pass at the unrelated
   activation guard. Exercise invalid finite controls under valid activation;
   execute predeclared 0/1/max/max+1 LLM caps with accepted parameter checks.
4. **Medium:** driver checks 180s only before a fixed30s child timeout; bound each
   child by remaining total time and save timeout/failure status. Stress document
   <=100products/case needs to distinguish extracted products from the deliberate
   999/1000/1001 raw-record boundary checks. Keep one sequential process at a
   time, with the already declared 512MiB observed-RSS stop and fixed case count.

No production edits during review. Reviewer executed only the one small controlled
empty-feed probe described above; it made no real network or provider calls.

## Coverage and affected design — repair review, 2026-10-25

Same independent reviewer. SHA256 _cli_extract.py
`47f66f232671998411fa7dc7cd0c57d3fe28c0f07f3f8cb0fbf55a0d4c09b92c`;
test_cli_extract.py `bafb52641d9f699869069db65f09a89d1f0abb6a54024808ed381a19dd6ec555`;
stress driver `1144fe7417943288f66fa38515914e21c39e08d50443f9a6be1796b5b5b02b1b`;
spec `741a57c6a48583b22c343302dc61fb0bb0336238e32b1bdaabe53c674cf91165`;
test-design `0b98cb764853f403717e5f492212964044b5199eb128edfcff16f59e925a931f`;
coverage-review-repair-final.log
`2652e0ca2d7cdae2ebb29f33eca1a7a0ae5a15ae7ef8a215da37d4c8c2193d7e`.
Other implementation/test digests unchanged from initial coverage review.

All four findings resolved: empty native-error feed/store paths now reject
unusable partial data; real BigCommerce401 and feed parser cases verify it;
overlapping helpers assert maximum active provider1/shared cap2; cancellation
and failure consume the call and clean up; activated numeric-invalid and accepted
min/max request cases exercise the intended validation; driver uses remaining
total timeout and saves timeout stop state. Raw-record1001 validation versus
normalized-product100 limits are explicit. **Coverage PASS to execute the reviewed
12-case bounded stress**. This does not claim stress or live execution passed.

Reviewer independently ran `PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
MKL_NUM_THREADS=1 python3 -m pytest tests/test_cli_extract.py
tests/test_cli_extract_limits.py tests/test_cli_core.py -q --tb=short`:
129 passed in1.72s,14 warnings (existing environment pytest/deprecation notices),
no real network/provider calls. Saved author run is129 passed in1.82s.
Affected **G1/G2/G3 PASS** for the explicit unusable-partial clarification;
component ownership and signatures unchanged.

Nonblocking final cleanup: remove obsolete earlier test-design phrase "empty feed
native error partial" in favor of the newer failure contract. Mixed-format test
currently starts with a malformed portable variant contract; a valid portable
record plus raw object would isolate the format-mixing assertion more clearly.

Author-reported additional gap after coverage review: `extract -o` writes the
data payload but quality FILE recognizes an envelope/portable array. The documented
pipeline therefore misclassifies the saved object. **Open, blocking final
completion:** predeclare full response-envelope file equality with stdout, then
verify real native extract/file/quality roundtrip including retained partial
products. Existing12-case stress review remains applicable; this additive pipeline
repair needs affected contract/test review and rerun before final passage.

## Affected G1/G2/G3 and coverage — file pipeline review, 2026-10-25

Same independent reviewer. SHA256: spec
`dd398f909dc06f429e08dfbffda1ed9889231bd030b7abb69b678a1ce4f2dbc3`;
test-design `fa599e082c5dcdaf426b0efd8dddaccb9f72049742e9e5c6e960162aebeef31b`;
_cli_extract.py `4176317142f2a513bf40ff132812b0484f35bbe3ab0f647d79a6fa8c9b2b119e`;
test_cli_extract.py `5c6b977eae4fa039b343a411edcbd8034a40448025ade06095a6873bf0c20fe8`;
test_cli_extract_limits.py
`3aac6f4f5c8503adbb40285a6820cb3b6164ab60150c421c7fccda80f03ab98b`.
Inspected real native Shopify transport-to-file-to-quality acceptance for both
complete and retained partial cases, exact file/stdout object equality, shared
P0 make_response construction and rejection of unusable results before writing.
The documented full-envelope file format resolves the pipeline gap and reuses
existing component ownership. Valid portable/raw mixed test is now independent
of malformed variant-contract rejection. **Affected G1 PASS, G2 PASS, G3 PASS;
coverage PASS**. Pipeline blocker is resolved in design/code/tests; final review
must confirm the complete/partial parameterized green run. No additional test
process launched during the author's sequential stress run.

## Final independent P1 review — 2026-10-25

Reviewer: `cli_p1_delivery/p1_reviewer`, sequential author-independent review.
Reviewed artifacts are enumerated with actual SHA256 in
`evidence/final-review-sha256.txt`, whose SHA256 is
`f12d6f70ad8d4146518b470a41d36cce2a0596cabc3d9db6c00138b012316ddc`.
The manifest covers P1 private modules, additive CLI/core/native seams, three
acceptance files, stress/fault/live drivers, docs/contracts and cited evidence.
Preexisting dirty category/tool/native changes are outside this P1 verdict;
whole-file digests identify reviewed working revisions, not attribution.

**Final PASS for P1.** No blocking findings remain. Real native Shopify/feed/
JSON-LD/normalization/quality/portable mechanisms, policy inheritance and
ambient-disable behavior, validation-before-I/O, retained partial versus failure,
exact money/evidence and atomic file pipeline are covered. Design changes were
reviewed at affected gates. Saved affected suite:298 passed in3.17s. Full
complete/partial file pipeline:2 passed in0.30s. Reviewer independently confirmed
the earlier129 focused subset; no redundant full rerun was needed after inspecting
the additive pipeline acceptance and saved final results.

Reviewed executed stress:12 sequential groups passed in28.671s, maximum observed
child RSS114372608bytes under512MiB, per-case30s/total180s stop limits and raw
record/product limits recorded. Fault proof genuinely catches dropped11th record
(11 declared versus10 emitted), then normal separate process passes. No fake
algorithm/report supplies these expected outcomes.

Reviewed actual live observation: original HTTP transport is delegated to beneath
the request guard; saved report shows one200 GET to declared Shopify endpoint,
two retained products,0.527s, expected capped partial exit3. Evidence captures
titles and native evidence contracts. No retries/expansion/browser/provider live
execution. This verifies that observed bounded integration only; provider/browser
behavior is controlled deterministic boundary coverage, not live verification.
No full-catalog/commercial-change/OS-hard-limit claims are warranted or made.

Tracked P1 diff whitespace check passed. Nonblocking handoff cleanup: status/tasks
can now mark final passage; verification.md still contains earlier chronological
"implementation pending"/"live result pending" text followed by actual outcomes;
label those as historical stages to keep current completion unambiguous. Capability
manifest quality input wording may explicitly mention retained partial envelopes,
which the tested consumer already accepts. Existing environment/deprecation
warnings remain disclosed; no dependencies installed or inference executed.
