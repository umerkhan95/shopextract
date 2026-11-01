# Draft PR delivery

2026-11-01. Delivery branch `fix/audit-remediation-main`, base `319ee9b` on
`origin/main`. Only the remediation commit was carried from the development
baseline; unrelated refrigerator commits and specs012 working edits are excluded.
Upstream #100 bounded sitemap discovery and #101 static enrichment/listing
category behavior are preserved. See integration-main.md and
integration-main-review.md for scoped independent review and regression evidence.

## Current integrated-tree validation
- 184 focused cases collected.
- 89 upstream/discovery/CLI checks passed in8.44s.
- 115 remediation adapter/HTML/portable/export compatibility checks passed in6.61s.
- A subsequently found retained-URL budget diagnostic regression failed first;
  after its narrow repair,59 related checks passed in6.15s and independent
  re-review passed. No merge/completion approval is implied.
- Current integrated full repository validation remains pending.

## Historical evidence and remaining gates
The earlier development tree had2229 passing tests before the compressed-response
repair. After that repair38 focused tests passed; its latest full run timed out
at239.16s. Those are historical observations, not a full pass for this PR tree.
Four one-request HTTP live checks passed on that development baseline. Khaadi
discovery remains inconclusive and browser live accounting remains blocked.

The original final-source-manifest.json describes the pre-integration development
tree. delivery-source-manifest.json records this delivery tree separately.
Verbose logs and binary profiling data remain local in the original workspace;
compact reports, reproduction commands, tests and engineering review documents
are committed. Pinned registry XML bytes retain their original line endings and
hash; path-specific Git attributes preserve those evidence bytes.
