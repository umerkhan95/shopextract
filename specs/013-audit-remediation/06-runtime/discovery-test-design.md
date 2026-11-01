# R4/R5 executable cases (15 cases, no network sweeps)

Seed fixed deterministic fixtures; loopback ThreadingHTTPServer only, external
boundaries mocked only when isolating supplied client. Each subprocess <=8s; full
new test file <=120s. First smoke timeout red <=10s before expansion.
1 real worker HTTP sitemap/index/cycle sorts/dedups, robots once, <=16requests.
2 actual blocked worker pid times out/reaped;3 explicit cancellation reaped.
4 robots Disallow excludes request and emitted URL;5 503 failsclosed/diagnostic;
6 robots404 allows;7 redirect to disallowed path never requested;
8 cross-origin redirect never requested;9 request cap counts robots and redirects;
10 streamed response >10MiB fails before consuming remainder (lower-only fixturecap).
11 worker entry stdout noise redirected, protocol one JSON;12 malformed/oversize
protocol rejected and output bounded.13 actual extraction serialized permutations
same ordered IDs/source values;14 actual CLI discovery uses robots and oneJSON,
plus real GuardedSources path forbids disallowed emittedURL. Parameter variants
are not inflated into claims of new mechanism coverage. Budget/error retains
coverage_unverified and diagnostics; no forbidden requests is the assertion.

G2 repair before code: existing timeout/cancel scripts create descendant PID and
TERM handler reaps it; both PIDs must disappear (parent-only kill fails). Existing
protocol case includes >4MiB stdout burst then60s hang, requires protocol rejection
<1.8s, plus1MiB stderr drainage. Added15th borrowed follow_redirects=True case
redirects to robots-disallowed target: no target HTTP even when underlying client
would automatically follow. Ordering oracle now retains actual passed result and
opposes canonical IDs to URL sort. These refinements exercise distinct gaps; no
extra source/network research. Cycle stress not claimed by acyclic loopback case.

Residual harness amendment: install TERM handler before parent-ready marker; all
lifecycle/protocol PID cases have finally cleanup of known owned PIDs. Both stdout
4MiB and stderr64KiB overflow programs write tracked PID then burst+hang; require
protocol diagnostic <1.8s and PID absent, finally cleanup on failure. This pins
kill-on-either-stream overflow, not merely eventual communicate() size checking.

G3 correction16th case: same canonicalID/URL/title, vendor A/B and opposed scrape
timestamps must still order A/B in both runs. Tie-breaker every declared Product
fact except raw_data/scraped_at (no dynamic contracts). Existing real-worker
loopback now root index -> nested self-cycle+leaf, each map fetched exactly once.

Affected compatibility diagnosis (before repair): existing native variants are
nested dataclasses, so source-fact projection must reuse the ALREADY encoded
portable product record, once per product, rather than pass dataclasses directly
to encode_value. Keep same facts/metadata exclusions. Existing extract-store
owned HTTP flow borrows an explicitly managed client for discovery, preserving
its controlled HTTP/cancellation boundary (borrowed cooperative exception); direct
public discover without a client still uses the real worker. R3 HTML recovery
must remain observable through its actual MockTransport HTTP, not subprocess
network bypass. Existing checkpoint ID order assertions must follow canonical-ID
order while comparing every expected record/GTIN/source value by identity.
Tool fixtures declare robots404 explicitly; their unchanged sitemap request budget
gets one additional accounted robots request, no forbidden sibling request.

D02 retained compatibility: denied cross-origin nested sibling is skipped before
request (no DNS/wire); accepted prior/later same-origin maps remain available.
Check policy at dequeue, maintaining lazy authority/no unvisited sibling DNS.

Functional repair design (3 distinct cases,19 total):
17 worker leader exits on TERM while descendant ignores TERM and closes inherited
pipes; known PID files/finally cleanup. Group must still KILL descendant after
leader reap; bounded poll confirms neither PID remains. This defeats leader-only
proc.wait escalation, unlike cooperative child control.
18 native GuardedSources aggregate loc count boundary:4999 duplicate index locs
plus one leaf product reaches5000 and succeeds;5000+leaf product hits5001 and
returns location-budget diagnostic without emitting over-bound URL. Queue dedup
and existing authority remain, no materialized unbounded pending map list.
19 native source real guard request budget: robots+root+14 maps exhaust16;14
accepted URLs retained,15th map never sent, discovery_request_budget forwarded.
Guard reasons emitted once beside existing coverage diagnostic at every return.
