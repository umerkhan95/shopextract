# R4/R5 documentary interfaces (no business code)

_discovery_runtime.py owns DiscoveryURLs(list[str]): reasons:list[str],request_count:int;
DiscoveryClient(client,*,max_requests=16,response_bytes=10MiB) shared GET/request
and robots allowed(url) cache; no authority broadening. async bounded_sitemaps(url,
platform,client,max_urls) uses existing XML parser and bounded queue. async
run_discovery_worker(payload,*,command=None)->DiscoveryURLs owns process/kill/reap,
retains protocol<=4MiB/stderr<=64KiB. Private command seam executes real controlled
children in tests, not fake process. _discovery_worker.main reads bounded JSON,
redirects stdout during imports/local discovery, serializes protocol after exit.
_discover.discover defaultworker vs borrowed-client _discover_local;
_discover_local wraps client once and calls existing native strategies with guarded
borrowed client, replaces SDK seed and bounded profile browser fallback. Existing
private browser helper remains explicit legacy use. _cli_extract surfaces reasons.
GuardedSources.discover borrows DiscoveryClient over existing guardedclient.
_cli_data.extraction_data orders serialized records deterministically without
mutating ExtractionResult/source buffers; canonical identity/source URL tie-breaker.
