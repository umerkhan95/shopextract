# Independent child G1 review

Reviewer `/root/audit_plan_review`,2026-11-01. Verdict: **PASS**.
Reviewed spec/test design before tasks/research/plan and shared primary-source
register. Source spot-checks reused current `_cli_data` bounds, canonical identity
allocation, schema ProductGroup handling and eager package/extractor imports.
No new probes, network requests, tests, production edits or subagents.

No blocking G1 finding. Eager import coupling is source/probe supported; no causal attribution to legacy100-poll failures is claimed. Lazy exports must return actual objects without wrapper signature drift. Woo per-page/item limits, deadline-aware retries, scoped checkpoints, caller cancellation and owned seeder cleanup have distinct requirements. G2 must pin worker start method/process ownership, real cancellation/interruption paths and robots origin/user-agent/redirect/cache accounting. Unavailable robots skipping URLs is an explicit local conservative policy, not a claim of universal protocol necessity. Preserve old full-driver failure status until actually rerun successfully; import improvements alone cannot waive six pending native polling regressions.

Audit mapping and bounded sequence remain explicit in each spec. Shared test
boilerplate is a ceiling, not concrete collected coverage; each substep must name
actual distinct fixtures, real-path assertions and edge counts before red execution.
Synthetic, stress, actual live and unsupported external-approval states stay
separate. Browser budgets include subrequests or integration is blocked.

## Pending gates

G2 skeleton/executable intended-red tests: pending. G3 components: pending.
Implementation/offline/full-driver/live/final: pending. Parent child01 functional
repair review does not pass its unresolved complete verification gate.

## Reviewed SHA-256

```json
{
  "spec.md": "92337add4d382449590c68ef087d3ada36ff7218b54ba3f25183cc9f85a6310b",
  "test-design.md": "98cfcf70c6f8716dc44b9c9564d5a609893808986c8f88cf66ad17320ea66af1",
  "tasks.md": "16d504482532a483d9c984b1656d138a1fc7030db52d93c53cb39eab9cdf5780",
  "research.md": "9cf98d4085cd0b00d412f7244ddb74ad20b9ee676b884aacc97ace5f8de60b93",
  "plan.md": "f1004e46dccc39b4792e24f64b44f5c0ef8f22242d9ac2bd468d341ae3b42989",
  "../primary-sources.md": "7efa271a2fb1860960fddcd349d7ba17edbe633478fdeb0f8ea8caf7d10a215d"
}
```

## R1-only G2 — CHANGES REQUIRED

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed documentary lazy-export
skeleton,6 acceptance tests and saved4 intended-red/2 passing evidence. No tests,
network/probes/implementation executed. R2–R5 are outside this gate.

Blocking compatibility coverage gap: `set(s.__all__).issubset(dir(s))` tests the
implementation's own current inventory against itself, so deleting any public
export except the three sampled identities still passes. Extractor public exports
are not independently inventoried either. Freeze prechange root and extractor
public export inventories as reviewed expectations, assert exact names and dir
coverage, and verify exported attributes resolve to their actual original module
objects (no wrappers). Include __version__ preservation. Use bounded fresh process
execution, no loader mocks and no increased worker/time ceilings. This directly
exercises R1's promised stable public API rather than mirroring a newly written
mapping. Save focused red/control evidence as appropriate.

Skeleton typed mapping/__getattr__/__dir__ contracts and cache/lifecycle direction
are otherwise suitable. Four import reds demonstrate eager coupling, not cause of
legacy polling failures. G3/components and implementation remain gated; full-suite
failures/live omissions remain unresolved independently.

```json
{
  "specs/013-audit-remediation/06-runtime/skeleton.md": "7503079ef04190410b9179c5472b3c38e48b71e84aaa9436378b3b9d42eae131",
  "specs/013-audit-remediation/06-runtime/verification.md": "6dacddbcaf1014d2b681e2bd2899e568dcc0429e9c69b505a454e5851366bbbf",
  "specs/013-audit-remediation/06-runtime/red-r1.log": "c08d6c8715c78c34a070fe1ab08fe3188b8e023bdbfd5086803ef606a7043c87",
  "specs/013-audit-remediation/06-runtime/red-r1.json": "07b096e6c1ac3741219a88412ee3eacc3f5b5d08d515c97bf1f352560e45418f",
  "tests/test_runtime_lazy_imports.py": "2d27fbaead5e93d3481e956085b8518f0c80dd7f720b20cceb607b96f6ab969e"
}
```

## R1 G2 inventory blocker re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed independent frozen
baseline initializer sources/inventory, repaired test and saved2-control pass
evidence. Verified frozen sources byte-for-byte against90d5bd1 with git show;
83root and10extractor declared exports/public objects. No model/network/test run.

Previous inventory coverage blocker resolved. Tests resolve actual lazy exports
before independent eager initializer reference execution; exact ordered __all__,
all intentional public names, dir coverage, actual object identities, callable
signatures,version and unknown AttributeError now have baseline-derived expected
values. Mapping is not its own oracle. Controls passed2; four unchanged import
graph intended reds remain applicable. Actual file now7 cases, no full-file pass
claimed. Verdict PASS for R1 G2 only; component author/G3 next. R2–R5 have no G2
approval. Production, full-driver/live/final verification still pending.

