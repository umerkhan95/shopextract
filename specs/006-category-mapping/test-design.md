# Category behavior/test design — before task breakdown

## Bounded live diagnostic supplement

After the reviewed six-attempt live sample, Magento returned products but companion
normalization rejected with CategoryError; the first driver saved only its class.
Expected diagnostic: exactly one remaining Magento request, same pinned query, two
products, 10s/request and existing cumulative live12/2/120s limits. Save original
captured raw data (<=2MiB) before normalization, preserving URL/time. Replay that
fixture offline and record whether the strict256KiB companion cap is legitimately
exceeded or another validation contract fails. A cap rejection is explicit unavailable,
not category success or an automatic limit increase. Preserve the first inconclusive
result. Any actual code defect returns to a regression case and affected review;
no additional live attempt beyond the platform's second request is authorized.

All checks PLANNED, no result implied. Requirements precede architecture/tasks.

| SC | Distinct risk and independently expected outcome | Proposed proof |
|---|---|---|
| 01 | Shopify custom Laptop, Woo Notebooks and declared Magento node map to a configured laptop ID only with explicit trusted namespace/version rules | same three targets, retained original observations |
| 02 | Woo sibling Boots/Sale, BigCommerce two memberships: no invented Boots > Sale path | actual adapters and exact two membership vs ancestry assertions |
| 03 | ID 12 reused in two stores/platforms cannot share a mapping without scoped rule | scoped collision and malicious alias fixtures |
| 04 | Shopify product_type and collections are not category taxonomy IDs | supported public/custom and separately authorized standard-node cases |
| 05 | missing/null/empty/unknown/default differ; category absence never implies known generic domain | source parser/support state cases across six families |
| 06 | conflicting mappings remain ambiguous, duplicates/reordering stable | fixed permutations and frozen expected target set/status |
| 07 | escaped separators/Unicode/locales and cyclic/truncated parent links remain data, not executable paths | finite adversarial tree/label fixtures, no regex backtracking sweep |
| 08 | pagination, tree-depth and denied origins cannot bypass existing HTTP/job limits | actual guarded transport + real adapter, zero-cap and at-limit cases |
| 09 | observed source category and derived mapping have separate evidence/version provenance after reopen/export | production portable persistence path, not copied fake reports |
| 10 | same category with RAM/boot-size conflicts remains review; mapping never overrides matcher or creates undeclared profile | real matcher and maintenance integration |
| 11 | opt-in behavior preserves old Product/Variant constructors and existing feed/tool shape | small baseline and affected regression checks, no duplicate full sweeps |
| 12 | each adapter produces shared typed source facts; shared mapper is called once | reviewed ownership/dependency model, controlled native/structured fixtures |

Platform authors must refine exact realistic source fixtures and expected outcomes
before generators, tasks or source changes; independent reviewer challenges gaps.
Only unavailable HTTP/clock boundaries may be mocked; parser, mapping, normalization,
evidence and profile mechanism under test must be real.

## Initial resource envelope (final execution requires reviewed exact case list)

Start with one tiny saved smoke. No inference/provider/token spending. At most three
read-only platform agents concurrently (user explicitly authorized parallel agents),
one local test/driver process at a time; CPU intra-op<=2/inter-op<=1 and BLAS/tokenizer
workers capped. Proposed deterministic seed26, <=24 distinct mechanism cases,
<=120s aggregate driver, <=256KiB per fixture, <=8MiB fixtures total. Do not expand
or treat limits as approval before reviewing exact source/fixture cases. One diagnosed
repair per blocker; preserve failures and continue independent work where possible.
Live applicability and endpoint/credential/request caps must be designed from actual
platform findings before implementation; missing public access remains an honest
limitation, with deterministic real-code synthetic proof for unavailable behavior.
Actual session token counters unavailable; no quota estimates. Reuse saved sources.

## G1 concrete mechanism matrix — planned, not executed

The rows below consolidate platform proposals into 24 distinct mechanisms. Each row
states independent expected outcomes before fixture/test authoring; platform discovery
files retain source references and native realistic payload shapes. Source payloads
are schema-valid unless explicitly called malformed. No assertion infers truth from
legacy category_path. FR01–14/SC01–12 are jointly covered below.

