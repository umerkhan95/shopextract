# P5 affected CI scheduling amendment — design before implementation

Authorized by root coordinator after final reviewer correctly refused completion
for the original required main-group240s timeout. Implementation/package/mechanism
review was otherwise clean. This amendment changes scheduling of the same tests;
no product/native algorithm, assertion, worker count or execution ceiling changes.

## Behavior / acceptance
CI-FR01 stable file-family partitions: (A) all tests except seven existing
maintenance files and tests/test_reliable_changes_stress.py, (B) that entire
native reliable oracle file (24currentcases), (C) same seven entire maintenance
files (106currentcases). Every collected test belongs exactly once, including
new scheduler tests in A. No numeric-prefix/index partition, skips, reordering or
saved-run reuse for the configured gate. Current exact commands generated from
recorded file-family constants; native assertions unchanged.
CI-FR02 one stdlib repository driver scripts/run_tests.py runs A,B,C sequentially,
using sys.executable and capped CPU/BLAS/tokenizer/download environment. Defaults
per-group<=240s, shared total<=480s, same old2x240 maximum execution ceiling.
No parallelism. Reserve cleanup time within each/shared deadline (max1s) so child
execution does not consume the cleanup allowance. CLI may narrow limits only;
nonfinite/zero/negative/over-cap rejected. OptionalSDK missing-import/present
checks remain existing CI steps. CI calls this exact driver once.
CI-FR03 each child owns a process group. Stop first failure/timeout/interruption,
terminate/reap the group, never start later groups, save report/logs. Preserve
nonzero failure, timeout exit1, SIGINT130/SIGTERM143. Final report includes every
planned/actual command, statuses/durations/cleanup, zero remaining owned groups;
only all3actualPASS under both ceilings yields passed. No silent cap increase.
CI-FR04 real harmless subprocess tests prove sequential ordering, stop-onfailure,
pergroup+shared deadlines, SIGINT/groupcleanup and input bound rejection. Test
fixtures may sleep/spawn bounded controlled children, not fake scheduler results.
Existing finalwheel remains valid because product/package source is unchanged.

## Exact test design before tasks
| SC | Input / action | Expected independent outcome / distinct risk |
| --- | --- | --- |
| CI-SC01 | inspect plan vs native file sets + actual current collection nodes | each node assigned exactlyone family; no lostoracle/maintenance/defaulttests; stable semantic files not progressindexes |
| CI-SC02 | two real Python children append A thenB marker |0passed, A beforeB, maxone active childgroup |
| CI-SC03 | first child exits7, second would create marker | exit7, failed first, second not launched/markerabsent |
| CI-SC04 | controlled process ignoresTERM, group cap .3s vs child sleep5s | timeout1, KILL/reap insidecap+small schedulingtolerance, zero ownedgroup |
| CI-SC05 | first child quick, second exceeds remaining shared .6s, group .5s | total deadline timeout, latergroup not launched, total bounded inclcleanup; independently distinguishes shared vs pergroup budget |
| CI-SC06 | driver subprocess running controlled child signals ready, sendSIGINT |130, activechildgroup stopped/reaped, report interrupted; no subsequentlaunch |
| CI-SC07 |0,negative,NaN,infinity,total481/group241 | usage2 before anyprocess; exact caps and narrowerpositive values accepted |

## Task breakdown / typed skeleton
1 author design/test matrix and genuine missing-driver/workflow red tests; reviewer
checks affected G1/G2/G3 contracts before implementation. No native productionstub.
2 implement TestGroup(name:str,command:tuple[str,...]); build_plan(root:Path,
python:str)->tuple[TestGroup,...]; run_plan(plan,output_dir:Path,*,group_seconds:
float=240,total_seconds:float=480)->dict{status,exit_code,groups,elapsed_seconds,
limits}; main(args:Sequence[str]|None)->int with strict parser.
3 affected independent review checks real subprocess tests and semantic partitions;
execute targeted firstsmoke before configuredfullgate. Actual new configureddriver
runs once from scratch, <=480s total and<=240s/group, no saved-prefix shortcut.
4 independent final re-review, root status/tasks/issues only after actualPASS.

## Research and concrete reuse
Reuse saved collection1580nodes and original CI timeout receipts for diagnosis
only. Main timeout at last of16seededoraclecases (~12.6s each); remainder225cases
64.9s andmaintenance106cases107.27s. Stable oracle-family split gives each group
headroom under240; overall remains480. Do not profile/optimize native businesscode.
Existing tests/maintenance_process_guard.py is lifecycle precedent; root driver
keeps equivalent POSIX process-group TERM/KILL semantics but adds shareddeadline,
SIGINT, always-finally cleanup and structured report needed by3groups. No product
code dependency/runtime initialization; stdlib+pytest already required. Driver
concrete consumers: GitHub3.10/3.11/3.12 matrix and local exact samecommand.
Logs bounded by finite testoutput; no credentials/modelinvocations. All prior
P5/phase evidence preserved; original configured240s timeout never relabelledPASS.

Affected review additions before implementation: CI-SC04b real leader spawns a
TERM-ignoring grandchild in the same process group and writes its PID; bounded
group timeout must remove leader and descendant, group gone after cleanup. CI-SC06
parameterizes SIGINT130 and SIGTERM143, always no activegroup/report interrupted.
CI-SC08 missing executable must produce safe failed report/exit1, no leaked PID and
no later launch, rather than traceback/missing report. CI-SC07 includes negative
caps as well as0/NaN/inf/overmax; exact240/480 and narrowedpositive .5/.6 accepted.
All cases controlled harmless childprocesses, no product/native assertions changed.

Affected implementation review disposition design: real SIGINT/SIGTERM at the
first report-save/inter-group boundary must yield interrupted130/143, persist
report and never launch next group. Signal handlers record intent; explicit safe
checkpoints raise the internal stop only after child ownership is assigned or
before launch, avoiding an asynchronous exception during Popen ownership transfer.
Outer interrupted handling covers between-group checkpoints/final report writes;
active-child finally cleanup remains authoritative. Regression injects one actual
signal at first report write after a real harmless child, not a fake run result.

One diagnosed platform blocker during focused signal checks: Darwin intermittently
returns EPERM for killpg(pgid,0) while the terminated group is disappearing. The
captured stderr proves the probe (not cleanup dispatch) raised PermissionError.
Do not equate permission denial to absence. Bound a process-table membership
fallback (pgid/uid/status only, no command/secret data) to determine actual group
presence; retain failed cleanup if a group remains unkillable. Test the real
harmless group with only the zero-signal OS probe deliberately unavailable, then
its actual disappearance after reap. No assertion relaxed; signal exit/report
and zero remaining owned group contracts stay unchanged.

Final signal interval predesign: with handlers now intent-only, cleanup must retain
them rather than SIG_IGN, so user SIGINT/SIGTERM during TERM/KILL/reap is latched.
Real controlled child times out; inject actual self-signal at real cleanup TERM
dispatch and then delegate unchanged original dispatch. Expect130/143 overall
interrupted/report, childgroup gone, no laterlaunch. This covers cleanup separately
from activework and between-group/report intervals. No asynchronous handler throws.