```json
{
  "tests/test_runtime_lazy_imports.py": "64f8f0ad40bf65625a4ddaebfae4df75247716bf0ea6735655fae17bd379a8fa",
  "tests/fixtures/runtime_exports/inventory.json": "f0e0286474336ecba7eb0d6c674899f4a9f731251c2ce6547f741caa5e2e8cb6",
  "tests/fixtures/runtime_exports/extractors_baseline.py": "3b5e8cf86ffb5e68219ed32002f4ad00ea372a6f8cfca1c1c0268dae1750492b",
  "tests/fixtures/runtime_exports/root_baseline.py": "8808e1cbce60945fab3199ee9ff5eefe3795f7610c3a80f5dc1bc0306ebae81a",
  "specs/013-audit-remediation/06-runtime/skeleton.md": "f438fc39346719affe8fca4b1a63ed70ec110b5762edcbfcd793822b3ec80a8b",
  "specs/013-audit-remediation/06-runtime/inventory-control.log": "b40b04ef618b9f0bd480a23e01e644c63d102aab1677e7a19053067615cc5c11",
  "specs/013-audit-remediation/06-runtime/inventory-control.json": "bb5ce9c8e8a5ddaa7f5c8d2eaface5acd54bf6ac4ad465589c1acff2fe3eda2a"
}
```

## R1 G3 — PASS

Reviewer `/root/audit_plan_review`,2026-11-01. Components align with approved
lazy-export signatures and7-case independent frozen oracle. Private per-module
registries, actual original objects, globals/importlib cache and explicit failure
propagation preserve ownership/lifecycle; no shared registry framework, proxies,
network or process allocation. Naming/submodule collisions are explicitly covered
by all-export compatibility controls. No source/tests/network executed by reviewer.

R1 implementation may proceed; R2–R5 and all final verification remain separately
gated. Full-driver/polling/live failures remain unresolved.

```json
{
  "components.md": "0eb17256f0fa623d43d4c12c8054be0050d4ea64a6b8188862c6c186abf90a70",
  "skeleton.md": "f438fc39346719affe8fca4b1a63ed70ec110b5762edcbfcd793822b3ec80a8b",
  "tests/test_runtime_lazy_imports.py": "64f8f0ad40bf65625a4ddaebfae4df75247716bf0ea6735655fae17bd379a8fa"
}
```

## R1 implementation functional review — PASS; final verification pending

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed actual lazy-export code,
all-export frozen oracle and saved7 import+5native passing evidence; no new probes,
tests,network or source edits. Typed private maps resolve original source objects,
successful globals caching and importlib module cache preserve identity; failures
propagate without placeholder caching. Three eager cheap aliases correctly avoid
Python package/submodule callable collisions; frozen83root/10extractor inventory
checks challenge omissions. No browser worker/thread/lifecycle framework introduced.

Functional PASS for R1 scope. Reduced import measurements are bounded observations,
not an SLA or causal proof for legacy polling failures. One generic native flow
still fails100-poll completion, so no affected-suite/full verification pass. Previous
full-driver timeout/unresolved failures, absent oracle/maintenance/live checks stay
open. Whole-runtime R2–R5 have no implementation approval from this review.

```json
{
  "src/shopextract/__init__.py": "46c7298b83b27b02e0aaa999b5e0c142b82f3d5248ccc4f06019e1cb56c309af",
  "src/shopextract/extractors/__init__.py": "87107dda02856eb7b4aff8521527771486891ca75296b27437c94732fb8ac28c",
  "tests/test_runtime_lazy_imports.py": "64f8f0ad40bf65625a4ddaebfae4df75247716bf0ea6735655fae17bd379a8fa",
  "specs/013-audit-remediation/06-runtime/components.md": "0eb17256f0fa623d43d4c12c8054be0050d4ea64a6b8188862c6c186abf90a70",
  "specs/013-audit-remediation/06-runtime/skeleton.md": "f438fc39346719affe8fca4b1a63ed70ec110b5762edcbfcd793822b3ec80a8b",
  "specs/013-audit-remediation/06-runtime/verification.md": "b81c26a30dd06d3b9418735b46f31d446820b4f6eda70ba4768357f49d2aa788",
  "specs/013-audit-remediation/06-runtime/r1-green.log": "153e6b030bcec2bd35ea27334d5c477c34bcf0e29873b4e4956acb6d8f54c64b",
  "specs/013-audit-remediation/06-runtime/r1-green.json": "fb507c0b7498ae418b676ae5fa4df9cc39f20a7874159980dcef86fb6eee1f76",
  "specs/013-audit-remediation/06-runtime/import-after.json": "63dba7230bac23c439a8ea8524e8f9715779e3f375f5a88f3e6b8609f850aaed"
}
```

## R1b/R2 G2 — CHANGES REQUIRED

Reviewer `/root/audit_plan_review`,2026-11-01. Documentary/tests/saved red evidence
review only; no probes/tests/network/source edits.

R1b module/header/function identity seams and fresh real import graph tests are
suitable. R2 pagination contract/fixture has a correctness blocker: per_page changes
100->1 while fake responder hardcodes offset=(page-1)*100,so max101 cannot detect
page2/per_page1 fetching the second record again. Count-only assertions permit
duplicate/missing product IDs. Use realistic request-driven pagination slices and
assert exact continuous IDs. Design supported offset/cursor pagination with source
research,or a stable page-size bounded overfetch+retained clipping policy; review
any changed query contract before implementation. Do not bless impossible dynamic
page-size continuity by adapting server fixture to algorithm.

Shared retry seam also needs a real Shopify path control if deadline policy applies
to existing Shopify Retry-After behavior (parent audit A29 includes both adapters).
One controlled429/remainingdeadline case suffices to catch a forgotten caller; no
new timing sweep. Existing Woo controls meaningfully cover header parsing/limits
and public/native forwarding. R3–R5 remain outside this gate.

