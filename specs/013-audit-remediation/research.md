# Bounded audit verification research

Date: 2026-11-01. Current source revision `90d5bd1`; the supplied report names
`461ec38`. Read source rather than assuming all historical results still hold.
This is a planning investigation: no production fixes and no fresh store requests.
Exact session token counters unavailable; no inference or model downloads.

## Methods and saved evidence

- `evidence/smoke.json`: primary author's first current normalizer/scorer probe.
- `evidence/diagnostic.py` and `diagnostic.json`: deterministic seed 0, one process,
  zero network requests, actual production parsing/normalization/analysis/feed/
  validation/Woo loop. Only Woo HTTP transport and CLI emission replaced.
- `evidence/historical-index.json`: byte counts and SHA-256 for selected original
  evidence, plus compact historical observations. Audit files remain in their
  existing temporary directory; raw captures are not copied into Git.
- Audit root below is `/private/tmp/claude-502/-Users-umerkhan/8731b0e2-9664-4309-82d7-cebd215bf991/scratchpad/audit/`.
- `R` = reproduced in current production functions offline; `C` = supported by
  current code inspection, not separately executed; `H` = historical sample only;
  `Q` = claim needs qualification; `U` = cause/current behavior unresolved.
  A code-supported defect does not reproduce a named store's present behavior.

## Finding matrix

