# Independent review gates

G1 pending. Author/task-breaker/researcher category_generic prepared spec/test-design/tasks/research/plan and actual official source inventory. Root will assign an independent reviewer with artifact digests. No self-approval or fabricated verdict. G2/G3/final not reached.

## G1 — 2026-10-18 — pass

Reviewer: `category_reviewer`, independent of author. Reviewed the actual eight
planning documents and full-source inventory/checkpoint in this worktree. Read-only
hash comparison verified all12 checkpoint entries, including gzip, extension YAML
and license, with zero mismatches. Bounded existing config/profile/package seam
inspection only; no tests, feature code edits, network, installs or source parsing
sweep by reviewer. This review entry postdates the checked snapshot.

| Artifact | SHA-256 |
| --- | --- |
| spec.md | 9bcc6aaf50636baaeac9d02e2f97d4ec4366da2d561322112574ead1e614286c |
| test-design.md | d4b8af141e551097ba7f21b78af936859c6270a080993093f765eee686bca866 |
| tasks.md | b9481c4a3efd82e21552e27344408798d460dc4ecb30ba98bd9398e83ce413be |
| research.md | ec47a8c7fd110db43a50004aed16a20c94ecb4938571c925188dd9ea1598b18f |
| plan.md | f897fdcb992a3c0d37448fdfb065d66076b1bb83093dda020800867e4fe78b55 |
| g1-checkpoint.json | 291a96edfdc2abf1cdc7954535936f15b2d317e6db9840590cf747917171cb5b |
| source-inventory.json | f5b9530b0b47192449296e9e7f13e329535ea38556375aaac5f04bac99bf696e |

No unresolved blocking G1 finding. Behavior/test/research coverage distinguishes
the full14606-category catalog from finite existing job subsets. It includes all
8240 canonical attributes,316 complete extensions including2 unused,74820 values,
93007 bindings,2891 contextual overrides and source-declared relations. Contextual
extension metadata and values_from lineage cannot be replaced by base labels or
an invented ancestor-value union. Source parent-first ancestors versus public
root-first view are explicit transformations. Lookup failures, malformed imports,
staged publication rollback, package completeness and hash-bound recovery are
specified before implementation. Exhaustive linear integrity and every-category
real capture/normalization/mapper/codec coverage have actual source denominators.

Existing source support, mapper, strict codec, Store policy/cache and profile gates
are reused; catalog metadata never becomes observed product properties or automatic
correction policy. Release+verified content identity fits existing registry fields,
and unchanged100/1000/config/companion caps are tested rather than silently widened.
768MiB one-off importer allowance follows saved621694976B inventory measurement;
compact runtime512MiB and separately bounded180s sweep are not yet claimed achieved.
Official-source live full-catalog validation, synthetic merchant assignments and
actual authorized Storefront observations are separately scoped. Pending merchant
access is an explicit live limitation, not assumed credentials or a synthetic pass.

**Verdict: G1 pass; skeleton/red work may proceed.** G2 must fix exact public
signatures/errors, namespace+release+content identity encoding, values_from resolution,
immutable schema_for input validation and import publication destination/discovery.
It must also establish the minimal versioned Storefront query/schema/producer/guard
and actual extraction/tool/worker dispatch; an adapter-only fixture is insufficient.
No native query implementation precedes that schema/access contract. G3 must verify
single responsibility and concrete reuse for every changed runtime file, compact
resource/import lifecycle and packaging. These are future gate obligations, not
approval of algorithms or absent query proof.

When authoring T09, generate decoded byte-boundary streams deterministically and
retain only small configuration/failure fixtures: testing128MiB decoded boundaries
does not authorize violating the stated1MiB retained-fixture cap. Save the first
small real-path smoke before exhaustive work, enforce watchdog/RSS/request limits
and report exact coverage/missing IDs without printing the catalog. No production,
all-category sweep or live merchant pass is implied by this design review. Actual
token counters remain unavailable; no quota estimate inferred.

## G2 — 2026-10-18 — changes required

Reviewer: `category_reviewer`, independent. Reviewed exact skeleton, source-schema
proof, acceptance red and G1 integration refinements. Read-only verification checked
all8 G2 checkpoint entries with no hash mismatch; no tests/network/business edits.

| Artifact | SHA-256 |
| --- | --- |
| g2-checkpoint.json | d2e783940781b2265a11023c515a7927770450f8534f60459a82e4913179f998 |
| skeleton.md | e92e4815ef68aa8d20ea925711dc9d63af3d6413102e8ca44588ae3fdf4d21b6 |
| test_shopify_taxonomy_skeleton.py | ed6090f5ff63377b6d2cf05b4cd4998b1163d061892f225a9fd46dfe6d16879f |
| storefront-schema-proof.json | 59d4335d790941db1eb1ad303bc7b8aadf0fbeeea9d86b77a7b084ea799229b6 |

**P1 — Storefront source cache lacks access-context isolation.** Skeleton defines
runtime-only Storefront token but includes only endpoint/API version in acquisition
cache identity. Two configured Storefront contexts with the same endpoint/version
can differ in listing permissions/publication visibility. Reusing a prior context's
category source result can bypass the later context's denial and expose unsupported
access-context facts. Existing origin authorization and taxonomy-policy digest do
not distinguish those contexts. Never persist/log raw credentials to solve this.

