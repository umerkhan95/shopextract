# Independent reviews

## G1 — behavior, test design, tasks and research

Date: 2026-10-24. Reviewer: `/root/plugin_reviewer`, independent of author
`/root/plugin_author`. Verdict: **pass**. No blocking findings.

Reviewed repository AGENTS.md, development workflow and constitution; the six
feature planning artifacts and saved baseline logs; existing tools CLI/config,
runtime/MCP contracts and deterministic SDK fixture seam. This is a design gate,
not implementation, parser compatibility or live approval.

SHA-256 artifact identities (before subsequent status/gate bookkeeping):

| Artifact | SHA-256 |
| --- | --- |
| spec.md | 17f309ecbd91a3c84a8faf0564b10b3ec083a2836b55bb26ccb22d4de73732c6 |
| test-design.md | af7a7c2251349aed414dbac96a26be9d7bef815ac78349322d085b15df8a6123 |
| tasks.md | 7c8610be3cf547644bdf336205172d79e6d1b0987d1d9f5524a33c1ba14fc1e2 |
| research.md | 171ee0499c5c6fa9d0a47d1c06071003a567adf18d0b22fd20bdd70406319e18 |
| plan.md | 989cf2997865c29c824bf190220253ae66cb91c6a396702a0f0ff3d839342c41 |
| status.md | ad82b2117492d740f18bfa91f06fa2eb8c040af8c858d0cded7b896f8301c463 |
| evidence/baseline-smoke-repaired.txt | ecf3357678eeff81d07ce3d4e1aaa760421ee1477950777e04702a54c1462806 |
| evidence/baseline-smoke.txt | d6ff4b2ee68e6fb3809940e2ba9b80a36f4ae3a8bcbceb1afb201d72f9f5bcc4 |

Findings and disposition:

- Scope/traceability: FR01–07 and SC01–08 cover the bounded #82 local package,
  Code-only #74 route and one #73 recipe. No remote, hosted, marketplace or other
  ecosystem implementation is planned. Parent PR merge/CI is explicitly unknown.
- Configuration: direct command/argv, no shell/defaults and operator-owned absolute
  setup are compatible with the existing CLI. Literal hostile-path tests and
  unset/empty/malformed configuration cases cover command injection and fallback.
  Existing relative-path CLI behavior is correctly distinguished from supported
  plugin setup; no core behavior change is required.
- Mechanisms: real native validation is separated from stricter repository
  inventory policy. SDK/config launch, real engine fixtures and fresh-process
  stale-handle checks are meaningful seams; baseline success is not red acceptance.
- Budgets and evidence: six calls include results/status/evidence; pending results
  terminate the recipe. Three-record/two-item partialness, duplicate identity,
  exact decimal support, source injection, denied outbound requests, failed and
  timed-out jobs, deadline/call exhaustion and disconnect are distinct designed
  adverse cases. Controlled transport is explicitly offline evidence, and harness
  completion waits do not establish host/model compliance.
- Live: native parser/version availability does not imply normal authentication.
  Disposable profile, controlled source, three prompts and explicit ceilings are
  predeclared. Missing access remains blocked; no credential copying or fake pass.

Nonblocking implementation checkpoints for G2/final: make the bounded stress
cases executable with explicit fixture sizes/timeouts and terminal assertions;
record exactly which native-negative mutations the installed parser rejects;
label any test-side environment expansion as SDK launch evidence, reserving
actual host expansion/activation claims for observed host behavior. These clarify
already agreed SC02/05/07/08 contracts and do not authorize production work before
G2, G3 and saved intended red results.

G2, G3 and final review: **not reached**.

## G2 — skeleton and executable red interfaces

Date: 2026-10-24. Reviewer: `/root/plugin_reviewer`, separate from author.
Verdict: **changes required** after coordinator raised the clean-CI host
dependency below. This supersedes only the earlier G2 not-reached status; G3
and final remain pending.

| Artifact | SHA-256 |
| --- | --- |
| skeleton.md | a6a35de248f86d5c884935840b68eabda8526086ae2e8bc1d63d740cb162fe05 |
| verification.md | 4eba37e87947fdb3ce966b74e38b674f2be15f82c74e243550a2e14e3cf233d4 |
| tests/test_claude_code_plugin.py | 5ae314641f8fdb146cd71aa55448cc8d31e9a4db52dffe006b9f92d2e9ec5c49 |
| tests/test_claude_code_workflow.py | ec4c2a146b591d4bd09c790a7c063af881437d5e16e6815ad98db564e155b073 |
| evidence/acceptance-red.txt | 6f7909d8ca0cb3ec26ac1dd722fc524eb95fb6cd8a405f42ce9684bcaf4e2e03 |
| evidence/host-preflight.json | 9d72eeee4db8e00ac385525972115becb491f37d719752a20b4067188e639704 |

Reviewed actual tests, proposed runtime/session/driver interfaces, five saved
missing-artifact failures and host preflight. Confirmed production directory is
absent; no runtime API/stub was introduced. No redundant baseline rerun.

- Red assertions fail for intended absent manifest/MCP/skill behavior, rather than
  an import or dependency error. The parser and SDK guards explicitly prevent a
  claim that those mechanisms ran already.
- Direct argv checks restrict placeholders and allowed fields. The hostile-path
  test uses the shipped declaration, real production CLI and SDK initialization,
  restrictive configuration, denied-origin envelope and sentinel absence. It
  exercises the launch seam without pretending to verify native host expansion.