| Case / FR / SC | Exact input and independently expected result | Distinct risk / real path |
| --- | --- | --- |
| C01 FR01,02,09,14 / SC04,11,12 | Shopify captured product_type=`Boots > Sale/Outdoor`: one custom merchant label verbatim, no standard ID/edges/path; default legacy single-item path unchanged; public absent category unavailable | Custom/standard confusion; real Shopify normalize wrapper |
| C02 FR01,02,04 / SC02,06,12 | Woo categories IDs7 Boots,9 Sale; [7,9] and [9,7,7]: same two semantic memberships, zero parent edges, raw pointers retained | Sibling/order confusion; real Woo adapter |
| C03 FR01,02,14 / SC02,08,12 | BigCommerce opt-in native page101 contains CategoryConnection nodes7 Boots,9 Sale, hasNextPage=false: two complete memberships, no path; actual outgoing reviewed query selects only verified fields | Fixture-only integration; actual extractor + guarded transport |
| C04 FR07,09,14 / SC08 | BigCommerce one node7, hasNextPage=true/endCursor=c1: supported node7, membership partial/category_budget_reached, zero followups; product page may finish independently | Hidden N+1/false completeness; extractor + adapter |
| C05 FR01,02,14 / SC02,08,12 | Shopware categoryIds=[A,B], categoryTree=[R,A,B], categories=null: two ID memberships, separate three-ID index, zero edges/paths, labels unavailable; default fixed body unchanged | Ancestors leaked into membership; real Shopware |
| C06 FR01,02,14 / SC02,08,12 | Magento opt-in `categories { uid name }` returns UID X/Tops,Y/Sale; default query unchanged. Exactly two scoped memberships, no path/parent inference, nullable name stays unknown, no Store header or tree request | Native Magento acquisition/scope interaction; actual extractor/normalizer |
| C07 FR01,02,14 / SC02,07,12 | JSON-LD categories=[Boots,Sale] => two unordered labels; category URL https://example.test/tax/12 => one opaque reference and zero HTTP; `A\>B / C` raw label unchanged | Generic delimiter/URL corruption; schema parser + wrapper |
| C08 FR01,03,14 / SC01,04,12 | Google XML/CSV google_product_category=2271 plus product_type=Merchant > Dresses: standard declared ID string2271/version unknown and separate custom label; explicit trusted unknown-version selector can map ID and separately declared full Google path to same target | Parser omission/namespace conflation; feed parsing before capture |
| C09 FR01,03 / SC03,07 | CategoryCode codeValue12 inCodeSet X vs Y yields unequal refs; missing code set retains code claim but cannot match exact namespaced rule | Object/stringification/global-ID collision; generic real adapter |
| C10 FR01,09 / SC05 | Fixed missing/null/empty-string/empty-list/malformed-object category inputs retain five distinct raw states; empty text vs empty list retain representation; malformed category preserves valid product siblings | Defaults become evidence; six adapters with appropriate native shapes |
| C11 FR01,09 / SC05,09 | Captured category ID changed after capture or absent due retention => unsupported ID, no exact-ID match; retained supported label may survive; expired evidence => unavailable for mapping | Fabricated support; real capture/Normalizer/evidence path |
| C12 FR01,02,10 / SC03,07 | ID7 at shops /a and /b unequal; endpoint aliases do not change configured shop; known channel1/locale-de vs unknown preserve assignment scope, unknown fails explicitly known-scoped selector; same global standard ID/version shares term identity while assignments differ | Scope/default leakage; shared refs + mapper |
| C13 FR01,02,09 / SC07,08 | Explicit root1->7 yields supported path[1,7]; orphan parent99 => unresolved partial path, root unknown; cycle1->7->1/self-cycle => invalid ancestry, no trusted path; hasChildren at depth cap => partial | Fake root/nontermination; shared finite ancestry validation |
| C14 FR03,10,11 / SC01 | Trusted registry v1 target laptop; exact Shopify custom label Laptop, Woo term Notebooks ID12, Magento scoped ID12 rules produce same configured target only within their selectors | Six independent mappers/implicit aliases; one shared mapping path |
| C15 FR04,11 / SC06 | Same source assertion matches target sets {A,B} and {B,C}: ambiguous candidates sorted[A,B,C], both rule IDs/versions retained; {A,B}/{B,A} agreed mapped[A,B]; distinct source members mapping A and C => explicit product union[A,C] | Hidden first-match/intersection vs valid multimap |
| C16 FR03,11 / SC05,06 | Unmatched supported term => unmapped; missing source => unavailable; invalid target/duplicate rule ID/unknown config keys => config rejection before network; explicit unknown-version permission required | Guessed mapping/unvalidated config; real validator + extractor entry |
| C17 FR05,12 / SC09,11 | Companion encode/decode/reopen restores raw source representations, evidence refs, support states, mapping version and Product unchanged; ordinary product_to_record remains old schema; old reader rejects envelope | Silent dynamic sidecar loss; strict actual codecs |
| C18 FR05,12 / SC09 | Change any Product field after companion construction => encoder rejects original immutable binding mismatch instead of recomputing; changed product digest/scope/dangling evidence ref/unknown envelope version rejected, not repaired on load | Stale companion reattachment; codec integrity |
| C19 FR05,13 / SC09,10 | Same policy/scope cache reopen hits only after origin authorization; changed rule/registry/scope/profile-binding digest misses; malformed companion misses rather than legacy fallback; checkpoint preserves mapping version on retry | Cache policy laundering/lost sidecar; real store/source/domain process |
| C20 FR06,13 / SC10,11 | Legacy explicit hardware-v1 job unchanged; category-enabled hardware-v1 + mapped footwear binding => review conflict; category missing/ambiguous => review even with explicit profile; agreeing mapping still cannot bypass RAM/boot-size/identity/variant safeguards | Category grants profile or field authority; actual maintenance/matcher |
| C21 FR07,14 / SC08,11 | Original BigCommerce query allowed; reviewed opt-in constant allowed only category mode; altered query/mutation and unauthorized origin denied before wire; original Shopware body allowed, unreviewed categories association/page21/limit21 denied | Native read guard broadening; real guarded transport |
| C22 FR07,09,10,12 / SC08 | Terms99/100/101, relation refs199/200/201, depth7/8/9: below/at preserved, excess bounded partial reason; config999/1000/1001 entries: excess rejected; 262143/262144/262145 encoded bytes: excess rejected; zero optional category limit performs zero optional acquisition | Off-by-one/resource overrun; bounded driver real parser/codec/transport |
| C23 FR01,09,14 / SC05,07 | XML Home &amp;gt; Bags decoded once to literal &gt;; CSV quoted comma retained; absent feed element/column vs blank distinguished; repeated OG Boots/Sale retained separately or explicit incomplete-loss; unsupported from_metadata/LLM never observed | Entity recursion/parser loss/model authority; real generic parsers |
| C24 FR05,07 / SC09,11 | Category mode false produces existing Product constructor/feed/tool/cache formats and request sequence; category enabled encode failure before checkpoint leaves no false complete record, retry after same policy produces one bound companion | Compatibility/persistence failure interaction; actual export/job/checkpoint |

