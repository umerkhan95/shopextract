# Behavior/test design before breakdown

Scenario IDs and exact expected outcomes: spec.md. Distinct uncovered risk:
Nested source ownership, placeholder short-circuit and unrelated DOM cues; actual SchemaOrg/unified/normalization/capture paths with sanitized saved HTML.

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

Live plan: one saved Naheed/Gartenmoebel product,max3HTTPrequests/1item/30s; no browser unless request cap enforceable; unavailable fields verified by synthetic real paths.
Offline: focused acceptance/affected checks then configured scripts/run_tests.py
240s-family/480s-total (never increase). Prior timeout does not satisfy this gate;
record unrun families and unknown failure nodes honestly. Separate synthetic
mechanism,stress and actual live evidence; inconclusive live is never a pass.

G2 executable fixtures before tests: root/list/@graph/ItemPage equivalence,linked
brand+Offer with cycle,externalref ignored; container boundary255/256/257 and
rootdepth7/8/9 via shared result diagnostics. Placeholder/lazy/real-name and gallery
19/20/21,scoped SKU+actual capture support,Magento productID,structuredSKU conflict,
ordered/malformed breadcrumb,policy/freeGroup/native controls. One fresh actual
tools.domain.synchronous generic parse checks no browser modules; companion actual
ToolRuntime HTTP/DNS-only fixture checks retained DOM-SKU. No duplicate parser.
Shared private result preserves diagnostics,legacy static projection remains list.
Seed0,<=64 cases,120s full run,15s freshprocess,10s bounded tool poll,64KiB ordinary
HTML (budget boundary blocks tiny),one worker. Save one nested-root red first.

G2 repair BEFORE tests:11 additions (final39). Actual domain serialization2cases
legacy list/opt-in typed object. Unified HTTP extraction3cases valid+overbudget,
valid+invalidbreadcrumb,emptyfatal; retain1/1/0,completeFalse and exactcode. Actual
ToolRuntime3samecases asserts retained diagnostic collection+partial state or
source_error/no handle on fatal. Ownership3cases URL-owned main vsrecommendation,
form-ID-owned main vsrecommendation,and ambiguoustwoProducts: only unique owner
gets DOM-SKU/productID/gallery/capture support; ambiguous fallback remains unset
with unsupported observations and diagnostic. No parser/serializer mocks,HTTP/DNS
external boundaries only; browser off. Seed0,oneworker,120s selected red run,10s
tool polls. Existing28 reds retained; no03 production/components authorized yet.

Functional repair design BEFORE cases:9 additions(total48). OG ownership uniqueURL
and ambiguoustwoProducts(2): only unique owner may receive page-global image,
description,url; sibling metadata absent/unsupported,chosen source evidence observed.
PureOG placeholder+DOMreal(1): actual OG normalizer consumes new image with retained
DOMsource map. Root/nested@graph BreadcrumbList objectitem @id/name forms(2) project
only category; overbudget nestedbreadcrumb block(1) diagnostic/no fallback category,
no independent unbounded reparse. Browser known200 DOMSKU+image,singlemalformed
breadcrumb diagnostic,andmixedbatch good+overbudget(3) through real single/batch
crawler boundaries,not private parser only. Existing legitimate group/free/native
and timestamps remain controls. Seed0,64KiB inputs,120s,oneworker;save red first.

Browser compatibility repair design BEFORE tests:4cases,total52. Known200 typed
Product missing fields gets renderedmetadata description +explicitEUR markdown
12.50 and metadataimage/mediaimage (2); actual normalization and source-supported
price/currency/image/description asserted. Explicitzero offer preserved over same
markdown(1). AmbiguoustwoProducts gets no page-global fields from renderedmetadata/
markdown/media(1). One owner only;no dollar=>USD guess. Actual crawler boundary,
no duplicate parser or normalization stubs.120s one-worker,existingURL/capturelimits.

Browser fixture realism clarification: give each admitted Product its own explicit
SKU so existing core usable-product guard does not discard price/image-absent
negative controls. Do not weaken source usability or positive fallback assertions.
The browser gap remains independently missing price/image/description,not identity.

Affected support expectation design before update: old layered-fallback test rejects
borrowed JSON-LD support. New dedicated browser_rendered capture legitimately
supports€12.00; assert observed only with that distinct method,pointer/rendered/price
and exact originalmarkdown source_excerpt. Title remains JSON-LD observed. This
strengthens source separation rather than borrowing a parent's capture.