- Planned fixture interfaces keep production runtime/jobs/parsers/evidence intact
  and replace only controlled outbound boundaries. The recipe trace and sequential
  session lifecycle can exercise pending, deadlines, failure, partial results and
  old-handle denial without fabricated successful reports.
- Metadata/skill string checks are initial packaging/policy assertions, not full
  semantic checks or model-compliance proof. Native malformed-package and stricter
  containment/inventory checks remain explicit T09 obligations; source/budget/
  restart execution remains pending and must appear in final coverage.
- Host preflight records exit1 `Invalid API key` for disposable plain auth status.
  Advertised `--text` failed before one plain-status repair. This is a live access
  blocker, not evidence native validation works or the plugin activates.

Nonblocking implementation checkpoint: save actual native parser structured
results and reject generic help/no-validation output even if a client exits zero;
the negative mutation matrix should demonstrate that parsing happened. Keep
policy text checks clearly weaker than executed mechanism assertions. These are
verification requirements, not new production components.

### G2 blocking finding: native host requirement leaks into default CI

Severity: P1. `test_native_parser_accepts_shipped_package` unconditionally fails
ordinary pytest when `claude` is absent. Claude Code is not a repository Python
dependency; this would make otherwise supported clean checkouts/CI fail for an
environment prerequisite. The blocker concerns test selection, not weaker native
verification.

Required disposition: make native-host tests explicitly opt-in (or an equivalent
dedicated integration invocation). Default CI must continue exercising package,
inventory and SDK tests without requiring the proprietary host. The dedicated
native invocation must fail explicitly when requested but unavailable; save its
actual results separately and never count the default skip as native validation
pass. Update skeleton/test design and verification commands to express this
distinction, then return for focused G2 re-review. Existing intended red logs
remain valid missing-package evidence and need not be discarded.

### G2 focused re-review — blocker resolved

Date: 2026-10-24. Reviewer: `/root/plugin_reviewer`. Verdict: **pass**.
The native test now has an explicit environment opt-in evaluated before execution.
Default pytest skips it; requested execution retains the missing-client assertion
and finite subprocess timeout. Package and SDK tests remain normally selected.
Design/skeleton/verification distinguish default skip from native compatibility
evidence and retain a separate mandatory native invocation for this feature.
Saved revised red log records four intended missing-package failures and one
native skip in 0.27s. No production files or invented native pass introduced.
The CI-dependency finding is resolved; G3/final remain pending.

Reviewed revised SHA-256 identities:

| Artifact | SHA-256 |
| --- | --- |
| tests/test_claude_code_plugin.py | 42d815e78a0a88b348ce42f3e1c115bae231f4077108cd0af81371b30540c753 |
| skeleton.md | 904ec5f35a1ff25bb347f7e40e1c52d4b5de07a192351b2c61ae574919627a3f |
| test-design.md | ab0f1e6771c868f9cd8efad4b14ceba8fbce5adca211d1c85d6050e4ee083f72 |
| verification.md | e7027598a3aaa04e90fe2eb652d1b85bbefa71b8cbf177ed0682cd70ded219f2 |
| status.md | d2c91a92e993811f1e2ddea712c11baac734b09071af44b19e8c2fe8b2a40f76 |

## G3 — reusable components and refined skeleton

Date: 2026-10-24. Reviewer: `/root/plugin_reviewer`, independent of author.
Verdict: **pass**. No blocking findings. Final implementation review remains
pending; this is not an offline/native/live verification verdict.

| Artifact | SHA-256 |
| --- | --- |
| components.md | 3ea1ce5a83a08e4edda49640465acc6b7b401ff199405f2827ab43c9a50204d5 |
| skeleton.md | 1d76fa5b83a2ba5849cf60e916df059236e25f0a5a22a0e6d1e45a3a45dee8cd |
| test-design.md | ab0f1e6771c868f9cd8efad4b14ceba8fbce5adca211d1c85d6050e4ee083f72 |
| tests/test_claude_code_plugin.py | 42d815e78a0a88b348ce42f3e1c115bae231f4077108cd0af81371b30540c753 |
| tests/test_claude_code_workflow.py | ec4c2a146b591d4bd09c790a7c063af881437d5e16e6815ad98db564e155b073 |

Reviewed component ownership, refined interfaces, designed scenarios, current
tests and G1/G2 findings/resolution. Production package is still absent.

- Reuse follows existing dependency direction: manifest invokes existing CLI;
  CLI/runtime own operator policy, jobs and retained evidence; MCP adapter owns
  protocol and cleanup; skill only instructs. No production wrapper, installer,
  generalized plugin framework or alternate data model is introduced.
- Test helpers have concrete bounded consumers. Exact placeholder substitution
  remains test-side SDK setup. Feature-specific controlled transport fixtures do
  not widen unrelated fixtures or replace production parsers/jobs/evidence.
- Discovery, host activation, variable expansion and model behavior belong to the
  host; parser/inventory/SDK results are explicitly different evidence. Fixture
  process entry is not misrepresented as shipped CLI source extraction.
- Lifecycle ownership supports sequential process restart, old-handle rejection
  and disconnect cleanup without adding durability. Pending synchronization is
  offline-only and counts toward wall time; call/deadline guards precede calls.
- Implementation/check plan retains real source caps, duplicate identity,
  permission denial with zero outbound work, partial/error/pending/timeout paths,
  native negative mutations, path containment and strict default-CI boundaries.
  These remain execution obligations for T09/final, not assumed successes.

G1/G2 findings are resolved or retained as explicit verification checkpoints.
Implementation may proceed against saved intended reds; actual native support
and SC08 host activation remain unproven/blocked respectively.