Simplest bounded repair: explicitly disable source-cache reads AND writes for
Storefront-enabled acquisition, leaving ordinary public/default source caches intact.
No new persistent CategoryOptions/job field is required. Alternatively define a
trusted nonsecret access-context identity with exact lifecycle/invalidation semantics,
but do not add a speculative credential framework. Amend affected G1 T07/T10/spec
behavior and skeleton together: same endpoint/version with tokenA then tokenB must
not reuse A's source result; B denial remains unavailable/partial, and removing
Storefront config must not recover cached privileged category data. Persisted
checkpoint replay remains original captured evidence under saved policy, not a new
claim that the currently supplied token could acquire it. Tests must distinguish
checkpoint replay from cross-job source-cache reuse.

Other inspected declarations are coherent: immutable full-catalog/context records,
all316 extension/value lineage, exact combined registry identity without new codec
fields, schema_for strict binding/namespace/version/target validation, staged atomic
publication/discovery and public product ID+handle-checked supplementary acquisition.
Saved version-selector document proof is honestly not live introspection. Producer
constant/endpoint/method/handle guard and public/tool/worker/parent paths are named;
their controlled executable proof remains future implementation verification. The
one red is an honest missing-public-API failure, not query/cache mechanism proof.

**Verdict: changes required on access-context source caching before G2 pass.**
No other blocking G2 finding. Resolve the bounded design/test issue and rereview the
affected artifacts; G3/business implementation remain gated. G1 catalog coverage and
resource decisions remain valid; this amendment affects its acquisition/cache tests.

## Amended G1 and G2 — 2026-10-18 — pass

Reviewer: `category_reviewer`, independent. Reviewed actual amended behavior/tests/
tasks/research/plan/skeleton and source-retention mapping; verified all20 amended
checkpoint entries with zero hash mismatches. Git status shows only small planning/
evidence/test paths; full source files and future build staging are covered by
existing ignore rules, with zero tracked files under those large-data locations.
No reviewer tests, network, build/install or business source edits.

| Artifact | SHA-256 |
| --- | --- |
| amended-checkpoint.json | 8da95e74a4b1805bd9265511b8ea6b63c7772d8d27b55bbad966dceb68e4278b |
| spec.md | 09bc6c586378364c6b19752ff075b6b4702ab3b76cfdc88aa2c593f2ac943935 |
| test-design.md | 8fd05f84e5c0a1650aaa1ba66dd5206b47cba05f3aa6e78adc5f7f0e1736faec |
| skeleton.md | ab2aabdeafa875cd574d789fa02af29384cb11f923b0b0a6752a726ecf12791c |
| research.md | 9b5d1d64fa3f2737d9ebb6f659ff93103e0706c4c863b16ceaffc386973e465f |
| plan.md | 135f043e375f87f7cf37a3832b54501858f20361bbd5038f1dc6aaf87f962099 |

**P1 cache finding resolved in contract:** Storefront-enabled acquisition bypasses
both source-cache reads and writes for discovery/public/native steps, including
failed/empty supplemental responses. TokenA->deniedB and config-removal cases have
explicit real transport/worker/Engine expectations; ordinary cache behavior remains
unchanged. Committed same-job replay is separately historical captured evidence,
retaining original time/policy without asserting current credentials could reacquire
it or inserting it into cross-job caches. No credential hash/new persistent framework
is introduced. Affected G1 acquisition/cache requirements and tests were rereviewed.

**User packaging amendment accepted:** complete source/generated bytes stay outside
Git; ignored verified sources/build resources feed explicit reproducible preparation.
Wheel AND sdist contain the same complete compact resource/identity through explicit
force-inclusion despite ignore rules. Published sdist->wheel uses embedded verified
data without taxonomy network/YAML/build extra; installed default lookup is offline.
Clean Git source is explicitly different: verified-local preparation works offline,
opt-in pinned download is bounded, missing inputs fail with guidance, and normal
build/import cannot silently fetch. Staging/discovery/idempotence/publication failure
contracts remain compatible with immutable catalog/version selection. Historical
checkpoints remain intact; moved large source references resolve through the saved
hash/path mapping rather than rewriting evidence.

**Verdict: amended G1 pass and G2 pass.** No unresolved blocking finding remains;
G3 component design may proceed, business implementation remains gated. G3 must
verify the tiny build-hook/validator/preparation boundary and ensure default offline
resource smoke runs against a prepared artifact or explicit catalog root without
accidentally depending on ignored files in a developer checkout. Actual wheel/sdist
membership, reproducibility, clean offline rebuild, full catalog denominators,
Storefront cache bypass and source/worker paths still require executable proof.
No prior missing-API red or source inventory is promoted to a mechanism/package/live
pass. No new source downloads or repeated research are needed for the next gate.

## G3 — 2026-10-18 — pass

Reviewer: `category_reviewer`, independent. Reviewed actual components.md, skeleton
refinement and unchanged affected behavior/tests. Independently verified all10 G3
checkpoint entries with zero hash mismatches. No tests, source acquisition, build,
install, network or business implementation by reviewer.

| Artifact | SHA-256 |
| --- | --- |
| components.md | 1eafcd51ce13d3814403ef4d9ad26c2ac5ef2294c49b5734f380d055dd599217 |
| skeleton.md | be155632900d96306feea44f3c629c8881b50fed9038266573b7bfe7cbc6ae8a |
| g3-checkpoint.json | 2808c2005d4b9a658eb48f0c45fc6cbf81c28b26812267f3e28e5d3728796300 |

