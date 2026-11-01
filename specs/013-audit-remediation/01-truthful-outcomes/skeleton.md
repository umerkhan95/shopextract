# Documentary skeleton — no business implementation

G1 reviewed spec is authoritative. Declarations below are planned integration
contracts, not runtime stubs. Existing APIs remain callable while red tests expose
the missing behavior; no placeholder success implementation is introduced.

- `_models.ExtractionResult.outcome: Literal['failed','partial','complete']`:
  read-only property; constructor and serialized field names unchanged. Delegates
  to shared assessment accepting product_count:int, catalog_complete:bool|None,
  errors:Sequence, incompleteness_reasons:Sequence. Assessment is pure and does
  not fabricate coverage; zero failed, positive unproved/contradictory partial.
- `_cli_extract` uses result assessment before extraction serialization/emission,
  rather than generic envelope defaults. Discovery uses its own conservative
  coverage projection; empty discovery allowed as retained partial data. File
  emission must use exactly the same classification as stdout before replacement.
- Shared generic admission helper takes raw structured metadata, returning bool;
  source evidence shapes remain unchanged. Consumers: unified static/browser
  parser, generic normalization, native tool domain parser. Explicit Product/name,
  OG product title+signal admitted; generic metadata/markdown title alone rejected.
- Browser transport gate takes crawler result, checks success and actual final
  status. Both `_extract_with_browser` and `extract_batch` apply before parsing;
  batch rejection is incomplete with retained siblings and diagnostic.
- `WooCommerceExtractor.extract` existing ExtractorResult signature unchanged;
  any404 supplies complete=False/page-specific error; prior products retained.
- `tools.sources.GuardedSources`
  and `DomainAdapter.execute`: preserve existing graph schemas; empty extraction
  raises ToolError('source_error',...); positive unproved coverage diagnostic makes
  graph partial. Discovery also partial absent proof, including empty list. Shared
  assessment/admission logic consumed without importing CLI into tools.

Dependency direction: model/pure assessment and admission have no CLI/tool/browser
imports. Adapters/parsers/normalizers own captured source interpretation; envelope
and graph layers own projections. No currency/runtime/field feature APIs added.

Executable acceptance: tests/test_truthful_outcomes.py. Transport, DNS and browser
crawler are external boundaries; actual normalizers/parsers/adapters/CLI/native
ToolRuntime/domain processes run. Tests may fail on missing outcome property (the
intended missing interface), not failed collection/import. Existing downstream
regressions and later stress are not claimed by these focused reds.

## G2 contract naming clarification

Planned concrete pure modules (documentary declarations, no code added):

```python
# src/shopextract/_outcomes.py
ExtractionOutcome = Literal["failed", "partial", "complete"]
def assess_extraction_outcome(*, product_count: int,
    catalog_complete: bool | None, errors: Sequence[object] = (),
    incompleteness_reasons: Sequence[str] = ()) -> ExtractionOutcome: ...
# src/shopextract/_product_admission.py
def has_product_evidence(raw: Mapping[str, object]) -> bool: ...
def crawl_document_allowed(result: object) -> bool: ...
```

has_product_evidence includes nonblank Product name or OG title and specified
product signal, preserves explicit zero; does not infer currency/identity or
mutate captured data. crawl_document_allowed reads success and final status,
requires integer2xx (bool is not valid HTTP status), missing/malformed rejects.
Both depend only on stdlib types; no models/CLI/tools/browser imports. Model
property imports assessment; CLI extraction/feed adapters and native sources use
it; unified/browser and generic normalizer use admission. Both helpers are private
shared contracts. Feed emission must use same assessment before own atomic/stdout
projection; native tool translates absent proof to catalog_complete None and
source diagnostics to assessment inputs. No duplicate CLI dependency in tools.

G2 added integration tests for actual feed transport/CLI and Woo adapter->pipeline
->CLI, as designed in test-design.md SC01c/SC03c; source behavior still unimplemented.
