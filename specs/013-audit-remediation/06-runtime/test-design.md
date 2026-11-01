# Behavior/test design before breakdown

Scenario IDs and exact expected outcomes: spec.md. Distinct uncovered risk:
Overfetch, cancellation data loss, native blockage, false robots compliance and machine output corruption; real transport/worker/CLI lifecycle paths with controlled external boundaries.

Fixture author uses tiny sanitized saved audit sources plus deterministic factories
seed0. Mock external HTTP/DNS/clocks/library boundaries only; actual algorithms,
normalizers,encoders,CLI/tool/persistence paths execute. Design all new edge cases
before tests/fixes; retain accepted native/freeProductGroup/empty-normalize controls.

Acceptance/stress cap64 concrete cases per child,one worker,120s subprocess,
1MiB ordinary input (child02 byte-boundary fixtures up to32MiB+1),256MiB target
retained test memory,stop first unexpected failure and one diagnosed repair.
Enumerate exact collected cases before red run;64 is maximum,not promised coverage.
Save one smoke before expansion. Distinct missing/null/empty/zero/conflict and
just-below/at/above limits from SCs are separate assertions; seed variation is not
new coverage. Independent reviewer checks fixture realism and real-path execution.

Live plan: after offline green one explicit Shopify or Woo endpoint,max3requests/2items/30s; one discovery domain max5requests/30s withrobots accounting. Browser integration blocked unless allsubrequests cap enforced; failures simulated with real worker offline.
Offline: focused acceptance/affected checks then configured scripts/run_tests.py
240s-family/480s-total (never increase). Prior timeout does not satisfy this gate;
record unrun families and unknown failure nodes honestly. Separate synthetic
mechanism,stress and actual live evidence; inconclusive live is never a pass.

## R1 executable red stage inventory (before tests)

Six cases,each fresh subprocess15s max,full run120s,one worker. Four module graphs:
importshopextract,shopextract._models,shopextract.tools.domain,shopextract.extractors
must not load crawl4ai/playwright; native/model and extractor namespace are distinct
transitive dependency risks. Browser export access case must load actual browser
module and return identical class twice (positive control). Public extract/normalize/
Product export identity+signature,allnames/dir and unknown-attribute case verifies
lazy resolution doesn't replace callable objects or hide exports/errors. Actual
import graph executes,no fake imports/modules. Record timings as diagnostics only.
First module smoke saved before all6. R2–R5 later red cases remain pending; no
claim that R1 imports alone resolve100-poll failures or resource deadlines.

G2 inventory repair BEFORE test changes: freeze original root/extractor initializer
sources and AST-derived ordered __all__, intentionally imported public bindings and
root__version__ in checked fixtures. Expected names come from prechange source,
not a production lazy map. Execute frozen eager imports as a reference namespace
resolving original module objects; actual package attributes for EVERY expected
name must be identical (no wrapper). Assert exact __all__ list/set,dir coverage for
all intentional exports,unknown AttributeError,and rootversion0.1.2. Python-added
submodule attributes are not newly promised exports. Two fresh inventory controls
(root/extractors) replace the single sampled control; R1 now7 cases. Each process
15s (within30s requested cap),one worker,120s outer ceiling; existing4 import reds
remain applicable. No production/components changes.

R1b/R2 executable design BEFORE tests:23cases,oneworker120souter. R1b3freshAPIclass
imports (Shopify/Woo/legacyMagento),each15s actualmodulegraph nocrawl4ai/playwright;
1actual _browser reexportidentitycontrol keepsfunction/dictsameobjects.
R2fourbounds1/99/100/101 exactper_page/pagerequestcounts/retainedcounts+partialreason;
2exhaustioncontrols(totalheaderexact/shortresponse),1page2HTTP500retains100records;
6Retryheaders60/malformed/negative/futuredate/pastdate/0 withremaining0.05s,outer0.2s
(first4 noretry/nosleep, last2 onceretry). Fourinvalidbounds0/-1/True/1.5 reject
beforeHTTP. RealpublicAPI andactualnativeToolRuntime eachmax1 assert queryper_page1
andoneproduct,evenifserverignoresqueryreturns100. HTTP/DNSonlyboundaries mocked.
Firstsmallimports/bound1smoke savedbeforefullnew. ExistingR1seven unchanged;
R3–5 remainseparatelygated/noapprovalfromthisstage.