No unresolved blocking G3 finding. Every proposed runtime file has a concrete
responsibility/consumer: immutable records, one identity implementation, standalone
resource verification, normalized relational validation, read-only indexes, offline
discovery, bound-schema projection, finite options and orchestration. Explicit
download/build/publish/preparation responsibilities are separated; no generic
taxonomy/plugin/credential framework or per-category modules are introduced.

Existing capture/Normalizer/source support, source adapters, exact mapper, strict
companion codec, policy/store/matcher and guards remain their actual mechanisms.
The bridge's private prepared-observation seam avoids normalizing/mapping twice;
schema projection delegates to the existing strict encoder instead of reimplementing
trust. Full metadata stays outside worker/job payloads, finite caps are unchanged,
and immutable catalog caching is by verified identity, not floating release.

The accepted build-hook refinement narrows the earlier optional-hook alternative:
**prepare owns download/build; Hatch hook only verifies and assembles preprepared
data.** Standalone stdlib resource.py is shared by loader/hook without eager root
application imports or copied verification. Force-inclusion explicitly addresses
ignored complete resources in both wheel and sdist; published sdist uses its embedded
resource without taxonomy networking/YAML. Developer red setup uses an explicit
session-prepared catalog root/fingerprint, while the separate installed-wheel test
proves default offline loading. These contracts make accidental reliance on a warm
ignored source cache testable rather than confusing it with artifact completeness.

Storefront producer remains category supplement to rich public observations, with
exact captured ID/handle joins and one producer-owned guarded query. Public and
guarded source/tool/worker/parent paths are concrete consumers. Runtime secrets
remain out of serialized policy; ALL Storefront-enabled acquisition source-cache
reads/writes are disabled, with ordinary caches and historical checkpoint replay
separately preserved. Real controlled tests must still prove this design.

**Verdict: G3 pass; bounded implementation may proceed with relevant saved reds
first.** Original missing-API red remains historical; add importer, pipeline,
packaging and native integration acceptance failures before their algorithms.
Full source/context/extension/value coverage, reproducible artifacts, offline
sdist-to-wheel/installed loading, RSS/watchdogs and actual live observations are
future verification obligations, not passes conferred by this review. No additional
research/download sweep or merchant credential assumption is needed to begin code.

## First core and explicit-auth amendment review — changes required

Reviewer: `category_reviewer`, 2026-10-18. Inspected actual importer/contracts/
identity/resource/validation/catalog/loader/publisher, source-shaped tests, saved
import/runtime evidence and affected auth-mode design. Read-only hash verification
checked all29 core-checkpoint entries with zero mismatches. No reviewer tests,
full import, network or business edits.

| Artifact | SHA-256 |
| --- | --- |
| core-checkpoint.json | 90fe704a207500b525d3efee652fe0d8a1aa268152c0bf236f94401e0da409ab |
| build.py | 660b278b48e0f8c3622ed9262ca439a39f399f05bb55450989a052c9bafafd09 |
| validation.py | 992b97041e10d06dceb68307fd6aeca8006bca455e257da1af2d81c4962224d1 |
| loader.py | 0ef9d600728d998c11c07113f842689e7ce2cc319629e614bd2cc97a909b9ad8 |
| publish.py | 1baee95eb7c71c41d0b1a192c6a21e275ea67b69d15d12ca2a9878f14f563ad1 |
| amended spec.md | 450303182c587b891044114db49ede307ce410981e32f8881443683c1cd7cdfc |
| amended test-design.md | aad33e59b72b340258bc3412c72d028d9a81c0a79911a7204a6aa312159ea618 |
| amended skeleton.md | d9e4d2838c2e3dde37da72b52e10db659f1edc38e73590e78c1e7811006f479f |
| amended components.md | 6b2d4029e451472379a6af00e1dc64d657e405326fb0dd5706a706ff7ad093c3 |

Blocking actual-code findings:

1. **P1 — Publication trusts unvalidated staged path metadata.** Publisher verifies
   resource bytes then compares only staged.manifest.fingerprint, while constructing
   directories from staged.manifest.release/fingerprint. Replacing a real staged
   manifest release with '../../outside' preserves fingerprint and can create/publish
   outside catalog_root; even a different ordinary release mislabels the destination.
   Validate safe release component/hex fingerprint and compare the COMPLETE staged
   manifest identity/counts/source hashes against verified resource metadata BEFORE
   mkdir/lock/write. The copied temporary manifest/resource must still equal that
   validated expected identity; mutable staging cannot substitute a different catalog.
   Use shared integrity helpers, not a second permissive schema. Add tiny traversal,
   staged-vs-resource identity/count mismatch and changed-stage-copy negative cases;
   each must leave destination/prior catalog unchanged. Resource logical identity
   must remain verified before a staged artifact is accepted for publication.
2. **P2 — Normalized metadata validation does not enforce immutable record types.**
   Validator checks IDs/references but not complete record field schemas/types.
   A value or attribute name supplied as list/dict passes reference validation and
   is retained inside frozen ValueRecord/AttributeRecord by catalog_from_data.
   Callers can mutate that returned nested object, violating the read-only contract.
   Wrong short_id and boolean level/schema integers also lack semantic type checks.
   Validate exact metadata schemas/scalar/sequence element types and ID/short-ID
   consistency before constructing indexes; reject malformed metadata with
   TaxonomyIntegrityError. Add a few tiny source-shaped adverse cases, retaining
   valid normalized output/fingerprint. This is strict input validation, not a new
   generic modeling framework or a request for a full source sweep.