Predesign exact new cases before code,save focused intended-red/control results,
retain small first smoke/sequential/time/byte limits. Components/G3 and production
remain gated. Existing independent functional passes and actual25/265roundtrip
remain scoped evidence; required full repository/live/final gate still pending.

```json
{
  "specs/013-audit-remediation/06-runtime/prefetch-skeleton.md": "8386b916c507e27df9d95dfda66710470d88730502a6cfd024ad6168aaf6dd65",
  "specs/013-audit-remediation/06-runtime/spec.md": "22d63e59a4435b1acb0e9ba412e3875f7afb3a4c4ff1965aff9ca867178bcc71",
  "specs/013-audit-remediation/06-runtime/test-design.md": "4d04f222e02307e052d1ae7058041e408fab610265f3e2330f05a6f160ba7187",
  "specs/013-audit-remediation/06-runtime/verification.md": "e3d2080345b44a9f870d9538c7210ce7020b3b5178b0308865c6856cda6dd1de",
  "tests/test_runtime_prefetch.py": "f42d3f204cee89f838e7047f869e99e2ef5bcf032cd706267fee08651674b9aa"
}
```

## R1b/R2 G2 repair re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01. Inspected design delta/tests and
saved bounded red evidence. No probes/tests/network/source edits. Prior G2 findings
resolved for reviewed hashes below.

Pagination design delta is accepted: official Woo Store Products source confirms
explicit offset and IDascending ordering; bounded calls keep page1,shrink per_page
and advance offset by retained count. Realistic responder honors either offset or
standard page math and returns reverse order unless requested; exact IDs/uniqueness
now expose overlap/order mistakes. Legacy unbounded page path remains unchanged.
Actual Shopify429/deadline case prevents shared retry policy being Woo-only.
24saved intended-red cases,small smoke first;no production or green claim.

Components/G3 next; implementation remains gated. RuntimeR3–R5 not approved by
R1b/R2 gate; profile-ready is not platform/account/checkout approval. Original
actual25/265roundtrip remains resolved historical integration proof,not merchant
live coverage. Required full repository/live/final gates remain pending.

```json
{
  "specs/013-audit-remediation/06-runtime/prefetch-skeleton.md": "d22b1b9c6420ee52cb3648c1a474ecf36e202c4696ac25dab8b74eddeb63cccd",
  "specs/013-audit-remediation/06-runtime/spec.md": "2666416281de87965372bc70f1f605f18e64e3e2dcb045c465bb4001e24cbd34",
  "specs/013-audit-remediation/06-runtime/test-design.md": "1894fa800784608bc9ff96f9486ff16648c44aff751ecf84741cf86bc3406dad",
  "specs/013-audit-remediation/06-runtime/verification.md": "0adca0d2511972b775357bee477a0ba9298cdab22548b5ba3dec7551b253154c",
  "tests/test_runtime_prefetch.py": "195b1abfcd38f38edf80788c2c6749dc32222eba0dcaad90ca21e6cd81691d56",
  "specs/013-audit-remediation/06-runtime/woo-offset-source.json": "9e0d98d0241ba20cd3bfad02e3068af6d343b1fdeb1a4c8fabd925ada0db1205"
}
```

## R1b/R2 G3 — PASS

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed component ownership
against approved24-case interfaces/offset evidence. Actual shared HTTP objects
live in lightweight module with browser reexports; no wrappers/cache/provider
probes. Woo owns bounded stable-ID offset traversal,local page accounting and
separate detail caps. Existing execution state owns deadline,shared retry parses
headers for both adapters and caller cancellation propagates. No detached lifecycle
or speculative transport framework. No probes/tests/network/source edits.

R1b/R2 bounded implementation may proceed; R3/R4/R5 remain future gates. Current
known exhaustion/clip distinction and actual public/native forwarding must remain
asserted. Full-driver/live/final pending; no merchant or import-time SLA proof.

```json
{
  "specs/013-audit-remediation/06-runtime/prefetch-components.md": "39966d62f9fca8143b6ff338ae33fc8db807c98c780f6d2d4f9a40da38768dce",
  "specs/013-audit-remediation/06-runtime/prefetch-skeleton.md": "d22b1b9c6420ee52cb3648c1a474ecf36e202c4696ac25dab8b74eddeb63cccd",
  "specs/013-audit-remediation/06-runtime/spec.md": "2666416281de87965372bc70f1f605f18e64e3e2dcb045c465bb4001e24cbd34",
  "specs/013-audit-remediation/06-runtime/test-design.md": "1894fa800784608bc9ff96f9486ff16648c44aff751ecf84741cf86bc3406dad",
  "specs/013-audit-remediation/06-runtime/woo-offset-source.json": "9e0d98d0241ba20cd3bfad02e3068af6d343b1fdeb1a4c8fabd925ada0db1205",
  "tests/test_runtime_prefetch.py": "195b1abfcd38f38edf80788c2c6749dc32222eba0dcaad90ca21e6cd81691d56"
}
```

## R1b/R2 functional review — PASS scoped

Reviewer `/root/audit_plan_review`,2026-11-01. Inspected actual shared HTTP objects,
Woo offset/sort/limit/page accounting and deadline-aware retry integration; no new
probes/tests/network/source edits. Exact browser reexports retained,actual native
imports avoid crawl4ai; single before/after measurement is diagnostic,not SLA.
Bounded Woo usespage1/offset with shrinking size and ascendingIDs,clips source
overreturns,marksbudgetpartial unless terminal/header proof;unbounded legacy path
remains. Shared retry parses finite/nonnegative delay or HTTPdate,checks remaining
monotonic budget before/after sleep,both adapters retain prior data on refusal;
CancelledError is not swallowed. Public/native limits forwarded before requests.

