# Dependency-ordered tasks

Task-breaker: integration_author, 2026-10-24. Coverage check: FR-01..24 and
SC-01..24 each map below. All runtime tasks remain unchecked; existing #24/PR54
is a reuse prerequisite, not a reopened implementation task. Independent review
of distinct cases remains required. Current author also researches; reviewer differs.

| Ticket | Deliverable / owner | Dependencies | FR / SC | Future completion evidence |
| --- | --- | --- | --- | --- |
| INT-01 | Shared HTTP/durable jobs; service author | #24 delivered; own G1/G2/G3/red tests | FR02,04,13,14; SC02,03,04,12,13,14 | API schemas, red/green, crash/replay/ownership/budget checks, owned HTTPS smoke |
| INT-02 | Remote MCP/auth; security/MCP author | INT-01; #24 reused | FR03,04,13,14; SC03,04,06,13,14 | OAuth isolation/transport checks and remote live session |
| INT-03 | n8n node; connector author | INT-01 | FR05,04,14; SC05,04,14 | Native node package/tests, private action/trigger evidence |
| INT-04 | Claude compatibility; MCP author | #24 local; INT-02 remote | FR06,03; SC06,03 | Separate local/remote actual-client runs |
| INT-05 | ChatGPT MCP app; MCP author | INT-02 | FR07,03,15; SC07,03,15 | Private app tool/consent evidence; separate public submission record |
| INT-06 | OpenAI Responses integration; SDK author | INT-02 MCP route; INT-01 function route | FR08,04,14; SC08,04,14 | Both documented routes, bounded orchestration tests and API smoke |
| INT-07 | Zapier integration; connector author | INT-01 | FR09,04,14; SC09,04,14 | CLI/private version, auth/action/poll/dedup tests/live |
| INT-08 | Make app; connector author | INT-01 | FR10,04,14; SC10,04,14 | Private modules, bundle/pagination/poll tests/live |
| INT-09 | Pipedream components; connector author | INT-01 | FR11,04,14; SC11,04,14 | Actions/source package, checkpoint/replay tests/live |
| INT-10 | INT-10a approved recipe definitions; INT-10b compatibility/release; integration author | 10a: reviewed spec/tool contracts; 10b: implemented INT-01..09/11..25 per enabled row | FR01,12,15; SC01,12,15 | Capability-gated recipes, version matrix, private versus published statuses |
| INT-11 | Portable skill pack; skill author | INT-10a approved recipe subset; #24 local OR INT-01/02 remote | FR16,18; SC16,18 | Trusted instructions, capability manifest, package checks |
| INT-12 | Claude skills; skill author | INT-11, INT-04 | FR17,18; SC16,17,18 | Local/team/API routes separated, activation/update evidence |
| INT-13 | ChatGPT skill/plugin support; skill author | INT-11, INT-05 | FR17,18; SC16,17,18 | Actual supported host route, no Knowledge/Actions conflation |
| INT-14 | Codex skills; skill author | INT-11, INT-02 or local #24 | FR17,18; SC16,17,18 | User/workspace discovery and MCP config evidence |
| INT-15 | Cursor skills (deferred wave); skill author | INT-11, remote/local tools | FR17,18; SC16,17,18 | Scope/install/discovery and negative activation |
| INT-16 | Copilot skills (deferred wave); skill author | INT-11, supported MCP route | FR17,18; SC16,17,18 | Supported client matrix/install evidence |
| INT-17 | Gemini CLI skills (deferred wave); skill author | INT-11, supported MCP route | FR17,18; SC16,17,18 | CLI install/enable/discovery and update evidence |
| INT-18 | Grok/xAI tool/plugin adapter; provider maintainer | 18a:#24local or INT-01/02remote;18b:18a+11/19 | FR19; SC19,03,04,13 | Source-supported API path, native/UI support separated |
| INT-19 | Grok skill compatibility/wrapper; skill maintainer | INT-11;18a or#24local, not18bplugin | FR19,16,18; SC19,16,18 | Native support proof or explicit application wrapper/unsupported |
| INT-20 | Anthropic Code plugin packaging; plugin maintainer | INT-04/11/12 | FR20,17,18; SC20,16,17,18 | Manifest/skill/MCP discovery and private lifecycle |
| INT-21 | Meta Muse plugin/tool mapping; provider maintainer | 21a:#24local/INT-02remote;21b:21a+11/22, manifest unresolved | FR21; SC21,03,04 | Consumer Muse/Code/API separate, unsupported states honest |
| INT-22 | Meta Muse skill compatibility/wrapper; skill maintainer | INT-11;21a or#24local; no21bdependency | FR21,16,18; SC21,16,18 | Documented native loader or application wrapper only |
| INT-23 | Mistral Vibe/Le Chat/API skill-plugin mapping; provider maintainer | INT-11, selected documented tool route | FR22; SC22,16,18 | Target-specific loader/MCP/API evidence |
| INT-24 | GLM/Z.ai host/API skill-plugin mapping; provider maintainer | INT-11, documented coding host/tool route | FR23; SC23,16,18 | Entitlement versus actual host loader contract |
| INT-25 | Hermes Agent skill/tools/plugin route; agent maintainer | INT-11, Nous runtime/tool route | FR24; SC24,16,18 | Real agent native schema/discovery, not model-only |