G2 repair: R1b/R2 now24cases. Fourbound fixtures use realistic serveroffset slicing,
exact orderedIDs1..N anduniqueIDs;101 uses requests(size100,page1,offset0) then
(size1,page1,offset100). Single actualShopifyRetryAfter60 withremaining0.05s must
returnpartial/no secondHTTP within0.2s. Oneofficialprimarypage fetched foroffset
mechanism,sourcepin saved;no merchant sweep. NativeGuardedTransport permits bounded
GETquery params underexistingoriginauthority,so no authorization widening.

Affected diagnosis before fixture repair: 240 pass/3 fail. Existing child01
midstream404/empty fixtures choose first response by page=1; bounded Woo now uses
page=1 plus explicit offset, so switch fixture to offset=0 (legacy page fallback)
and retain exact100 products/2requests/status assertions. Existing live-regression
currency fixture explicitly conflicts variantCAD/storeUSD; child02 approved result
is unresolved empty currency, not CAD precedence. Preserve both stock assertions
and strengthen with a non-observed currency contract assertion. No production
repair is justified by these superseded expectations.

R3 first concrete tests before implementation: real CLI Woo100 accepted records
then second request blocked =>exit3,exact accepted raw facts/IDs/price/stock and
valid portable evidence retained,operation_timeout/catalog_complete=false. First
request blocked =>exit1/E_TIMEOUT/no data. Same runner restart must not reuse old
checkpoint. Actual external async caller cancellation propagates after accepted
page and cleans clients. Shopify250 accepted with response-cookieCAD then blocked
page preserves currency observation. Generic completed HTTP product before another
blocked request retains its source,using actual sitemap/parser pipeline. Resource
mechanisms use small private-source fixtures and existing codecs at1000/1001 and
small narrowed byte/node/depth boundaries; no large allocation needed. First real
CLI smoke saved before expanding;oneworker/120s/process/thread caps unchanged.
The HTML acceptance uses real declaredMagento API-failure→platform sitemap→Unified
HTTP parsing: first admitted source then laterURL blocked. Installed parser import
is warmed outside ownedtimeout; fresh imports are separately covered. This directly
covers historicalA27 mechanism without replacing extraction/checkpoint logic.
Initial R3 executable inventory6cases (Woo partial/empty,restart,HTML,Shopify,cancel).
Remaining private resource boundaries use reused codecs after lifecycle review.

R3 resource acceptance before code:8 additional private producer cases,total14.
Normalized Product buffers1000/1001 retain at most1000 with explicit limit reason.
Byte boundary uses existing canonical portable JSON record bytes at/below fit;
node boundary spans TWO actual records to prove aggregate accounting; depth boundary
uses existing lexical shape at/onebelow fit. Tests may narrow private limits only,
never raise hard ceilings. Existing codecs execute unchanged; no mocked checkpoint
or large allocation. Cancellation test enables the real private owner checkpoint.

G2 metadata repair before tests: HTML timeout must keep actual unified_crawl tier,
Magento result platform and exact catalog_scope. Two opt-in controls compare actual
Shopify normalcompletion versus timeout with restore-short-GTIN false/true;250
accepted rows carry original11digitbarcode,restored value/observed transformation
only when requested. One small private normalized source fixture proves result
Magento can coexist with Generic Product/source normalization metadata. Total17.
No hard total-walltime claim: bounded synchronous freeze follows canceled I/O.

Before final R3 review, two actual crawler-boundary cases (total19) guard browser
admission and latest accepted view: HTTP partial product followed by admittedbrowser
view for SAMEURL must retain one browser view,not duplicate/staleHTTP data. HTTP404
plus browser404 metadata must never create a checkpoint. Execution context releases
its progress reference on exit. No browser/network runs: only SDK boundary replaced.
The stale node-edge test imports CLI bounded_tree,not the portable guard. HEAD and
current portable default are both1M nodes (unchanged). Move ONLY this catalog
fixture to999999/1000000/1000001,matching reviewed02 allowance; no guard change.