Saved36new/lazy/native pass plus42focused compatibility repair pass are valid
scoped evidence. Prior240pass/3fail affected run and edit-harness error remain
historical,not silently upgraded to whole affected green. Offset-related fixture
correction follows reviewed query contract; unresolved currency fixture follows
02 source-authority policy. No limits/expected factual support weakened.
R1b/R2functionalPASS;R3progress/R4worker/robots/R5order still not implemented or
gated here. Required full-driver/live/final remain pending.

```json
{
  "src/shopextract/extractors/_retry.py": "90fc9519e44bd328552900b38a8c3e5d931d5d3d725010928751c66f5469e9bc",
  "src/shopextract/extractors/_http_defaults.py": "3a1e3131c40f68f8aef83ff71ef924a11e2d7ba1f40a9549c825b5900eaef4b7",
  "src/shopextract/extractors/woocommerce.py": "7afedbececf066a534e8a100eac15685d7e74234aad4540ac0f8ee43fe09e13a",
  "src/shopextract/extractors/shopify.py": "b067bc64b2f624560259fb94d42f4d69a2887b89aa6c57ef6214bbfff6d88804",
  "src/shopextract/extractors/magento.py": "4378af6109fbab840228e69437d8f87679455d99f1da17f9f9977e033be3625a",
  "src/shopextract/_execution.py": "fa4b2ef48be3694bd75ab47acd4149217d392ccf06e934c386cf2762a6f99a65",
  "src/shopextract/_extract.py": "757e1a7626bf09bf655e00dc87515420bf4b9a1e9d445a6b556471c3c1f7d140",
  "src/shopextract/tools/sources.py": "4bb24d7f97a21467a44ca1ea06db0404da14e1184ef86c5d127cfa0336c47289",
  "tests/test_runtime_prefetch.py": "195b1abfcd38f38edf80788c2c6749dc32222eba0dcaad90ca21e6cd81691d56",
  "specs/013-audit-remediation/06-runtime/verification.md": "4a5867deee15898901a0dba7ad9efbc66173a95b84af37489334807533cd5565"
}
```

## R3 lifecycle clarification — G1 PASS; G2 CHANGES REQUIRED

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed14 actual-loop/CLI/private
codec red cases and documentary lifecycle; no new probes/tests/network/source edits.

G1conceptPASS: owner enables checkpoint only for extract-store;producers register
accepted buffers by reference,no per-page normalization/serialization,new global
cache or independent budget framework. Owned cancellation is awaited before sync
existing-normalizer/portable freeze;other command result types/external cancellation
remain unchanged.1000/8MiB/250knodes/depth56 caps reserve response framing margins.
Actual Woo/Shopify/HTML loss-after-progress,emptytimeout,restart,client cleanup and
small narrowed codec boundaries are meaningful intended-red mechanisms.

One G2 compatibility/interface gap blocks implementation:
- Metadata scope/resultplatform/restore flags are promised,but register_source only
  names normalizationplatform/shopURL. Name exact private context/metadata shape
  and setter/arguments,plus snapshot()->ExtractionResult|None. HTML normalized as
  GENERIC after declaredMagento API failure must still report actual selected tier/
  resultplatform/scope correctly;do not overload one platform variable for both.
- Strengthen real HTML timeout case to assert returned tier/platform/nonempty
  expected observation_scope. Add --restore-short-gtin timeout compatibility case
  with known checksum-valid short source,requiring same opted-in normalized value/
  original source support as normal execution and preserved unopted behavior. This
  catches a recovery path forgetting caller conversion policy while scalar prices
  happen to look correct. No fake checkpoint/pipeline substitute.

Document timing limit honestly: byte/node/product bounds cap recovery work,not
wall-clock completion by original networkdeadline. Sync freeze after cancel and
cooperative cancellation do not prove hard deadline/native-block cleanup;R4/final
mechanism evidence must cover remaining wall-clock lifecycle. No new SLA/budget
increase or per-page serializer is inferred here. Components/G3 and production
remain pending revised G2;full-driver/live/final still open.

```json
{
  "specs/013-audit-remediation/06-runtime/spec.md": "269ca8ac0df8c50d891f95f00d77626ec5bb1a520bc32122f59a408968853e62",
  "specs/013-audit-remediation/06-runtime/test-design.md": "a0f5413173b12340188d27a704b01d212fd7caf03d71e293f818d7e3ff827da6",
  "specs/013-audit-remediation/06-runtime/checkpoint-skeleton.md": "8a774ecb33589859bf675c332da2ed871410efa9d07e0c798a208247c3d3e63b",
  "specs/013-audit-remediation/06-runtime/verification.md": "f336b8a1bb06581286022f635a8fb9e0942d9b075e072ba747126def082e7497",
  "specs/013-audit-remediation/06-runtime/checkpoint-full-red.log": "50f4f63db246801809442893ae3b037a099fd7f19cb0f933f6bfbf5f6fd9bcf5",
  "tests/test_runtime_checkpoint.py": "70f9f392621aa387901dd267de6893808b514ba9442b9bfafa29a7300e41a7cb"
}
```

## R3 G2 metadata repair re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01. Inspected named metadata API and
17case acceptance,actual16intendedred/1emptytimeoutcontrol evidence;no new probes/
tests/network/source edits. Prior G2 compatibility findings resolved:
configure_result separates resultplatform/scope/conversion policy from source
normalization platform;tier is source-specific,snapshot returns ExtractionResult
orNone. Actual Magento-fallback HTML recovery asserts Unified tier/Magento/exact
catalog scope. Independent typedGeneric source preserves its own Productplatform.