## Final — local package and available offline engineering

Date: 2026-10-24. Reviewer: `/root/plugin_reviewer`, independent of author.
Verdict: **pass for the implemented package and available offline engineering**.
**Full integration/native compatibility completion remains blocked**, not passed.
No blocking code findings. This verdict does not waive SC01/07 native parser or
SC08 host observations and must not be used to close broader #73/#74 work.

Reviewed every shipped package file, four new test/helper modules, docs link,
feature planning/review history, verification/status and saved actual parser/auth
responses. Inspected CI: ordinary tests install `.[dev,mcp]` and native tests remain
explicitly opted out. Checked `git diff --check` successfully. Reused recorded
147-pass affected run and subsequent supplemental/package results rather than
repeating completed bounded suites. No claim of full-suite or CI success.

| Final artifact | SHA-256 |
| --- | --- |
| .claude-plugin/plugin.json | 7e37db870b0c4ff45fda020987e8b54a8b2056d2326b95fc3756c3659ad2a3f2 |
| .mcp.json | a30ea4ec1468cbf74a0944ddcacc418bd5b5698a1d2f303eb9ae4514bf6c5abd |
| skills/shopextract-review/SKILL.md | a4c2ccc40d96dd6aef549401a157a5cf28b0c892f164a6d77357cbd744f37b22 |
| README.md (package) | 4dd2e518e74ef4c12a4684e394930632fa5641bb836e5a23efce82f72a0d9e74 |
| LICENSE (package) | 1dfef98018c8b7ad8a9f34f3de9383cf704435b8e7729bb6f89e2f95858a81a2 |
| tests/claude_code_fixture.py | 9edda0ae868dd74d682d7dc9b2f2322edd509d96962f032e79c3b4ab80c68ef2 |
| tests/claude_code_recipe.py | 74d7bd500b736080fee044fe42197163c18bf92285468ccdc3ff1892b73f92f9 |
| tests/test_claude_code_plugin.py | bcbf4d717a0e95f15b1912490f7f8275e62aeb6576bf82b3c56ea47b6a9fd143 |
| tests/test_claude_code_workflow.py | 2ca764754da84578a3b0ce5b014d79b433af8e9c5cd2f2606ba3a0e8a8ffdefc |
| verification.md | e74398aae286eb52aa71eef53386c4926909a8ae5b21571e5bb682d9485e36a8 |
| status.md (before final bookkeeping) | a4e581e7e13a47729badf2d2a93bf9858458f7a3a751ce99a5d6ab46c9966429 |

Findings/disposition:

- Production surface is exactly five small files: native metadata, direct stdio
  executable/argv, one instructions-only skill, guide and MIT license. No operator
  credentials/paths, shell, install code, hooks, background agents, remote service
  or runtime/core changes. Guide requires an installed operator-chosen executable
  and external trusted configuration without relying on plugin cwd.
- Recipe is explicit about the six total host tool calls (including any preflight
  calls), two products, 120 seconds, no retries, pending/error stops, exact schema,
  selected server, granted origin, owner-bound evidence and session lifetime. It
  cannot enforce model behavior or grant host permissions and says so. It preserves
  uncertainty/partialness and rejects source-originated policy instructions.
- Real SDK hostile literal filenames initialize the actual CLI and exercise
  restricted discovery/denial. The symlink/venv test repair supplies existing
  installed dependencies without creating a production launcher or claiming host
  interpolation. Invalid startup cases and missing executable cover explicit
  failure instead of permissive configuration fallback.
- Controlled fixtures replace only resolver/wire data. Runtime parsing, jobs,
  evidence and normalization remain production paths. Distinct cases cover two-item
  partial caps, duplicate discovery, unknown support, exact money, zero-refetch
  evidence, failure, genuine pending/timeout jobs, pre-call count/deadline stops,
  queue capacity and cleanup. Sequential SDK restart tests old-handle denial and
  stable canonical identity with a fresh owner. Existing regressions cover broader
  field/evidence interactions. This is mechanism evidence, not model injection
  resistance or host activation.
- Native negative cases are **not executed natively**: only project inventory
  negatives passed. Documentation and verification correctly distinguish this.
  Actual strict parser attempt rejected a flag; its single plain repair required
  login. The test will reject unavailable/auth/help output instead of accepting
  exit0 alone. Default native skip is no compatibility proof.
- Private directory-load/reload/disable instructions avoid global config mutation
  and public marketplace publication. Their actual discovery/install/update/
  disable/variable expansion/activation behavior remains unobserved. The guide
  explicitly records all of these limitations; no host prompts were sent.

Gate validity: G1 behavior and G2/G3 seams remain applicable. Later additions
(standalone license, tighter preflight call counting, finite stress fixtures and
supplemental identity/no-refetch assertions) refine their existing contracts;
this final independent review covers those refinements. No unreviewed production
contract change or broadened ecosystem scope was found.

Remaining required evidence: a functioning authoritative native parser (positive
and supported malformed-package checks), then normal signed-in disposable-profile
host discovery/activation/lifecycle and bounded prompts. Preserve blocked status
until observed. Ticket/PR handoff may describe implemented offline package work
with these explicit limitations; it must not state full host integration passed.

## Revision 1 G1 — user findings on PR #89

Date: 2026-10-25. Independent reviewer: `/root/plugin_reviewer`.
Verdict: **changes required** for contradictory current-contract presentation.
Original gates remain historical and do not approve revised implementation.

Reviewed FR08–14, SC09–15, revised tasks/research/plan/status/verification and
saved unsynchronized baseline. No implementation changes or model execution.
Scope correctly excludes Product/dict, HTML entities, USD and other integrations.

