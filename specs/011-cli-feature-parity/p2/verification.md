# P2 actual evidence
2026-10-25 PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_cli_analysis.py
saved evidence/acceptance-red.log before production. Intended missing command/flag
failures cover matching/identity/evaluation, stats/competitive mapping, images/
duplicates/export, machine validate stdin, exact portable identity, native safe
signature and staged rollback. Grammar tests mostly pass generically while
commands absent and must rerun after implementation. No network/model/install.

First green: focused P2/P0/P1 tests155PASS2.48s in evidence/focused.log. Expanded
mechanism first55cases found2failures: exception object unconverted by safe_error
prevented JSON failure metadata; diagnosed repair converts exception to string at
native boundary. Native stats intentionally excludes zero, so reviewed expected
fixture changed to positive1 with zero retention separately checked. Green55PASS
2.46s evidence/mechanism-green.log. Controlled server images newly added; pending.

Independent coverage C01–04 repaired and approved, G1/G2 reaffirmed, G3 retained.
Currency provenance uses each Product.raw_data (real normalize of valid second row
after dropped raw first row) and never index-pairs normalized/raw arrays. Reviewer
caught a weak timing fixture; corrected first80ms+second80ms under120ms total,
asserting second cancellation/finally and no third dispatch. Focused2PASS0.32s in
evidence/coverage-focused-final.log. Coverage suite before timing refinement71PASS
3.26s evidence/coverage-green.log. Nonempty evidence fixture setup failures retained
in coverage-repair.log / coverage-focused.log; repaired deterministic pointer.

Stress driver declared12sequential groups, seed11025, case30s/total300s/512MiB RSS,
input1MiB/1000records, workers1, no inference. Driver saves each subprocess log and
progress JSON. Actual result pending. Controlled images run local HTTP HEAD, no
public sources. Public live P2 not run: shared P1 activation receipt reused only
for shared extraction activation; not universal comparison source verification.

Bounded stress actual: PYTHONPATH=src .venv/bin/python tests/cli_analysis_stress_driver.py
12groups PASS,54selected test executions,35.308s, maximum113340KiB child RSS. Limits
30s/case300s total512MiB, seed11025/workers1 recorded per-case in
 evidence/stress/status.json. It reuses reviewed synthetic cases against real CLI,
native match/stat/export and controlled local HTTP images; no public source proof.

Fault proof: /tmp/p2_fault.py temporarily normalized portable price Decimal0.10 to
0.1 at report boundary; exact-money assertion failed1 (intended), original restored
byte-for-byte and same assertion passed1. evidence/fault-mutant.log,
fault-restored.log,fault-proof.json. Production source restored=True.

Affected regression command:
PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_cli_core.py tests/test_cli_extract.py tests/test_cli_extract_limits.py tests/test_cli_analysis.py tests/test_cli_analysis_mechanisms.py tests/test_compare.py tests/test_identity_matching.py tests/test_analyze.py tests/test_validate.py tests/test_export.py tests/test_evidence_bundle.py tests/test_evidence_contracts.py
399PASS6.26s in evidence/affected-regressions.log. P0 deferred guard uses snapshot
now analyze is implemented, preserving pre-native failure protection. `git diff
--check` affected tracked sources/tests clean. Existing requests/Click deprecation
warnings retained. Full repository/wheel smoke deferred to integrated P5.

Live: no new public P2 requests; shared P1 public receipt1HTTP/2products0.527s reused
only for extraction policy activation. Source-ranking semantics established through
controlled transport/native mechanisms; does not establish all real stores' support.
Parquet engine missing path tested by injected dependency boundary, no install.
No local inference or agents in parallel; actual token counters unavailable.

Final F01 repair: plain Click independently confirmed '--' applies to current
parser only. New two help cases saved genuine red2FAIL0.25s in evidence/f01-red.log.
Scanner resets termination on descent, retaining leaf operand behavior and root
flag scope. Final affected command same12files as above:401PASS6.18s in
 evidence/final-regressions.log. No domain algorithm/stress changes; prior12group
stress/fault evidence remains applicable. Final independent closure pending.