Actual Shopify normal completion versus timeout covers restored/unrestored known
11digitGTIN for250products with exact expected canonical values,original raw source
and observed restore transformation. This exercises real existing normalizer/
portable codec,not fabricated expected checkpoint output. No scalar defaults become
observed currency facts. Restart/external cancellation/resource boundaries remain.

G2PASS;components/G3 next before implementation. Sync recovery bounds are explicitly
work/retention caps after owned cancellation,not total wall-clock proof within I/O
timeout. R4/native hard-deadline and final docs/evidence must retain that limitation.
Full-driver/live/final remain pending;no policy/timeout-budget enlargement inferred.

```json
{
  "specs/013-audit-remediation/06-runtime/checkpoint-skeleton.md": "3d645cef1566f87522f17c00bf4ef0b72836fe1fc36553a54147090ea80f7d65",
  "specs/013-audit-remediation/06-runtime/spec.md": "269ca8ac0df8c50d891f95f00d77626ec5bb1a520bc32122f59a408968853e62",
  "specs/013-audit-remediation/06-runtime/test-design.md": "7b0c3805a71ffc5e1374d83f3f19820f549ccc0cd4e35e9cdd60abdd254ceb54",
  "specs/013-audit-remediation/06-runtime/verification.md": "1bd9cd27627a8afee804fce6e59ff184266ec12c715664a043a6233d8ecadf1a",
  "specs/013-audit-remediation/06-runtime/checkpoint-metadata-red.log": "27ed00e22933b6ebb10b032c130d0e351b8b6287daf9fce7c022cf342b110117",
  "tests/test_runtime_checkpoint.py": "bb2eac9f34e999403b33888de1b19e5fbba034ca798bcfaaa03cd5c0859d20a0"
}
```

## R3 G3 — PASS, reference ownership and bounded freeze

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed component map against
approved17-case interfaces/lifecycle and source metadata. No probes/tests/network
or source implementation. Context-owned producer references avoid per-page
serialization;metadata separates detected result scope/restore policy from source
normalization/tier. Accepted Shopify currency support precedes registration.
Owner cancellation is awaited before existing normalizer/portable-codec freeze,
explicit positive incomplete prefix/no-usable timeout,external cancellation and
other command result types stay separated. No detached lifecycle/persistence/cache
framework. Fixed limits reserve response margins and can only narrow privately.

Minor reviewer clarification makes generic collector count within existing max8
source references,rather than ambiguously eight-plus-one;no expanded limit.
Sync freeze remains bounded work after I/Odeadline,not walltime/peak-memory SLA.
Actual green/affected/cleanup verification is still required.

G3PASS allows bounded R3 implementation,first saved Woo/HTML smoke then focused
17case/affected checks. R4/R5,required full-driver/live/final gates remain pending.

```json
{
  "specs/013-audit-remediation/06-runtime/checkpoint-components.md": "de8ce90c5370f4ac502724fec7b6e47f61e0d423d724481b5490a32c4fdba8ed",
  "specs/013-audit-remediation/06-runtime/checkpoint-skeleton.md": "3d645cef1566f87522f17c00bf4ef0b72836fe1fc36553a54147090ea80f7d65",
  "specs/013-audit-remediation/06-runtime/spec.md": "269ca8ac0df8c50d891f95f00d77626ec5bb1a520bc32122f59a408968853e62",
  "specs/013-audit-remediation/06-runtime/test-design.md": "7b0c3805a71ffc5e1374d83f3f19820f549ccc0cd4e35e9cdd60abdd254ceb54",
  "tests/test_runtime_checkpoint.py": "bb2eac9f34e999403b33888de1b19e5fbba034ca798bcfaaa03cd5c0859d20a0"
}
```

## R3 functional review — PASS scoped, work-bound timing limitation retained

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed actual owner/checkpoint/
producer integration,17acceptance pass and focused8repair pass;no new probes/
tests/network/source edits. Source references/normalization/tier/restore/captured
currency policy and result metadata follow reviewed contracts. Owned wait_for
finishes cancellation before snapshot;external cancellation propagates and clients
close. Context finally drops progress reference. Generic same-URL collector keeps
latest admitted view and404 never registers source.

Snapshot cost is per-record incremental bytes/nodes plus one bounded final decode;
it does not repeatedly serialize entire retained prefix.53.89s acceptance duration
is not proof of quadratic behavior. Existing codecs validate/freeze values/support,
no per-page serializer. Product/node/byte/depth limits remain fixed,narrow-only,
and positive result explicitly incomplete. Sync cleanup/freeze can follow I/O
deadline;this is not total-walltime/peak-memory SLA.

Source-format inference now reuses existing generic normalizer for captured
structured HTML even when result platform is detectednative;no new source facts
or cross-store merge. Current17green plus focused8 are scoped evidence;prior
240pass/1CLI-node fixture failure is not a fresh whole affected pass. Portable
default1M remains unchanged;correcting CLI-specific stale100k fixture does not
relax existing codec guard.

Nullable variant-stock portable amendment remains a relevant pending cross-feature
interface fix;unknown child stock cannot yet be declared fully portable from this
R3pass. R4/R5,required full-driver/live/final and docs reconciliation remain pending.

