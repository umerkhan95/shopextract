# P2 independent reviews

## G1 — 2026-10-25 — changes required
Reviewer: independent sequential `p2_reviewer`; no implementation edits.
Reviewed SHA-256 digests:
- spec: `38cd82bae4497e835799f29362e2236e2780323d4353f585e722815d4a244a7c`
- test-design: `bd5f6cf0b01d9cbfb9ee58635cb61be0e5cfbad6199eee691bde54ede8aad6bd`
- tasks: `f8565d1294ec8d8de927778ccf700167d2916092d400a93e518e06d1f239c420`
- research: `4d9e26ed8c20aeb9f2da5ebaae75493af2edd616ac752b6c76a44a0c135557bc`
- plan: `00d72e12492df60f480fc99676340bfb416acdd212e7e96514ecd0e50e246732`

The proposed reuse and bounded scope are sound. Blocking findings must be resolved
in behavior/test design before the skeleton and intended-red tests.

1. **High / G1-01 — Currency provenance cannot be derived from Product.currency alone.**
   FR26 prohibits unknown currency becoming USD, but `Product.currency` defaults to
   USD and `_collect_matches` currently copies that scalar. Grouping existing Match
   records therefore does not establish explicit currency. Specify the supported
   provenance signal for extracted/portable products, treatment of products with
   default USD but no captured currency, and unknown-group ranking. Predesign a
   real-code-path case containing both explicitly observed USD and default-only
   USD, plus absent/null/empty competitor currency; assert the latter do not enter
   USD rankings. This closes a gap in SC24's bare unknown-currency fixture.

2. **High / G1-02 — Source failure and deadline outcomes are unspecified.**
   Native compare gathers exceptions and skips failed stores; competitive analysis
   reads raw products without completeness reporting. FR27 promises one shared
   deadline but SC21–27 never specifies/asserts partial-source, all-source-failure,
   or deadline behavior. Define result completeness/error metadata and exit statuses
   (consistent with root FR03), how partial results survive if supported, and
   cancellation behavior. Add controlled transport/real native-path cases for one
   failed store beside one success, all failures, and a later sequential source
   exhausting the single remaining deadline. Assert no additional requests after
   expiration and that failure is not reported as a successful empty catalog.

3. **Medium / G1-03 — Export rollback omits initially absent and aliasing paths.**
   SC26 tests restoring two preexisting files only. FR27 must also define rollback
   when the first target did not exist (remove newly installed output on second
   replacement failure), when one old output exists, and how collision detection
   treats relative/absolute aliases and symlinks. Add distinct fault cases for
   absent first output and staging failure of companion after payload staging,
   with exact retained/deleted paths. Specify stdout plus companion behavior and
   reject unsupported combinations before writes. Otherwise an implementation can
   satisfy the current assertions while leaving a new unpaired artifact behind.

Nonblocking design improvement: record exact command spellings/options and minimal
machine payload shapes (especially currency groups, exclusion metadata, precision
metadata, and assignment/inspection results) in spec/skeleton so tests can assert
stable user-facing fields rather than infer them from implementation. Exercise
node/depth and resource boundaries as well as the already listed bytes/records.

Disposition: open G1-01 through G1-03. G2/G3/final pending.

### G1 amended-design check
Amended spec digest `1d1c966cbbbdcf9d20b8bd2633959d1fd2f2513afccfee1c39111d3c37882674`;
test-design digest `cb3a3dbceaec1836a239458fde54a4c06d6fcb340a23d7d16e1fd8f944c32231`;
other artifact digests unchanged from above.
G1-01 and G1-02 resolved by the new behavior and scenario contracts.
G1-03 behavior contract resolved; scenario amendment remains incomplete: absent
second target does not exercise removing a newly installed first target after
second-replacement failure. Require absent first/existing second, plus companion
staging failure after payload staging, with absence/unchanged/no-leak assertions.
Verdict: changes required on this narrow G1-03 test-design correction only.

