# Reusable component model — G3 ready

2026-11-01. G2 PASS prerequisite recorded in reviews.md. Author
/root/audit_research; independent reviewer /root/audit_plan_review. Documentary
component stage only; no production implementation.

| Component / owner | Existing behavior to reuse | Consumers and boundary |
| --- | --- | --- |
| ExtractionResult / `_models` | Existing products, errors, tri-state catalog_complete and reasons; preserve constructor/identity | Python API retains inspectable result; additive outcome property delegates to assessment; no mutation or hidden I/O |
| Pure outcome assessment / `_outcomes` | Existing complete/partial/failed meaning from reviewed contract; existing reasons/error collections remain authoritative | Model, CLI extract/feed, tool native sources; one private function signature in skeleton.md, no CLI imports into core/tools |
| Product source admission / `_product_admission` | Existing schema.org typing and unified browser product signal intent, refined to distinguish unsupported generic metadata | Unified static/browser and generic normalizer/tool domain parser; pure bool decision, no fabricated fields or source capture |
| Crawl HTTP gate / `_product_admission` | Static httpx rejects HTTP errors already; browser result exposes success/status | Browser single and batch call same gate before parsing; unknown/error response rejected, batch retains good siblings with incomplete error |
| Normalizer/ConversionOutcome / `_normalization`, `_normalize` | Source selections, accepted/rejected conversion outcomes, defaults explicitly unsupported | Reuse for factual support and normalization; admission runs before generic fallback can invent a product. No monetary/default changes in child01 |
| Capture/evidence/identity / `_capture`, existing portable codec and identity modules | Capture provenance, canonical identity and exact Decimal transport | Existing parser/normalizer paths remain responsible for facts; admission does not rewrite captures, prices, IDs or timestamps |
| CLI projection / `_cli_extract`, `_cli_data`, `_cli_core` | Existing E_OPERATION/E_PARTIAL enums, response shape, atomic_json, serialization | Extraction/feed use shared classification; discovery keeps separate unknown-coverage semantic; generic make_response unchanged for unrelated commands |
| Native tool projection / `tools.sources.GuardedSources`, `tools.domain.DomainAdapter` | Guarded transport, auxiliary real parser, ToolError, retained graph complete/partial, diagnostics | Translate native source state into same assessment inputs; no CLI dependency. Empty extraction source_error before catalog retention; positive unknown graph partial |
| Woo pagination / `extractors.woocommerce` | Existing bounded page loop, capture and ExtractorResult aggregation | Source404 consistently incomplete with page-specific error and existing records retained; pipeline projects errors/unknown proof without treating adapter termination as catalog proof |

## Ownership and lifecycle

Pure helpers contain no models, browser imports, network, cache, global mutable
state, process/thread allocation or background lifecycle. They inspect per-call
inputs and return deterministic classification/admission; callers own diagnostics.
Source adapters own HTTP/crawler clients and cleanup as before. Native tool runtime
continues owning auxiliary processes/retained graphs; no new persistence component.
CLI owns encoding/atomic file replacement only after outcome is known. Existing
capture objects remain source support, never a place to store synthetic certainty.

## Error and compatibility contracts

Assessment is not an exception generator: zero failed, positive without proven
coverage partial, positive clean proof complete. Python retains result; CLI maps
failed to existing E_OPERATION and partial to retained E_PARTIAL; tools map empty
to existing source_error and incomplete positives to partial graphs. Transport
failures retain existing exception/error ownership; no silent successful fallback.

Admission rejects unusable generic metadata and invalid/unknown HTTP statuses;
explicit free Product/offer remains admitted. Rejection does not create a zero
price or fabricated product record. Browser batch records failed admission as
incomplete with retained legitimate siblings. Product constructors, identity,
default feed formats, response enum and capture codecs remain unchanged.

New shared helpers are justified by concrete consumers across model/CLI/tools and
static/browser/normalization seams. No public framework, plugin registry or
configurable policy engine is introduced. G3 review checks this component map
against skeleton signatures and all46 designed acceptance cases; implementation,
green/stress/full-driver/live/final evidence remain pending.

G3 compatibility clarification: the generic HTML/metadata admission policy must
not accidentally reject native API, feed or explicitly supported portable record
formats merely because they lack OG/schema.org keys. Apply source-appropriate
admission at existing dispatch seams; preserve feed and native identity controls
from G1/G2. A blanket guard over every normalization format would violate scope.