```json
{
  "src/shopextract/_execution.py": "e4c427f65c998f6afe7d551ddba904accb5e02bc23661a62d628e7820904abe6",
  "src/shopextract/_cli_extract.py": "ae4367a4c50afbe936389959503f159e8664d76f29d555321e18cd9c49cf6447",
  "src/shopextract/_extract.py": "1466e2c55c37378ef5069c3223f8967dc965fd3fdfedbce74c884efe673ac210",
  "src/shopextract/extractors/unified.py": "69ef165e3b544406d368c0fda0ec4ee10608d2564588f62a0828d9bad90d2c78",
  "src/shopextract/extractors/shopify.py": "1b24ee5e4a33249b73e27136d2304a6941ac96682e9ab8deb244cc07531c512b",
  "tests/test_runtime_checkpoint.py": "57bc6b1335394d1f99fc55cfcc015faa3da6b20546f46ff1d32af8e7948b1174",
  "specs/013-audit-remediation/06-runtime/verification.md": "d3df8d76e2abbb4ba2c18b395d319210d04c0cec26079ec7b11dcf7a5e97b039"
}
```

## R4/R5 refinement — G1 concept PASS; G2 CHANGES REQUIRED

Reviewer `/root/audit_plan_review`,2026-11-01. Focused review of14cases and
current documentary interfaces;no probes/tests/network/source edits. Owned default
worker with explicit borrowed-client cooperative exception,bounded existing-parser
HTTP walk,fail-closed robots/same-origin guards and list-compatible reason metadata
are a coherent refinement. No SDK/browser walk or native tool authority bypass.
Borrowed client lacks hard-kill guarantee intentionally;document that compatibility
exception. Default strategy loss must be explicit rather than fabricated complete.

Three bounded G2 corrections before code/components:

1. Lifecycle tests prove only directPID death;require one controlled owned descendant
   cleanup assertion to prove process-group reaping. Existing finite oversized
   stdout can pass communicate-then-check,which is not bounded streaming. Use
   bounded burst-over-cap then hang for stdout/stderr,expect protocol-overflow
   termination before timeout and PID absence. Tests must finally clean their
   known owned PIDs even on assertion failure;no unlimited writer/large allocation.
2. Borrowed AsyncClient may have follow_redirects=True;existing redirect fixtures
   defaultFalse and cannot catch auto-follow before policy. Add one actual borrowed
   configuration case proving forced manual hop/robots checks and no forbidden or
   cross-origin request. Existing transport authority stays beneath shared guard.
3. R5 mutation assertion constructs a fresh ExtractionResult,not the instance passed
   to extraction_data. Retain actual input/source buffers and assert unchanged.
   Oppose canonical-ID and URL order to prove required keypriority rather than
   coincidentally aligned externalID/URL fixture;preserve exact source values.

No new broad investigation required;these adjust current mechanisms/fixtures.
Current loopback is acyclic,so do not claim executed nested-cycle coverage solely
from that fixture;the designed cycle invariant remains a final mechanism check.
Corrected Product.product_url/synchronous worker.main harness is honestly recorded
after initial red run;do not upgrade it to rerun evidence without execution.
G2/components/production remain gated;source/request/body/URL/queue guards must
still be verified honestly during implementation. Full-driver/live/final pending.

```json
{
  "specs/013-audit-remediation/06-runtime/discovery-spec.md": "57eacdef371ca3e73e186a1f5172e701d6c75823e354c4469f9a52a174ec1184",
  "specs/013-audit-remediation/06-runtime/discovery-test-design.md": "6d53254a464fbd328f5d47462dca0a932790d76dd7a2360277bd51d4295ee942",
  "specs/013-audit-remediation/06-runtime/discovery-skeleton.md": "d443ef649667ead984e4f6f21dcdb0ea4d5f3968649a94e5f677a5fee62e7ba2",
  "specs/013-audit-remediation/06-runtime/verification.md": "1c05a9ad12fb610b7a06fedfa2265aa7575db541851cd7c8500f9264f9892ee9",
  "tests/test_runtime_discovery.py": "3c5716d06aaca4de0abf0b18ba2828023b82ffb5c8fcac48841017664f582d4b"
}
```

## R4/R5 G2 repair re-review — lifecycle harness completion required

Reviewer `/root/audit_plan_review`,2026-11-01. Focused15-case source/test review
with saved4intendedred;no probes/tests/network/source edits. Borrowed client
auto-follow guard and actual-input canonical-order/nonmutation findings resolved.
Descendant PID assertions and stdout burst-then-hang improve lifecycle coverage.

Remaining small harness correction before G2PASS:
- Timeout/cancel tests lack finally cleanup of known ownedPIDs when a deliberately
  broken helper fails to kill descendants. Add bounded failure cleanup,not leaked
  60s processes outside the driver group. Install parent TERM wait/reap handler
  before parent-ready PIDfile so cancellation cannot race handler setup.
- Protocol overflow still has no trackedPID/absence assertion,and stderr program
  prints malformed stdout and exits. That passes plain malformed-JSON handling
  without proving stderr budget kills. Track known PID and use bounded stdout/
  stderr burst-then-hang variants,require protocol-overflow/no lingeringPID and
  finally cleanup. No unlimited output allocator or extra case family needed.

These complete originally requested bounded-drain/group-cleanup invariant;same
15case count and limits may stay. G2/G3/production still pending this correction.
Current acyclic loopback still not claimed as cycle pass. Full/live/final pending.

```json
{
  "specs/013-audit-remediation/06-runtime/discovery-test-design.md": "d7eb669fdb5286cab59254cded0429b4ea963ec142f55c692c8861a87fda4b8e",
  "specs/013-audit-remediation/06-runtime/discovery-skeleton.md": "d443ef649667ead984e4f6f21dcdb0ea4d5f3968649a94e5f677a5fee62e7ba2",
  "specs/013-audit-remediation/06-runtime/verification.md": "4a48f6af39a242d22ce9ba5f284786903a5aa4a87b3fd9ea138c485e143cfc6b",
  "specs/013-audit-remediation/06-runtime/discovery-repair-red.log": "8d077d59e2c0ea3e3c8a73b39eb4d1b9b3f9ee6ebf57c4af02609697cddcbcec",
  "tests/test_runtime_discovery.py": "8c326d9e6e1aa6802a162a68d056080392cdcd4ae405589abdd19f4b5b78c436"
}
```

