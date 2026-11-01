# Isolated main integration — 2026-11-01

Remediation492f89e cherry-pick onto origin/main319ee9b, isolated
fix/audit-remediation-main worktree. Preserves main#100 advertised native sitemap
traversal (12requests/20MiB/robots/scoping/category-map exclusions), #101 static
image/brand/SKU enrichment and listing categories. Guarded stream adapter keeps
one physical send per native traversal hop, reuses one robots fetch, forwards
native stop reason, and honors longest robots match. Shared HTML parser retains
main DOM enrichment with source-owned ImageObject leaf paths and avoids filling
an explicitly conflicting brand. No unmerged QuantityValue/fridge cache dependency.

Focused collection184cases1.55s. Critical upstream/discovery89passed8.44s;
remediation adapter/portable/HTML/frozen-export controls115passed6.61s. Earlier
83pass6fail and114pass1fail attempts retained in local/tmp logs, not represented
as passes. All eight conflicts resolved/staged; source/tests/README/CLI diff-check
clean. Pinned SIX XML CRLF bytes deliberately preserved (full artifact diff-check
reports whitespace in immutable source XML and two preexisting profile summaries).
No external HTTP/store test, full-driver rerun, continue/commit/push performed by
conflict author. Prior branch full/live evidence remains historical; latest full
gate pending also applies to this integrated source. Primary owns cherry-pick
continuation, commit/push and draft PR. Original workspace/specs012 untouched.

Review repair design: native traversal can retain positive URLs before budget
exhaustion. Record stop_reason before returning those URLs, without restarting
fallback. Regression uses actual robots/index/leaf parsers, MockTransport only,
lowered native request cap3: robots,index,first leaf accepted; second leaf not
sent. Assert retained URL AND native_sitemap_budget diagnostic/exact request list.
Regression failed on missing diagnostic0.33s before fix; native/discovery/CLI
focused59passed6.15s after reorder. Local logs /tmp/audit-native-budget-{red,green}.log.
No full/merchant run or cherry-pick continuation performed for this repair.
