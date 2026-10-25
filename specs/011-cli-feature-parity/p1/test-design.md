# Predesigned P1 verification

Seed11025; synthetic fixture URLs `.invalid`, not live captures. Source algorithms remain real; mock only HTTP/browser/provider boundaries. Initial saved P0 smoke before expansion.

|Case|Requirements|Fixture/risk|Expected outcome|
|---|---|---|---|
|S1|F1,F4|11 Shopify records with variant0.10, leading-zero barcode, false stock, null/absent fields|11 envelope portable records; exact Decimal roundtrip, string IDs, false preserved, attached evidence aligned; full stdout single JSON|
|S2a|F2,F4|controlled HTTP Shopify products endpoint actual adapter|native normalized facts and complete metadata, --max11 preserved|
|S2b|F3|controlled CSV/XML feed and generic JSONLD HTML|native feed/parser facts; feed --max1 reports truncation; one raw extraction object|
|S3|F5|stdin raw object/list, no-title record, title+image record, empty list|native normalize dropped index, quality0 and0.55; empty batch0|
|S4|F2,F5,F8|native option boundary capture, invalid caps0/1001, unknown key, duplicate/nonfinite JSON, protocol mismatch, LLM flags without activation|exact native options or usage error; no transport/provider side effect; secrets absent|
|S5|F6,F8|ambient provider/model key plus native API failure/crawl fallback, nested call; sleeping transport finally cleanup; KeyboardInterrupt boundary|no provider call; no env mutation; timeout E_TIMEOUT, cleanup true; interrupt130; policy restored after failure|
|S6a|F6|browser blocked/default and missing executable explicit|HTTP extraction works; no browser launch by default; explicit missing browser E_DEPENDENCY|
|S6b|F7|controlled provider returns JSON, rejects malformed response;3candidate URLs/call cap2,input limit16/output limit8|at most2 sequential completions, no retries, finite input, params exact; deadline cleanup; malformed response sanitized partial/error|
|S7|F1|P0 suite + legacy native API boundary|legacy defaults/preview unchanged; bounded machine complete list|
|S8|F8|www.boardgamebliss.com explicit Shopify, max2|<=5actualHTTP attempts, <=2retained products, <=30s, no retries; save first result, stop failure|

Additional predesigned F4/F5 failure cases: input bytes1048575/1048576/1048577 (first two parse if valid padded JSON, last rejects); 999/1000/1001 records (first two accepted, last rejects); depth63/64/65 and nodes99999/100000/100001 (at/under accepted by structural validator, above rejects); atomic output replacement fault preserves existing file and emits no success. Invalid UTF8/BOM/duplicate/nonfinite inputs reject before algorithm. Native options forwarding covers all six storefront keys, shop/platform/identifier controls; model selection ignores ambient model override under policy.

Live stop seam: driver wraps `httpx.AsyncHTTPTransport.handle_async_request` and delegates to original transport. It counts actual attempts, rejects attempt6/repeated URL before sending, and raises a driver-only BaseException on first HTTP failure to bypass native retry/fallback handlers. All targets/redirects must remain declared host. Native retries remain unchanged outside this driver.

Independent coverage review required before stress. Bounded stress: sequential12cases, seed11025, <=1MiB/case, <=100products/case,30s/case, total<=3min, one process, no inference. Distinct cases: raw malformed/depth/size/duplicate; item caps below/at/above; money/null/false/missing; ambient policy nested; timeout cleanup; provider calls/input/output limits; unknown storefront; optional browser. Existing native test coverage supplies parser adversarial regressions; exact selected commands recorded later. Fault proof: temporary omitted11th-product output must fail S1; restore immediately. Live follows offline; browser/model live blocked absent separate budget and installed executable, synthetic mechanism tests remain mandatory.

G1 adverse matrix refinement: malformed portable schema/version/variant-contract alignment and malformed `$type` decimal/mapping reject quality before scoring; mixed raw and portable array rejects, normalize portable input rejects. Retained extract products with errors or catalog_complete=False produce exit3/data retained/completeness partial; catalog_complete=None without errors produces exit0 and explicit unknown coverage. Feed truncation adds product_budget_reached and false coverage; empty feed native error unavailable failure. Timeout NaN/Inf/0/negative/>300 and temperature NaN/Inf/<0/>2 reject before credentials/transport. LLM call/output/input caps0,1,max,max+1 check reject/accept finite values; explicitly selected model survives ambient SHOPEXTRACT_LLM_MODEL. LLM provider valid object/list, empty response, malformed JSON, oversized output (provider max_tokens request bound; no retrospective billing claim), provider exception, deadline cancellation and budget exhaustion retain sanitized partial/empty mechanism behavior; no secrets in diagnostics. Unknown model/provider syntax rejected before source read, already-running Ollama requires no key and never starts server. Endpoint unavailable produces bounded sanitized failure. Browser explicit preflight must occur before network. Unsupported machine CSV output and file replacement failure occur before success emission, old target preserved.

G2 accounting case: one operation policy max_calls2, two consecutive bounded_llm invocations each with2candidateURLs must yield total2 provider calls, not4; nested task uses same state. Advance fake monotonic before provider call: timeout <= remaining operation deadline; expired state submits zero calls. Increment immediately before provider await, consumed even on provider failure/cancellation.

Contract clarification: empty extract-one => E_OPERATION/exit1/data null/completeness unavailable; no invented partial. Explicit product cap with retained records => partial/exit3/retryable false, no wrapper retry. S1 asserts exact inner portable decimal value string0.10.

Coverage/stress realization: tests/test_cli_extract.py and test_cli_extract_limits.py exercise native parsers, normalize/quality, strict files, policy state and native fallback. Sequential driver tests/cli_extract_stress_driver.py fixes12 case groups and limits before execution; <=100 normalized products/case, schema-only count validation uses999/1000/1001 empty records without algorithm expansion. Max input1MiB except explicit just-above rejection (1048577bytes); node bound cases use JSON values only. Child RSS limit512MiB via rusage, max30seconds/case,180seconds total, one child at a time; persist status after each case, stop first failure. Provider module stub is external provider boundary only; all policy/native fallback code real, zero model execution.

Coverage review additions: empty CSV feed native-error => E_OPERATION1/null;
empty failed store same binding behavior (actual BigCommerce customer-context401 controlled transport).
Overlapping child tasks exercise common LLM lock/cap (peak submissions1,total2);
provider-await cancellation runs cleanup and consumes allowance, provider failure
also consumes one. Activated LLM caps0/1/max/max+1 and finite-temperature invalid/
0/2 are now distinct acceptance cases; accepted edges assert actual submitted
provider parameters and source input byte length. Stress total deadline uses
min(per-case30,remaining180), persists timeout stop state. Raw schema records up
to1001 for rejection edges, normalized products<=100/case.

File pipeline acceptance: successful bounded extract -o writes exactly its full stdout envelope; quality FILE then reads portable records and scores actual products. Atomic replacement failure remains preserved-old-output.