A test may parameterize the fixed boundary inputs above; it must not claim each
parameter/seed is a new mechanism. Fixture author records the exact bounded parameter
count before execution and reviewer checks expected outcomes independently. No >24
mechanism expansion without amended design and affected gate review.


G1 error/completion variants refine C03/C06/C10, not new mechanisms. Six added fixed
variant families remain within100 total invocations and120s; fixture author records total count:
- C03a: BigCommerce data has product101/name valid, categories node7 ID valid/name=null,
  pageInfo.hasNextPage=false, errors.path=[site,products,edges,0,node,categories,edges,0,node,name].
  Product101 and supported ID7 survive; failed label unsupported; memberships partial
  with category_source_error, never complete even though hasNextPage=false. Zero retry.
- C03b: BigCommerce data has valid product101 and node7; pageInfo absent, then malformed
  {hasNextPage:"false"}. Both retain node7; completeness unknown with
  completion_metadata_unavailable, never complete/observed-empty. Two fixed inputs.
- C06a: Magento data.products.items has valid SKU/name and categories=null plus relevant
  errors.path=[products,items,0,categories]. Product retained; categories unavailable,
  no observed empty, source diagnostic retained, zero fallback/default-query retry.
- C06b: Native field-validation rejection data=null/errors unsupported categories, then
  HTTP403 denial on next separately designed input. No new product invented; any prior
  captured page products retained, extraction incomplete/source error and categories
  unavailable. Exactly one failed attempt per input, no automatic retry/fallback.
- C10a: BigCommerce explicit empty edges and hasNextPage=false with category-level error
  is unavailable, not known empty/complete. Magento categories=[] with no relevant
  errors is observed-empty membership only; absent/null remains unavailable. Error
  with no usable path conservatively prevents category completeness across response.
