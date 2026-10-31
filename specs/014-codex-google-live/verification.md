# CLI, Pakistani sites and actual agent response verification

2026-10-31. Existing Google implementation retained. User authorized CLI setup,
live website attempts, repo skill and actual agent-response tests, then steered
to Pakistani sites and requested blocked sites be skipped. No global settings,
authentication files, plugins, source permissions or credentials were changed.

## Actual evidence

| Layer | Observed result |
| --- | --- |
| CLI configuration | Strict root config `examples/cli/google-live-cli.json` plus separate closed profile `google-live-profile.json`; `taxonomy google verify-live`, convenience script and optional project root wired to shared package runtime. |
| Repository skill | `.agents/skills/shopextract-google-mapping/SKILL.md` and reference manifest added; initial foreign sites retired after user steering. Current candidates are Priceoye A16 and Liberty Atomic Habits product pages. |
| Actual source preflight | Initial Priceoye product and Liberty www-root CONNECT attempts were proxy403; canonical Liberty product was not fetched. See `evidence/pakistan-preflight.json`; do not claim the root denial was a product response. |
| Current-policy live workflow | Fresh run reads supported restricted policy, skips both selected merchant hosts with current policy digest/time and requests0. No retry, alternate proxy or fabricated product/category. |
| Controlled mechanisms |23tests passed, including actual structured/CSS parsing and DOM evidence, real native CLI normalization/export/portable reload, no-rule nonassignment, same-origin/escaped-path/public-IP guards, limits/duplicate config/rule semantics, report write failure and artifact hashes. Injected transport forces controlled mode/live_verified=false. Reds precede repairs. |
| Native Codex CLI | Actual0.163.0, signed-in eligibility. Native exec launched with literal skill prompt via stdin, JSONL and final schema, bounded118s+2s cleanup. Backend WebSocket/HTTPS proxy403 occurred before any command/skill use; stopped after46.814s.0command starts, no final model answer, unchanged identities, process group gone. Native activation and negative nonactivation are UNVERIFIED. |
| Existing Codex app agent | A separate actual orchestrated agent explicitly read the skill and ran exactly one real CLI workflow. Its actual answer and fresh report independently matched: blocked/live_verified=false,0requests/0products, both URLs policy-skipped and extraction/mapping not_run. Report/profile/runtime hashes match. Reported7shell calls are not native CLI JSONL evidence. |
| Unrelated agent response | Fresh orchestrated agent answered2+2 JSON without requesting workflow; this is an unrelated-response control, not native implicit skill-discovery proof. Parent recorded its actual final answer verbatim. |
| Complete repository checks | `python scripts/run_tests.py --output-dir build/google-live-ci`:1800passed (1670main+24oracle+106maintenance), zero failures/skips,115.99641s, original240/480s limits, no remaining owned groups. |

## Review and repairs

Independent G1/G2/G3 and Pakistan/fresh-policy amendment precede runtime code.
Nine genuine missing-API reds were saved first. Additional designed negatives
reproduced invalid Shopify root/policy bool acceptance, CLI artifact hash versus
stdout newline mismatch, semantic rules admitted before HTTP, duplicate CSS
fields, repeated escape and multicast guards, and installed-profile path base.
Narrow fixes reuse native option validation, public-address guard, source parsers,
mapper/binder/codec and existing CLI. Code/root/skill identities froze before
actual agent cases. Current23focused cases and full driver pass.

Native host supervisor reused tested repository `_cleanup` and temporary
subreaper, capped stdout/stderr1MiB and at most8command starts. Native case was
externally stopped upon known backend403; `positive.summary.json` reasonNone is
paired with `codex-stop-reason.json`, not misreported as a deadline. No second
native call against the same known block. A parent diagnostic checked only
nonsecret selected provider/model/MCP/hooks metadata after failure; no alternate
configured provider existed. No auth file was inspected/copied and no secret
values or global config were exposed/modified. Normal native CLI auth access is
not proof its backend can execute a model.

## Honest completion state

CLI/profile/skill code and controlled/reporting behavior are verified. Actual
orchestrated agent answer consistency is verified through the existing Codex app
runtime, explicitly file-based. **No Pakistani product mapping was verified live,
no native Codex CLI skill activation was verified, and all_live_verified=false.**
Both routes are network-blocked. User asked blocked sites be left alone, so no
random-domain sweep, permission question, proxy bypass or credential change was
used. The earlier spec0135595target native mapping/export gate remains separate
and blocked; these small cases do not waive it.

Main receipts: evidence/host-verification.json, orchestrated-positive.answer.json,
orchestrated-positive.report.json, positive.jsonl, positive.stderr.log,
codex-stop-reason.json and configured-ci-summary.json. Raw runtime artifacts stay
under ignored build/google-live and build/google-codex-host. Actual session token
counters unavailable; no quota estimate. No local model/browser download or run,
merchant write, commit/push/merge or public publication.
