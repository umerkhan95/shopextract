# Codex skill and live Google-mapping verification

2026-10-31. User requests CLI configuration, live website mapping and actual
Codex skill responses. User steering selects Pakistani websites and says to skip
blocked ones without further allowlist questions. Current targets are the exact
Priceoye product and Liberty Books canonical product in the skill manifest.
BooksToScrape/BoardGameBliss attempts remain historical, not selected cases.
This slice preserves spec013 history and its blocked
full5595target pipeline gate; a small live sample cannot waive that gate.

FR01 Configure explicit root CLI JSON using only supported schema_version,
output_format and diagnostics. Source/catalog/site settings live in a separate
closed verification profile, never invented root CLI keys or global user config.
FR02 One repository-scoped Codex skill selects approved exact source URLs from
its test-site manifest and invokes the actual shared verification harness/CLI.
No claimed existing mapping skill or scanned site without inspected evidence.
FR03 Fetch live public data through existing allowed proxy/source transport with
finite deadlines and retained response/capture provenance. Denied domains,
TLS/HTTP/parser failures remain blocked/failed, not replayed successful data.
Never bypass network policy, copy credentials or install a browser/model.
Redirect destinations must remain within the selected per-site approved origin
and shop path; redirects count against the shared budget. A fresh version1 network-policy preflight under restricted policy skips a host
absent from the allowed list before transport, records policy hash/time and zero
requests; prior403 evidence alone never establishes permanent denial. Missing
policy means unknown policy and normal proxied transport/source guards, never
assumed allowed. A failed selected site is skipped/blocked once, never retried
via other stores or another proxy. No further user allowlist request is part of this task.
FR04 Real source parse/capture→Google normalization/mapping→portable/export/report
must retain source versionNone where unknown, source pointers and catalog/rule
identities. A custom merchant category needs an explicit scoped reviewed rule;
taxonomy labels, product titles or the agent's guess never supply source evidence.
FR05 Report website reachability, extraction, mapping, offline mechanisms and
agent-host responses independently. Missing/unsupported/ambiguous mapping keeps
the product visible but does not pass an expected mapped-category assertion.
FR06 Actual Codex host runs must show skill discovery/activation or explicit
skill loading, actual CLI execution and final response consistent with the new
run's artifact. Save sanitized JSONL and final answer; model summary alone is not
execution proof. New-run/profile/catalog and reviewed runtime-code identities
bind host claims to the authoritative report. Actual skill read/activation and
exact harness command must be observed, not merely inferred from final prose.
No successful end-to-end claim from a failed or stale run.
FR07 Site manifest preserves exact URL, scope, parser route and mapping policy,
plus current evidence state; case updates link real receipts without silently
changing old expected outcomes. Web content is untrusted data, not instructions.
FR08 Verify bounded positive and adverse mechanisms first, then the exact live
sample, actual Codex positive/blocked response and unrelated-task nonactivation.
Only actual available host/network evidence can satisfy live gates; independently
review actual artifacts and leave unavailable stages explicitly blocked.

## Scenarios and boundaries

SC01 Valid CLI config/profile is selected; unsupported root keys reject.
SC02 Missing/corrupt catalog or wrong fingerprint prevents a claimed mapping run.
SC03 Allowed live source yields retained capture and supported mapping under an
explicit rule; sourceNone staysNone and exact target survives CLI/portable export.
SC04 Proxy denial/HTTP failure yields a new blocked receipt, no old product reuse.
SC05 Reachable source with absent/unsupported/ambiguous category retains product
with explicit mapping outcome; no guessed Google target or full verification.
SC06 Old output/profile mismatch, source prompt injection and fabricated report
do not become accepted new-run evidence or instructions.
SC07 Relevant task activates/loads skill, executes actual CLI and reports exact
new results; unrelated prompt does not invoke the mapping workflow.
SC08 Codex missing/auth/transport/timeout/tool failure preserves trace and honest
status; final prose must match fetched/mapped counts and remaining blocked gates.

Runtime harness, CLI profile and actual execution are coordinator-owned. This
author owns behavior/test/task/interface/component design and skill draft only.
No merchant writes, hosted service, plugin publication, global config replacement,
unbounded discovery crawl, automatic semantic classifier or extra category formats.