Blocking finding R1-G1-01 (P2): appended revision notices do not consistently
make conflicting original rules historical. In particular test-design.md's
original State and compatibility contracts still says any host preflight tool
execution consumes the six-call budget; status.md's top-level Limits/usage
repeats it. Those sections read as current, conflicting with schema-only
ToolSearch exclusion. Original spec FR03 similarly remains current-looking,
though the revision later supersedes part of it. Original verification must
remain historical evidence; current-facing rules must have one clear authority.
Required fix: update current contract/status wording or explicitly mark entire
older contract sections historical/superseded with a link to the current section.
Preserve historical observed counts/results. Skill implementation must eventually
contain one unambiguous domain/schema accounting rule.

Other reviewed design findings (nonblocking checkpoints for G2/execution):

- Six domain invocations include failed calls; only schema-only host discovery is
  excluded and separately counted. Unknown namespace/non-schema actions fail;
  no grant or permission is inferred from instructions. Good scope boundary.
- Product selection conservatively filters returned authorized URLs, rejects
  blog/article/news/journal even with product markers, ranks deterministic markers
  and stops exactly when the visible two contain no qualifying URL. At skeleton/
  tests, pin encoded path-separator handling explicitly so exclusion cannot be
  bypassed by `%2F` inside a nominal segment; do not broaden discovery to rescue it.
- Finite-delay unsynchronized pending is the correct new coverage. Ensure at
  least one delayed-discovery case observes the outbound request entering the
  delayed wire boundary before asserting pending, without joining completion;
  otherwise another zero-request queued result merely repeats the baseline.
  Extraction-pending already permits request-start phase coordination.
- Source bootstrap before source MCP installation is grounded in repository
  build seams. No PyPI shortcut, automatic dependency mutation or library edits.
- Nested manifest.errors acceptance and false-validity/malformed/auth negatives
  correct the old assumption. Listing warnings remain separate; no invented
  marketplace icon requirement or public publication is justified.
- User-reported 2.1.310 success is attributed separately from local 1.0.35 flags/
  auth failures. Skip-plugin environment troubleshooting avoids asserting unknown
  public semantics or silently changing flags/configuration.
- Real host harness is separately opted in, literal argv, copied assets with
  recorded test-only MCP override and real runtime/source trace. Replay verifies
  parser only. Stream ID dedup/correlation, owner/evidence lookup matching,
  unexpected-tool failure and explicit pending outcomes address false success.
  G2 must specify the actual finite max-turn value and preflight that establishes
  support/auth before any model execution; independent process120s supervision
  and bounded cleanup remain required. A detected seventh call fails and cannot
  be claimed prevented if already emitted/executed.

Return revised current-contract presentation for focused G1 re-review before
skeleton/red changes. Native model execution remains blocked unless all stated
normal-access/known-limit prerequisites are met.

Revision G1 artifact SHA-256 identities:

| Artifact | SHA-256 |
| --- | --- |
| spec.md | 596915f1f9b347a22101b26fbe01263adfb2753411a49562c5218208ac8ac628 |
| test-design.md | 247eebb42d906827545437abd6567b5fd79a9da1d7f99c799815e7fd971bbb32 |
| tasks.md | d5bf227d56153e37b849af2185dde0b8ce36b55b002597d9cebb9442759619d4 |
| research.md | 0271c151ac1ba538a3797aeee875318a83661b35be8fdc781e3268abfa832405 |
| plan.md | f4e76a98041d8220d0726a2b6e11d066eaf425067d2c103eb1b25722ae549992 |
| status.md | e1e921fb821b1516a4946e1dd719b7234199de4f426b4c3b7e84dec72594b5d0 |
| verification.md | 08a11961ce1d6d7484698af6f8b00fafc02b3e2f3e94e85c733ef97b79f5655e |
| evidence/revision-1/baseline.json | c57a51d80afbf27cf6f9552ea64a072cd835307f55294eef13a5c85a248495b6 |

### Revision 1 G1 focused re-review — pass

Date: 2026-10-25. Independent reviewer: `/root/plugin_reviewer`.
Verdict: **pass**. R1-G1-01 resolved. Current FR03, test-design state/live
accounting and status now consistently use six domain invocations and separately
record schema-only loading; all share120seconds. Original matrix and original
skeleton/components are explicitly historical where superseded. Historical
verification remains observed evidence, not rewritten success. Production skill
still awaits its authorized revision stages and must adopt the single rule.

Reviewed correction digests:

| Artifact | SHA-256 |
| --- | --- |
| spec.md | cf94ae790d13d37b9962e4db85f5cbcf90bd0241273203fec88d981829468a86 |
| test-design.md | 45e791028bb05339ff1eada686aafcaf6294a2ca5fe31d2ac293c3bac36954be |
| status.md | bae0dac12e8eb96dcf1edf151750a73b5c36a4801811f40436f4d368f28aa81b |
| research.md | 47d2fe20920c78c8c0a7529e2438acedc86e2eec5a37def7d0d9be26cb88f5dd |
| skeleton.md (historical notice only) | 54cda606f918398a186885a75db8ccfb2bf7dfbcb18603ae1658cf74cc0a1002 |
| components.md (historical notice only) | c1cb9b14ea3f10c8c2ef577985a8201d566f61a9936ef0591a515acda6b9def9 |

Other revised G1 artifacts retain the immediately preceding review's identities.
Encoded-separator handling, actual finite-delay request entry and concrete
supported max-turn supervision remain G2 checkpoints, not waived checks. Revised
skeleton/intended reds may proceed; revised G2/G3/final remain pending. No model
run, native pass, implementation edit or additional scope was approved here.