## R4/R5 G2 final lifecycle harness re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01. Rechecked exact residual harness
findings only;no probes/tests/network/source edits. Parent installs TERM handler
before ready marker;timeout/cancel prove both parent/descendant absent,finally
knownPID cleanup covers broken helper paths and active task cancellation. Both
stdout4MiB+1/stderr64KiB+1 tracked-PID bursts hang rather than finish;tests require
protocol rejection before timeout and no lingeringPID,with failure cleanup.
Malformed JSON remains separate control. Same15cases;three focused seam reds
saved,not whole repaired15green.

Prior borrowed-auto-follow and actual-input/nonaligned canonical order controls
accepted;all previous G2 findings now resolved for reviewed hashes. G2PASS permits
component authoring/G3 next,not production yet. Cycle mechanism still designed
but not proven by acyclic loopback;full implementation verification must report
its actual coverage honestly. Required full-driver/live/final remain pending.

```json
{
  "specs/013-audit-remediation/06-runtime/discovery-spec.md": "ff15dba87b4ca73294b61a53b6c0fd6bda2c05e84142f9ba8207df542ef93487",
  "specs/013-audit-remediation/06-runtime/discovery-test-design.md": "785f78d7c7475ce1a54f2a83eb4c6bb8ae45b7827d051f75880051bc01605467",
  "specs/013-audit-remediation/06-runtime/discovery-skeleton.md": "d443ef649667ead984e4f6f21dcdb0ea4d5f3968649a94e5f677a5fee62e7ba2",
  "specs/013-audit-remediation/06-runtime/verification.md": "4a48f6af39a242d22ce9ba5f284786903a5aa4a87b3fd9ea138c485e143cfc6b",
  "specs/013-audit-remediation/06-runtime/discovery-harness-red.log": "d85b6e4fd0ced157627074f1e8f534a8742445a32eb8cb453eae6b8561283db5",
  "tests/test_runtime_discovery.py": "4758dfd4bf213d5b9550774003fef5cb67065d12fd419b339da6b6396c58539b"
}
```

## R4/R5 G3 — one stable-fact key correction required

Reviewer `/root/audit_plan_review`,2026-11-01. Component architecture otherwise
sound: existing strategy/parser/transport reuse,operation-owned robots/cache/
request/body limits,bounded FIFO,one owned process group with concurrent bounded
readers/TERM-KILL-reap,explicit borrowed-client cooperative exception. No probes/
tests/network/source edits.

R5 proposes full portable-record tie key,but that contains scraped/capture/evidence
metadata;for equal canonicalID+URL,timestamp variation can reorder distinct stable
source facts. This differs from reviewed stable SOURCE-VALUE tie contract. Define
bounded normalized fact projection excluding volatile metadata;include meaningful
Product scalar/source facts and stable variant facts rather than relying on input
completion order when chosen keys tie. Add one equal-ID/equal-URL A/B record pair
with opposed observation times and require factual order invariant across changed
timestamps,without changing source/evidence values. No serializer framework needed.

Author acknowledged exact correction. Existing loopback may be strengthened to
actual self-index cycle+leaf with once-per-map assertion to execute planned cycle
mechanism (no new source/network sweep or separate fixture family). Until executed
do not claim the acyclic fixture covers it. Same small budget,one new tie case.
G3pending that documentary/test correction;other ownership accepted. No production
or full-driver/live/final approval yet.

```json
{
  "specs/013-audit-remediation/06-runtime/discovery-components.md": "7f6adbdd0392f26ad8267d4434ce133deaf421ea5b81048d13b18529b70c07f3",
  "specs/013-audit-remediation/06-runtime/discovery-spec.md": "ff15dba87b4ca73294b61a53b6c0fd6bda2c05e84142f9ba8207df542ef93487",
  "specs/013-audit-remediation/06-runtime/discovery-skeleton.md": "d443ef649667ead984e4f6f21dcdb0ea4d5f3968649a94e5f677a5fee62e7ba2",
  "tests/test_runtime_discovery.py": "4758dfd4bf213d5b9550774003fef5cb67065d12fd419b339da6b6396c58539b"
}
```

## R4/R5 G3 stable-fact correction re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01. Exact correction reviewed,no new
probes/tests/network/source edits. Tie projection uses declared Product fields
except raw_data/scraped_at,including normalized variants/attributes;dynamic
evidence/capture metadata excluded. Smaller projection remains within validated
record bounds.16th duplicatecanonicalID/URL/title pair varies vendor facts against
opposed timestamps and has saved intended red;it tests metadata-independent order.
Existing loopback now has real self-index cycle+leaf with once-per-map assertions.

Prior component ownership accepted;G3PASS allows bounded R4/R5 implementation.
16designed cases/priorred evidence are not green or executed cycle proof yet.
Required full-driver/live/final pending;borrowed-client cooperative exception and
source/request/body/worker bounds remain mandatory.

