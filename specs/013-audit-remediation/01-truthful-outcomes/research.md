# Bounded source research

2026-11-01; source90d5bd1. No new network requests. Parent research.md and saved
smoke/diagnostic/replay reused; no repeated sweep or full suite for design.

- `_cli_extract.py:128,166`: empty guard conditional on partial; None coverage
  ignores reasons. `_cli_core.py:175`: generic success always complete. Fix at
  extraction/discovery projections, not globally across unrelated commands.
- `_models.py:129`: ExtractionResult already has tri-state catalog_complete,
  errors and reasons. Additive read-only assessment preserves constructor and
  existing serialized fields; no new public envelope enum/version needed.
- `_extract.py:187`: non-Shopify catalog coverage intentionally unverified. Keep
  that conservative scope rather than turn all native complete=True into coverage.
- `_cli_data.py:96`: serialization includes coverage and reasons; continue using
  same codec/atomic writer. Python extract result remains inspectable even failed.
- `unified.py:108,194`: single/batch browser only check success; static fetch already
  raises HTTP errors. `_extract_structured_from_html` returns generic OG without
  product admission; browser fallback `_has_product_signal` already exists but
  is not sufficient to protect static/normalization/tool seams. Reuse/refine a
  shared predicate rather than another independent policy implementation.
- `_normalize.py:692`: title-only OG accepted with defaults. Generic normalizer
  seam must reject no-signal input; Product/name remains admitted regardless zero
  offer. Product identity is separate from price/merchant eligibility.
- `woocommerce.py:59`:404 after existing records leaves complete=True. Unconditional
  incomplete404 fixes loss of source-error meaning without pagination refactor.
- `tools/sources.py:105–194`: separate native source path, complete-empty early
  return at172 and final len(value)<maximum inference. `tools/domain.py:136` turns
  complete bool into graph completeness; empty extraction must be source_error,
  generic HTML and non-Shopify unproven coverage partial. Existing source error
  type and partial graph schema suffice; discovery at103 also needs conservative
  coverage diagnostic. Tool parse runs in auxiliary domain process, so exercise
  actual parser/normalizer path, not only a fake sources result.
- Existing tests `test_cli_extract.py:88,105` cover Shopify capped and exhausted
  controls; `:47` covers empty extract-one only. Those do not cover empty batch,
  unknown catalog coverage or generic policy admission. Inventory browser/tools
  tests before adding precise seam regressions.

Decisions: use failed/partial/complete assessment and preserve unknown catalog
field; CLI existing E_OPERATION/E_PARTIAL semantics and tool source_error/partial;
discovery list API unchanged, machine discovery is partial until catalog proof;
HTTP unknown fails closed; generic title/markdown alone insufficient; zero source
price preserved; no new currency/identity/runtime contracts in this child.

Compatibility risk: existing callers relying on exit0 for unknown HTML/discovery
must handle exit3 and retained data. Browser wrappers/test doubles must include
HTTP status; unavailable status cannot silently certify a product. Tool category
or maintenance callers may currently retain empty catalogs, so affected regressions
and final independent review are required; do not weaken tests without contract
traceability. No claim of fresh live observations or destination compliance.
