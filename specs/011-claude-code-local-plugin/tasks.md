# Dependency-ordered tasks

Behavior/scenario coverage above was checked by author/task breaker before this list. All FR01..07 map to SC01..08; implementation is not authorized by this document alone.

- [x] T01 #82, FR01..07/SC01..08, author: write spec/test design from reviewed parent scope; evidence: spec.md and test-design.md authored before this breakdown.
- [x] T02 #82, FR02/07, author/researcher, depends T01: save small baseline, inspect existing server/test seams and exact official manifest/discovery/MCP facts; evidence: research.md, evidence/baseline-smoke*.txt. One diagnosed PYTHONPATH repair; no sweeps.
- [x] T03 G1, independent reviewer, depends T01/T02: review all behavior/tests/tasks/research/plan; save artifact digest, blocking findings and verdict in reviews.md.
- [x] T04 #82, FR01..07/SC01..07, author, depends G1: skeleton.md plus missing-package acceptance assertions in tests/test_claude_code_plugin.py and tests/test_claude_code_workflow.py; save intended red logs in verification.md. No production package yet.
- [x] T05 G2, independent reviewer, depends T04: verify parser/process interfaces, fixture boundaries and failure-path reachability.
- [x] T06 #82, FR02..05, author, depends G2: components.md reuses existing tools CLI, MCP serve/SDK and fixture transport; justify any new helper and refine skeleton.
- [x] T07 G3, independent reviewer, depends T06: review ownership/reuse/lifecycle; save verdict before production implementation.
- [x] T08 #82+#74 Code subset+#73 recipe subset, FR01..06/SC01..08, author, depends G3+saved intended red: implement integrations/claude-code manifest, .mcp.json, single instructions-only skill and README private setup/lifecycle guide. No new runtime launcher or production package validator by default.
- [x] T09 available offline checks #82, FR01..07/SC01..07, author, depends T08: real native parser positives/negatives, package safety inventory, real direct CLI config launch and SDK/MCP deterministic mechanisms; affected tool regressions and repository required checks. Save versions/commands/results/fixture seed and coverage in verification.md; don't count optional skips as MCP passes. Available mechanisms passed (147 affected regressions plus supplemental checks); actual native parsing remains separately blocked below.
- [ ] T10 #82, FR06/07/SC08, author, depends offline green: attempt one isolated private host smoke then bounded fixed prompts/update/disable only with normal access; save observed/blocked status separately. No credential-copy workaround or new provisioning.
- [x] T11 Final independent engineering/offline reviewer: complete diff, designed cases, refinements and blocked native/live limitations reviewed; no blocking code findings (reviews.md).
- [x] T12 Coordinator delivery: update #82 with narrow #73/#74 subset evidence without closing broader tickets; open/attach focused draft PR; check branch/commit/PR/labels/author policy.

- [ ] T09-native #82 FR07/SC01/07: actual compatible native parser and native-negative matrix BLOCKED. Strict actual CLI rejects --strict; one plain repair requires /login. Recorded attempts, not a parser pass; no further retries/install.

T10 status: preflight attempted honestly, host activation/lifecycle BLOCKED by normal isolated authentication. Fixed prompts not sent. T11 final engineering/offline review passed; T12 delivered draft PR #89 and #82 evidence comment; #82/#73/#74 remain open. Historical planning parent PR remains open; no other ecosystem tickets started.

## Revision 1 tasks (2026-10-25; behavior/test design written first)

Original completed items remain historical. FR08..14 and SC09..15 revise the existing PR #89 slice; prior gate approvals do not authorize these changes. Coverage checked by author/task breaker: each new FR maps to a scenario including its adverse state. No library/core edits.