```json
{
  "specs/013-audit-remediation/06-runtime/discovery-components.md": "8b310d02200d440b83fc1733f18845a8b98601de414f12f839528edba535db73",
  "specs/013-audit-remediation/06-runtime/discovery-spec.md": "ff15dba87b4ca73294b61a53b6c0fd6bda2c05e84142f9ba8207df542ef93487",
  "specs/013-audit-remediation/06-runtime/discovery-test-design.md": "f3c44843c326157b469bec03c6f42a2250c5bebbb14255d29421bfc3d74bb8ec",
  "specs/013-audit-remediation/06-runtime/discovery-order-red.log": "1e350d900e691d6dd617ccf8d8b4fdf01f2e696b52297fd4962d802e0e33c101",
  "tests/test_runtime_discovery.py": "a4ba48530c63f10c70dd86a2234c5689b69cb73b776834f1fafb3a51eb809b38"
}
```

## R4/R5 functional source review — BLOCKED (two repairs)

Reviewer `/root/audit_plan_review`, 2026-11-01. Bounded source inspection only;
author saved 16 acceptance green and final18 focused green are scoped evidence,
not a full affected-suite pass. No reviewer network/test sweep or production edit.

1. Worker cleanup: `stop()` escalates to group KILL only when leader `proc.wait()`
times out. A leader that exits on TERM can leave a descendant ignoring TERM alive;
the existing descendant fixture accepts TERM and therefore misses this branch.
Ensure surviving owned group members are killed even after leader exit, retaining
the cleanup reserve and leader reap. Design one resistant-descendant lifecycle
case before repair; known-PID finally cleanup remains required.
2. Native `GuardedSources.discover` still builds unrestricted candidate/pending
lists from each bounded XML response and has no aggregate5000 locations/maps guard.
The request cap bounds network count but does not implement the agreed queue/CPU
limit. It also omits wrapper reasons from successful return diagnostics (e.g.
cross-origin nested denial). Share the bounded traversal accounting or add the
same operation-wide guard with explicit diagnostic; exercise the actual native
path with overflowing index and no extra fetch after limit. Retain tool authority
and accepted sibling behavior.

Other inspected contracts match design: manual redirects force follow_redirects=False
even on borrowed clients; robots precedes requests/emission; response streaming
bounds consumption; default worker vs cooperative borrowed exception is explicit;
platform/browser imports remain outside bounded walking; copied portable Product
facts exclude raw_data/scraped_at and preserve original objects. Native transport
continues through existing GuardedTransport.

Separate final-doc discrepancy: capabilities currently advertises json_nodes100000
while catalog default is1M; reconcile in already planned final documentation pass.
Functional approval awaits only the two concrete repairs above. Full driver,
actual live observation and final independent gate remain pending.

```json
{
  "src/shopextract/_discovery_runtime.py": "2e55bbea0503551bb9e33b3f5edb00978d13b6c330739eb5fdd2ed4bc569e745",
  "src/shopextract/_discovery_worker.py": "ead1a8f55b256f3f4458be2d19abc69b1ae3db051aa82b6b08d0802a6395cdff",
  "src/shopextract/_discover.py": "b4538d1d15c84a42dd84ef88b56ff7106685dbf1a132695d6a4d269ce172492f",
  "src/shopextract/tools/sources.py": "35befb4e955034cd0b09af67a4843e4e0d333d75ac470d44ee8eeef34fb02e3b",
  "src/shopextract/_cli_data.py": "4f1372aad19f50e3ce74cdeca862036c2541f4de231c8e215b2c10d33b43e070",
  "tests/test_runtime_discovery.py": "a4ba48530c63f10c70dd86a2234c5689b69cb73b776834f1fafb3a51eb809b38",
  "specs/013-audit-remediation/06-runtime/discovery-final-focused.log": "aedd955807485ab573771da2dc59261a64357f1455cfa485f4a40a98ba89deb6"
}
```

## R4/R5 focused functional blocker re-review — PASS

Reviewer `/root/audit_plan_review`, 2026-11-01. Exact repair source/tests/logs
reviewed; no independent broad tests/network or production edits. `stop()` now
sends group KILL after the leader wait regardless of whether TERM reaped its leader;
new real descendant fixture ignores TERM with DEVNULL pipes, tracks both PIDs,
waits boundedly for disappearance and finally cleans up on failures.

Native collector increments one operation-wide location count across index and
leaf XML before queue/admission and stops above5000; 4999 index+one leaf boundary
versus5000+one leaf exercises the actual GuardedSources transport. Deduplicated
finish diagnostics preserve wrapper reasons. Request-budget fixture verifies
robots+root+14 maps=16 requests, retains14 accepted URLs, forbids map15 fetch and
returns explicit budget reason. Existing queue identity and tool authorization
remain intact. Saved three designed reds preceded source repair; saved19 cases
green5.40s are scoped functional evidence. Both concrete blockers resolved.

This permits proceeding to required full test driver and planned live checks;
it is not full affected-suite/final approval. Earlier failed broad logs remain
historical failures until rerun. Final capabilities node-limit reconciliation
remains in the planned documentation pass.

```json
{
  "src/shopextract/_discovery_runtime.py": "ca50bbe3b031a7a3c4380518c2767dd029a6a3a75a737ac1c93f2a632b4ec090",
  "src/shopextract/tools/sources.py": "2d735254bc9414ab467799e872c7815823343dad660b4cc81664d6aca5e977b8",
  "tests/test_runtime_discovery.py": "a8ab32bab172e294e1b5a6145b26d835d68f89e00a43a7fe3f73824f7cf70c6b",
  "specs/013-audit-remediation/06-runtime/discovery-functional-red.log": "5dfbf84cd785aea091c41c5741fee9a47eb694b35e16960f85e22c8ded47f79c",
  "specs/013-audit-remediation/06-runtime/discovery-functional-green.log": "41656b3f9e9262c7a1992a72c43860b465b2f8da162c2b112e2c9dfe2ebf4db9"
}
```