The current real-source smoke supports its limited claims: all declared category/
attribute/value/context/parent/ancestor/reason counts match inventory;316 extension
lineages and canonical/context overrides are explicitly joined. The diagnosed source
ReturnReasonDefinition namespace and YAML-before-JSON memory ordering fixes preserve
original failure evidence. Repaired import25.467s/790441984B stays below768MiB;
cold runtime2.875s/430354432B stays below512MiB; compact2486600B is ignored data.
These are full-record structural/lookup smokes, not complete adversarial, installed
package, normalization-sweep or merchant-live proof.

**Affected auth-mode G1/G2/G3 amendment: pass.** Token mode requires a nonempty
configured token; explicit tokenless requires None/absent credential header, rejects
conflicting inherited credentials and never follows invalid/denied token fallback.
Both modes retain complete cache read/write bypass and fixed-query/guard/request
limits. Primary tokenless capability note is correctly not merchant category proof.
Controlled source/tool/cache tests and bounded actual merchant observation remain
pending before any operational claim.

**Core verdict: changes required for grouped P1/P2 boundary repair.** Use designed
tiny red/green cases and focused existing tests. Do not rerun the full source import
or expand acquisition merely for boundary validation; the approved valid normalized
fingerprint should remain unchanged. Preserve current full import/runtime evidence.
After bounded rereview, continue remaining pipeline/build/source tasks; no final
verification pass is implied at this partial milestone.

## Grouped core boundary repair rereview — pass

Reviewer: `category_reviewer`, 2026-10-18. Bounded inspection of publisher/resource/
validator/loader changes, actual tiny adverse cases and saved red/green/resource
results. All17 repair-checkpoint entries independently hashed with zero mismatches.
No reviewer test, full import, network or business edits.

| Artifact | SHA-256 |
| --- | --- |
| core-repair-checkpoint.json | dfcf466c4f1d934659a6977e9562e7b9e38665f573353b5dacba59599f016c73 |
| publish.py | 0b77d23459c4d0dc7f88b95a3188ab66a0d38dc54ca08c43cc0b22ef7428bd8f |
| resource.py | a3c40e044c4c7b689571fcf2aa593167f29a2a6a8dc201042af4df30c07f5488 |
| validation.py | d3239fa7704d6a93dd1890972a320b8ca051a08b40ba4a0417c71fcf5fab7015 |
| loader.py | 78ed08849ea1e6bae2272703872b78703c4fec360c396fd9785983de9c548050 |
| test_shopify_taxonomy_data.py | d52c0262cc6601aa1ddec1ac7bbf0a149de77ef578be0490b6260eb1b9c30f71 |

P1 resolved: safe release/full-hex identity, complete staged-vs-resource manifest,
strict logical fingerprint/structure and source/count identity are verified before
directory creation. Temporary copied bytes/metadata/logical state are checked against
the original expected proof before rename; existing identity is verified idempotently.
Tiny cases detect traversal, metadata substitution and coherent resource rehash with
unchanged logical fingerprint, preserving prior/destination state on rejection.

P2 resolved: exact normalized record fields, primitive text/sequence types, resource
kind/suffix, matching short alias and strict integer schema/level/count checks reject
the mutable/mistyped inputs before constructing frozen indexes. Shared logical
validation serves loader and publisher; standalone resource/manifest verification
remains stdlib-only and there is no copied permissive fallback. Saved12-failure red
and17-pass0.30s green evidence targets the identified defects rather than weakening
immutable-record expectations.

Existing compact resource passes the stronger loader in3.325s/432939008B, preserving
fingerprint1ecad259cf8cc558711b472e9194af93f68d12708fa51d6350ac13febd903c17
and original counts. No full source reimport/download or normalized data change was
needed. Previous import/runtime evidence remains valid within its documented scope.

**Verdict: core repair checkpoint pass; remaining bounded pipeline work may proceed
with relevant reds first.** No unresolved finding from the grouped core review.
Complete adversarial/import-update, package delivery, every-category pipeline sweep,
native/tool/cache and live proofs remain pending; this is not final feature approval.
The earlier explicit token/tokenless amendment pass remains unchanged.

## Pipeline/package and performance amendment — grouped changes required

Reviewer: `category_reviewer`, 2026-10-18. Bounded inspection of actual new pipeline/
options/schema/native/downloader/build-hook paths, narrow existing-file diffs,
representative tests and saved package/profile/partial-sweep evidence. Verified all53
checkpoint file hashes with zero mismatches. No tests, network, builds or sweeps by
reviewer. Existing queued downloader/cache/lifecycle verification remains pending.