## Revision 1 G2 — skeleton and intended-red interfaces

Date: 2026-10-25. Independent reviewer: `/root/plugin_reviewer`.
Verdict: **changes required**. Reviewed revised skeleton, all revision tests,
29-failure red log, revised G1 contract and compatibility attribution updates.
Missing-helper/file/case guards are intentional behavior reds rather than import
errors. Their post-implementation assertions are useful, but two harness seams
need correction before G3.

Blocking R1-G2-01 (P2): G1 explicitly required a concrete finite max-turn value at
G2. Skeleton still says only "max-turns"/known support and pure capabilities true;
it declares no numerical turn bound or actual `run_host_case` parameters/return
contract for the requested invocation. Declare one explicit finite turn ceiling
and process/cleanup ceilings, literal argv construction and unsupported-option
failure contract. No inference may run if selected client/support/auth cannot be
established. The eligibility bool alone is not actual support evidence.

Blocking R1-G2-02 (P2): all new tests can pass with `reduce_stream` and
`assess_preflight` implemented while `host_preflight`/`run_host_case` are absent.
There is no executable acceptance for the real host launch/supervision interface,
default-no-launch behavior or enforcement of preflight by the launcher. Add
intended reds for those actual planned entry points, not merely the pure gate.
Require a denied/unset-opt-in runner to make zero launch attempts; validate
literal selected executable/plugin argv and finite configured caps; cover bounded
process termination on an actual harmless controlled child or equivalent genuine
subprocess seam. Such fixtures are supervisor/driver evidence, never native model
proof. This stays test-side and does not authorize default inference.

Positive findings/checkpoints:

- URL selection signature and vectors pin decode-before-split, article exclusion
  before positive ranking, backslash rejection, exact original URL and same-origin
  preservation. Encoded separators cannot conceal blog segments under this design.
- Finite pending cases now assert observed requests plus active response delays;
  caller latency is explicit and never joins completion. Actual runtime remains
  intact. No-product integration consumes real discovery rather than canned jobs.
- Schema preflight validates exact selected-server definitions and schema version
  without spending a domain call. Stream fixtures deduplicate actual tool IDs,
  reject unknown tool/article/seventh-call/error completion and correlate selected
  owner/field evidence with successful lookup. Supplemental conflict-ID, missing
  result/error-envelope and genuine pending-stream vectors should appear in final
  coverage as already designed, not be inferred from the happy stream.
- Nested manifest errors/warnings and attributed cloud 2.1.310/local 1.0.35
  observations are correctly separated. Named but unavailable external bundles
  and reported wrappers/real-server calls cannot become locally reviewed raw
  trace evidence. No fake marketplace files, credentials or permissions added.

Return the bounded launch declarations and intended-red runner tests for focused
G2 re-review. No implementation edits or model executions were made by reviewer.

Reviewed revision G2 SHA-256 identities:

| Artifact | SHA-256 |
| --- | --- |
| skeleton.md | 83cb59f6bfaee1a8e671dd21a284efe55b745444989370e62ecc36916d9c5710 |
| tests/test_claude_code_revision.py | 0ee08f9f0f569ad4f4af70a05aea19267743a64a169ca2b62f8346a7f2bda202 |
| evidence/revision-1/acceptance-red.txt | 30bd022a4425fdfcd53bcd6287926d6a024acbfe131107b1a0440b88b6129c34 |

### Revision 1 G2 focused re-review — pass

Date: 2026-10-25. Independent reviewer: `/root/plugin_reviewer`.
Verdict: **pass**. R1-G2-01 and R1-G2-02 resolved at skeleton/red stage.

Explicit native invocation ceiling is now10turns,120seconds wall and2seconds
total cleanup (TERM1second/KILL1second), with required capability/auth evidence.
Actual preflight, argv builder, process supervisor and runner signatures/results
are declared. Missing/unsupported eligibility returns blocked before launch.
Built-in tools are restricted to schema search/skill activation; MCP names remain
explicitly checked separately. No permissions bypass or shell is authorized.

Three new intended-red tests reach actual planned entry points: disabled and
ineligible paths forbid subprocess launches, eligible runner must route literal
argv/exact limits through the supervisor, and a genuine TERM-ignoring controlled
Python process must time out, be killed and reaped. The latter has an independent
4second watchdog and test-owned fallback cleanup; replay/wiring remains explicitly
distinct from model evidence.32saved intended failures preserve no-implementation
status. No actual Claude inference occurred or is authorized by this gate.

| Revised artifact | SHA-256 |
| --- | --- |
| tests/test_claude_code_revision.py | c85f380132eb309e25d0c7f8dab7cb7c7a13f8f60be61575534af26944c36f80 |
| skeleton.md | 2a14d21c3c1c8db65c1399cd764a4f1801543168a2b4eef40622424981434da8 |
| evidence/revision-1/acceptance-red-g2.txt | f176cc199abae0e8dc87a88b2ba4d0e7164ce4645134ce9c0e3527590a078c18 |

Revised components/G3 may proceed. Final review must verify actual supervisor
implementation covers stream size/call breach and process-group cleanup, and
that actual native runs remain blocked without trustworthy normal-access and
bounded-capability preflight. Other G2 positive findings/checkpoints remain valid.

## Revision 1 G3 — reusable components and bounded lifecycle