- C10b: Unrelated GraphQL error path outside categories with product still valid and
  independent nonempty categories + valid completion metadata preserves supported
  category facts/completeness; category parsing does not erase valid sibling facts or
  infer that unrelated failed fields are supported.
These execute actual native request/response parsing and capture/adapter/guard paths.
Unavailable HTTP is the boundary fixture only; do not mock native error interpretation
or manufacture diagnostics. Total parameter invocations must be explicitly counted
within100 (six variant families contain the fixed subinputs stated above).

## Red and production-path proof
After G1 the shared skeleton author writes executable acceptance tests C01/C03/C14/C17/
C19/C20 first, with actual missing-public-wrapper/codec/mapping/cache behavior failures
saved to artifacts/category-mapping/red.log. Remaining designed cases are added before
their implementation; imports/stubs must fail explicitly, not fabricate success.
Fixture author uses sanitized saved samples/native schema shapes and capture() with
explicit synthetic source metadata. Mock unavailable external HTTP only; no fake
mapping/normalization/codec/cache/maintenance mechanism. Controlled transport request
logs prove exact pinned query, limits and zero followups. C11/C18/C20/C21 are critical
negative assertions; demonstrate detection using a narrowly injected unsupported source,
stale binding, policy mismatch and altered query respectively, not duplicate algorithms.

## Final bounded envelope for review
Seed26, one sequential driver/process, <=24 mechanism cases and <=100 fixed parameter
invocations, <=100 nodes/200 relation refs/depth8 normal fixtures (one-over explicit
boundary input allowed), <=256KiB/fixture, <=8MiB aggregate saved fixtures, <=120s
aggregate mechanism/stress driver, <=15s per invocation; stop/save first failure.
Boundary codec bytes may require 262145-byte explicitly labelled oversize record;
config entry-boundary fixtures may contain1001 entries but remain below1MiB. No local
inference/provider calls; CPU threads<=2, interop1, BLAS/tokenizer/download workers1.
One diagnosed repair per blocker, rerun affected checks only. Saved baseline normalize
smoke44 passed/0.15s is compatibility baseline, not category proof. Actual session
counters unavailable, no quota percentage estimate.

## Bounded live verification (after offline pass)
Sequential <=12 actual HTTP attempts total, <=2 attempts/platform, <=2 retained products
per platform, 10s/request,120s aggregate, zero retries beyond budget, no model/browser
fallback or writes. Root selects explicit already authorized source URLs from saved
platform cases and records target/access prerequisites before dispatch. First one
public Shopify/Woo smoke must be saved before expanding. BigCommerce requires explicitly
published/configured Storefront token and approved endpoint; Magento public schema/store
scope as findings; Shopware published/configured Store API key; no Admin acquisition.
Generic uses one explicit permitted structured feed/page. All native acquisition uses
finite opt-in query constants and no tree followups. Each platform reports observed
source relation and evidence support; available incomplete native categories must stay
partial. If resolving token/discovery would consume its two requests, record blocked
rather than exceed caps or misreport adapter success. Missing access or target transition
stays blocked/inconclusive; reuse passing C01–24 mechanism evidence separately, never
call fixture replay live or waive an explicit real native observation requirement.

## Interim review repair cases — designed 2026-10-17 before edits
- C06/C11 nonnull native failure: captured Magento categories UID MTI=/label Boots plus unaffected sibling Other; inject localized uid then name error, ancestor/category error and global error. Failed facet remains inspectable but UNSUPPORTED with rejected conversion and cannot match its exact rule; unaffected facet/sibling stays OBSERVED and matches. BigCommerce same paths use the identical shared rejection primitive. This closes null-only test blind spot.
- C13 endpoint mutation: real captured Shopware parent7->child12; replace only declared bound parent with99 while raw/outcome/evidence remain7. Real validator, mapper and companion binding must reject, rather than accepting a new proven edge; test parent and child independently.
- C13/C22 finite ancestry: valid explicit chains containing7/8/9 edges, all nodes included and no invented root declaration; maxdepth8.7/8 edges remain complete explicit-edge membership;9 partial/category_ancestry_depth_reached. Missing parent99 is partial/category_parent_unavailable, retains supported declared edge but zero ordered paths/root claims. No HTTP/tree generator. These boundaries distinguish endpoint support from graph closure.
- C20 real engine/matcher: category-enabled saved trusted config agrees with explicitly selected hardware/footwear profiles. RAM8GB vs16GB; bootUK8 vsUK9; same description but conflicting product identity. Existing matcher/field safeguards must emit needs_review and no proposed correction even though category mapping agrees. Include a profile-binding conflict with supported exact identity to prove category veto in the real engine. Use controlled captured companions at the existing parser boundary and real Store/Engine/reconcile/matcher, no mocked algorithm.
- C24 atomic failure: inject one real companion encode failure before successful source checkpoint, then same-policy explicit retry; zero committed successful source/checkpoint/cache from failed encoding, one successful committed companion after retry. Separately crash immediately before checkpoint; pending outcome never becomes committed/cache success; retry same policy cannot duplicate successful companion. Failure injection at codec/checkpoint boundary only; real parsing/evidence/persistence retained.
- Driver contract: each collected pytest node gets <=15s wall time and total collection+all nodes<=120s; one sequential child session, group kill on timeout/failure and wait/reap child. Bound each retained log to64KiB and all retained driver logs to1MiB; save each node outcome/elapsed and stop first failure. Fixed controlled timeout-child test proves no auxiliary descendant survives; do not execute mechanism driver until reviewer approves revised source/plan.