| Artifact | SHA-256 |
| --- | --- |
| pipeline-package-checkpoint.json | 5a2142e7349b2ca36936ba3086337321612abbd841f8846423998ff668d54699 |
| performance.md | 26a9593586b980b9bb07d32f188daaafbf738abfef0656c870ff8efce7ca62e9 |
| extractors/shopify_taxonomy.py | b0fee03a0feae3ccde2591e18dcaa65c5d5f548a5f5a2957729da3208da6e129 |
| taxonomies/shopify/api.py | 8dfda11d62ab3a850e6e88b3ec8885a3a152766f25bff01fbe0b7969c3c87ef6 |
| tools/security.py | 271a6e25ecd2635d3dda0d93690cff46c5aef27bed6388d0344fc465c563b3cb |
| package-proof.json | 93a4ae2d714637466cdae6bc204193f81d3f8e3668ab395bbdd708ed618f6a23 |

Three bounded source-contract repairs are required before performance edits:

1. **P1 — Supplement diagnostics cross independent source boundaries / join errors
   are unchecked.** Global/no-path supplemental GraphQL errors are attached as global
   raw diagnostics, causing the Shopify adapter to reject independently captured
   public product_type/collection facts. Conversely nonnull matching Product.id/handle
   accompanied by errors on those join fields can still authorize category projection.
   Keep supplemental errors scoped to its category projection; error-affected/global
   ID+handle joins must not support projected category facts. Preserve public facts.
   Tiny real producer->capture->adapter tests must show supported original custom type
   survives a global supplement failure, while failed nonnull join ID/handle cannot
   map the returned standard category. Keep existing failed-category-leaf isolation.
2. **P2 — Wrong HTTP method bypasses Shopify fixed query contract.** Configured
   Shopify endpoint GET/HEAD currently takes the generic read path; the fixed body/
   category-mode gate is only inside POST. Reject wrong methods at the configured
   Storefront endpoint before wire, including query-string attempts. Controlled guard
   tests must assert zero dispatched requests; ordinary public GET remains unchanged.
3. **P2 — Convenience extraction drops merchant basepath.** api.py reconstructs
   shop_url from scheme/netloc only. A supplied shop basepath is lost from assignment
   scope and normalized Product URL/identity. Preserve the configured shop basepath
   consistently with raw extraction and existing scope rules. A controlled shop URL
   under /a versus /b must retain distinct scopes and correct Product paths, without
   changing global standard taxonomy term identity or inventing locale context.

**Performance design amendment: approved first bounded slice.** Saved profile gives
a concrete static type-resolution cost, so cache immutable type-schema metadata only
for finite application dataclass types (max128), preserving recursive checks, binding/
hash validation and rejection semantics. Do not cache mutable object validation or
normalization results. Run P01 baseline/candidate timing/RSS/outcome comparison and
P02 affected codec/mutation/worker/policy rejection checks before broader claims.
Measure cold/warm lookup, real normalize+schema, explicit codec and controlled native
dispatch separately; native request counts/guards/independent facts must stay unchanged.
Slots/lazy/index redesign remains evidence-gated, not authorized by this first slice.

**Per-ID duplicate codec amendment: acceptable if explicitly recorded before sweep.**
Every14606 ID must still use real capture/normalization/shared mapper/binding and
schema_for's strict encoder, exact target/catalog/source provenance and complete
per-ID coverage. An extra identical explicit decode+reencode for every ID adds no
distinct schema mechanism when only category strings differ. It may move to fixed
representative root/leaf, Unicode/escaping/contextual and distinct malformed/mutation/
replay codec cases, retaining exact roundtrip assertions there. Report codec coverage
as representative, never14606 decoder roundtrips. Catalog all-record integrity stays
exhaustive. This is test-design refinement, not permission to skip validation in code.

**No exhaustive budget increase approved yet.** Original300/14606 progress is partial,
not a pass. After the bounded optimization and affected greens, measure one small
batch, forecast all remaining work and propose an exact hard deadline for independent
approval (one process, existing thread/RSS caps, checkpoints/batch watchdog/stop-first
unchanged). A15-minute forecast is not itself approval; preserve prior evidence and
do not restart the blocked sweep before that review.

Packaging proof is credible within its stated scope: same complete compact resource
in wheel/sdist and rebuilt wheel, extracted sdist build with socket denial, installed
default lookup with no YAML import,14606 categories/74820 values and pinned identity.
The environment reuses existing application dependencies via system-site-packages;
it is not a clean independent all-dependency installation. No tracked large data is
needed. Final package/native/cache/adversarial/regression evidence remains required.

**Checkpoint verdict: grouped source changes required; narrow performance/test-design
amendment approved as above.** Author may diagnose the three small source cases with
designed reds/greens, then continue bounded metrics/optimization; no extra mid-review
is needed unless another contract changes. Final review and sweep-budget review remain.

## Source/performance repair — pass;540s sweep budget conditional on runner alignment

Reviewer: `category_reviewer`, 2026-10-18. Bounded inspection of repaired source,
shared static schema cache/diffs, saved focused results, baseline/candidate/native
timings, updated artifact proof and current sweep source. Independently verified
all62 checkpoint hashes with zero mismatches. No tests/build/network/sweep execution
by reviewer.

