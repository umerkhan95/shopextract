# Verification evidence — planning investigation

2026-11-01; current source90d5bd1, historical audit461ec38. Source unchanged.

| Check | Actual result | Scope / limits |
| --- | --- | --- |
| First smoke: production CSS Normalizer and QualityScorer | Reproduced3,720=>3.720; Rs.3,720=>0 rejected; DE3.720,00=>3.72000; junk score1.0 | evidence/smoke.json; synthetic offline; not acceptance green |
| Bounded production-path diagnostics | Saved root ItemPage0/@graph1; policy OG retained; unsupported USD scalar; missing Woo brand/variants; category2; stock default; feed missing brand/ID; invalid-currency fixture passes validation; empty success; Woo100 then404 complete=true | evidence/diagnostic.py/json; transport and emission boundaries patched, no algorithm replaced; not full CLI/browser coverage |
| Historical evidence selection | Eight named audit files hashed; counts and selected response summaries retained | evidence/historical-index.json; original data remains temporary; not current live proof |
| Current source review |35 findings classified R/C/H/Q/U | research.md exact source line references; counts/precision/timing qualified |
| Independent planning review | PASS, planning only | reviews.md; no child implementation verdicts |
| Full repository test driver | Not run, not applicable to docs/diagnostic-only planning deliverable | Mandatory for future production child slices |
| Fresh live verification | Not performed; not applicable to verification-plan delivery | Present store state/performance unverified; historical captures labelled historical |

## Reproduce bounded diagnostic
From repository root, configured .venv, Python3.10. Initial import without
PYTHONPATH failed; one diagnosed environment repair sets PYTHONPATH=src. Installed
requests emits dependency-version warning; no network is used or environment changed.

```sh
PYTHONPATH=src OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 TOKENIZERS_PARALLELISM=false .venv/bin/python specs/013-audit-remediation/evidence/diagnostic.py
```

One process, fixed fixtures/seed0, two controlled Woo responses, no external network,
no models/downloads. Capture timestamps in synthetic metadata change on replay;
they are labelled diagnostic captures, not real-store observations. Final replay is planned with a30s subprocess timeout; its result will be stored
in evidence/replay.json. It is not yet a passed check.

Mechanism diagnosis: reproduced only the listed functions and controlled Woo loop.
Stress: not run in this planning task. Live: historical evidence only. Child stress
and full integration evidence remain planned, never silently promoted to pass.
Exact session input/output counters unavailable; this limitation is recorded rather
than estimating weekly quota use.

## Final bounded replay and handoff
Actual replay completed with exit0 in3.353s under30s timeout. Seven diagnostic
assertions reproduced the expected current defects/control outcome; no network
requests. See evidence/replay.json and replay.stdout.log/replay.stderr.log. This is
diagnostic confirmation, not repair acceptance. Synthetic capture timestamp in
diagnostic.json changed on replay after the planning review; diagnostic script and
behavioral results stayed unchanged. G1 hashes describe the artifacts at review time.
`git diff --check` passed; no src/ or tests/ modifications. Existing unrelated
spec012 edits remain present and untouched. Independent planning G1 passed; all
child implementation gates remain pending.

## Final integration repair verification
First full configured driver source-frozen: main14failed/2070passed/9setup errors
236.62s, driver238.95s; oracle/maintenance NOT RUN under configured fail-stop.
Exact logs/report: evidence/final-driver. No live run during failed offline gate.
Independent integration G1/G2/G3 amendment PASS in reviews.md before repairs.
New cache/capability smoke4passed1.51s; first attempt1failed/3passed exposed store's
additional complete-only guard, addressed with optional extract-only flag/default
preserved and one shared shape predicate. File-backed spawned diagnostic saved;
stdin spawn probe invalid, not counted as proof. Existing category namespace,
cache corruption, atomic rollback and common-reader boundaries retained.
ALL failed/setup node IDs (old empty-success test renamed to approved errorpolicy),
plus cache/capability/19discovery:45passed40.99s under120s, exact argv saved in
evidence/integration-focused-command.json and log integration-focused.log.
Then explicit lower-only legacy resource fixture reuse (actual32MiB boundary still
in3 money acceptance cases and was also green in45-run), stronger exact11-ID set:
4passed3.85s evidence/integration-resource-controls.log. No production/driver caps
increased. Fresh full driver/final functional review still pending.
Integration functional review caught advisory call-site leakage from broad edit.
Before repair actual injected advisor publication+reuse control failed NameError
(mode out of scope), evidence/integration-advisor-red.log0.99s. Exact two advisory
calls restored to original complete-only defaults; all optional flags now only
_source get/put (mode and page_only locally defined). Same actual publication,
second cached reuse and both source-cache controls3passed1.39s in
integration-advisor-green.log. No model/provider process launched. Reviewer
re-review/fresh frozen full driver pending; no broad success inferred.

