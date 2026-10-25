# Actual evidence

Planning only, 2026-10-25.

| Check | Result | Saved evidence |
| --- | --- | --- |
| Current root help via `PYTHONPATH=src .venv/bin/python -m shopextract.cli --help`, 20s timeout | PASS, exit 0; nine commands | evidence/baseline.json, evidence/baseline-help.txt |
| AST/import surface inventory | Saved, used for planning; not an exhaustive executable parity audit | evidence/surface-inventory.json |
| Runtime CLI acceptance/red tests | NOT RUN; future implementation slices | test-design.md |
| Synthetic mechanism/stress | PLANNED, NOT RUN | test-design.md |
| Live commercial-source observation | NOT APPLICABLE to docs-only planning | No network executed |

Unrelated dirty working-tree files were observed and preserved. No test suite or
production behavior changed. Independent planning review recorded in reviews.md
after completion; review cannot substitute for implementation evidence.

Planning artifact JSON/whitespace check: PASS; saved in evidence/planning-checks.json. Independent planning G1 and narrow follow-up: PASS, see reviews.md. Runtime gates remain unexecuted.

## Delivered implementation phases (current)

P0 foundation and P1 extraction have independent final PASS. P0: 52 core tests,
181 affected regressions, 12 bounded stress cases and duplicate-key fault proof.
P1: 298 affected tests, 12 stress groups, truncation fault proof, envelope file
roundtrip and bounded public Shopify smoke (1HTTP/2items/0.527s). Exact commands,
limits, logs and artifact digests remain in p0/ and p1/; reuse rather than
repeating completed checks. Shared actual live spend: evidence/live-budget.json.
P2 active; P3–P5, integrated repository/wheel checks and final parity audit remain
pending. No complete CLI parity or publication claim yet.

P2 final independent PASS: 401 affected tests/12 bounded stress groups and
exact-money fault detection/restoration. Native currency/source provenance,
partial-source deadlines and export recovery independently challenged/repaired.
No new public live spend. Exact evidence/digests: p2/verification.md,reviews.md.
P3 active; P4/P5 and full integrated repository/wheel remain pending.

P3 final independent PASS: final511 affected tests/12 bounded stress groups,
exact history-money fault proof, read-safe/prune resource+cleanup and portable
file pipelines. Live1GET/2products/1.148s nativeSQLite/CLIload/get,0lookupHTTP;
actual pricechange unobserved with deterministic native transitions proved.
Global live2HTTP/4products/1.675s. Exact evidence/digests: p3/. P4 active, P5
and whole integrated repository/wheel/parity remain pending.

## P4 completed locally

Independent G1/G2/G3, coverage and FINAL PASS; actual phase artifacts in p4/.
678 affected checks passed (59.13s), 12 bounded stress groups / 74 selected
executions passed (48.464s), peak RSS199499776 bytes, zero orphans. Scope-guard
mutation detected and restored source byte-identically. Native Woo live tree
retained2nodes complete / 1native-accounted GET200 / 3.954s. Original auxiliary
transport-hook miss preserved; corrected low-level counter was proved offline
without a second public probe. Global3HTTP/6items/5.629s. P5/final suite and wheel
checks still pending; this is not whole-feature completion.

## Integrated P5 verification — configured gate PASS

Exact gate: `PYTHONPATH=src .venv/bin/python scripts/run_tests.py --output-dir
specs/011-cli-feature-parity/p5/evidence/configured-ci` with capped CPU/tokenizer
environment. Actual from scratch result exit0:1,595 tests(1,465 main,24 native oracle,
106 maintenance),419.517006 seconds total <=480;group driver seconds187.612391/
121.997828/109.903748 each<=240. Zero skipped/failed tests and no surviving
process groups. Report:[p5/evidence/configured-ci/report.json](p5/evidence/configured-ci/report.json).
The original single-main240.165s TIMEOUT is retained as historical diagnosis;
complete-prefix accounting was not misrepresented as a configured gate PASS.
Independent affected review approved stable scheduling with unchanged assertions
and original shared ceiling; the configured workflow now calls that exact driver.

Real builtwheel outside checkout/importorigin/help/schema/examples PASS;85 help
entries/70 executable commands. Official MCP SDK rootstdio and durable maintenance
subprocess/native session evidence PASS. P5 newstress5 groups / 19 executions
PASS in 45.041s,peak RSS 212,385,792 bytes,zero orphans;critical session-reference mutation
detected and source byte-identically restored. Parent24 mapping explicitly reuses
20 applicable prior scenarios+4 new resource/session scenarios. Capability manifest
533 classified rows/zero missing workflow bindings. No new publiclive or real inference.
Exact phase commands/artifacts and final FR/SC mapping in p5/verification.md and
p5/final-traceability.md. Final whole-feature independent re-review PASS; see p5/reviews.md.

## Final local delivery verdict

Independent FINAL PASS for P5 and whole-feature local delivery is recorded in
[p5/reviews.md](p5/reviews.md). No open blocking findings remain. Root completed
T21 and final issue/status reconciliation administratively after that verdict.
Product, test and CI contracts were not changed after the final review. Local
Python/version and live-observation limitations above remain explicit.
Documentation, examples, packaged schemas and all six ticket bodies are current.
Changes remain local on `cli-feature-parity`; publication is separate.
