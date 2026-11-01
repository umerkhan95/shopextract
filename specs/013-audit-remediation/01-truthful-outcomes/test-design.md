# Test design before breakdown

| FR / SC | Fixture / exact outcome | Distinct risk and existing gap | Production path |
| --- | --- | --- | --- |
| FR01a/b SC01a | Deterministic0/1 products × coverageNone/False/True; extra True+errors and True+reasons; expected failed/partial/complete per spec | Empty success, unknown upgrade, contradictory complete; existing Shopify capped tests don't cover all these states | ExtractionResult assessment + real CLI encoding/emission; native tool source/domain |
| FR01b/c SC01b | Positive HTML unknown/capped API ->exit3; Shopify exhausted ->0; empty extraction ->1; empty discovery ->3; positive discovery ->3 | Catalog and operation completion conflated, empty discovery differs from empty extraction | Click runner with replaced transport only where possible; existing real Shopify transport tests reused |
| FR01b SC01b | Existing file sentinel; complete and partial write envelope identical to stdout; failed preserves sentinel | Output-path behavior can bypass CLI outcome fixes | Actual atomic_json/file and CLI |
| FR02a SC02a | status200/302/404/500/None/0/malformed with successTrue and plausible Product; status200/successFalse | Browser success currently bypasses HTTP validity; both single/batch gates need assertions | Fake crawler external boundary only, actual single/batch code and actual parser; static MockTransport HTTP404 vs200 control |
| FR02a SC02a | Batch[200 legitimate,404 plausible] ->one retained, incomplete diagnostic | Good sibling hides dropped failed page | Actual batch aggregation and outcome projection |
| FR02b SC02b | Policy title/image/website plus markdown price ->none; OG product/title/zero and schema Product/name/zero ->retained | Avoid blocking free products while rejecting generic pages; presence differs from truthiness | Real static/browser OG/schema parsing, normalization and tool domain parse; no fake admission helper |
| FR02b SC02b | Explicit product metadata with whitespace title ->none; native API supported zero ->retained | Admission bypass/blank usability; avoid generic rule leaking into native adapters | Normalizer and core extraction paths |
| FR01d SC03a | Woo100 then404; prior IDs unchanged, incomplete/page-specific reason; CLI retained100 partial | Failure after successful page masquerades as exhaustion | httpx.MockTransport + real Woo loop/pipeline/CLI; first-page404 negative |
| FR01d SC03b | Woo99 terminal or100+empty200 complete adapter, unknown pipeline ->partial | Correct termination should not be broken by404 fix or promoted to catalog proof | Actual Woo adapter and pipeline |
| FR08 SC13a | Artifact methods/revision/provenance recorded | Synthetic result mistaken for fresh live observation | Saved JSON and independent review |

State invariants: no accepted products ->failed extraction regardless source flag;
positive data is never discarded merely because coverage unknown; HTTP errors
never parsed as admitted products; explicit zero is not absent; discovery zero is
not empty extraction failure. Existing Product/Variant constructors and envelopes
stay compatible apart from intentional truthful exit/status corrections.

Red tests: add tests/test_truthful_outcomes.py after G1/skeleton; first demonstrate
empty/None success, OG policy acceptance,404 browser acceptance, Woo404 completion
and tool empty success failures. Existing test_cli_extract.py Shopify capped and
terminal tests and test_cli_extract_limits.py remain controls, not renamed cases.
Inventory tool/browser tests before authoring; reviewer checks seam coverage.

Synthetic execution: fixture author reuses tiny sanitized original metadata and
a deterministic Woo factory; seed0, max100 products/page, two pages, max64KiB HTML,
no model/browser process for controlled mechanism checks, one worker. Stress is
bounded invariant enumeration:12 outcome combinations,8 admission statuses×2
browser modes,6 OG/schema variants,4 Woo transitions,3 file cases =41 cases maximum
(keep parameter bookkeeping exact in implementation). Max200 source products and
1MiB serialized synthetic input per case,120s outer subprocess timeout, stop on
first unexpected result, save minimal fixture and one diagnosed repair. First
save one case before full enumeration. Independent reviewer validates expected
results and real-path traversal. Genuine browser integration remains live below.

Offline verification: focused child/CLI/unified/schema/OG/Woo/tool regressions;
then python scripts/run_tests.py under repository480s total/240s-family limits.
No skipped asserts or generated fake green reports. Save commands/logs/revision.

Live after offline green: first one Shopify audited domain, max3 requests/2 items,
30s process ceiling,zero retries, save smoke. Next one known HTML product and one
non-product/error URL on one audited domain: max3 requests each, one item,30s each;
browser one known live404 case max1 crawl/30s, if browser available. Total max12
requests, four sequential runs, max120s; budget includes redirects/adapter probes,
so pin explicit platform/URL to avoid broad detection. No LLM, no inference,
BLAS/intraop<=2/inter-op1. Stop after first unexpected failure. Reuse saved URLs
from audit; finalize exact endpoints before execution.429/access/browser unavailable
is blocked live, never pass. Woo midstream404 and missing status use controlled
mechanism coverage; no attempt to induce real merchant errors. Native browser
cancellation integration and broad performance remain future runtime scope.