- [x] R01 author/task-breaker, FR08..14/SC09..15: append revised spec/test contract before this task breakdown. Evidence: revision sections in spec.md/test-design.md; scope exclusions explicit.
- [x] R02 researcher, depends R01: save one small baseline first and refresh only exact official schema discovery/CLI/manifest facts; inspect existing source-bootstrap implementation. Evidence: evidence/revision-1/baseline.json and research.md revision. No package/core edits or inference.
- [x] R03 independent G1 reviewer, depends R01/R02: review revised behavior/tests/tasks/research/plan and report attribution, timing/accounting ambiguities; save actual digest/verdict in reviews.md.
- [x] R04 author, depends revised G1: revise skeleton/test interfaces and write executable intended reds for domain/schema accounting, candidate choice/no-product message, nested native report and host-trace detector, source bootstrap/troubleshooting docs. Save red evidence. No production fixes yet.
- [x] R05 independent G2 reviewer, depends R04: check source/stream boundaries, immutable package fixture override, real async phase scheduling, limit supervision and test reachability.
- [x] R06 author, depends revised G2: revise components.md; reuse existing CLI/runtime/SDK. Clarify ToolSearch parser/classification, URL selector, source fixture and native subprocess/trace ownership. No new production framework.
- [x] R07 independent G3 reviewer, depends R06: review updated reuse, package asset safety, fixture provenance and model-versus-mechanism distinction.
- [x] R08 author, FR08/09/10/SC09/10/11, depends revised G3+saved reds: update trusted skill and test-side recipe/fixtures with explicit schema preflight and separate counters; deterministic product-only candidate choice; honest unsynchronized pending. Preserve synchronized SDK mechanism trace label.
- [x] R09 author, FR11/12/13/SC12/13/14, same dependencies: correct source-bootstrap setup, native nested report handling, optional icon/marketplace warnings, user-reported2.1.310/local1.0.35 attribution and reported inherited skip-flag diagnosis. No fake marketplace/public publication or auto-install.
- [x] R10 author, FR14/SC15, same dependencies: implement explicit opt-in `claude -p --plugin-dir` stream-json harness with supported limits, request evidence and separate host/domain counters. Parser/supervisor fixtures run offline; native inference defaults skipped and unavailable access recorded blocked.
- [x] R11 author, depends R08..10: small saved focused smoke, deterministic selection/redirect/finite-delay cases, native-report/stream adversarial corpus and affected regressions. One diagnosed repair per blocker; no broad suite/model sweep. Save actual outcomes and resource/counter limitations.
- [ ] R12 author, depends offline green and normal access/clear supported caps: at most3prompts, six domain calls/two products/120s each sequential; no login/new client/credential copy. If prerequisites unavailable, save blocked host status, retain user-reported observations separately.
- [x] R13 independent final reviewer, depends R11/R12: inspect revised diff/evidence/attribution and resolve findings; coordinator updates only PR89/narrow related issue evidence after naming/author/label checks. No commits/push during current design assignment.

Current revision: R08..R10 implemented; R11 prior affected191passed/1native skip69.03s; focused corrections28passed4.52s and latest affected219passed/1native skip74.39s; R12 locally blocked before inference (version1.0.35,0model calls), with cloud evidence only user-reported/uninspected. R13 review findings were resolved by F01..F04; final engineering/offline re-review passed. Historical original tasks above are not new revision verdicts.

## Focused final-review corrections (current)

- [x] F01 author FR15..18/SC16..19: design/test/skeleton/components before repair; intended red20failed/8passed4.73s in final-review-red.txt; actual controlled boundary checks executed.
- [x] F02 independent focused affected G1/G2/G3 review: case/outcome binding, probe supervision authority, encoded URL policy and real supervisor coverage.
- [x] F03 author after F02: implement bounded narrow repairs against saved reds, align docs/existing call sites and rerun only justified focused/affected checks. No native/model/client install.
- [x] F04 independent final engineering/offline re-review passed (reviews.md); coordinator delivers through existing PR #89.

R13 original final revision review returned changes required (reviews.md). Prior available191passes remain historical; F01..F04 now govern the next work. No author commit/push.

F02 focused affected G1/G2/G3 passed; F03 implemented with final-review-green.txt28passes and final-affected-regressions.txt219passes/1native skip74.39s. F04 final independent engineering/offline re-review passed.
