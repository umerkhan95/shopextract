# Compatibility and delivery matrix

As of2026-10-24. This matrix records researched construction paths, not achieved host
compatibility. `DOC` means planning documentation authored; independent final is pending.
`NOTRUN` means not exercised in this documentation task. `PENDING` means future work.
Existing local #24 is delivered software, not proof of actual Claude/Codex/etc client
compatibility. Version/account/source refresh is required before every implemented row.

| Ticket / target | Documentation route | Implementation state | Real-path mechanism/stress | Private host live/install | Public submission / acceptance |
| --- | --- | --- | --- | --- | --- |
| INT-01 HTTP/jobs | DOC: owned durable API/journal | PENDING; current local jobs ephemeral | NOTRUN | NOTRUN; owned HTTPS/storage/identities needed | N/A platform directory; optional service release PENDING |
| INT-02 remote MCP | DOC: OAuth/shared service, protocol candidate conditional | PENDING; current server stdio only | NOTRUN | NOTRUN; provider/host negotiation needed | N/A single directory; host rows separate |
| INT-03 n8n | DOC: native HTTP action + programmatic poll | PENDING | NOTRUN | NOTRUN; private node rights/versions needed | npm/verification PENDING / not accepted |
| INT-04 Claude local | DOC: Desktop and Code stdio routes | Reuses delivered #24; host setup PENDING | Existing #24 history separate; new row NOTRUN | NOTRUN; exact client/Python/operator config needed | N/A local config; directory listing not claimed |
| INT-04 Claude remote | DOC: account connector via cloud network | PENDING INT-02 | NOTRUN | NOTRUN; account/network/OAuth needed | Optional listing PENDING / not accepted |
| INT-05 ChatGPT | DOC: MCP/private plugin route | PENDING | NOTRUN | NOTRUN; workspace/account/OAuth needed | Package/review PENDING / not accepted |
| INT-06 OpenAI MCP | DOC: remote API MCP route | PENDING | NOTRUN | NOTRUN; exact model/tokenizer/pricing/key needed | N/A API example; repository release PENDING |
| INT-06 OpenAI function | DOC: application dispatch/continuation | PENDING | NOTRUN | NOTRUN; ≤5request budget and model preflight | N/A API example; repository release PENDING |
| INT-07 Zapier | DOC: CLI actions/completion poll | PENDING | NOTRUN | NOTRUN; developer/private connection needed | Public promotion/review PENDING / not accepted |
| INT-08 Make | DOC: connections/modules/completion poll | PENDING | NOTRUN | NOTRUN; custom-app/scenario access needed | Invite publish PENDING; catalog approval PENDING |
| INT-09 Pipedream | DOC: actions/timer source/checkpoint | PENDING | NOTRUN | NOTRUN; private component/deploy rights needed | Private publish and public distribution PENDING |
| INT-10 recipes/release | DOC: a definitions, b runtime recipes/matrix | PENDING executables | NOTRUN | NOTRUN per enabled platform | Per-row pending, no blanket release claim |
| INT-11 portable skill | DOC: instructions-only pack/safety | PENDING; no SKILL.md built | NOTRUN | NOTRUN; host/tool route required | Versioned directory/ZIP PENDING |
| INT-12 Claude skills | DOC: product ZIP, Code dirs, Managed Agents separate | PENDING | NOTRUN | NOTRUN; per-store rights/version/tools needed | Personal/team/API rollout PENDING; no universal sync |
| INT-13 ChatGPT skills | DOC: real plugin skill support verified in sources | PENDING | NOTRUN | NOTRUN; eligible plugin/skill surface needed | Plugin submission/acceptance PENDING |
| INT-14 Codex skills | DOC: repo/user .agents/skills, tools separate | PENDING | NOTRUN | NOTRUN; exact local/cloud surface needed | Repo/package rollout PENDING; no directory acceptance assumed |
| INT-15 Cursor skills | DOC; deferred implementation wave | PENDING/deferred | NOTRUN | NOTRUN; local/cloud/SSH tested separately | Distribution PENDING |
| INT-16 Copilot skills | DOC; deferred implementation wave | PENDING/deferred | NOTRUN | NOTRUN; client/cloud tool access needed | Repo/package rollout PENDING |
| INT-17 Gemini CLI skills | DOC; deferred implementation wave | PENDING/deferred | NOTRUN | NOTRUN; trust/CLI/tools required | Directory/extension rollout PENDING; web/API N/A |
| INT-18 Grok Build plugin | DOC: native plugin/skill+MCP route verified | PENDING | NOTRUN | NOTRUN; parser/version/owned profile needed | Marketplace PENDING |
| INT-18 grok.com/xAI API | DOC: custom MCP consumer/API, separate formats | PENDING | NOTRUN | NOTRUN; auth/consent/model needed | Consumer connection not catalog approval |
| INT-19 Grok skills | DOC: Build native affirmative, API wrapper separate | PENDING | NOTRUN | NOTRUN; native consumer skill loader unverified | Build distribution PENDING |
| INT-20 Anthropic plugin | DOC: Code manifest+skill/MCP; local next-session priority | PENDING/NOT STARTED | NOTRUN | NOTRUN; clean local Code profile/#24 | Marketplace/organization rollout PENDING |
| INT-12 Messages skills addendum | DOC: code-execution container, no network | PENDING | NOTRUN | NOTRUN; model/container rights and app-fetched input | Separate API store; no product sync |
| INT-21 Meta plugin/tool | DOC: Code MCP verified, exact plugin manifest unresolved | OPTIONAL DEFERRED; plugin packaging blocked on contract | NOTRUN | NOTRUN; personal Muse/API distinct | Unknown native/public contract |
| INT-22 Meta skill | DOC: Code native verified, personal consumer loader unverified | OPTIONAL DEFERRED | NOTRUN | NOTRUN; Code skill route can proceed without plugin | Distribution PENDING; no consumer claim |
| INT-23 Mistral | DOC: Vibe Code native skills/experimental plugin | PENDING | NOTRUN | NOTRUN; exact version/trust/reload | Work/API separate; catalog PENDING |
| INT-24 GLM/Z.ai | DOC: provider MCP+external Code host; ZCode loader unknown | PENDING | NOTRUN | NOTRUN; entitlement/model/host prerequisites | Native ZCode/catalog unverified |
| INT-25 Hermes Agent | DOC: native skills/MCP plus portable/native plugins | PENDING | NOTRUN | NOTRUN; runtime/parser/namespace needed | Catalog PENDING; model-only N/A |

General export/analytics/validation/category/maintenance and fresh-capture commerce
monitoring integration capabilities are DEFERRED, not available by virtue of this
matrix. Completed-job polling does not prove a live price/stock transition. Public
marketplace rejection/acceptance has not been attempted. Missing prerequisites are
listed without claiming an actual failed live test or presuming account entitlement.

Current documents identify Python3.10 support/current optional MCPv1 in existing core;
new ASGI/framework/schema/protocol/native package/host version pins are not established.
INT-06 budgets and source60page snapshot are dated planning evidence, not permanent
platform quota promises. All actual future row evidence must cite exact versions,
commands, counts, date and saved sanitized outputs in child verification.md.

Expanded25ticket/24FR/24SC revision awaits affected G1/G2 then G3/final; baseline
passes remain historical. No current row is implemented or live-passed by docs.