C24 parent-boundary rereview refinement: corrupt the actual returned child envelope original_binding WITHOUT calling a codec in the injector. Parent must strict-decode and verify saved config/scope before accepting fresh source results, checkpoint or cache. Current late reconciliation rejection is insufficient: assertions independently require no committed source/result/cache. Same saved-policy explicit retry must produce one valid committed companion. Reuse strict decoder plus the same category collection/policy validator for fresh and cached data; legacy source path remains unchanged. This replaces the earlier preemptive codec-fault fixture which masked acceptance ordering.

## One diagnosed mechanism-runner repair — design before implementation
First approved attempt stopped at aggregate120.019s:42 invocations started,41 passed and one interrupted when only2.4s remained. Per-node process/import overhead exhausted budget; last reason must be aggregate_timeout, not invocation_timeout. Preserve original status unchanged in archive and annotate correction separately. Archive status/plan/collection/source checkpoint with SHA256/log manifest before overwriting any main status; original node logs stay at their saved paths.

Reuse exactly41 completed successful node IDs only after all saved source/test digests match current source; no completed tests restarted. Keep original75-node/24-mechanism plan. One repaired attempt selects only34 remaining exact nodes, including interrupted C16. Cumulative invocation upper bound42+34=76<=100, and each attempt stays bounded120s; combined actual elapsed necessarily exceeds120s and must be reported as split evidence rather than a clean75-case single-run pass.

Use one pytest session for collection+34 nodes. A small plugin only validates exact remaining collection (<=100) and atomically saves bounded per-node start/report/end/outcomes. Outer independent selector watchdog reads progress: collection15s, setup/call/teardown invocation15s, aggregate120s, stop first failure. All timeouts kill whole child sessiongroup and wait/reap with existing cleanup. No in-pytest timer/GIL dependency or new subprocess per node. Retain one64KiB session log and bounded75-node progress; preserve original logs. Failure reason distinguishes aggregate_timeout from collection_timeout/invocation_timeout. No source/fixture/assertion/limit changes. Reviewer must approve before execution; only static preparation now.

C22 byte-fixture correction designed before edit: wrapper Product has dynamic evidence_contract retained by strict Product codec; dataclasses.replace drops that attribute while initial envelope length includes it. Padding therefore undershoots exact boundary. Deep-copy the original Product including dynamic trust state, then set only its initially empty description to target_size-initial bytes. Preserve all three exact262143/262144/262145 expectations and real bind/codec cap checks unchanged. This is a deterministic fixture-construction repair, not a production codec/cap change. Archive attempt2 status/progress/log/hash evidence first; retain59 unique completed passes. Run only three byte variants. Any remaining-node driver continuation needs fresh reviewer/root authorization; no restart here.

Final bounded completion preparation: root authorizes preparation only for exact13 unseen nodes. Reuse59prior unchanged cases plus3targeted byte cases using archived whole-file/reverse-patch proof; no completed node repeated. New fixed completion manifest freezes all75 original nodes,62 successful nodes,13remaining,64 prior starts/proposed77total. Revalidate archived attempt metadata/logs, source hashes and one reviewed fixture diff. Existing independent watchdog/session cleanup/budgets unchanged. A new exclusive completion marker permits only this fixed manifest; no generic restart/resume option. One120s attempt, stop/save first failure and record blocker if it fails. Root execution requires reviewer approval; no tests/source/live work during preparation.
