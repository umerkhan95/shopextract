# R4/R5 components and ownership

Reuses _discover platform API strategies, XML parser, filters, existing Platform,
CLI response schema and GuardedTransport authority. No new public model/export.

_discovery_runtime.DiscoveryURLs is list-compatible; copied unique reasons start
with discovery_coverage_unverified, request_count records actual guarded HTTP.
DiscoveryClient borrows AsyncClient and never closes it. It owns one operation's
origin/robots cache/request count, GET/request delegation with explicit manual
redirects, streamed response/body limit and diagnostics. Bootstrap robots bypasses
its own policy check only, still consumes request/byte budgets. Missing404 permits;
auth-denied and unavailable fail closed. Same origin only, max5 redirects. Native
tool uses this wrapper over its existing authority transport, never bypassing it.
Tool failures retain its standard errors; blocked emitted URLs add diagnostics.

bounded_sitemaps owns bounded FIFO/visited identity sets, existing defused parser,
5000 queued locations and max1000 outputs. Platform-specific paths then root
sitemap; nested indexes/cycles cannot cause unbounded traversal. Unavailable native
API falls back through same wrapper; no browser/SDK private network in this bounded
profile. Private explicit legacy browser function stays lazy and otherwise unchanged.

run_discovery_worker owns exactly one child process group, stdin JSON, concurrent
bounded stdout4MiB/stderr64KiB readers and deadline<=30s. Exceed either stream cap
or invalid protocol => diagnostic, terminate group then reap child. Timeout does
same; external cancel propagates after cleanup. TERM grace then KILL, total cleanup
reserve2s, no communicate() unbounded buffering. Parent only accepts validated
bounded URL strings/count/reasons/count from JSON. Failure returns empty partial.
_discovery_worker.main redirects stdout to stderr during imports/local execution;
only final validated protocol writes real stdout. No browser model processes.

_discover.discover owns default-worker vs explicit borrowed-client local seam;
local timeout cooperative for injected transports, documented exception. CLI reads
list-compatible reasons, never claims complete discovery. _cli_data.extraction_data
sorts a copied product view by canonical_product_id (fallback external_id), URL,
then bounded deterministic source-fact projection tie-breaker; leaves input list/objects
and raw_products unchanged. Projection uses every declared Product field EXCEPT
raw_data and scraped_at; nested normalized variants/attributes included. Dynamic
evidence/capture contracts never participate. Existing validated record bounds
bound this smaller projection. No source identity or evidence synthesis.

Acceptance16 cases; cycle stress and full driver/live/final remain separate gates.