### G1 final design verdict — pass
Reviewed corrected test-design digest
`9622d2cb0b2f294d301422efd4a11a6171aa59bbbe18a983dfcce5cc1b11bba2`;
spec and other artifacts retain their amended-design digests above. SC26 now
explicitly tests absent first/existing second rollback and companion staging
failure without leaks. G1-03 resolved. All G1 blocking findings resolved; G1 passes.
G2/G3/final remain pending and are not implied by this design approval.

## G2 — changes required
Reviewer: independent sequential `p2_reviewer`.
Skeleton SHA-256 `535df7e71ca7656c1a125fc036ed5316906f136a39e2c8939b189ab7d6f75a9a`;
acceptance test SHA-256 `05c0e754167c13a57b509b58c37d5d8ca045f5886ab61b96d3f0c29a71e11285`.
The saved acceptance-red log establishes missing analyze-file and nested help.
The existing tests are useful grammar/smoke seams; the four usage tests passing
before command registration do not establish their eventual parser behavior and
must run again after registration.

**High / G2-01:** Skeleton names “source-aware native optional safe APIs” without
signatures or result types. This is precisely the new seam required for G1's
currency provenance and partial-source/deadline decisions; existing native return
values lose this information. Declare actual additive native signatures, source
status shape, provenance association (including raw-vs-Product index/identity),
unknown-group output, and how legacy defaults remain unchanged. Define the
explicit flat-to-Product conversion boundary for export (CatalogInput.products is
currently None on flat input) and error contract. Document-only declarations are
sufficient; no runtime implementation needed.

**Medium / G2-02:** Executable intended-red coverage covers only grammar and one
aggregate. Add at least one red acceptance case for each consequential new seam:
exact Decimal/variant transport or portable export, explicit-vs-default currency,
partial-source reporting, staged rollback. These must fail for the intended absent
interface/behavior rather than a generic missing command. Save red evidence and a
compact verification.md entry. Full scenario/stress implementation can follow G3.

Verdict: changes required; G2-01/G2-02 open. No production code reviewed/approved.

### G2 amended check
Skeleton digest `f5e0a73bfc539390e32967d89c25b15fe6f691762e4d43a393b3b8d82e19c5a8`;
tests digest `71eaeedc7a5f698cc3d02d1da0a56d8b487f6dde3b6f3441f2b65f6fc61164b8`.
G2-01 resolved by concrete native signatures and source/projection declarations.
G2-02 mostly resolved by expanded red tests and verification.md; two test defects
remain: family case match-pair expects success for empty operands, contradicting
SC22 exactly-one cardinality; rollback test must prove replacement was reached
(first installation and second attempt), since any early exit1 otherwise passes
its assertions. Correct fixture/cardinality and add replacement reachability
assertion before pass. Behavioral source/currency mechanism tests remain required
before final coverage approval; signature checks alone do not prove mechanisms.
Verdict: changes required only for these test defects.

### G2 final verdict — pass
Reviewed corrected tests SHA-256
`c0f616a56312835fefffa9856639a8b40f741ef3eab44b4544829120b8bd2c47`;
skeleton remains `f5e0a73bfc539390e32967d89c25b15fe6f691762e4d43a393b3b8d82e19c5a8`.
Pair fixture now supplies one record per side. Rollback requires payload and
companion replacement attempts, eliminating early-error false success.
G2-01/G2-02 resolved. G2 passes; G3 and final coverage remain pending.

## G3 — changes required
Reviewer: independent sequential `p2_reviewer`.
Components SHA-256 `41a274953d66233105a5e7982ff15f7b86e54f17dac27ebaa49e0eddc4ad64f2`;
skeleton SHA-256 `f5e0a73bfc539390e32967d89c25b15fe6f691762e4d43a393b3b8d82e19c5a8`.
Existing codecs, root policy, execution context, native algorithms and staging
ownership are cohesive; no unnecessary framework identified.

