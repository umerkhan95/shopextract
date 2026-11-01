# R4/R5 bounded discovery and output refinement

2026-11-01, AR10/SC03/SC11/SC12. Completes existing R4/R5; design before code.
FR-D1: default public discover runs the complete native discovery operation in one
owned Python worker, capped at min(caller timeout,30s); timeout/cancel terminates
and reaps process group,2s cleanup reserve. SDK seeder is replaced by bounded
HTTP sitemap traversal using the existing XML parser. No unaccounted browser walk
in this bounded profile; unavailable strategies remain explicit diagnostics. A
borrowed AsyncClient uses the same guards in process (cooperative deadline only;
no promise of killing arbitrary injected transports). Never parallel workers.
FR-D2:16 HTTP requests INCLUDING robots, redirects and detection; max1000 returned
URLs,10MiB per response streamed before materialization, max5000 queued locs/maps,
2048 URL chars,256KiB robots. Robots ShopExtract cached once per origin;404 means
absent/allow,2xx parse policy,403/401 deny,other/error fail closed with diagnostic.
Same-origin redirects only,max5; check destination robots before sending. Reject
cross-origin sitemap/returned URL; fail-closed policy before crawl AND emission.
FR-D3: bounded discovery returns list-compatible DiscoveryURLs with reasons and
request_count; coverage always unverified. CLI adds those reasons. Native guarded
tool discovery applies robots before sitemap requests and emitted URLs using its
existing GuardedTransport accounting/authority (no subprocess bypass of toolguard).
FR-D4: worker redirects imported library stdout to stderr, protocol stdout exactly
one JSON value <=4MiB; parent drains stdout/stderr with bounded retention and kills/reaps
on overflow of EITHER stream. No private worker status leaks into public stdout. Final discovery
URLs lexical sorted unique; final extraction products canonical ID then source URL,
stable source-value tie-breaker. Original identity and source evidence unchanged.

SC-D1 owned worker real loopback sitemap returns sorted URLs under request budget.
SC-D2 hang timeout and explicit cancellation reap the actual process (PID absence).
SC-D3 robots allow/deny/unavailable/404 and redirect destination checks issue no
forbidden request, record distinct policy diagnostics; nested cycles stop.
SC-D4 request/body limits retain already observed URLs or empty partial, no overrun.
SC-D5 noisy child stdout is isolated by worker entry; malformed/oversized protocol
is rejected without corrupting CLI JSON. SC-D6 source completion order permutations
produce equal ordered identities; actual CLI emits one JSON document despite noise.
No strict whole-command recovery/render walltime or browser subrequest claim.
