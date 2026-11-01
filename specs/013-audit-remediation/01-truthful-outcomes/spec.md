# Truthful extraction outcomes — child 01

2026-11-01. Implementation authorized for the umbrella plan; this child is currently
G1 design only. Parent FR01/02/08 and SC01/02/03/13 apply. Baseline90d5bd1,
branch fix/audit-remediation. No change to unrelated profile pilot.

## Outcomes and requirements

FR01a: one outcome assessment: `failed` iff no accepted usable products; `complete`
iff positive accepted products, catalog_complete is exactly True, no errors and no
incompleteness reasons; otherwise `partial`. None coverage remains unknown, never
promoted to True. Contradictory True+errors/reasons is partial. Accepted product
means normalized nonempty title and product-specific source evidence for generic
HTML; existing native source identities remain valid. Quality scores alone do not
certify admission or coverage.

FR01b: preserve ExtractionResult constructor and fields; add a read-only `outcome`
property using the assessment. CLI machine envelope remains schema1.0 and existing
complete/partial/unavailable enum. Positive partial -> ok:false E_PARTIAL exit3 with
data; complete -> ok:true exit0; failed -> E_OPERATION unavailable exit1, data null.
Apply extraction and feed/catalog emission consistently, preserve atomic output
semantics. Existing extract-one raw product return type stays; absent/rejected
page -> existing E_OPERATION. Plain Python extract returns failed result, not a
new exception. Tool empty extraction raises existing source_error; positive
unknown/error/capped result retains graph as partial and diagnostic. Tool graph
schema remains complete/partial. No successful empty extraction catalog handle.

FR01c: discovery is URL enumeration, not product extraction. Python discover
continues list[str] return type with no new completeness promise. CLI discovery
has successful execution but unknown catalog coverage: retain urls/count, add
catalog_complete:null and incompleteness_reasons:[discovery_coverage_unverified],
and emit existing partial envelope/exit3 (including zero URLs). Tool discovery
uses partial with same semantic diagnostic unless a future contract proves full
catalog coverage; list exhaustion is not proof. Discovery exceptions/deadlines
retain existing failures; this child does not redesign swallowed error recovery.

FR02a: both browser single and batch paths accept crawl documents only for
success=True AND known HTTP2xx status. HTTP3xx/4xx/5xx, missing/malformed/zero
status cannot become products. Do not trust crawl success alone. Static httpx
already checks HTTP errors; retain it and test equivalent status admission. Error
pages with plausible Product/OG/CSS text must fail. Redirect's final2xx is allowed.

FR02b: generic OpenGraph admission requires a nonblank title AND explicit product
signal: og:type=product (case-insensitive exact token), or nonempty product-specific
identifier metadata, or explicit product/OG offer amount metadata (presence of zero
counts). Generic website title/image/markdown amount alone is insufficient. Apply
at static/browser and normalization/tool parse seams, so policy-page fallback
cannot bypass admission. Explicit schema.org Product with nonblank name is product
signal, even if offer missing or zero; it may be incomplete but is not a policy
page solely due to missing price. Reject blank-title/no-signal artifacts. A forged
Product declaration on HTTP200 is not fraud detection; that is out of scope.

FR01d: Woo404 on ANY page is source incomplete, retains prior records, sets
complete=False and explicit page-specific error/reason. First-page404 remains
unavailable. Successful terminal empty/short200 page keeps adapter complete;
pipeline catalog completeness remains conservatively unknown where already so.

## Acceptance scenarios

SC01a: products0 × coverageNone/False/True ->failed; products1 × coverageNone/False
->partial; products1/True/no reasons/errors ->complete; True+error or reason ->partial.
CLI and Python outcome agree. Tool semantic projection agrees, with unchanged enum.
SC01b: HTML positive/unknown and API positive/capped both CLI exit3/data retained;
empty CLI exit1; successful empty discovery CLI exit3/data urls=[]; complete
Shopify exhaustion remains exit0. Atomic file gets same envelope as stdout for
positive complete/partial; failed extraction preserves existing target file.
SC02a: browser single AND batch 200 Product accepted,404 Product rejected; missing
status rejected;302 rejected until final200;500 with convincing metadata rejected.
One batch good+404 -> only good record retained, source incomplete diagnostic.
SC02b: generic policy og:title+image/type website+markdown price ->rejected;
og:type product+title+explicit price0 ->accepted; typed Product/name/offer0 ->accepted;
product metadata without title ->rejected; valid native API zero price preserved.
SC03a: Woo page1=100/page2=404 ->100 retained, adapter incomplete+page2 error,
pipeline/CLI partial; first-page404+no accepted fallback ->failed extraction.
SC03b: Woo page1=99 or100+empty200 ->adapter terminal complete; pipeline still
unknown until coverage proof; no false upgrade by source termination alone.
SC13a: new offline fixture labels synthetic; saved historical defects remain
historical. Review only actual current outcomes, not invented live store claims.

## Boundaries and compatibility

Intentional correction: HTML unknown-coverage runs/discovery now exit3 instead of0;
zero complete catalogs no longer extraction success. CLI consumers must accept
retained partial data. No Product/Variant constructor or feed format changes.
Do not broaden into price/currency fixes, field coverage, max_products propagation,
partial timeout checkpointing, robots policy, stdout/seeder runtime repair, or new
readiness. Resource and deadline contracts remain otherwise unchanged. Native
tool source pipeline differs from Python pipeline: align semantics explicitly,
not by assuming shared implementation. Existing saved profile pilot gate unchanged.

## Workflow

G1 design/research/tasks review now. Skeleton+red tests then G2; components thenG3;
implementation; affected regressions/full driver; bounded live; independent final.

## Compatibility refinements from independent implementation review

SC02c/FR02b: existing explicitly supported named schema.org ProductGroup survives
admission in exact type,list and schema.org URL forms; unrelated substring types
(e.g.NotProductGroup) are rejected. No new variant/enrichment policy is introduced.
SC01d/FR01b: failed-empty extraction applies only to extraction/feed entry points;
normalize [] and all-dropped [{}] remain successful empty reports with exact
product_count0 and dropped_indices[]/[0]. Generic emit_result is not an extraction
validity boundary. SC02d/FR02a/b: HTTP200 policy/blank product admitted transport
but rejected metadata marks batch incomplete, retaining legitimate siblings and
useful rejection diagnostic. These refine reviewed compatibility, not new scope.