**High / G3-01:** Semantic adapter keyed by original record object identity cannot
work for Product input: identity_match._record uses asdict(Product), and native
match_products calls semantic_candidates(_record(a), ...) only for sources lacking
rule candidates. Callback receives a fresh dict, not the original Product or its
stored record. A simple callback-call counter is also unsafe because skipped
rule-matched sources shift row alignment. Specify a stable indexed handoff (or
another mechanism preserving duplicate source rows and skipped callback positions)
that works for both portable Product input and URL catalog Product lists. Add
predesigned cases: preceding source with rule match, later source requiring
semantic row, and duplicate equal-valued sources with distinct candidate rows.
This is a component-seam defect, not approval to duplicate native matching.
Verdict: changes required on G3-01 only.

### G3 amended verdict — pass; affected G2 reaffirmed
Reviewed digests:
- skeleton `63cdf88030bd7950311e9dfbd5bc41dbe7e9e6088384e32c5842d5a7abeb3380`
- components `57da468decd71031472e2cef1d0dcb904405f7baf1548f09dd1c1d24108967e8`
- test-design `19ec9b34e90ff5dcb2d2bb1f3665d90c755c5a0a7d4debaf53ec755a7aec7027`
G3-01 resolved: additive native declarative rows use existing source index and
preserve callback compatibility while rejecting simultaneous APIs. Actual URL
catalog dimensions necessarily validate after retrieval; structural/global caps
validate before HTTP. New duplicate/skipped-rule scenario exercises the specific
alignment failure. Changed native signatures remain cohesive and testable, so the
affected G2 interface approval is reaffirmed. G3 passes. Runtime and final coverage
are still unverified; implementation must execute the newly designed scenario.

## Independent coverage review — changes required (before stress)
Reviewer: sequential `p2_reviewer`, 2026-10-25. Reviewed current P2 implementation,
CLI/codec/native seams and both acceptance/mechanism test modules. Relevant digests:
- _cli_analysis `c255073395fb0147fd20820098b82099ec62318fe1f365782aa009622eb000b0`
- _analysis_safe `e15f66c2348c0fa54736222f03704c7a0114d5f7ce137e475d7bf97c23f6f4a6`
- _cli_data `5bca9c1d8231c0c389e5a867204ff8f05f1a94d0845feac4455ce6d8bd43016a`
- compare/price `fb899214a3a38aa0029d28e251d66ece740d2fbe73b1c464f276d5252b7d0849`
- compare/catalog `d774095c0495e88fb3aec0205fb4def1c8654cd9b352ebecefe7b947eb4e1a39`
- identity_match `e1e9569e047be0141b92b8965878c6f818f65bcb618c3cf1249c7ae5f3ddfe91`
- acceptance tests `619813f7d5c2ea046f09d460cae680427522357a03c13ec6cc07bb60fa8ef5cb`
- mechanism tests `69c87f9ed6b6471e02e5c4a3d5c3825dd7abce1219f4dfda5edc5966581f0774`
- test-design `4fa421e3f55a8575c09f137e0c789a31d2dfa30cc5ed834651ea85f8bcea7d4d`
Reviewer executed both test modules once: **62 passed / 3.19s**; saved
`evidence/reviewer-coverage-current.log`. These passes do not resolve the gaps below.

1. **High C01 — Wrong currency after normalization drops raw rows.** Safe compare
   and catalog compare associate products with `result.raw_products[index]`.
   Real `_extract` explicitly permits normalization_dropped_records, and normalize
   retains each actual source in Product.raw_data. Reviewer reproduced with raw
   `[{'currency':'EUR'}, {'title':'Widget','price':'10','currency':'USD'}]`, one
   Product from normalize(second): safe compare reports currency group EUR although
   the Product is observed USD. This can produce cross-currency rankings. Amend
   G1/G2 provenance association to use the product's own associated raw source or
   captured contract, not positional arrays; add distinct dropped/reordered raw
   fixtures through real normalization for both compare and compare-catalogs.