Current planning work:

- [x] P01 Author behavior/test design before breakdown; saved spec.md/test-design.md.
- [x] P02 Task-breaker coverage check above; no omitted FR/SC. Independent edge review passed; see reviews.md.
- [x] P03 Bounded official research and issue-ready twenty-five ticket bodies; source register.
- [x] P04 Expanded-scope G1 independent review passed; historical verdicts retained in reviews.md.
- [x] P05 Expanded-scope G2 declaration review passed. No runtime stubs/red claims.
- [x] P06 Reuse/component document authored; independent G3 passed.
- [x] P07 Documentation checks and independent final content review passed; EPIC #62 and 25 native sub-issues created and mapped in issue-map.md/json. Documentation PR delivery is recorded separately by the coordinator.

Each future child must execute this sequence independently; the epic is not one
unchecked implementation block:

- [ ] Child behavior/test design and distinct-risk inventory reviewed; preserve traceability.
- [ ] Child production research recheck exact limits/versions; G1; skeleton and executable acceptance tests fail for the intended missing mechanism, saved red evidence; G2.
- [ ] Reusable components and affected interfaces reviewed at G3 before production logic.
- [ ] Implement one bounded child slice against tests, then real-path offline acceptance/regressions.
- [ ] Fixture author serializes the44predesigned family/variant cases from test-design.md into exact fixture/assertion manifest before generation; no executed corpus is claimed.
- [ ] Fixture author builds deterministic factories with predeclared expected results; independent reviewer verifies realism and uncovered interactions before stress execution.
- [ ] Verification author runs one saved smoke then sequential mechanism/stress driver (test-design.md); record seeds/config/counts/minimal failures and fault-detection evidence.
- [ ] Bounded live private compatibility after offline success; missing access is blocked, unchanged commercial transitions are inconclusive; synthetic mechanisms remain mandatory.
- [ ] Independent final reviewer checks diff, truth of evidence, secrets, versions, distribution readiness and unresolved limitations; publication is separately authorized and externally reviewed.

#27 owns signed outbound push/delivery/dead letters and merchant writes; polling
connectors do not depend on merchant-write approval. #26/#27 contracts are links,
not duplicated scope. Owner roles become named maintainers when assigned. Planned
checks do not count as completed research, runtime implementation or public listing.

Provider expansion is user-authorized after baseline G1/G2; revise behavior/tests
first (done), then bounded official research/new ticket bodies, then affected G1/G2
before G3/final. Preserve earlier40sources; add at most8xAI/Anthropic and4Meta pages,
no installs/runtime/publication. INT-10b consumes only enabled implemented new rows.

Latest expansion: INT-23..25 bounded primary research max3pages each after behavior/test
revision; preserve51prior sources, total cap61. INT-21/22 Meta optional/deferred. Current
scope only docs/tickets. Next-session handoff recommends single local Claude Code
plugin+skill slice reusing#24; do not start it or require INT-01/02. Affected G1/G2 then
G3/final must review expanded documentation; historical passes retained.