## Recurrent full-main time ceiling / scoped serialization repair
Fresh source-frozen driver2 timed out239.06s at93%, completed nodes all passing;
current node truthful Woo100 later404 control. Oracle/maintenance NOT RUN, no live.
One original real Woo100 control cProfile under60s passed3.41s. Saved pstats+summary
identify portable projection1.457s,57,842 deepcopy calls/400 contract validations;
not proof of entire driver cause. Independent projection G1/G2/G3 PASS before code.
Four exact standard-asdict/order/all-field/contract/mutable/unsupported/cycle cases:
2red2controls0.25s before code;4passed0.12s after. First implementation attempt
3failed1passed0.38s because Python3.10 Enum lacks __deepcopy__; standard reducer and
explicit overrides now respected (attempt log overwritten by final green, not a
separate preserved trace). Shared immutable projection at3 serializer call sites;
no global cache, limits or supported public types changed. Existing validations
retained, duplicate synchronous validation reused only after trust_view.
SAME Woo100 before/after profile experiment passed: calls57,842→8,942;
contract validations400→300; portable cumulative1.457→1.076s, full profiled
process5.176→4.826s. Single controlled sample, no whole-driver guarantee.
Original30s actual25Products/265variants fullvalues/entirecontracts/analyzer/CSV+
sidecar reload passed again; prior report preserved evidence/actual-audit-before-
projection.json, current02 actual-audit-roundtrip.json and after-projection.log.
Spy now exercises module deepcopy fallback with mutable str-subclass positive
control; all selected portable/evidence/reliable/money cases240passed12.44s
under120s, projection-affected argv/log. Functional re-review/fresh driver pending.

Driver3 whole report: main2099passed231.66s; reliable-oracle24passed67.09s;
maintenance101passed5failed40.40s, total344.30s. Offline gate not green then;
no live requests. Maintenance amendment G1/G2/G3 independently passed before code.
Focused4red2control4.25s (maintenance-integration-red.log); narrow store reason
selection now distinguishes inferred generic partial from caller-explicit reasons.
Durable model stops outrank only inferred source_partial; coverageFalse/statepartial,
usage, settlement and dispatch assertions unchanged. Robots-first fixture declares
404 and exact request accounting. Same6 actual cases passed3.66s
maintenance-integration-green.log. Functional re-review/fresh driver pending.

## Final live execution pin (before requests; offline full-pass prerequisite)
Use existing01 live_driver.py Shopify case first: https://www.allbirds.com,
explicit Shopify/max2/no-browser,3 attempted HTTP requests max,20s source/30s
outer process, no paid/model request. Record statuses/outcome; stop new merchant
requests on unexpected/inconclusive result. Only after success may follow scoped
Woo smoke https://woocommerce.com (historical saved perf-discovery Woo origin),
explicit Woo/max2/no-browser, same3requests/30s. No claim variant-detail429 or
browser status reproduced live; reviewed synthetic mechanisms cover those.
Known HTML/missing Naheed URLs in01 script remain optional within original3req/
case and domain budget, not a mandatory sweep. Discovery, if still eligible, uses
one original audit domain with explicit borrowed DiscoveryClient(max_requests=5),
30s/no browser; count robots/redirects too, record actual policy separately from
historical Disallow claim. A non-observable browser subrequest budget is BLOCKED,
not a live pass. Do not expand beyond these prior per-adapter/live ceilings.
Final discovery target pinned from saved disc_khaadi_50.out before request:
https://www.khaadi.com, explicitMagento,max2,borrowed DiscoveryClient cap5,
20s source/30s outer. Assess current robots policy/no forbidden requests/emission;
empty bounded discovery is not failure if policy/budget prevents coverage. If
policy itself unobservable, record inconclusive; never infer historical Disallow.

Full driver4 PASSED2229cases344.10s before compression amendment (main2099,
oracle24,maintenance106). Actual bounded HTTP live: Allbirds200→2partial,
Woo200/per_page2→2partial, Naheed product200→one, Naheed missing404→no product;
one request each, all assertions passed. Khaadi discovery robots200 once then
policy unavailable/no forbidden fetch; inconclusive, attribution NOT established.
Compression G1/G2/G3 passed after real HTTPX2red1control0.37s; _read decoded copy
now removes only encoding/oldlength from copied Headers (multiplicity preserved),
status/request/cookies unchanged. Existing decoded cap enforced first.38 actual
compression/discovery/tool controls passed6.09s (compression-green.log).
Source changed after driver4; fresh full gate required, no retroactive pass.

One bounded LOCAL SDK capability inspection, no launch/network: hook exists at
async_crawler_strategy.py615, receives ALREADY created context; BrowserConfig has
no service_workers parameter, BrowserManager.new_context uses context_settings
without any service_workers forwarding (inspectionJSON records file/line evidence).
Thus supported production configuration does not establish blocking worker-owned
requests before contexts exist. Page route hook alone cannot prove global request
ceiling including service workers; browser merchant live remains BLOCKED rather
than inventing a counted pass. Existing deterministic browser admission/merge
mechanisms passed offline. No custom manager/new browser feature added.

Primary authorized ONE retry of failed discovery after fresh offline green only:
remaining4 HTTP attempts (first1+retry<=5 total),20s source/28s outer (first~0.76s),
same Khaadi target, no other merchant expansion. Preserve first inconclusive file;
record current response encoding/policy for retry without attributing old response.

Latest driver5 source-frozen main timed out239.16s at80%, starting restore-GTIN
control; completed nodes passed. Oracle/maintenance NOT RUN in5. Driver4 full2229
pass predates compression fix and is not substituted. No merchant retry performed.
One post-timeout ps snapshot has unrelated Logitech updater68.7%CPU; this does
NOT establish cause and no other process was touched. Current source/tests unchanged
and diff-check0errors;282-file hash manifest explicitly labels pending latest-full
status. All implemented fixes have functional reviews; final gate assessment pending.

Independent final assessment completed in reviews.md: implemented functional
stages PASS; G4/latest-source full-resource/final PENDING, no latest-full green
inferred. Reviewer verified all282 current manifest hashes and accepted four
narrow HTTP livepasses, retaining Khaadiinconclusive/browserblocked. No new source
blockers, optimization/sweeps not warranted by unproven host cause. Any separately
primary-authorized unchanged rerun requires demonstrated settled host activity.
No further source/test edits or merchant requests after driver5.