| Artifact | SHA-256 |
| --- | --- |
| performance-repair-checkpoint.json | 17a02a00d33d35f84b48333ed25b2201a9e4cd5d23ead73a75ef47d227bb1982 |
| _schemas.py | af6789a807395c50a0c8cd800f07af139da339a785eb25bc1dd9453aef2c94a6 |
| extractors/shopify_taxonomy.py | c76f1236f34163d4bf2428b3ffe85eb95dbca6affd30d647e2e811da5e5d2342 |
| taxonomies/shopify/api.py | 06e38e2b4002f7909ee8f185fcffffe62f22202fdc2217d8ae501d3031995cb5 |
| tools/security.py | 2cdd234303ac9026d8834eaa5acaf3dc7c80f57d934147a3592acc79d27fe289 |
| performance-candidate.json | 9feafe51fbe16ed727091214fb559d0a04bb9c8f299f1231fab877be92eafbae |
| current sweep.py (NOT ready) | 490c580d4e9a221afc33f408f99e3d78542ed43dc87a65bfe75614a4794aff46 |

Three prior source findings resolved: supplemental global/join errors now reject
only the supplemental category projection, preserving independent public facts;
failed nonnull Product.id/handle cannot establish the join. Exact endpoint wrong
methods are denied before wire, and supplied shop basepaths remain assignment/
Product scope. Saved intended9-failure red and focused23-pass/independent-fact4-pass
greens exercise these defects. Affected67-pass23.21s evidence covers strict codecs,
mutation/worker/policy, cache tokenA->deniedB/removal/replay and downloader boundaries.

Optimization is narrow and safe by inspected structure: one shared max128 LRU of
read-only static type-hint mappings for application dataclasses; recursive value/
binding/hash checks still execute. External dynamic types are not retained. No value,
Product, successful validation or credential cache was added. Saved candidate uses
17 static schema entries, unchanged semantic SHA/catalog fingerprint and improves
100 real normalize+strict-schema operations6.052s->2.890s (~2.09x). Cold3.580s and
sampled steady434MB/end438MB are separately reported; warm lookup/resource verification
remain intact. Controlled native41.95ms/operation is CPU/MockTransport evidence, not
merchant network latency or a universal production SLO. Latest offline artifact proof
11.865s retains complete resource/default installed loading without runtime YAML.

**Source/performance checkpoint: pass.** No unresolved finding from that slice.
**Budget amendment: approve one540s hard-deadline exhaustive attempt**, based on
measured422.047s forecast, one process, existing thread caps, RSS512MiB, batches100,
15s batch watchdog, source/code/catalog-bound durable progress and stop-first behavior.
Every14606 ID still requires real normalize+schema_for strict encoding; approved
representative/adversarial decoding remains separate. Report old300 partial attempt
honestly, never a pass or source-invariant substitute for new optimized validation.

**Do not execute the currently checkpointed sweep unchanged.** It still asserts180s,
has only after-batch time assertions, no enforced RSS cap and lacks the promised
per-ID/source-code-hash-bound resume state. Author must align the runner with the
approved540s/independent watchdog/RSS/progress contract before root's short static
readiness check and launch. This is runner-only preparation, not another feature
gate or permission to expand scope. Preserve prior attempt evidence; no silent
cap increase/restart. Required regressions and bounded actual live observations may
follow successful exhaustive coverage; final independent evidence review remains.
# Root runner readiness — 2026-10-18

Independent coordinator static review of sweep-readiness-checkpoint.json and runner SHA256 b293af8aba567d96f892ee45e34e73a26794078d4c303019ba578eebfb7aeff7: PASS for the previously approved single 540-second attempt. Parent enforces aggregate deadline with independent process-group kill, sampled RSS 512 MiB, 15-second batch progress deadline, bounded logs, cleanup and exclusive attempt state. Atomic exact-ID progress binds source hashes, resource hash, catalog fingerprint, interpreter and all source/runner code hashes, with pre/post checks. No implicit resume or duplicate per-ID decoder claim. Four author control tests passed; this static review did not rerun them. Feature code remains frozen during execution.

## Independent cookie isolation and index experiment design review — 2026-10-18

**PASS for the bounded design and author execution described here.** This is not
approval of an implemented cookie fix or a claim of measured SQLite improvement.
Static review only; no tests, network, benchmark, or feature edits by reviewer.
The current candidate's 142 recorded file hashes match disk. Reviewed SHA256:

- current-runtime-candidate.json: `c0cf693a6a4360a2481315d00ddd37d81abf4c05e935659f6c65073f9ea975d6`
- cookie-isolation.md: `60625bbd5967394e1815826472da5e86a13a9c74de0cfa474508b6a03fef4a25`
- index-comparison.md: `92d6b21fd5addf515744ea2d72b11fb50a361d48f2e55b138bcb74a1e8d04a01`

The cookie design retains the credential-conflict guard and borrows the same
GuardedTransport through a non-owning clean client lease; authority, query checks,
request accounting and pool ownership must remain intact. Required real Set-Cookie
public/tool/worker and explicit-token cases precede the fix, including prevention
of response-cookie persistence on the second supplementary request. After those
checks pass, exactly one remaining POST is permitted within the original two-HTTP
ledger, ten-second request cap and no retry/GET. Persist the strict historical006
projection and attempt reservation before wire. Retain its original timestamp and
URL; the new008 GET retained status only, so no current public-body pairing or
current merchant-category observation may be inferred from that historical record.
Persist the outcome before raising; exact ID/handle mismatch remains unsupported.

The dependency-free dict versus stdlib SQLite prototype is appropriately bounded:
one tiny saved smoke, one full-catalog preparation, sequential fresh candidates,
60-second preparation/30-second candidate/180-second aggregate and512MiB limits,
source-bound saved status, watchdog cleanup and bounded logs. The paper-derived
batching/packing hypotheses justify measurement, not a Python speedup claim.
No additional backend, dependency, production abstraction or exhaustive rerun is
needed for this first experiment.