2. **Medium C02 — New-group error routing is incomplete.** `stats missing` emits
   plain `Error: Unknown command or option.` while new data groups promise default
   machine envelopes. Default routing recognizes complete child paths only.
   Amend grammar expectations for unknown child/missing child/invalid group option
   without explicit root --output-format; assert E_USAGE JSON and unchanged text
   help. Root/legacy behavior remains as designed.

3. **Medium C03 — Shared deadline scenario was not implemented.** Current timeout
   check uses only one slow source, so it passes even if each store receives a new
   deadline. Add the designed later-source exhaustion case, assert the third source
   never starts and native task cleanup occurs; deterministic controlled transport
   or clock injection is appropriate. Verify source completeness false/error cases
   separately from unknown completeness; unknown-alone success is consistent with
   P1, and positive-only native statistics/zero-retention clarification is accepted.

4. **Medium C04 — Evidence and successful restore coverage gaps.** Companion
   roundtrip fixtures have no evidence_contract, so equality proves money/scalar
   preservation but cannot detect evidence dropping. Add one real captured-source
   contract/observation with portable variant money and assert full contract survives
   CSV/feed roundtrip. Fault tests cover absent-first deletion and failed recovery,
   but not successful restoration of two preexisting outputs after second replace
   failure: inject a once-only failure, assert both original byte sequences and no
   leaks. Check reported recovery paths actually exist when recovery fails.

Indexed semantic duplicate/skipped-rule test exercises the G3 seam correctly;
controlled image HEAD tests, byte/record edges, malformed syntax/types, aliases and
companion staging provide distinct real-path coverage. P1 reader depth/node saved
checks may be reused explicitly because the bounded reader is unchanged. Add
invalid concurrency/timeout no-request assertions for the new images command.

Verdict: changes required; stress/final approval pending. C01 requires affected
G1/G2 provenance-contract update/review; G3 ownership otherwise remains approved.

### Coverage repair review; affected G1/G2 reaffirmed
Reviewed price `b89af334aa44eb97efa18a279b2484d3625fefc9406016265567763d611fc542`,
catalog `ea63635eeb2b90db84e7d4f948b08f5db40fff701a8023abf39f0b49a2379e58`,
core `b4112a415bf749e9d39ef0600376f6ec881b4fdc93326eaf1764b7103b6f364c`,
mechanisms `bbcad6379ac8929abbe34ccf2139a6977cf168c82d519f6f161d0e802bb282de`,
test-design `f9fae9c836d7458b2a6f220513585fd86e784bb8704fd107168a40a8e763d596`,
skeleton `ba1cedb7a6b1d68edfcc91aa4341babeb36f44c5639d5fc8e78a34c0f9dddeef`.
C01 raw-data association fixes actual wrong currency classification; amended
G1/G2 association contract is approved. C02 default group routing and C04 nonempty
product/variant evidence plus both-existing successful restore are resolved.
C03 remains narrowly open: immediate first source + second source slower than the
full deadline cannot distinguish reset per-source deadlines from shared deadline.
Require both source durations below full timeout, sum above timeout, then assert
third never starts and second cancellation cleanup. Real normalize in the dropped
fixture should match the recorded provenance design. Stress approval awaits this
focused discriminating test correction.

