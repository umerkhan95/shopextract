# R1b/R2 documentary seams — G2 proposal, no implementation

`extractors/_http_defaults.py`:DEFAULT_HEADERS,HTTPX_USER_AGENT,
get_default_user_agent()->str. NativeShopify/Woo/Magento importlightweightmodule;
_browser imports/reexports identicalobjects,not duplicatefunctionwrappers.
`WooCommerceExtractor.extract(shop_url,*,max_products=None,enrich_variants=False)`
validatesbeforeHTTP,computesremaining/perpage beforeeachrequest,clips retainedrows,
setscompleteness_reason product_budget_reached unlessknownexhaustion.
`_execution.remaining_execution_seconds()->float|None` reads existingmonotonicstate.
`extractors/_retry.py:wait_for_retry(header,default=2)->bool` parsesseconds/HTTPdate,
checks remainingdeadline beforewait,returnsFalse oninsufficientbudget. No global
clock/caches;one retry maximum existingadapter ownsbase retention/error state.
Pipeline/nativeprovider forwardmax_products includingWoo. No broadtransportrewrite,
no changedconstructors/defaultHTTPidentity. R3checkpoint/R4worker/R5sorting future.

BoundedWoo uses page=1 + explicitoffset=retainedcatalogcount and deterministic ID
ordering; internalpagecounter stillowns requestlimit/pages_completed. No overlap
from shrinking per_page. Legacyunboundedpagepath remainscompatible. Shopify429
consumer shares remainingdeadline retryhelper aswell (not justWoo-only claim).
