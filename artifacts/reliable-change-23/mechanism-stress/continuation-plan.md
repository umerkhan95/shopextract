# Explicit bounded continuation proposal — before further execution

Original plan produced 15 successful logical batches: SM01–08 and seed1701
indices0–6. No production mismatch found. Remaining: seed1701 index7 (interrupted)
and seed2909 indices0–7. Preserve all completed cases and original failures.

Three distinct diagnosed fixture repairs were allowed once per blocker: enum
state typing, documented membership presence oracle, and establishing full expiry
instead of the retention API's default 100-record batch. A separate run reached
its timeout. These are not production failures or successful coverage counts.

Budget exception: resumed timer bookkeeping omitted 4.503 seconds from an older
stress attempt. The intended cumulative 60-second stress phase was exceeded by
about four seconds. Record this explicitly; do not report original phase budget
compliance. Sum of all four measured driver invocations is 72.586 seconds.

Proposed amendment: one additional continuation phase capped at 60 seconds, only
for the 9 remaining predeclared cases. Original total execution ceiling remains
180 seconds and total fixture-attempt ceiling32. Current19 attempts plus9 means28
maximum. No new seeds/scenarios, weaker assertions, smaller stress sizes or
repeated completed work. Original raw input/entity/variant/snapshot caps remain.

Before execution, repair accounting and check its deadline arithmetic independently:
spent72.586 + next chunk60 =132.586 <=180; remaining107.414. Hard subprocess timeout
must be min(60, remaining overall). Persist cumulative invocation durations and
attempt counts including setup failures/timeouts; do not carry only latest phase.
The interrupted case may restart from its saved seed/manifest, with an explicit
new-attempt record. If deadline or another unresolved failure occurs, stop and
save partial results; no automatic extra chunk. Independent review must approve
this amendment before running. Actual live commercial-change coverage remains
inconclusive. All execution is synthetic/offline; no production source changes.

## Boundary-fixture correction (additional review required)

Author self-review found SM05/SM06 used a single warranty event rather than the
approved mixed native report. Those assertions passed but do not yet fulfill the
planned mixed-fixture coverage; do not count them as conformant completion.
Use the six-event native smoke shape with non-ASCII warranty for both entry and
UTF-8 byte boundaries, preserving their N-1/N/N+1 and B-1/B/B+1 assertions.
Rerun only these two affected scenarios in addition to the nine pending seeded
cases: 11 continuation attempts, 30 total maximum (still <=32). Thirteen prior
fully conformant successes are reused; final goal remains24 logical batches,
not26. Archive initial N=1/B=3125 results as superseded fixture evidence. Same
60-second continuation and180-second cumulative bounds; no weaker checks.

## Final completion proposal — no further execution yet

The explicit continuation hit its hard timeout at60.021s including termination
overhead. Recorded cumulative runtime132.607s;29 attempts. Twenty-two of24
logical cases are now conformant and passed. Remaining allowlist: seed2909 index6
(interrupted) and index7 (not started). No production mismatch established.

Propose one final chunk <=25s for exactly these two cases (31total attempts <=32),
then <=15s read-only audit of saved report references against persisted canonical
owner IDs. Invariant: reference snapshot+record_key identifies a product with the
candidate product ID and, when applicable, the candidate variant ID. Preserve
existing qualified evidence/value/source/time assertions. Design/strengthen that
assertion before audit; no new generated datasets or repeats of completed cases.
Use read-only SQLite/cached snapshot identities and/or existing production loader
without schema initialization, never modify saved source evidence.

132.607+25+15 =172.607 seconds maximum, below original180s with headroom for
bounded termination overhead. Record timeout and attempts honestly; preserve
interrupted raw/progress under unique paths. Independent review required before
execution. If failure, timeout or budget exhaustion occurs, save partial evidence
and stop; do not launch any further chunk. This does not change source code,
add random scope or establish actual-live commercial-change coverage.
