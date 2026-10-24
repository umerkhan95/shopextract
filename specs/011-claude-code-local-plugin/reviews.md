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
