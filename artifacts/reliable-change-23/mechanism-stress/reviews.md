# Mechanism/stress review record

Target: merged PR #48, source revision 1bc9f77cb8732ff5119ee47ec6aa6ab9876897b9.
Scope: supplemental synthetic mechanism and bounded stress verification; do not
reopen or repeat completed baseline work. Actual session token counters unavailable.

## Plan review
Independent reviewer /root/workflow_review: PASS after SM04 clarified unsupported
recheck price vs partial coverage. Source-selection delta also PASS: Shopify
selects the first variant price, not the minimum; source order differs from
canonical variant matching. Both resolved before generator execution.
- `plan.md` SHA-256: `8b8d468ea0223f25c97a5883524d7b329124c4e3fb083763031981733bcd736e`
- `scenario-matrix.md` SHA-256: `7dc81a4afb29434afd198c389e0f6af163a05942928833a04ce61ffaffed416c`

Execution results and independent final review pending.

## Diagnosed fixture corrections and bounded continuation
Independent reviewer accepted membership presence correction (unknown/None plus
qualified refs/coverage, absent opposite side). Enum typing and full-retention
cleanup were distinct fixture-precondition repairs, not production failures.
Original failures retained; no production code edits.

Pre-continuation review PASS after explicit amendment: source execution spent
72.586s; prior resumed phase exceeded its intended cumulative cap by about4s
because accounting missed an older invocation. Preserve this as a budget deviation.
New chunk hardcap60s, overall180s, attemptcap32; no hidden automatic expansion.
Mixed native six-event Unicode boundary fixtures restore approved SM05/06 coverage.
Exactly11 allowed attempts (SM05,SM06,1701/7,2909/0..7),13 conformant prior cases
reused, final24 logical target/30total attempts. Two old boundary passes superseded.
Independent reviewer: /root/workflow_review. No user approval needed for internal
resumption within authorized test scope. Require immutable logs/interrupted data,
correct cumulative timing and count-before-execution before launching.

Continuation-plan SHA-256: `7a7a73de4cf37c5be25ef754695bad4f35b5ae48f661cdde3f381ecda4826a04`

## Final bounded completion amendment — PASS
Independent reviewer: /root/workflow_review. Actual state checked:132.607s,
22 conformant successes,29 fixture attempts. Final allowlist only2909/6 and2909/7,
<=25s and<=31attempts; then <=15s read-only canonical-owner audit of saved reports
via sqlite mode=ro/direct records with caches, no regeneration/production rerun.
Allcandidate old/new/recheck references must map to candidate product ID and
appropriate variant ID/scope. Count exact reports/refs; fail on mismatch.
132.607+25+15=172.607<180 original total. Record actual overhead and original
phase breach; preserve original/interrupted artifacts. No further continuation
on failure/timeout and no presumed pass. This plan was saved before execution.

Final amended plan SHA-256: `a02608f11c059e9002d042512517613eb5810d15dd7cf5110079b575ab455a0f`

## Final independent review — PASS for quality/accuracy, incomplete execution
Reviewer: /root/workflow_review; 2026-10-16. Actual tests, independent oracles,
real native pipeline, rollback/limit/fault sensitivity, hardstop records and
read-only owner audit reviewed. No remaining artifact-quality blocker.
This is NOT full stress completion:23/24 logical batches complete,31attempts,
2909/7 unverified;196 ownerrefs across23 saved reports checked. Budget deviation,
fixture repairs, superseded runs, interruptions and charged overhead disclosed.
No production mismatch demonstrated. Execution stopped; no further batch approved.
Reporting nit corrected: all saved candidate references, regardless of state;
no claim that rejected candidates were necessarily observed.
- `tests/test_reliable_changes_stress.py` SHA-256: `9df4c675d5e08488a557e21a96099fee30240e458218ac256cfdbd175fafaa4a`
- `artifacts/reliable-change-23/mechanism-stress/plan.md` SHA-256: `8b8d468ea0223f25c97a5883524d7b329124c4e3fb083763031981733bcd736e`
- `artifacts/reliable-change-23/mechanism-stress/scenario-matrix.md` SHA-256: `7dc81a4afb29434afd198c389e0f6af163a05942928833a04ce61ffaffed416c`
- `artifacts/reliable-change-23/mechanism-stress/run.py` SHA-256: `af5f9295bb2e0c63ea05aaa03c07c16b4d4c6658b9ee0f38fe2e4167bb43cb12`
- `artifacts/reliable-change-23/mechanism-stress/final_chunk.py` SHA-256: `1d9066228e052bd674ee05643d52f000508dd515de04393777c5a0e1e7f4d7fd`
- `artifacts/reliable-change-23/mechanism-stress/audit_owners_direct.py` SHA-256: `796fa1691565b5d9e2e7a6f95d649add489a70deaeb57ee81b988725c90b3e9d`
- `artifacts/reliable-change-23/mechanism-stress/summary.json` SHA-256: `b07555fae0a5075315b5ce46aa052e7eacf56288c53ced212a7747da3100d9e1`
- `artifacts/reliable-change-23/mechanism-stress/final-summary.md` SHA-256: `027d9f0d446f1d9d5bb2964d627fed0d0c3a9f4cd6b0137764488db3e60c4442`