| ID | Audit claim and classification | Current source / evidence | Assessment and next slice |
| --- | --- | --- | --- |
| A01 | Zero products can report ok/complete: R + H | `_cli_extract.py:128,166`; `diagnostic.json` empty_None and empty_True; historical `perf-discovery/runs/res_example_extract.out`, `res_nxdomain_extract.out` | Current emission path reports complete for empty products if no errors and coverage None/True. Guard currently only applies when partial. Named historical outcomes are confirmed in saved files, not freshly live. Slice1. |
| A02 | Browser404 document can become product: C + H | `extractors/unified.py:108,194` checks success but no HTTP status before parsing | Browser acceptance lacks explicit status rejection. Exact Naheed404 response not independently reconstructed here; original claim remains historical. Slice1. |
| A03 | Policy page becomes product: R | `unified.py:153`; `_opengraph.py:38`; `_normalize.py:692`; diagnostic policy_page | Generic og:title/og:type accepted without product signal. OG normalizer supplies missing price/currency defaults. Slice1. |
| A04 | Woo midstream404 treated complete: R | `woocommerce.py:59`; diagnostic woo_midstream_404 | Real loop returns100 products, complete true, error None after page2=404. Slice1. |
| A05 | Discovery always complete: C + Q | `_cli_extract.py:175`; `_cli_core.py:175` | Successful discovery emission uses generic complete envelope with only URLs/count; no coverage proof. Failures/timeouts can emit unavailable, so “always” is too broad. Distinguish operation completion from catalog coverage. Slice1. |
| A06 | API/HTML capped exit inconsistency: C + H | `_extract.py:168–193`; `_cli_extract.py:166` | Explicit false/errors yield partial exit3; HTML None with reasons alone does not. Do not assert every API path returns3: non-Shopify API may also have None. Slice1. |
| A07 | Makeup City PKR became USD: R mechanism + H store | `shopify.py:93`; `_normalize.py:281`; diagnostic currency; `api-paths/ground_truth_report.txt` | Shopify discovery uses cart_currency cookie; normalizer falls back USD. Important: evidence outcome already marks absent-source default accepted=false; scalar/export remains misleading. Slice2. |
| A08 | CSS separator/Rs parsing: R | `_normalization.py:103`; smoke.json | 3,720 ->3.720 accepted; Rs.3,720 ->0 rejected; DE3.720,00 ->3.72000 accepted. Failure evidence rejection exists, monetary scalar still wrong. Slice2. |
| A09 | Observed zero API price: R + Q | `_normalize.py:311`; diagnostic woo_fields | Explicit source zero is genuinely observed, not fabricated. Add anomaly/destination eligibility diagnostics, preserve legitimate zero/free products. Missing/malformed/default zero differs. Slice2. |
| A10 | Placeholder image prevents better extraction: C + H | `unified.py:64,268,333`; historical HTML gap counts | Nonempty image sufficient for early return; _fill_image only fills absent values. No placeholder semantic rejection here. Exact historical404 image status not re-requested. Slice3a. |
| A11 | Shopify bulk barcode unavailable, enrichment429: C + H + Q | `_normalize.py:286`; `shopify.py:130–166`; saved truth .js.json files/ground_truth_report | Normalizer already supports barcode; missing bulk field is a source-coverage issue. Existing opt-in enrichment joins by variant ID and retains errors; rate limit blocks observed enrichment. Do not promise bulk barcode coverage or bypass429. Slice3b. |
| A12 | Woo variants/brands omitted: R | `_normalize.py:297–359`; diagnostic woo_fields | Normalizer emits neither vendor nor variants even when supplied in fixture. Live Store API variants may require separate requests: source availability and fetch budget remain research decisions. Slice3b. |
| A13 | ItemPage.mainEntity ignored: R + Q | `_schema_org.py:126–155`; diagnostic jsonld | Root ItemPage returns0; same ItemPage inside @graph returns1. Target root/nested/link traversal; do not claim all ItemPage unsupported. Slice3a. |
| A14 | Breadcrumb/gallery/span.sku/Magento HTML id absent: C + H + Q | `extractors/` source search; `html-paths/gt_extractor_gap_counts.md` | No dedicated HTML mechanisms found for these cues. Existing structured category/image/SKU support remains; Magento REST normalizer already has media_gallery_entries at `_normalize.py:517`. Scope HTML-specific additions, not “no gallery parser anywhere.” Slice3a. |
| A15 | Magento GraphQL gallery/brand/GTIN/categories absent: C + Q | `magento_graphql.py:11,23`; `_normalize.py:362` | Default field selection omits these. Categories already available via include_categories opt-in query; preserve that native route. Brand/GTIN may be installation-specific schema fields; negotiate/fallback rather than unconditional query. Slice3b. |
| A16 | Magento detected generic confidence1: C + H + Q | `_detect.py:96,119,214–281` | No Magento HTML rule; header/REST/GraphQL probes do exist. No-signals fallback gets one signal/max1 =>1.0; this is heuristic fraction, not calibrated certainty. Slice3b. |
| A17 | Quality presence score can equal1 for junk: R | `_quality.py:36`; smoke.json | Negative nonzero price, arbitrary image/description/id and policy title score1.0. Presence score must be named distinctly from factual/destination quality; preserve callers' thresholds until designed. Slice4. |
| A18 | Google validator too weak: R + C | `validate/marketplace.py:16,99`; diagnostic validation | Only4 required fields; invalid currency + placeholder + empty description still valid with missing-GTIN warning. Validator does reject negative numeric prices, so not every bad price passes. Current official destination rules research remains prerequisite, not assumed done. Slice4. |
| A19 | Google XML missing id/brand but ok: R + H | `export/_feed.py:55`; diagnostic feed; `downstream/gmc-feed-attribute-coverage.csv` | Export reads external_id and brand, while canonical Product uses vendor. Writer doesn't gate eligibility. Saved coverage: Naheed0/50 id; all3 samples0/80 brand. Canonical fallback ID needs stable identity design, not invented manufacturer identifier. Slice4. |
| A20 | Fuzzy precision0.25: H + C + Q | `downstream/fuzzy-precision.csv`; `compare/match.py:37`; CLI `_cli_analysis.py:290` | Saved sample8 pairs,2 correct. Current helper already calls classify_match and rejects explicit conflicts; missing attributes still allow title candidates. Sample precision is not population precision or proof no safeguards exist. Slice5. |
| A21 | Title duplicates5/5 wrong: H + C | `validate/duplicates.py:50`; saved `dup-title-*.json` | Current algorithm uses title SequenceMatcher only, no variant/function/quantity guard. Exact claimed five-pair adjudication not independently re-scored here; review source pairs before acceptance fixtures. Slice5. |
| A22 | Every category double counted: R + Q | `analyze/stats.py:202`; diagnostic analysis | Overlap category_path[A] + product_type=A yields2; category_path duplicates also count. Not every category always doubles. Define per-product versus occurrence measure. Slice5. |
| A23 | Unknown stock assumed in stock: R + C | `stats.py:217`; `export/_feed.py:76`; `_normalize.py:352` | Missing dictionary key defaults true. Explicit None is falsey and can count out-of-stock, also misleading. Normalization compatibility defaults require evidence-aware projection. Slice5 +4. |
| A24 | No readiness command: C | `_cli_core.py` command declarations and `_cli_analysis.py`; source search readiness | No dedicated readiness surface found. Do not equate future Google validator, schema.org semantic completeness and ACP protocol readiness. Slice6 deferred. |
| A25 | 1MiB downstream input cap breaks own output: C + H | `_cli_data.py:15,45,96`; historical summary shows10.8MB/50 Allbirds | Reader hard cap1048576. Extraction includes raw_products plus products/provenance, producing incompatible large outputs. Choose compact or explicit bounded larger/streamed input; don't remove limits. Slice0/2. |
| A26 | Woo -n fetches catalog first: C + H | `_extract.py:498`; `api-paths/woo_mock_results.jsonl` | Default non-category Woo extractor receives no max-products/pages budget; truncation after response. Category mode already bounds max_pages. Saved controlled1190 records/limit50 used12 requests;3467/limit5 used35. Slice0/1. |
| A27 | Timeout discards partial results: C + H | `_cli_extract.py:141`; `_cli_core.py:181`; `perf-discovery/runs/ext_woo_10.out` | wait_for raises before final ExtractionResult; failure data null. Streaming/checkpoint propagation currently absent at this seam. Design adapter-level batch retention plus explicit deadline outcome. Slice0/1. |
| A28 | Discovery595s hang, seeder suspected: H + U | `_discover.py:57,96,275`; `perf-discovery/hang_sample.txt` | 300s internal wait_for exists, CLI outer timeout also exists. Cancellation latency/native blocking can defeat coroutine timeout; seeder attribution not proved. A macOS sample file does exist in saved evidence; report's “no stack” should not become an absolute assertion. Analyze minimal captured stack/controlled blockage before repair. Slice0. |
| A29 | Retry-After60 sleeps without budget clipping: C + Q | `woocommerce.py:51`; `shopify.py:60`; `_cli_extract.py:141` | asyncio.sleep uses header directly; no local remaining-deadline calculation. Outer wait_for can cancel cooperative sleep; not proof all CLI calls really sleep60s. Slice0. |
| A30 | Robots ignored/disallowed home returned: C + H | `_discover.py:265–276`; saved `disc_khaadi_50.out` and sitemap/robots evidence | Seeder configured check robots false; no common per-URL allow check identified. Saved discover includes/home; exact current robots policy not live rechecked. Slice0. |
| A31 | crawl4ai progress corrupts stdout: H + U | `_browser.py:139,147`; `_discover.py:275`; historical run .out files | Browser config already verbose false; library/seeder may still write stdout. Need narrow stdout capture with controlled integration to locate emitter; do not blindly flip an already false setting. Slice0. |
| A32 | Output ~216KB/product: H + C | `_cli_data.py:96`; historical50-item10.8MB summary | Raw+normalized evidence both serialized; audited size is sample-specific. Profile provenance payload before changing capture support; no measured quadratic-growth finding yet. Slice2 (roundtrip/compact). |
| A33 | Output order changes every run: H + U | `_extract.py:551`; `_discover.py:393` | gather preserves input order, so don't blame task completion ordering. Discovery upstream ordering/set traversal may vary; isolate it and specify stable canonical order. Slice0. |
| A34 | Allbirds/Naheed/Woo timing/RSS table: H | `perf-discovery/runs/`; `api-paths/runs/summary.txt` | Historical environment/endpoints/caches only; not independently benchmarked current code. Carry baseline samples, not performance guarantees. No fresh network benchmark required for plan. Slice0 verification baseline. |
| A35 | Positive claims (Shopify core, minor units,20 discovery URLs, HTML money, identity no false matches, cautious taxonomy, browser cleanup): H + C + Q | `ground_truth_report.txt`; `_normalize.py:311`; original audit artifacts | Woo minor-unit conversion directly supported and retained. Other counts and browser cleanup remain original sample observations; zero accepted identity pairs does not establish useful recall. Preserve controls in each affected slice. |