### Coverage verdict — pass for bounded stress; final still pending
Mechanism test digest `7799480879af49a41d1129277b18245d825479143edf10717714f0b9f3b683bd`.
Reviewed final focused evidence: 2 passed / 0.32s in
`evidence/coverage-focused-final.log`. Dropped-row fixture now uses real normalize;
shared deadline test uses 80ms + 80ms under 120ms total, asserting cancellation,
cleanup, and no third dispatch. Unlike the previous test, it detects renewed
per-source deadlines. C03 resolved. C01–C04 are closed. Affected G1/G2 approval is
reaffirmed; G3 remains approved. Coverage is adequate to execute the previously
bounded stress/fault plan. Record actual 120ms timing in verification (the earlier
design's 10ms description is superseded). Final verdict still requires stress,
fault proof, affected regressions and honest live limitations.

## Final review — narrow grammar correction required
Reviewer `p2_reviewer` inspected final runtime changes, docs/manifest, stress driver
and saved evidence. Stress 12/12 groups (54 selected executions, 35.308s,
113340KiB peak), mutant rejection/restored pass, and 399 affected passes are
consistent with stated bounds. Evidence is mechanism/controlled transport; no new
public P2 integration observed. P1 receipt proves shared policy activation only.
Full-repository/wheel checks remain explicitly integrated P5 work. No blanket CLI
completion claim identified.

**Medium F01 — Option termination leaks across Click parser contexts.** Root or
group `--` stops option scanning only for that parser context; child parsers start
fresh. scan_bootstrap retains terminated globally. Reviewer compared plain Click:
`-- stats distribution --help` and `stats -- distribution --help` show child help
(exit0), while current main with invalid --config returns E_CONFIG exit2. Thus
valid nested help no longer bypasses configuration as FR21 promises. Reset scanner
termination on group-to-child descent; add both cases with bad config and retain
leaf `stats brands -- --help` as an operand. This modifies affected G2 grammar seam;
review focused evidence and rerun P0/P2 parser regressions before final pass.

Nonblocking handoff cleanup: collapse status.md to current resume state; mark stale
“pending” paragraphs in verification as historical/resolved. Mark D7 only after
actual final pass. C01–C04 remain resolved; no additional runtime blockers found.

### Final verdict — PASS for P2 scope
Reviewer: independent sequential `p2_reviewer`, 2026-10-25.
F01 fixed: scanner clears termination on command descent; two genuine-red help
cases now pass, while leaf option termination remains covered. Core digest
`1e762eb9b7e64c2cc0fd090ce1e0c3b23b41ead34be0f430b78209170e6cba2d`;
acceptance digest `ceaefd9f218df8aeca0b63edfb4508206f8a9a436d5bc80c7f5e54ad90787a52`;
test-design digest `13f76076c1d73cacedd3a4d6ee3ca78948e224784f9e75a40d412d80e72f182d`.
Affected G2 parser-interface approval reaffirmed. Saved final regression evidence
confirms **401 passed / 6.18s**. Prior bounded stress and restored mutation proof
remain applicable: this final repair changes parser bootstrap only and is covered
by affected parser/P2 regressions. All G1/G2/G3/coverage/final blockers closed.

Final 15-file aggregate SHA-256:
`667a84eb2acd32163bae9a6f9483b4527f2e54c60e7133034807d6b7cc02a84f`.
Computed over sorted relative path + NUL + contents + NUL for:
`src/shopextract/{_cli_analysis.py,_cli_data.py,_cli_core.py,_analysis_safe.py,_models.py,cli.py}`,
`src/shopextract/compare/{price.py,catalog.py,identity_match.py}`,
`src/shopextract/analyze/competitive.py`,
`tests/{test_cli_analysis.py,test_cli_analysis_mechanisms.py,cli_analysis_stress_driver.py}`,
`docs/cli.md`, and `specs/011-cli-feature-parity/p2/capability-manifest.json`.

Approval is bounded to P2 implementation and recorded mechanism/controlled HTTP
coverage. No new public P2 integration was observed; P1 public receipt only covers
shared activation. Full repository/wheel verification remains P5 integration work.
Missing Parquet dependency is validated at injected dependency boundary, without
installing an engine. Existing warning output is retained. No inference, public
P2 requests, commit or push performed by reviewer. Author may now mark D7 complete
and replace historical status paragraphs with current resume state; those routine
artifact updates do not require another implementation review.
