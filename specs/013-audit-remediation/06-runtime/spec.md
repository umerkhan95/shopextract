# 06-runtime — behavior specification

2026-11-01; implementation authorized umbrella-wide; this assignment DESIGN ONLY.
AR10; parent FR06,SC03/11/12. Sequential resource safety and output reliability, split concrete substeps.

## Outcomes and requirements
FR-R1: lazy public export resolution (__getattr__ cached actual objects, stable __all__/dir/signatures) avoids crawl4ai/browser imports for plain package/model/native domain imports; extractor namespace likewise lazy. Explicit browser use loads it. No fixed timing guarantee; measure before/after. Existing100-poll failures are not proven caused by imports.
FR-R2: Woo max_products propagates before fetch: per_page=min(100,remaining),stop at bound,partial budget reason unless known exhaustion. Retry delay parsed defensively and clipped to remaining execution deadline; insufficient budget returns incomplete,never sleeps past deadline. Source errors retain accepted prior records.
FR-R3: private execution progress checkpoint stores normalized accepted batches (max1000); owned CLI timeout with positive checkpoint ->existing E_PARTIAL/data,none ->E_TIMEOUT. Explicit external cancellation still propagates/cleans up. Preserve atomic output; no fabricated completion. Checkpoint ownership ends with execution context.
FR-R4: discovery seeder isolated in one owned worker with hard30s default (caller may narrow),terminated/reaped on deadline; no parallel workers. robots per origin/user-agent ShopExtract read once,Disallow excludes URL before emit/crawl; robots unavailable ->diagnostic/partial and skip unknown-policy URLs; redirects authorized per hop. Browser disabled unless explicitly allowed.
FR-R5: library progress routed stderr at owned subprocess boundary; stdout one validJSON document. Sort final products by canonical ID/sourceURL tie-breaker,URL discovery lexical stable; no order-dependent identity. Capture dedup handled by child02.

## Acceptance scenarios
SC-R1: freshprocess import package/domain/extractors no crawl4ai loaded; accessing browserexport loads it; callable/class identities and signatures stable. Record timing distributions only3 sequential samples,not performance SLA.
SC-R2: Woo bound1/99/100/101 exact request/page budgets,500page2 retainsbatch; Retry-After60 with remaining0.1 does not sleep60; malformed/headerdate deterministic fallback.
SC-R3: timeout after accepted batch retains exact records/partial,timeout before any ->E_TIMEOUT; caller cancellation propagates; repeat/restart checkpoint not reused.
SC-R4: controlled blocked seeder exits/reaped within deadline+2s cleanup reserve; robots allow/disallow/unavailable/redirect no forbiddenrequests; stderr noise does not corruptJSON.
SC-R5: shuffled source completion yields same ordered IDs and bounded result; max item/request/deadline boundaries and no owned zombie process.

## Boundaries and compatibility
Child01 functional review passed; full-driver/live gate remains pending. Preserve
constructors,identity,default feed syntax. No production/tests changed here.
Each numbered substep gets executable red tests and independent gates before code.

R1b/R2 concrete compatibility refinement: actualnativeAPIclassimports mustavoid
crawl4ai too. `_http_defaults` owns SAME DEFAULT_HEADERS/HTTPX_USER_AGENT/function
objects; _browser reexports them forcompat,explicitbrowserclassesstillloadbrowser.
OnefreshShopifyAPIprobe1.653s/1156modules/crawl4ai=true saved,notRAM/SLAproof.
Woo max_products optionalNone preserves legacyunboundedcall;positiveintegerbool
excluded. Bound1/99/100/101 per_page=min(100,remaining),retained<=bound,stopbefore
nextfetch. Exactfullpageatbound is partial unless valid total header confirms
exhaustion;empty/shortpage confirmsfinished. Ignore malformedtotal asunknown.
Retry-Afterseconds orHTTPdate defensively parsed;invalid/negative ->2sfallback.
Ifdelay>=remainingexecutiondeadline no retry/sleep,returnpartialerror. Pastdate/0
retryonceimmediately. Pipeline AND nativeprovider passboundbeforefirstfetch.

G2 pagination correction: shrinking page sizes change page offsets. Official Woo
Store Products API supports explicit offset (woo-offset-source.json). Bounded path
uses page=1,offset=accepted catalog count,orderby=id/order=asc and shrinkingper_page.
Never combine growingpage with shrinkingper_page. Realistic serverfixture slices
dataset by suppliedoffset (otherwise standard(page-1)*per_page),asserts exact IDs
1..N/uniqueness,not just counts. Legacy max_products=None unchanged. Sharedretry
helper also used by actualShopify429 path;one deadline integrationcontrol required.

R3 concrete lifecycle (before code): only owned extract-store CLI timeout recovery
is enabled. Producers register their already-validated accepted list with the
current execution state; no per-page serialization. The owner cancels/awaits the
operation before normalizing and freezing a snapshot. Native accepted buffers and
completed generic HTTP products are covered; the selected usable source follows
pipeline tier priority. Other command result types are unchanged. External caller
cancellation propagates. No global cache or state survives the execution context.
Recovery retains at most1000 products/8MiB portable record bytes/250000 record
nodes/depth56, using existing normalizer/portable/preflight codecs. Limits leave
room for response framing/raw projection within catalog transport bounds. A limit
is explicit in incomplete reasons; no bounded usable snapshot means E_TIMEOUT.
Shopify captured currency context is attached before accepted-buffer registration
can be consumed; defaults never become observed currency during recovery.
