# Bounded stop and diagnosis — 2026-10-16

Saved code before execution; no production sources edited. Smoke SM01 passed and
was reused: six exact mixed-field events, fourteen qualified reference checks,
2,032 raw input bytes. SM02 then passed its three successive rechecks and eight
qualified reference checks. No seeded stress batches have run.

One setup repair used: initial SM02 fixture assigned observation.state as a plain
string, violating the portable schema's SupportState enum. Changed to
SupportState.UNSUPPORTED; preserved setup-failure.json and failed raw artifacts.
No expected behavior changed in that repair and passed smoke was not repeated.

The resumed driver stopped at SM03 before its expiry step. Oracle assumed
product membership presence would use old.state=observed; actual _presence returns
unknown with identity support references/coverage, explicitly avoiding a fabricated
observed scalar. All four event identities and field/state decisions otherwise
matched. This does not demonstrate a production defect; it is a second
oracle/fixture contract mismatch requiring independent review before correction.
The single preauthorized setup repair has already been consumed, so no second
correction or further execution was attempted.

Exact expected/actual delta and bounded traceback: failure.json. Known smallest
already-generated reproducible batch: ignored raw/SM03/current-manifest.json and
SM03.db. The generated inputs are synthetic, never actual live commercial changes.
Remaining SM03 completion, SM04–08 and all sixteen SM09 batches are pending.
Mutation sensitivity has not executed; no killed-fault claim is made.

Execution: initial driver 5.712 seconds, resumed driver 5.271 seconds. Zero network,
zero inference, one child process at a time with thread caps; all limits held.
Usage counters unavailable. Independent reviewer/root owns next disposition.

## Reviewer-approved membership correction and next bounded stop

Independent reviewer approved the documented unknown-presence expectation and
stronger membership reference/coverage checks for SM03 and SM04. Corrected both
under one diagnosed membership blocker; resumed SM03 only, reused SM01/SM02.
SM03 four-event oracle then passed, including membership references, but stopped
at all-expired check: default prune batch expires 100 evidence rows; 159 of the
259 old/current/recheck rows remained available. This is an unmet fixture
precondition, not a demonstrated retention defect. Proposed bounded one-shot
batch_size=1000 plus explicit precondition checks; awaiting parent disposition.
Original membership failure remains in membership-oracle-failure.json; latest
failure.json and raw/SM03 preserve the new failure. Further cases remain pending.

## Prune repair and bounded expansion result

Root approved explicit batch_size=1000, no remaining available records and
has_more=false precondition; stronger expiry assertions then passed. SM01–08
passed, including exact entry/UTF-8 byte edges and a detected/killed currency-gate
fault with normal behavior restored. Seven seed batches passed (1701 indices0–6).
The driver then timed out during1701 index7; no assertion failure was observed.
Nine seed batches remain; no completed case was rerun.

Measured driver time across invocations:72.586 seconds, within180-second wall
execution ceiling. Resume accounting missed4.503 earlier stress seconds while
carrying the immediately previous1.697seconds. Each subprocess was bounded below
60seconds, but cumulative stress execution was approximately63seconds rather than
the planned60seconds. This accounting limitation is recorded, not described as a
budget pass. Current process has stopped; no automatic continuation or source
changes. Root may independently review a predeclared budget amendment before
running the remaining nine batches. Current counts:15successful logical batches,
three setup-failure attempts, one interrupted attempt,19total attempts.

## Saved diminished final precheck and replay rationale

The earlier authorized22-case full-graph owner audit timed out after20seconds;
it did not save a final elapsed measurement and is not passed. Ledger charges
132.607 measured prior driverseconds +20s hard timeout +0.100s unmeasured overhead
reserve =152.707seconds. This is a conservative charged figure, not an invented
exact audit duration. Remaining27.293seconds. Final2-case hardcap is
min(21,27.293-5-1)=21seconds; direct standard-library read-only owner audit<=4s,
with additional elapsed-time guards and safety reserve. No automatic next chunk.

Reviewed test-only optimization: after valid recheck, seeded replay calls the
same pair without re-supplying the third snapshot; asserts full events equality
and zero new_events. Exact event set, fixture sizes and expected states remain.
Repeated explicit recheck and terminal immutability already passed SM02/03.

## Final diminished scope and audit

Last reviewed generator chunk hard-stopped at21.016seconds after seed2909/index6
passed; index7 remains interrupted. No more fixture generation followed. Root
then authorized only the saved-record standard-library owner audit:23reports and
196qualified owner references passed in0.191driver seconds, no DB writes. Final
charged cumulative173.914seconds,31fixture attempts,23/24conformant successes.
The24th case is incomplete, not failed correctness or waived coverage. The
full-graph audit remains timed out. No production source repair was attempted.