G1 review clarification: the41-case figure is an upper bound, not a claimed
executed test count. Before red-test authoring, enumerate the exact outcome/status
parameter sets and report actual collected cases; extra combinations cannot replace
distinct seam coverage. Browser one-crawl is not one HTTP request: the12-request
aggregate includes browser navigation/subresource requests and redirects. Enforce
that cap with supported browser interception/accounting, or record this live browser
case blocked on inability to enforce the request budget; do not run an unrestricted
crawl and call it budgeted. Static/control mechanism coverage remains required.

## G2 blocking-gap repair design (before executable additions)

SC01c/FR01b feed seam: transport supplies valid CSV header with0,1,2 rows, CLI
feed --max1. Empty ->E_OPERATION/exit1; one positive record with unknown catalog
coverage ->E_PARTIAL/exit3 with1 retained; two ->capped partial/exit3 with1 retained
and product_budget_reached. Distinct risk: extract_feed has its own projection,
so extract_store/assessment tests cannot catch a forgotten feed path. Existing
native feed cap regression is reused as a control, not proof of unknown/empty.

SC03c/FR01d: real Woo Store API100 schema-valid records then page2HTTP404 vs
page2empty200. Actual pipeline+Click CLI receives transport only. Both retain100
and remain partial (Woo full catalog coverage unverified);404 additionally retains
page-specific404 error and catalog_complete False; empty200 has no errors and
catalog_complete None. Distinct risk: correct adapter errors can be dropped or
misprojected by pipeline/CLI. No stubbing pipeline, adapter, normalizer or envelope.

Five new cases; actual acceptance count now46. This reviewed-gap expansion is
bounded to one small focused run under120s. Original41-case red evidence remains
historical for that test revision. Stress enumeration/budget will be updated to
cover these additional seam risks before implementation stress execution; no
stress pass claimed. Fixture max100 records, two requests, ~64KiB source payload.

## Finalized complementary status mechanism/stress inventory

Acceptance46 covers outcome,atomic/feed/Woo/native seams. Complement only missing
HTTP status classes with10 deterministic cases: statuses302,500,0,'bad',True ×
single/batch. Expected no admitted products in every case; batch complete=False
with diagnostic.302 prevents unfollowed redirect admission;500 is server-error
content;0 missing sentinel;string malformed;bool exposes Python bool/int confusion.
Use existing real browser code/parser and controlled crawler boundary with realistic
Product HTML <=64KiB. No seed variation/load claim. Seed0,one worker,30s subprocess
ceiling,10cases,stop after first unexpected failure,save minimal failure. This
fulfills remaining predesigned admission-status mechanisms;46-case acceptance is
not relabelled as a different stress count. Full driver remains separately required.

Affected-regression compatibility disposition before assertion changes: existing
option-fidelity test returns an empty unknown ExtractionResult from its API spy;
FR01a/b now requires E_OPERATION/exit1 while preserving identical forwarded
options. Existing Shopify discovery transport expectation exit0 now contradicts
FR01c; require exit3 plus retained URLs and unknown-coverage diagnostic. These are
intentional reviewed contract corrections, not unexpected outputs adopted as truth.

Pinned live endpoints before execution: Shopify smoke https://www.allbirds.com
explicit platformshopify,max2,no browser,no identifier enrichment,30s outer ceiling,
max3 actual HTTP requests including redirects. HTML product
https://www.naheed.pk/max-factor-creme-puff-pressed-powder-42-deep-beige and missing
https://www.naheed.pk/shopextract-audit-missing-product-20261101 via extract-one,
no browser,30s/max3requests each. Missing URL is deliberately constructed, not a
historically captured404; actual HTTP status decides whether404 was observed.
Require Shopify partial+positive count, HTML product success iff source accessible
and product supported, missing404 ->E_OPERATION/no product. Three sequential runs,
max9 actual requests/90s. Fourth browser case blocked absent enforceable browser
subresource request accounting; controlled browser status mechanisms remain valid.
A request hook stops before sending request4; save observed URLs/status/counts.

Implementation-review repair design BEFORE tests/source repair:11 distinct cases.
SC02c: ProductGroup exact/list/URL forms×static/browser parser paths (6) preserve
one named group with variant offer; static NotProductGroup negative(1) stays
rejected despite old substring parser matching it. Risk: shared admission narrowed
existing supported schema types. Assertions do not demand new URL/list enrichment.
SC01d: normalize empty/all-dropped(2) via real CLI/normalizer ->exit0,products[],
count0,dropped[]/[0]. Risk: generic emitter wrongly imposed extraction semantics on
normalization; original extraction empty guards still covered by existing tests.
SC02d: batch good+HTTP200policy and good+blankProduct(2) ->one retained,incomplete,
nonempty admission diagnostic. Risk: transport success hides product-admission
failure. Existing good+404 only tests transport rejection, not this interaction.
Actual acceptance count57; complementary status10 unchanged. Seed0,max2 crawler
results/64KiB per fixture,one worker,120s red/green ceilings; no full-driver rerun.
