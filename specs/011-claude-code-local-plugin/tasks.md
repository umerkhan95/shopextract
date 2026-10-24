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