Execution obligations for meaningful numbers: compare the same returned metadata
representation and timed materialization work, with exact hit/miss/context/value
signatures. Use an equal common application-import baseline for RSS comparisons,
or report total plus baseline/delta and label the result storage-prototype-only.
Separate preparation/import/open/first-query/steady-query costs; preload excluded
from timing must be explicit. Cold means fresh process, not controlled OS disk
cache. Report full current-loader verification versus weaker prototype-open
integrity and preparation verification separately; neither memory nor startup
numbers establish production integrity or end-to-end normalization parity. Keep
p50/p95, counts/checksums, sampled/peak RSS, resource/file sizes and environment
identity with the actual results. No performance result is presumed by this pass.

The saved14606-category/93007-binding sweep and1087-test suite are prior evidence,
not rerun by this review. Final feature evidence review remains after the narrow
repair, experiment and bounded live outcome. Session token counters unavailable.

## Final independent feature review — 2026-10-18

**PASS. No unresolved actionable blocker within the approved008 scope.** Author
stopped during review. Reused prior gates and saved evidence; no tests, importer,
benchmark, network or package builds executed by reviewer. All201 final checkpoint
file hashes match disk. Final checkpoint SHA256:
`cf4dcb6b5eb50240d9bf00629b765d5469c77068d9283ceca665b94abb3e9406`.

Exactly three acquisition source files differ from the successful exhaustive sweep:

- extractors/_storefront.py: `131dedde10690350d5e74a671291e1b5833a74e83b53e819e2d5841cdd7940c6`
- extractors/shopify_taxonomy.py: `4ce12a4d21b869640ae8784e2af215e7e243283230e5ab2eb0e7581e3d661df2`
- tools/sources.py: `6f4df6b6334ac177d2dbe7dfeea1332637ce217bceb2e75b2cb38c7cfe6291c6`

The repair supplies a clean stateless metadata client through a tiny non-owning
lease of the same GuardedTransport. Its close does not close the parent transport;
origin/query/byte/request enforcement remains with that transport. Caller-provided
inherited credentials still reject; owned metadata response cookies cannot provide
subsequent authority. Token/tokenless real Set-Cookie fixtures exercise actual tool
and child-worker acquisition and exact GET/GET/POST request accounting. Saved red
and65-pass affected green support this disjoint repair. No normalizer, mapper,
strict codec, taxonomy resource/pin, or guard implementation changed after the
14606-ID/93007-binding sweep passed395.459s under540s and512MiB. The1087-test
repository pass222.91s is explicitly pre-repair; it is not mislabeled a final-tree
whole-suite run. Prior SRP/reuse boundaries remain intact; no duplicate mapper or
new storage framework was introduced.

The final live result retains one actual native Board Games assignment and its
capture, identity join, shared mapping and schema projection. Its exact two-request
ledger is exhausted: GET200 plus one POST200, no retry. The Product projection is
historical October16 evidence; the native category observation is October18.
Documentation states this limitation and does not imply fresh public-body retention
or live merchant coverage for all14606 categories. This completes the bounded live
observation requirement alongside separately identified exhaustive synthetic paths.

Latest artifact proof14.13s covers installed offline default loading and extracted
sdist-to-wheel resource equality, full catalog fingerprint unchanged, no runtime
YAML/network. The fresh environment deliberately inherits existing application
dependencies; no clean all-dependencies-install claim is made. Source preparation,
explicit downloads, installed behavior and ignored generated/source bytes are clear.
The saved scope audit lists no candidate Git file above1MiB; publication is not done.

The18.251s standard-library SQLite experiment reports equal timed canonical JSON
materialization,128 actual schema outputs, exact misses and matching workload
checksum, common imports with baseline/delta RSS, separate preparation/verification,
fresh-process versus OS-cache caveat and p50/p95. Its file-hash-only open is explicitly
weaker than current logical/reference validation. SQLite's106090496-byte file and
slower varied128 reads37.87ms versus17.32ms accompany its smaller measured RSS; no
production-integrity, full-pipeline or general speedup claim follows. Dictionaries
remain production. This answers the paper-informed/no-new-dependency experiment
without broadening implementation. Prior2.09x static-type-metadata optimization
remains supported by separate identical-output measurements.

Additional exact reviewed SHA256:

- docs/shopify-taxonomy.md: `0a63e83951edebb0a4331ec721729c3084dc39e9bfe52395de3a19317be0de3b`
- README.md: `7c4e2ef6a6cf9d5a51a9dc81c44f205ec248d7dc202c051dc899f7369a9e8b3f`
- merchant-live-final-result.json: `5d6f874770bce9d98e87f6183c13c44f7f7180f2e40ab5af2bbc996419b0183b`
- index-benchmark/result.json: `9a89fc1dcf044c232798d9d2d9a385e11400885adaea045007bd4d62b17a5390`
- package-proof.json: `8d232907d793432b0dc84cd6f7b35f793fef609940b4a1af488ba9dee56cfe0b`

Feature may be marked complete with these recorded limits. Git publication remains
outside this review. Actual session token counters unavailable; no quota inferred.

## Independent cold-checkout delivery amendment design — 2026-10-18

