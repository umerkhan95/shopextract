# Native sitemap integration skeleton

Coordinator author, after independentG1PASS. New private module `_discovery_sitemaps.py` owns `SitemapDiscovery(urls:tuple[str,...],stop_fallback:bool)` and async `discover_sitemap_urls(base_url,*,max_urls=100,timeout=30,client=None)->SitemapDiscovery`. Stub raises NotImplementedError; no fake success.

Private helper owns bounded HTTP/robots/XML traversal, canonical same-origin/store-path guards, category exclusions and resource counters; existing public discover signature unchanged. stop_fallback distinguishes authoritative robots/resource stop from unsupported native path eligible for existing fallback. Cancellation and enclosing deadline exhaustion escape to existing bounded caller; no new browser launch after deadline.

`_discover.py` propagates max_urls through private platform fallback functions to `_discover_via_sitemap`; calls native helper first, then legacy known sitemap/seeder/browser only when permitted. Legacy seeder itself gets requestedmax, not5000. Public discovery wraps operation in remaining deadline without changing output shape. No Product/Variant/CLI format changes.

Acceptance tests call actual public discover and actual Click CLI+extractor/normalizer. Only HTTP transport and browser/seeder external boundaries replaced. Shared-client ownership remains with caller; owned HTTP client closed after traversal. Red acceptance required before implementation; reviewerG2checks these interfaces and tests.
