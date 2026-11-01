# HTML documentary skeleton — no production/components

G1 PASS,shared-parser refinement in spec/test design. Signatures planned:

```python
# _structured_html.py: pure BeautifulSoup/JSON/source capture dependencies
@dataclass
class StructuredHTMLResult:
    products: list[dict]
    diagnostics: list[dict]
def extract_structured_products(html: str, url: str, *, include_categories=False,
                                max_nodes=256,max_depth=8,max_images=20) -> StructuredHTMLResult: ...
```

Limits may narrow,not enlarge. Reuse SchemaOrgExtractor type/group handling and
OpenGraph extraction/admission; refine bounded walker/same-doc resolver there,
not separate native parser. Result owns block/resource/error diagnostics; caller
Unified projects products through existing static interface and propagates failed
admission/partial errors. tools.domain consumes same browser-free function and
actual normalize/portable projection; no import of Unified for generic parsing.
Explicit Unified class import/browser behavior unchanged.

Scoped DOM enrichment occurs only after product admission; actual projection
capture via existing capture(),with _field_sources linking selected fields to
retained /dom/... inputs. Placeholder/gallery/breadcrumb/sku/productID candidates
retain source ownership,conflicting values and diagnostics; no catch-all title
product synthesis. Existing Normalizer and evidence support consume source maps.
Canonical identity,free products and native formats preserved. No extra network.

R2–R5 runtime work,adapter enrichment and money code are not implemented here.
Skeleton/red tests require independent G2,then components/G3 before business logic.

G2 exact consumer seam: domain.synchronous(payload) optional include_diagnostics
bool defaultsFalse ->existing portable list; True ->{products:list,diagnostics:list}.
Native sources always setTrue,validate object/field types,append parser diagnostics
before completeness projection. Nonempty +diagnostics ->partial;emptyfatal ->
ToolError(source_error,message includes code). Native graph diagnostics stays
existing collection schema. Unified.extract directly consumes StructuredHTMLResult
and maps codes to ExtractorResult.error/completeFalse,static wrapper retains list.
Ownership resolver is private shared-parser responsibility; exact URL/form-ID
association precedes DOM source capture. No extra module-level browser imports.