Date: 2026-10-25. Independent reviewer: `/root/plugin_reviewer`.
Verdict: **pass**. Reviewed revised ownership matrix, refined skeleton, prior
G1/G2 findings and32intended reds. No implementation or model execution reviewed
as completed at this gate.

| Artifact | SHA-256 |
| --- | --- |
| components.md | 5064c41232a1af8924e4cfd954da5d67ccea57ec5290637463bc2be03804472b |
| skeleton.md | 59a2baeefaad9295fda9edff6f4a95714a3a2f97ba950880d9d870d52ae20eb5 |

No blocking findings. Production remains concise instructions/assets around the
unchanged CLI/runtime/source/MCP contracts. Selection/schema helpers have concrete
recipe/trace consumers; native report parsing remains test-owned. The one native
test module owns eligibility/argv/stream supervision/reduction without becoming a
production framework or granting permissions.

Finite source fixtures retain real business/parser/job state and observe only
wire delay/requests. Disposable-copy MCP override and original/copied hashes are
separately recorded; wrapped synthetic-source host runs cannot be claimed shipped
operator-CLI proof. Normal graceful disconnect and forced group termination have
explicitly different outcomes. No cloud bundle or reported observation is promoted
to locally inspected evidence.

Resource/lifecycle refinements are consistent with G2:10turns/120s case,2s total
TERM/KILL cleanup,1MiB combined trace cap and owned POSIX group only. Default
preflight performs zero probes; eligible setup has at most3non-inference probes,
5s each plus bounded cleanup, stops at first blocker and never retries/login/
installs. Uncertain safe group control or exact supported caps blocks execution.
Final verification must exercise oversize/invalid streams, tool breach and owned
process cleanup, beyond parser fixtures alone.

Setup guidance reuses the actual bootstrap/preparer/Hatch seams and accurately
distinguishes static/offline build-contract checks from fresh installation. No
dependency/network mutation is justified merely by documentation verification.
Revised implementation may proceed against saved intended reds. Independent final
review and actual native eligibility/model evidence remain separate obligations.

### Supplemental SC15b affected-design review — pass

Date: 2026-10-25. Independent reviewer: `/root/plugin_reviewer`.
Verdict: **pass for affected G1/G2/G3 design obligations**, no implementation
verdict. Reviewed the new SC15b normal-parent-exit/owned-descendant risk against
the existing supervisor signatures, group ownership and cleanup component model.

| Artifact | SHA-256 |
| --- | --- |
| test-design.md with SC15b | abe38f0e00249d6cd8f3d0c45081b55887710285c6f6a79f646afd78b831a3a9 |
| skeleton.md (unchanged interface) | 59a2baeefaad9295fda9edff6f4a95714a3a2f97ba950880d9d870d52ae20eb5 |
| components.md (unchanged ownership) | 5064c41232a1af8924e4cfd954da5d67ccea57ec5290637463bc2be03804472b |

No blocking findings. This adds distinct lifecycle coverage: parent exit0 and
pipe EOF can coexist with a live MCP descendant, unlike the existing direct-child
timeout. One controlled descendant, readiness/PID/group evidence, redirected
stdio, TERM resistance, finite30s self-exit, outer5s watchdog and owned fallback
are bounded and exercise genuine OS group cleanup without model/native access.
Always cleaning the still-owned group is cohesive with the existing supervisor
contract; no new production abstraction or stronger application cleanup promise.

Preserving direct-parent returncode0 must not hide group cleanup failure: include
diagnostics/failure state when no-running-descendant cleanup cannot be established
within2s. PID/group/session ownership must be verified before fallback signals;
indirect zombies are OS-ancestor reaping responsibility and must not be reported
as supervisor-reaped children. Native-case success requires its cleanup evidence,
not merely preserved parent exit status.

Author may add the intended failing SC15b process test, save its actual red, then
repair the supervisor against this agreed case and run affected cleanup checks.
Final review must inspect the executable identity/cleanup safeguards and observed
result. This review neither certifies implemented cleanup nor authorizes native
model execution. Work remains sequential.

## Revision 1 final review — changes required

Date: 2026-10-25. Independent reviewer: `/root/plugin_reviewer`.
Verdict: **changes required**. Reviewed complete diff/new helper and acceptance
modules, package docs/skill/version, current design/gates,191-pass affected log,
SC15b red/green evidence and local preflight. No native model execution or broad
suite rerun. A bounded pure mocked-supervisor probe below establishes a false
pass; it is parser/runner evidence only.

### Blocking findings

R1-FINAL-01 (P1), case-specific host success: `run_host_case` validates whichever
outcome the model chooses, with no expected case/outcome input. An extraction
prompt can return a successful final `{outcome:"unrelated"}` with zero domain
calls and an empty source log and receive `status:"passed"`. Reviewer reproduced
exactly this using a unit supervisor result: status passed, outcome unrelated,
domain_count0, requests0. `main` would save it under the positive success case.
The same issue permits a prerequisite outcome to satisfy the wrong fixed case.
Require expected case/outcomes: unrelated must be unrelated/no activation;
missing-grant must be a supported prerequisite; positive extraction must be
actual pending or completed evidence with corresponding actual execution. Pending
remains distinct from completed evidence. Add intended regression before repair.

R1-FINAL-02 (P2), eligibility ignores unsafe probe results: `host_preflight.probe`
drops `diagnostics`/group_cleanup and subsequent decisions inspect only exit code/
stdout. A probe can report cleanup unverified, timeout/invalid/oversize diagnostics
or forced termination while still emitting recognized identity/auth text; such
evidence must not establish eligibility for later model execution. Fail closed on
any probe timeout, supervisor diagnostic or unverified owned-group cleanup, save a
sanitized reason, and stop at the first blocker. Add deterministic gate tests with
recognized text plus failed supervisor evidence; this requires no native client.