## Questions, alternatives and decisions

1. **Outcome contract first.** Generic response completeness currently means success
   of an operation, while users infer full catalog coverage. Choose a canonical
   extraction outcome plus coverage evidence, then version/project CLI/API/tools
   consistently. Do not silently redefine discovery's empty success as extraction
   failure. Zero extraction => failed per proposed spec; positive unknown coverage
   must not become complete.
2. **Currency compatibility.** Canonical Product constructor/defaults are preserved
   by constitution. An ISO field literal `unknown` is unsuitable. Prefer an explicit
   unsupported currency observation/diagnostic plus null/omission in opt-in truthful
   projections; if scalar defaults change, record a versioned compatibility decision.
   Evidence already distinguishes some defaults, so reuse conversion outcomes.
3. **Zero price.** Observation correctness and sale eligibility are separate. Keep
   exact supported zero; warn based on destination and product context. Nonfinite,
   malformed and absent are different outcomes, never accepted free products.
4. **Field coverage.** Enrich only justified sources with budgeted request accounting
   and parent/variant identity links. Shopify bulk does not promise barcodes. Woo
   variants and Magento custom attributes need explicit capability/source research.
   Root JSON-LD and lazy image repairs can be independently reviewable HTML slice.
5. **Quality/readiness.** Preserve presence as a named diagnostic, add support and
   destination-specific rule failures; no opaque single readiness probability.
   Official Google/ACP/schema.org sources must be pinned during slice4/6 research.
   No fresh external standards claims are made by this investigation.
6. **Resource contract.** Introduce budget/partial-result behavior using existing
   execution state and adapter seams, not parallel crawlers. One sequential driver,
   explicit outer process timeout for native/library hangs; retain cleanup evidence.
   Do not relax downstream byte limits globally or discard provenance wholesale.
7. **Priorities.** Keep user priority truth -> money -> coverage -> eligibility.
   Use a small bounded verification harness before the first repair; split
   fetch/deadline/output work into cross-cutting children alongside affected paths
   (plan.md defines ordering), because it prevents verification hangs and data loss. Similarity/statistics fixes are separate from
   extraction truth. New readiness command remains final/deferred.

## Limitations and compatibility risks

No live store behavior, present robots policy, full browser404 run, current timings
or memory footprint was re-observed. No complete repository test driver was run:
production tree is unchanged and the task is verification/planning. Diagnostics
prove listed production mechanisms under synthetic inputs, not full CLI/integration
coverage. Original temporary evidence can disappear; the hash index locates it but
is not a backup. Select minimal sanitized regression fixtures into each child spec
before implementation. Existing profile-coverage pilot and its blocked live gate
are unrelated and unchanged.