**PASS for D01–D03 design and narrow implementation.** This reopens delivery
closure only; final runtime/source evidence remains valid. Static review confirms
the current test workflow's editable installation and release workflow's build run
before any ignored catalog preparation, so both need the proposed ordering fix.
All nine delivery-design checkpoint hashes match. Checkpoint SHA256:
`b74792227493b36f513de69dbe642385e9aff67b07525954e2cbc3c6ea722bd8`;
delivery.md SHA256:
`8c92db16da35f6320b8317ed3bb224ba49d06777eea67ac9fc9031674cbff793`.

One shared composite action plus a metadata-derived bootstrap is an appropriate
small boundary. Install declared tooling/runtime/taxonomy-build requirements
before eager application imports, reuse the existing prepare CLI, then perform
existing job-specific editable install or release build. Keep Python3.10's actual
Hatch TOML fallback executable and tested, not assumed. Do not duplicate dependency
lists, importer/download validation, or turn the offline Hatch hook into a downloader.
Use exec for the importer and preserve the approved one-import memory budget.
CI/release explicitly opt into pinned downloads; verified local source override
must fail without network fallback. Existing publishing settings/test commands stay.

Run and save the tiny cold D01 result first; only then the single bounded D02
full-source proof using retained official files, no source HTTP. Tests must really
exercise absent generated/embedded resources and cannot succeed via another
installed checkout. Metadata-derived dependency selection and both TOML paths,
pre-preparation actionable failure, post-preparation real backend/editable metadata,
full resource identity and wheel/sdist membership, and missing/tampered source
D03 failures are required. Existing dependency availability is explicitly inherited,
not evidence for a fresh dependency-install matrix. Retain offline/no-index behavior,
exact commands, source hashes, logs and stop-first limits. No complete repository
suite, full sweep, runtime edit or further merchant request is justified by this
ordering amendment. Final delivery implementation/evidence review remains required
before merge. No tests/network/source changes by reviewer; counters unavailable.

## Final independent cold-checkout delivery review — 2026-10-18

**PASS. Delivery ordering blocker resolved; no remaining merge blocker identified
in this amendment.** All24 delivery-final checkpoint hashes match disk; checkpoint
SHA256 `09714aaab17426c6cf6dcc61555153d68e850f3c78a8079ab9a7f5a377406a8b`.
No runtime source file differs from the previously final-reviewed feature candidate.
Reviewer inspected files/evidence only; no tests, source imports, network or builds.

Reviewed exact implementation hashes:

- scripts/bootstrap_taxonomy.py: `5020a4d3e99290bfa09b00c769df9f2910fbcc107250437065c8e7e309d29312`
- shared action: `adee159398968cea42b4683fc6f6ed54b0564c88dcac171bd0ede379aa2344a1`
- test workflow: `79b2ee863be4dd47a76dfa5dd4125b1486532f53ecf2ecf9fcb4b98c3f4ee8db`
- publish workflow: `0e9de5d27ccac0338f4b84d2056184820b3cb21748608f8507d3938f63fabbee`
- delivery.md: `9fb4fabe38f9057a44beec49f26385e640fe48ee7c87548efb4876fd4b41dc34`
- full proof: `239ac2fac6376b8334d31120995fe9c8131b7cacd293f07e2d329dbd5cfb4494`

The final contract explicitly narrows initial all-runtime dependency installation
to metadata-selected exact HTTPX plus the declared taxonomy-build requirements.
The process-local build-only namespace executes the same trusted prepare and its
relative build modules, bypassing eager application initializers without duplicating
builder algorithms. Hatch supplies packaging and Python3.10's tomli; no new runtime
dependency or package-import refactor was introduced. This refinement is accepted:
it removes unnecessary application dependency/memory bootstrap while retaining
existing import/download/validation/publication code. Same-process preparation has
no imported application parent. Both workflows call the ONE shared action before
editable install or package build and explicitly authorize pinned CI downloads;
ordinary hooks/runtime remain offline. Verified offline local mode rejects missing
or corrupt inputs without source fallback or pin mutation. Existing workflow test
commands and publication settings remain intact.

Saved tiny4-pass evidence covers absent prepared data, exact dependency selection,
actual Python3.10 tomli choice, fresh-process trusted builder loading without app
imports, real fixture preparation, hook success, and missing/corrupt source failures.
The stdlib branch is conditional code/fixture coverage on the relevant interpreter;
Python3.11/3.12 have not been run locally and remain the actual CI matrix obligation.
Do not describe the local3.10 proof as execution of those interpreters.

ONE retained-full-source cold bootstrap passed28.741s, sampled708714496-byte peak
below768MiB, no source HTTP, exact fingerprint/counts/resource identity. Actual cold
wheel/sdist builds passed. The first editable metadata failure is preserved; only
its declared missing editables backend dependency was installed, followed by a
metadata-only1.365s successful retry, with zero second source import. Offline
resolution inherited existing build dependencies and is documented accordingly;
it does not establish an independently clean dependency-install matrix. Previous
installed-artifact/offline and full runtime evidence remain separately valid.

Delivery may proceed to the already authorized commit/push/PR/CI/merge sequence.
Require the actual configured CI checks before merge; this local review does not
replace them. No further local whole-suite/sweep/import/merchant run is warranted.
Actual session token counters unavailable; no quota inference.