R1-FINAL-03 (P2), supervisor boundary verification missing: revised G3 explicitly
required executed oversize/invalid-stream/tool-breach cleanup checks. Current
supervisor tests exercise direct timeout and normal-exit descendants, while
seventh-tool/invalid events are only reducer fixtures. Add bounded real harmless
child cases for invalid stdout, combined stdout/stderr byte cap and emitted
seventh/unexpected tool while child remains alive. Assert diagnostic, termination/
reaping/owned-group cleanup and finite limits. Replay cannot prove that live pipe
collection/supervision stops the process. Save actual focused results, then only
affected regressions warranted by changes.

### Required contract clarification

R1-FINAL-04 (P2), URL policy consistency: selector currently accepts original
`https://store.example/products%2fwidget` after decoding to `/products/widget`,
while skill says reject ambiguous encoded separators. Existing encoded vectors
also contain blogs/dots/backslash, so do not discriminate this policy. Make one
explicit shared decision about a single encoded slash versus residual/double
encoded separators, align skill/design/oracle and add a direct discriminator.
Do not invent a broader source policy. Also keep empty discovery's early-stop
wording explicit versus exact no-product candidate outcome; current step2 says
empty reports its state, so it should not silently be described as the latter.

### Other findings and preserved evidence

Source bootstrap order matches existing preparer/build seams and the help check
is noninstalling. Package remains local/instructions-only with unchanged .mcp
argv and core code;0.1.1 is consistent in metadata/guide/tests. Conservative
visible candidate ranking, real index/blog-first/redirect mechanisms, observed
finite-delay pending and owner/evidence handling are meaningful offline checks.
SC15b implementation adds always-owned-group cleanup and reports indirect zombies
separately, without claiming indirect reaping or graceful shutdown after kill.

ToolSearch currently supports query-only arguments and fails on optional extra
arguments. This is conservative fail-closed behavior, not universal installed-
host payload compatibility; keep that limit explicit or support verified optional
schema-only fields with tests. The unavailable reported bundle is not proof of
payload shape. No new external research/model run is needed to address the above.

Reported cloud2.1.310/sonnet5-5/wrappers versus separate real-server startup remain
correctly attributed. Local1.0.35 one-version-probe blocker and0model calls remain
honest. Native opt-in skip is no native pass.191passed/1skip is a valid recorded
affected result for that revision, not proof against the newly reproduced gap.

Resolve these findings, record affected design/red/green evidence and return for
focused independent final review. No commit/push or native inference performed
by this reviewer. Full native reproduction remains blocked.

Reviewed final-revision SHA-256 identities:

| Artifact | SHA-256 |
| --- | --- |
| skill | 179f9c3a67cd69f46090199dd7ec1227b3a13f03721448bfab795728d6a1dcce |
| package README | 2dab0693e940166b464e6e38f00abffbd5336186d3c015fd87024b2705c327b9 |
| tests/claude_code_host_smoke.py | 5a21389df58a120066c0beb853e29b0c91d2dc63e31476b76b402fe2a0d28d17 |
| tests/claude_code_recipe.py | 7d8daffae3a93f66cc0c55049a500725e000e494f5cd59521da636364bf2c505 |
| tests/test_claude_code_revision.py | 3fcbe2c492162d10cbc19ecffa61dec59846119028aa9fe499fa5591c871522b |
| revision-1/affected-regressions.txt | 26eea0e28f9de8e3175d0a3c569fdfa68827227ac438ce28d048ed757f92f174 |
| revision-1/local-preflight.json | 2ff31d661d3f5d9f6c8a38366aa90b50e7376dbe6db819f827d961c521a0c21e |

### Focused final-finding affected G1/G2/G3 review — pass

Date: 2026-10-25. Independent reviewer: `/root/plugin_reviewer`.
Verdict: **pass for affected behavior/interface/component design and intended
tests**. This is not final approval of repaired implementation.

Reviewed appended FR15–18/SC16–19, refined required `expected_case` signature,
controller/reducer/eligibility ownership and all28new regression instances.
Saved pre-repair result20failed/8passed establishes intended old false-pass,
unsafe-probe and encoded-separator gaps. Four actual controlled boundary cases
already pass and newly supply the formerly missing live-supervisor mechanism
coverage; those green results do not hide the20remaining reds.

No blocking design findings. Positive native case requires actual completed
verified evidence; truthful pending is incomplete and no automatic retry follows.
Unrelated and missing-grant are distinct trusted caller cases; missing-grant
requires a correlated selected-server permission_denied, not arbitrary host
approval failure/zero-call prose. Case binding never comes from model summary.
Eligibility rejects unsafe supervisor evidence before parsing each stage's text
and stops immediately. Pure failed-probe fixtures cover all3stages without native
execution. Existing runner/collector own these responsibilities; no new framework.

Original single encoded slash is now explicitly rejected, as are residual/double
separators; unreserved encoded product text retains the original URL. This is a
small conservative recipe decision, not a core source-security change. Empty
discovery stays a separate empty stop. Query-only ToolSearch limitation is now
explicitly failed/unverified for optional fields; no unsupported compatibility
claim. Four real pipe/tool boundary tests use only controlled Python, fixed small
output limits, watchdog and owned fallback; no Bash/domain/model tool actually
executes from the emitted synthetic events.

