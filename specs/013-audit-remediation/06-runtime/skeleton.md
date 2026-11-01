# Runtime documentary skeleton — R1 first, other substeps separately gated

G1 PASS. R1-only executable skeleton stage; no production business logic/stubs.
Existing constructors/API signatures remain authoritative.

## R1 package/extractor lazy exports

Planned declarations in `shopextract/__init__.py` and `extractors/__init__.py`:

```python
_EXPORTS: dict[str, tuple[str, str]]  # export -> (relative module, attribute)
__all__: list[str]                 # exact existing public names

def __getattr__(name: str) -> object: ...
def __dir__() -> list[str]: ...
```

On known attribute, importlib.import_module(relative_module,__name__),get actual
object,cache in globals and return. Unknown ->AttributeError. No wrappers or new
function/class identity; source __module__/inspect.signature unchanged. Import
failures propagate normally,never dummy objects. Keep __version__. Root may retain
cheap model exports only if plain/native domain imports remain browser-free.
Extractor namespace uses same small mechanism,not another plugin framework.
Export mapping audited against current imports/__all__, no speculative exports.
Lifecycle: process-local Python import cache; no worker/network/thread creation.
Independent subprocess tests exercise the actual package loader and module graph.

## Later runtime substeps (not G2-approved by R1)

R2: Woo.extract(shop_url,*,max_products optional positive int), passed from pipeline
and tool source before first request; helper remaining_execution_seconds reads
existing execution context. No clock mutation,adapter owns partial/error result.
R3: execution context owns bounded ProgressCheckpoint,commit normalized batches,
snapshot immutable result on owned timeout; explicit caller cancellation propagates.
R4: single owned discovery-worker runner with typed JSON request/result and hard
parent deadline+cleanup; robots decision component takes origin/user-agent/URL and
captured policy,fail-closed unknown. External access never delegated unboundedly.
R5: stable output ordering helper over canonicalID/sourceURL; worker stderr owns
library progress,stdout only result. No identity rewriting.

R2–R5 require their own concrete fixture/red/skeleton-component reviews before
implementation; these seam descriptions do not approve a blind runtime refactor.

G2 expectations now independently frozen: tests/fixtures/runtime_exports stores
original eager initializers + exact83 root/10 extractor public inventories.
Tests execute original imports as reference,not a copied lazy lookup mapping;
implementation must preserve all objects/signatures/ordered __all__/dir/version.
No runtime dependency on test fixtures; production export resolution remains
self-contained. Current documentary mapping interface unchanged.
