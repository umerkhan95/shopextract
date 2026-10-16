# Bounded production research — G1 candidate, 2026-10-17

Scope: component model AND implementation requested. Discovery first; no category code
or tests executed by synthesis author. Six platform findings read and reconciled before
this package. Baseline44 normalize tests passed previously (0.15s), saved by coordinator.
Actual session counters unavailable; no inferred quota percentage.

## Sources and concrete findings
- `platforms/shopify.md`, `artifacts/category-mapping/findings/shopify.json`: public product_type custom label supported, GraphQL standard taxonomy/collections separate authorized capability, not available from current public products.json.
- `platforms/woocommerce.md`, findings/woocommerce.json: product categories are unordered store-scoped product_cat terms; category graph requires separate parent evidence; shop base path matters.
- `platforms/magento.md`, findings/magento.json plus findings/magento-schema-minimal.json: coordinator bounded official schema lookup resolves ProductInterface.categories:[CategoryInterface], uid:ID!,name:String. Opt-in query append only, no new Store header or tree request. Original author unresolved note superseded only for minimal fields.
- `platforms/shopware.md`, findings/shopware.json: saved categoryIds vs categoryTree prove direct memberships vs separate index; category association unrequested/null, source channel/language unknown; current guarded association body must remain unchanged.
- `platforms/bigcommerce.md`, findings/bigcommerce.json plus findings/bigcommerce-schema-minimal.json: saved Product.categories args first/after, CategoryConnection/pageInfo/edges/node and entityId/name/path resolved from official embedded RSC type table, no fresh storefront. Optional first20 membership selection verified; no followup/tree/breadcrumb query.
- `platforms/generic.md`, findings/generic.json: feed drops Google declaration before capture, XML entity decode once, Google ID/path representation and unknown version separate; Schema.org URL/CategoryCode require typed handling; OG repeated property loss cannot imply completeness; LLM source unsupported.
All relative findings paths above resolve under `artifacts/category-mapping/` from repository root. Saved source dates/provenance remain in original files; derived-offline schema is not live observation.

## Shared decisions and alternatives
1. One source-facts contract + one mapper + explicit companion codec. Rejected six platform mappers and attaching unencoded runtime attributes: current `_portable.product_from_record` requires exact Product fields/top-level schema, so default product encoding would silently lose arbitrary attachments.
2. Public named opt-in wrappers expose ordinary Product + companion; existing constructors/default feed/tool records unchanged. Rejected unconditional new required Product fields or replacing legacy category_path semantics.
3. Separate term vocabulary/namespace/version identity from source assignment scope. Merchant term ownership preserves configured store/catalog/basepath; standard global term may be shared across stores while observations are not. Endpoint aliases cannot overwrite merchant identity. Reuse `_scope.catalog_scope` semantics where suitable but do not mistake per-product URL for merchant scope.
4. Source category observations track relation kind, raw representation/state, support and completeness independently. Memberships/collections/custom type are not ancestry; explicit index is not ordered path. Only captured parent edge or declared path grammar supports hierarchy; first slice does not invent escape grammar or network trees.
5. Exact trusted rules + versioned target registry; unknown versions match only explicit unknown-permitting selectors. All applicable per-assertion target sets must agree exactly. {A,B}/{B,C} ambiguous union[A,B,C], not intersection. Different memberships may legitimately map to multiple targets. No standard taxonomy download, fuzzy guess, model classification or inferred domain policies.
6. Source facts retain existing `_capture` evidence references, `_normalization.Normalizer` source selection/outcomes and SupportState; derived rule decisions retain separate rule/version/source refs. Codec verifies immutable full Product+scope binding at construction/encode/decode, evidence alignment and bounds. Re-encoding cannot bless mutated Product with stale companion.
7. First native acquisition includes bounded opt-in BigCommerce/Magento minimal fields with unchanged defaults. BigCommerce guard consumes producer-owned exact constants; no duplicated query text or arbitrary GraphQL. Magento continues existing bounded GET transport. Shopware reuses returned IDs/index; no associations/query broadening. Captured generic declarations are retained before loss/default collapse.
8. Maintenance runtime opt-in persists config digest alongside policy/job; source/domain child process explicitly returns companion envelopes. Cache identity includes schema/scope/registry/rules/profile bindings. Current `_category_conflict` is a conservative explicit-profile veto, not mapper: category mode adds review reasons, never selects profiles or grants field/identity authority. Legacy jobs keep prior behavior.
9. No separate category SQLite database/framework: reuse portable record/maintenance cache/checkpoints and existing expiry/origin/job budgets. Invalid cached companion is a miss; unchanged policy resume preserves original mapping version. Config/scope mismatch blocks stale replay.

## Direct peer consultation
BigCommerce <-> Shopware directly agreed scoped opaque terms, optional channel/language,
membership/index/path distinction, per-relation completeness and separate mapping provenance.
Shopify <-> WooCommerce and Magento consulted directly (saved exchanges); Magento <->
generic and BigCommerce <-> generic exchanged schema/namespace/codec constraints.
Inactive-peer findings were reused, not fabricated live replies. All authors must cite
this shared decision before adapter code; shared owner alone changes common modules.
Independent reviewer preliminary notes resolved overlapping rule-set semantics,
immutable binding at encode as well as decode, and category-mode review vs legacy
explicit-profile behavior. These discussions are not a G1 verdict.

## Limits, failure and remaining limitations
- Spec limits:100 terms/200 refs/depth8/256KiB companion;1000 rules/targets and256KiB config. Oversize config rejected before network; category limits truncate with explicit partial reason and never fabricate empty. Native BigCommerce first20 has no followup; Magento source list bounded by existing10MiB response + category parse cap.
- Existing tool origin, timeout, request/byte/item/graph limits remain authoritative; category wrappers cannot widen them. No credentials in evidence, cache identity or logs.
- Driver:24 distinct mechanisms/<=100 fixed parameter invocations/seed26/120s; one process and capped threads. Live12HTTP max/2 per platform/2products, explicit existing authorized sources/access prerequisites,10s request/120s total, no tree followup/model/write. Some live native access may remain blocked; deterministic mechanism proof is separately required.
- Per-platform schemas establish capability, not universal current shop support. Unsupported native query returns explicit unavailable/incomplete diagnostics; never report categories observed via HTML fallback merely because platform detection says BigCommerce/Magento.
- G1 reviewer must check exact public wrapper/error/config shape and C01–24 coverage; G2 fixes signatures/code seams; G3 approves reuse/ownership before implementation. No gate is assumed passed. Native full taxonomy/hierarchy visibility, Store-header enrichment and standard Shopify access remain out of this slice.


G1 reviewer revision: native GraphQL errors+data are interpreted per retained error path,
not discarded wholesale by default JSON helper behavior. Valid products/supported leaves
survive; affected category relation partial with supported terms or unavailable without.
Missing/malformed BigCommerce completion metadata => unknown, not known empty/complete.
Schema rejection/access denial yields explicit unavailable diagnostics and no automatic
extra default-query/HTML/model request. Current default path unchanged. C03/C06/C10
fixed variants specify native parsing/guard expectations within existing24/100/120s
limits; shared owner must provide common error interpretation seam, adapters only translate.
