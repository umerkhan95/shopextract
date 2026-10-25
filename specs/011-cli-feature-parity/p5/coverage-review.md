# P5 and parent24 pre-stress coverage proposal

Author cli_p5_delivery; independent reviewer verdict pending in reviews.md.
38 mechanism tests first green28.91s; expanded operations+core103PASS31.95s.
Actual SDK initialized root tools serve,8schemas,bootstrap resource,denied origin;
real maintenance separate subprocesses and timeout/SIGINT persisted cancelled,
lock reacquired; native tool capture/match/pages/evidence/stale handles/cleanup.
Synthetic/native fixtures count2products, seed11025, no public network/model.
Initial3failures diagnosed: required group --db blocked nested help (required at
operation validation instead); evidence fixture needed native retained evidence ID
rather than unresolved trust_view; MCP client's default stderr had captured
CliRunner stream (explicit real errlog FD). All resolved, same expected contracts.
Literal per-step preflight now validates all request steps before runtime creation;
reference-derived values still validate at dispatch. Native CategoryRuntimeConfig
is unversioned, not integer1; spec/skeleton corrected to actual native record;
versioned category portable records/CLI profiles remain integer1. No invented codec.

## Exact parent24 mapping
| Case | Risk / independent expected outcome | Reused/executed evidence |
| --- | --- | --- |
| I1 | UTF8 byte bounds below/at/above reject oversized, no partial JSON | p1/evidence/stress/byte-edges.log |
| I2 | depth64 boundary blocks deep hostile JSON | p1/evidence/stress/depth-edges.log |
| I3 | node100000 boundary blocks broad hostile JSON | p1/evidence/stress/node-edges.log |
| I4 | bool/null/empty/zero/Unicode typed values preserved/rejected by native shape | p1/evidence/stress/typed-mixed.log |
| I5 | exact Decimal/evidence/11products no human truncation | p1/evidence/stress/money-evidence-eleven.log |
| I6 | record cap boundary rejected; normalization <=100products | p1/evidence/stress/record-edges.log |
| S1 | snapshot restart/canonical persistence and roundtrip | p3/evidence/stress/snapshots.log |
| S2 | reliable recheck/replay no duplicate event | p3/evidence/stress/reliable.log |
| S3 | exact canonical history vs title ambiguity | p3/evidence/stress/history.log |
| S4 | reference-protected retention preview/apply | p3/evidence/stress/retention.log |
| S5 | publication failure restores artifacts | p3/evidence/stress/atomic.log |
| S6 | corrupt stored evidence fails safely without refetch | p3/evidence/stress/corruption.log |
| C1 | six native platform binding/scope facts | p4/evidence/stress/01-six-native-bindings.log |
| C2 | explicit empty vs unavailable/partial category sources | p4/evidence/stress/02-source-states.log |
| C3 | native map/policy/multiple-match decisions | p4/evidence/stress/03-map-policy.log |
| C4 | foreign scope/digest projection never authorizes | p4/evidence/stress/04-authority-scope.log |
| C5 | tree complete/partial/unavailable/cycles codec preserved | p4/evidence/stress/05-tree-states.log |
| C6 | same-scope supported membership only; partial missing != absence | p4/evidence/stress/06-tree-memberships.log |
| R1 | ambient keys do not authorize inference | p1/evidence/stress/ambient-guard.log |
| R2 | finite watch deadline/cleanup and failed baseline | p3/evidence/stress/watch.log |
| R3 | denied tool origin is E_OPERATION and session closes | new P5 group origin/preflight |
| R4 | same-session bootstrap/match/poll/page/evidence + stale IDs and cap partial | new P5 group session |
| R5 | maintenance durable restart/timeout/SIGINT + tools deadline/terminal-error lock/child cleanup | new P5 groups durable and deadlines |
| R6 | real SDK protocol under hostile ambient config + missingextra action + lazy help | new P5 group protocol |

Reused saved status/config: p1/evidence/stress/status.json (12cases, normalized max100,
raw boundary records1001 intentionally schema-invalid), p3/evidence/stress/status.json
(12groups; relevant cases small fixtures), p4/evidence/stress/status.json (12groups,
74executions48.464s, maxRSS199499776,0orphans). Test fixtures are synthetic/derived
offline. Public live receipts remain separate; no public transition inferred.

New P5 groups run sequential, one worker,seed11025,<=1MiB input,<=100products/case,
30s/group,720s total,512MiB aggregate child RSS,zero orphans. Existing actual smoke
saved before expansion. Stop first unexpected failure; scoped mutation breaks
session-reference pointer resolution, must fail exact real session test, restore
byteidentical and rerun. Driver saves each group and checks process-group cleanup.

Additional distinct edge tests (non-count inflation): later-step preflight no earlier
side effect; reduced actual encoded envelope byte cap includes UTF8/framing;
allowlist scalar/false/0/numeric max; category policy native persisted digest and
profile collision; real timeout swallowed by native cancellation cannot report
success; absent DB read never creates scope. Expected before code in test-design.
Final wheel/fullCI/API parity review remain pending, no waiver from mechanism pass.
