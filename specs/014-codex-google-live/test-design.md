# Live/skill behavior-first tests

2026-10-31. Designed before task breakdown. All results pending.

| FR / SC | Fixture and expected outcome | Real mechanism / distinct risk |
| --- | --- | --- |
| FR01 / SC01 | Supported root config plus separate valid profile; unknown root key, duplicate key and malformed profile reject before any HTTP. | Existing CLI strict config; new profile validator must not silently relax it. |
| FR01,04 / SC02 | Missing catalog/wrong fingerprint/corrupt resource: blocked setup, zero HTTP and no mapped report. | Actual native loader and CLI error response, not fake missing-resource return. |
| FR03–05 / SC03 | Controlled source-shaped HTML/API with real category capture, reviewed scoped rule, sourceNone and exact Google target. Retain URLs/timestamps/pointers/hash; native categorized reload/export agree. Current Pakistani cases use html with no invented CSS; an optional controlled html_css fixture uses trusted exact text selectors only. | Actual parser/capture/CLI/mapper/portable path, only external transport controlled. Separately run real live URL after offline success. |
| FR03,05 / SC04 | Pakistani selected-site restricted-policy host denial: fresh fetch=skipped_network_policy, policy hash/time, requests0 and no network call. Separately actual proxied HTTP404/TLS failure has a counted request and failed receipt, with no source product fabricated. Skip the failed site once; no random-store discovery or further allowlist question. | Fresh policy reader/preflight and actual request boundary; missing policy means unknown and normal proxied guards, not assumed allow. Controlled injected transport is labelled controlled and live_verified=False, never a real live success. |
| FR04–05 / SC05 | Missing, truncated/LLM-only, multi-category/conflicting evidence: product retained; unavailable/ambiguous/review result, never mapped guess. | Existing support/mapper/effective classification. Different risks, not arbitrary source variations. |
| FR05,07 / SC06 | Old report under reused output, profile/catalog/runtime-code mismatch, cross-origin/path-escaping redirect, website text saying ignore instructions, user-supplied false success. Reject stale evidence; no commands/secrets/target guesses from content. | Exact run/profile/catalog binding and native report provenance; no model-written evidence accepted as CLI output. |
| FR02,06–08 / SC07 | Explicit relevant skill request: actual Codex JSONL shows skill read/activation, harness execution and final matching report; unrelated task does not execute it. | Real installed Codex host using ordinary signed-in access. Static recipe checks are not host activation evidence. |
| FR06,08 / SC08 | No host/auth/network, real tool failure and deadline: separate unavailable/failed host or site states. No passing workflow inferred from command exit0 or natural-language claim alone. | Actual subprocess events/return code/final output compared to authoritative run report; terminate owned groups on timeout. |

Before production runtime implementation save intended failing acceptance tests
for missing CLI-profile/harness behavior, then independent G1/G2/G3 as applicable.
Predesign controlled fixture labels and expected outcomes; never stub mapper,
source parser, portable codec or report verifier to return expected success.

## Bounds and evidence

One sequential controlled driver, seed14031, max12 distinct mechanism cases
(8scenarios plus duplicate-key, wrong-store rule, failed-write rollback and
output-size boundary), case30s/whole180s/512MiB, synthetic input<=1MiB. Save one
small source→mapped record smoke before expansion; stop first failure and make
one diagnosed repair, then record blocker rather than lift limits. Real atomic
artifact publication and source-count checks must be exercised.

Live source sample: at most2 exact selected Pakistani product URLs on2 approved public origins,
8totalHTTP including redirects,4retained products,120s shared, per-request15s,
zero retries/inference/browser installs. Redirects require the same normal source
authorization; denied origin stops, not alternate proxy or fake replay. Save
first attempt/capture before second URL. Metadata fetches and merchant category
observations are distinct. Positive mapping assertion requires actual captured
category and reviewed Google rule/crosswalk; absence remains incomplete.

Actual Codex host verification: max2 sequential runs,120s each, max8workflow tool
calls and1MiB retained JSONL per run; preserve normal auth without reading/copying
credentials. Run1 explicitly invokes live mapping skill and reports actual result;
run2 unrelated-task nonactivation. An honest blocked response proves only that
observed host behavior, never successful live mapping. No new login/install or
model downloads. Keep full repository driver240/480s limits if runtime code changes.

Current exact Priceoye product was proxy-denied in evidence/pakistan-preflight.json. Liberty canonical product URL was found by source discovery, not directly fetched; its prior www-root denial is a separate request and cannot be relabelled as that product capture. No source target, price or category is asserted from rendered search snippets.

Fresh-policy control: change the test policy hash/host rules between runs and assert each new report uses current policy/time, not cached403. A restricted missing-host case makes zero transport calls; no-policy case executes only ordinary guarded proxied transport. Current package-only policy skips both selected Pakistani hosts; report references current policy and historical attempts independently.