Author may repair against these saved reds and run affected checks. Final review
must verify actual trusted case propagation, sanitized supervision diagnostics,
required no-running-group cleanup and no false native completion. Native inference
remains separately opted in and locally blocked. Prior final verdict remains
changes required until implementation/evidence re-review.

| Reviewed correction artifact | SHA-256 |
| --- | --- |
| spec.md | 16a22605e61daf9d0516fbae76a6a1b2668dc710801863592d53f29286590b88 |
| test-design.md | 619f0732f081ff12fda1e064f9adaf70377e2465932d59d93fc228a09d6e7778 |
| skeleton.md | 28c9239c4c928f017966e1ce0646c0b20da1211e9f2451a71a8fe8d723c9ab6c |
| components.md | 4ab15ba49df1c50651e5a93f1820e3bf9c8f742a81a9b1696a72c50a9d5c0958 |
| tests/test_claude_code_review_repairs.py | b3a1e1d7c6ccf910fbb9fe16e3c3f349adbb75afbb4d35099cce75f6d3294a8b |
| revision-1/final-review-red.txt | cfd793ad5778f7fb39dfd78aaa5bac9793e16e07729bf7e81cc3081a950da8a8 |

### Revision 1 focused final re-review — pass with native limitations

Date: 2026-10-25. Independent reviewer: `/root/plugin_reviewer`.
Verdict: **pass for revised implementation and available offline engineering**.
R1-FINAL-01 through04 resolved. Full locally reproduced native compatibility/model
completion remains **blocked/unverified**, not passed. No further blocking code
findings in this focused review.

Reviewed actual repaired runner/reducer/probe/selector logic, CLI propagation,
updated skill/README, correction design/tests and saved red/green/affected logs.
Reused existing recorded tests instead of repeating completed suites. Independently
ran `git diff --check` successfully. No native/model/client execution, broad
research, commit or push by reviewer.

- R1-FINAL-01: required trusted expected_case is validated before launch and passed
  from each fixed CLI case. Positive pass requires complete, correlated evidence,
  domain execution and source request evidence. Actual supported pending returns
  incomplete. Unrelated requires no activation/source work; missing-grant requires
  selected-server discover/extract permission_denied provenance. Zero-execution
  or wrong-case summaries no longer satisfy positive success.
- R1-FINAL-02: `_clean_supervision` requires exit0, explicit no timeout/termination,
  empty diagnostics and verified group cleanup. All3preflight stages check this
  before consuming stdout, retain sanitized stage supervision and stop immediately.
  Recognized text cannot erase an unsafe probe result.
- R1-FINAL-03: four actual harmless controlled child tests now exercise malformed
  stdout, combined stdout/stderr cap, seventh tool and unexpected tool while alive.
  They assert diagnostics, termination/reaping, group verification, byte cap and
  finite watchdog/cleanup. These are real supervisor mechanisms, not model/Bash
  execution or native success. SC15b separately covers normal parent exit with
  owned descendants; indirect zombie observations remain accurately labeled.
- R1-FINAL-04: skill/oracle explicitly reject original single encoded slash or
  backslash, then residual encoding/backslash/dots; direct discriminator tests
  preserve unreserved encoded product text unchanged. Empty-state stop remains
  distinct from nonempty/no-qualifying candidate output. Query-only ToolSearch is
  explicitly limited/unverified for optional fields, without a universal native
  payload claim.

Saved correction result28passed/4.52s follows20intended failures/8already-green
checks. Latest affected result219passed/1native skip74.39s is supported by its
saved log; outer driver exit0/no timeout/no diagnostics, direct child reaped,
group disappeared and0indirect zombies. This is affected verification, not a full
repository CI or native pass. No redundant broad suite was needed.

Prior G1/G2/G3 and focused correction design still apply: production remains
instructions/assets around unchanged core CLI/runtime/MCP; source bootstrap
guidance is not fresh-install proof; default paths do not infer or provision
credentials/permissions. Reported cloud2.1.310/sonnet5-5 wrappers and separate
real-config5tool startup stay attributed and distinct from unavailable raw bundle
and local1.0.35 one-version-probe blocker. Locally0model calls, pending asynchronous
work and optional listing/payload limitations remain explicit. Do not describe all
host bugs or full native integration as verified solved.

Coordinator may hand off/update focused PR89 evidence with these limitations.
Broader #73/#74 and other ecosystem work remain outside delivery; native-required
completion still awaits eligible normal-access host observations.

| Reviewed final artifact | SHA-256 |
| --- | --- |
| tests/claude_code_host_smoke.py | 7e3d9f42908b2d18b2e4693558ff8d782fe637180ebb384d51910f6ff1a64d2a |
| tests/claude_code_recipe.py | c3a21203045afacc646526cfb0494fd7b48ad8c28952dcdda1203204c33d0e90 |
| tests/test_claude_code_review_repairs.py | b3a1e1d7c6ccf910fbb9fe16e3c3f349adbb75afbb4d35099cce75f6d3294a8b |
| package README | 79c88d450e67b93816efc422ebafb8958652d5e1a913c6cbf8b14d4368127a0f |
| skill | a818009d84e4f6fbac9530c28fd91907addbe77af44b560929b6638ee648b921 |
| revision-1/final-review-green.txt | 5f20dbc7c52999c4e4e3f7c264935403b54f6c8261104db42e0621516968600c |
| revision-1/final-affected-regressions.txt | 811e4ecd46e0d729694970811968248c1d7be8b722e94207a2b38b1178c58bad |
| revision-1/final-affected-driver.json | 8cbbe8e03b55dc715052405c2f4230ec9450b01ef2c11a2c1109c30dd8421fbf |
