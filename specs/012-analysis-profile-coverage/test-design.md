# Behavior and test design (before task breakdown)

Author: primary agent, 2026-10-25. Planning only; all new executable checks below are planned.

## Scenario matrix

| FR | SC | Fixture and action | Exact expected outcome | Distinct risk / existing gap | Offline / live |
| --- | --- | --- | --- | --- | --- |
| 01,02 | 01 | Hash-verified saved three YAML category branches plus attributes; run inventory twice with reordered input | Stable category-ID rows and totals; separate proposed vs implemented vs checked; explicit denominator and unassessed branches | Adapter count mistaken for domain coverage; no current reproducible inventory | Offline inventory snapshot; live N/A |
| 02,03,05 | 02 | Saved three reference IDs and refrigerator umbrella attribute definition | Laptop/boots partial, refrigerator missing before implementation; umbrella excluded; no inferred numeric RAM capacity | Upstream metadata can be irrelevant or lack operational fields | Saved-source review; live N/A |
| 03,06,08 | 03 | Existing three profiles, custom text/decimal/mass profile, legacy goal and CLI/schema fixtures | Existing definitions/results unchanged, custom definitions accepted, collisions still rejected; legacy selection default unchanged | Silent profile mutation or schema drift breaks old jobs | Focused regression + full driver; live N/A |
| 03,04 | 04 | 500 ml vs 0.5 L; 60 cm vs 0.6 m; 250 L vs 300 L; 0 ml vs 0 L; independent width/height/depth fields | Equal/equal/different/equal with exact decimal transforms; width never compared as height | New physical dimensions unavailable in current three-kind engine | Real compare_field and validation, then engine fixture; live equivalent values optional |
| 04,05 | 04 | Missing, null, empty, false, negative, NaN, infinity, 1–2 L, unitless 250, 250 kg, unknown units; net vs gross volume, packaging vs product dimensions | Unknown with specific reason and preserved input state; no proposed correction; bool distinct from numeric zero | Unsafe coercion, cross-dimension conversion or semantic alias collapse | Deterministic table, real rules/parser/engine; live not safely inducible |
| 05 | 05 | Controlled captured raw quantity/alias; exact pointers; absent/truncated/expired/LLM-only companions | Supported raw fact reaches normalized attributes with source evidence; unsupported values remain unavailable; no taxonomy-supplied defaults | A working comparison on hand-filled dicts can hide extraction gaps | Real capture → normalize → companion → store → engine; live required per affected seam |
| 06 | 06 | Exact refrigerator binding + explicit profile; then remove selection/binding, conflict it, add competing targets, mark partial | Valid case enables comparison subject to other guards; every missing/conflict case needs_review and no proposed correction; no automatic selection | New binding may accidentally bypass explicit selection | Real category_review_reasons plus engine; synthetic |
| 07 | 07 | Same anchored identity, 250 vs 300 L; same volume but conflicting GTIN/MPN; distinct model/dimensions; existing RAM and shoe-size conflicts | Identity_variant change remains needs_review with no proposed correction; matching quantities never override matcher veto | Correct normalization can mask unsafe identity/variant changes | Production matcher/engine/recheck, no mocked decision |
| 07 | 08 | Selected refrigerator profile: capacity checked, width missing, malformed height, depth not requested; generic-only product | Separate configured/requested/checked/unavailable/invalid/unsupported sets; no full coverage claim; API/CLI report agrees | Profile presence mistaken for actual analyzed-field coverage | API/CLI golden structure and engine output; live no forced missing-state assertion |
| 08 | 09 | Save job, resume unchanged; alter rule definition/unit policy or category snapshot before resume/recheck | Identical-policy replay stable; changed definitions/config rejected through mismatch contract; original snapshot retained | Policy upgrades alter historical findings | Real temporary SQLite + restart/recheck; synthetic |
| 05,06,09 | 10 | Realistic Shopify/Woo/Magento/Shopware/BigCommerce/generic fixtures, explicit exact scoped mapping to same reference ID | Same profile definition reused; supported attributes analyzed only where captured; unsupported lanes explicitly unavailable | Platform parity on category extraction falsely implies attribute parity | Real six adapters and normalizers; only external transport controlled |
| 01,09 | 11 | Valid synthetic registry subsets of 999/1000/1001 targets; reordered duplicates/scope-conflicting IDs | First two within existing validator cap; 1001 rejected; existing duplicate/scope validation retained; inventory may hold >1000 but runtime subsets may not | Importing saved taxonomy bypasses existing runtime bounds | Real config validator; no full-taxonomy runtime import |
| 03,08 | 03,09 | Persist a job under only the prior registry, reopen after adding refrigerator; separately alter a selected rule | Unrelated registry addition resumes unchanged; selected definition change fails profile_mismatch; original snapshot remains unchanged | Registry growth confused with changing a historical selected policy | Real Store and restart; offline |
| 07 | 08 | Report limit 0/1/999/1000/1001, default 100 and nonzero offsets over 101 findings; diagnostics-enabled UTF-8 envelope/newline sized at 1 MiB −1/at/+1 | Valid pages preserve deterministic finding order and accurate scoped diagnostics; invalid limits reject; first two byte sizes succeed, +1 rejects before partial output or file replacement | Pagination skips/double-counts or additive diagnostics exceed output budget; multibyte text miscounted | Real Store/report/public operation/CLI; offline |
| 03,07 | 03,08 | New goal requests a field absent from selected profile; separately labelled persisted legacy/corrupt-state fixture reaches real engine without that rule and with supported inputs/strong identity | Creation retains invalid_argument; defensive runtime case is unknown/review-only with unsupported-field diagnostic, never exception/correction | Weakening existing admission versus unsafe runtime dereference | Real validator and engine, not mocked comparison; offline |

## State and compatibility contracts

Coverage dimensions are independent: category mapping → explicit policy/binding validity → captured attribute availability → requested rule execution → finding guarded by existing identity/evidence policy. A prior state alone cannot claim the next. Record deterministic ordered reason sets. Unknown numeric comparison is never equality. New rule kinds must have consistent Python validation, CLI JSON schema, serialization and stored policy digests. Existing profile definitions are immutable; new capabilities cannot reinterpret old persisted definitions. No automatic profile selection is included.

## Red-test plan

After G1, author writes tests/test_profile_coverage_inventory.py, tests/test_profile_quantities.py, tests/test_profile_coverage_integration.py and tests/test_profile_coverage_cli.py (names proposed, finalize at skeleton). Save intentional missing inventory/new-rule/profile/report failures before production logic. Existing regressions must pass at baseline; environmental failures are not accepted red behavior. Exact report keys and unknown reason enums must be frozen at G2; tests derive semantics from this matrix.

## Unobservable behavior and synthetic mechanism plan

Fixture author: implementation delegate, independent expected-outcome review: separate reviewer. Use deterministic factories, seed 26, schema-valid products and source-shaped raw payloads derived from sanitized saved examples. Label generated URLs/timestamps synthetic. Capture metadata explicitly, never invent live provenance. Exercise real normalization/category mapper/codec/Store/Engine/matcher/recheck; mock only network, time and injected persistence failure where necessary. Existing tests may satisfy identical scenarios only with matching saved evidence. Add one rollback/retry fixture: injected failure before finding commit leaves no partial committed finding; retry under unchanged snapshot emits one logical finding. Add an assertion-sensitivity check using a temporary faulty unit conversion, restored before shipping, to demonstrate detection of 500 ml vs 0.5 L error.

## Bounded stress plan

First smoke: one complete synthetic refrigerator job; save before expansion. Then one sequential driver with 48 cases: 12 valid unit/equality/inequality cases, 12 invalid-or-missing/semantic-context cases, 6 adapter cases, 8 binding/identity/partial interactions, 4 replay/fault cases and 6 registry/order cases. Case manifest must assign each risk/outcome before generator implementation; variation alone is not distinct coverage. Seed 26; each payload ≤64 KiB, registry fixtures ≤2 MiB, aggregate input ≤16 MiB, logs ≤256 KiB; at most 25 products/job, 16 requested fields/product, one worker, 120 seconds total including cleanup, per-case ≤10 seconds; stop at first failure and save minimal repro. One diagnosed repair then affected rerun within same limits or record blocker. Registry cases validate configs, not 1000-product inference. No model calls. Child process timeout cleanup required. Observed memory is recorded, with driver memory ceiling 512 MiB and orderly stop if exceeded; fixtures do not prove production scale.

## Bounded live plan

Only after offline success and before each slice's final verification: choose explicit publicly readable product URLs from existing saved domain discovery, log them and expected supported fields before requests. No invented or assumed accessible targets. Begin with one refrigerator capture; at most 3 product URLs total across platforms with affected extraction seams, 2 requests/URL, 6 requests total including redirects/retries, one worker, 15 seconds/request, 90 seconds driver including cleanup; zero automatic retries, stop on access denial or first unexpected behavior. Each redirected request consumes budget. Record source data/support and actual profile comparison; retain missing attributes and unchanged products honestly. If more than three adapter extraction seams change, split implementation slices and run a separate bounded plan per slice. Unchanged adapters use real-path synthetic parity, not fabricated live claims. No live product change is required or induced. Required live attribute evidence blocked by access remains blocked; complete synthetic mechanism/stress checks separately, and do not declare that slice fully verified. Planning/docs-only work: live N/A.

## Inventory fresh-checkout and retained-source test distinction (G2 repair)

SC01/02: default tests use7 deterministic synthetic source-shaped nodes across
three branch files; known IDs exercise3 reference assessments and4 unreviewed
nodes remain pending. Fixture attribute counts are2 each, not actual19/16/10.
Test-only SOURCE_PINS replacement supplies size/hash authority; real parser,
hash integrity, graph validation and report assembly stay untouched. Default
immutable production pins are independently asserted. No network, raw corpus
checkout requirement or skip is introduced.

SC01/11 adverse cases: empty selection, duplicate branch, unknown/repeated IDs,
missing/changed unselected source must fail closed. Re-pinned malformed YAML,
duplicate category IDs and dangling child exercise structural rejection after
hash success. These target admission, integrity and graph risks separately.
Existing real runtime999/1000/1001 cap tests remain independent of report size.

Actual retained-corpus acceptance is separately executed with
 evidence/retained_inventory_acceptance.py; absent/changed inputs fail, not skip.
Exact4125 node/4122 pending counts and actual19/16/10 declared attributes belong
to that gate, not synthetic expected outputs. Raw sources remain local. Driver
first saves actual smoke before expansion once production logic is reviewed and
implemented. Current declaration must fail intentionally after hash verification.

## Inventory additional distinct parser/resource risks (before implementation)

A disconnected self-cycle plus one valid branch root must reject invalid_source;
existing dangling-child tests cannot reach parent-walk cycle detection. Build it
by appending one self-parent node with a valid declared attribute. A category
that declares an unknown attribute must reject invalid_source after source pins
are valid; taxonomy definition links must not silently disappear in reporting.
These2 synthetic fixtures are re-pinned only at the authority boundary.

Iterable admission must materialize no more than4 branch names or5001 selected
IDs; more than3 branches or5000 IDs rejects invalid_selection before parsing.
A sentinel generator yields5001 IDs then raises if read further; expected result
is invalid_selection with exactly5001 consumed, proving bounded materialization
rather than merely testing unknown names. No large corpus/generator sweep.

## APC07 pilot refinements for independent refreshed G1

Candidate exact contract: pilot-contracts.md. Quantity equality examples now use
explicit semantic wrappers; bare500ml string cannot establish total-volume meaning.
Distinct per-axis normalization IDs reject width/height substitution in compare_field
itself;128-character input boundary and long coefficient under lowDecimal precision
must prove context-independent exactness. Product annotation widens additively.

One demonstrated generic extraction gap is opted-in only for persisted selected
refrigerator jobs; same raw input with defaultFalse must preserve old3 results and
hardware model outcomes. Tests follow real parser→normalize(record_inputs label+
value)→support→portable→Store→comparison. Add ambiguous propertyID/name, duplicate
conflicting declarations, raw-attribute conflict and model-source conflict tests;
none may silently pick an interpretation. Native5 paths intentionally report
selected quantity support unavailable, not parity fabricated from source shape.

New fridge without category config/binding is review-only; exact mapping alone
never selects it. Anchored wrong-Boots and capacity equal plus GTIN/MPN conflict
retain veto. Goal unknown rule still invalid_argument; legacy/corrupt engine path
returns unknown/unsupported_field without dereferencing absent role.

Report classifications derive only from retained snapshots/findings; unknown
legacy input states stay unknown. Requested fields include persisted goal while
page_fields identify which outcomes can count in this page. Page0/1/999/1000/1001,
nonzero offsets over101 findings and UTF8 exact1MiB−1/at/+1 envelopes prove bounded
materialization and atomic stdout. Existing report APIs have no file destination;
no new report export API is invented. Existing atomic artifact helper regressions
remain applicable; diagnostics preflight must precede any future artifact replace.

48-case design manifest: evidence/pilot-case-manifest.json, seed26, each case
names risk/input/expected outcome/real seam and is designed_not_executed. Separate
focused old-profile/customschema/reportbudget/mutation checks remain required;
48-case count is not a substitute. Source audit receipts are synthetic mechanism
research, not future full engine/stress/live passes. Concrete live target missing:
follow bounded search+predeclaration in pilot-contracts.md, or report required
seam blocked without waiving it. No pilot fixture generator or tests added yet.

Observed carrier portability blocker: explicit wrapper control fails strict
product_to_record annotation guard before Store. New acceptance must prove old
string attributes unchanged, valid closed QuantityValue wrapper portable/Store
roundtrip, invalid-source wrapper preservation through real engine, and malformed transport
(nested/list value,extra keys,nonstring/overlong semantic) rejection. Finite scalar
value0/False/None and semantic strings net_volume/gross_volume/package_width MUST
roundtrip into source-supported unknown/review-only findings. Inner null/empty
states are preserved; finite0 is unit_missing,False invalid_type,wrong semantic
semantic_mismatch,never whole-job portable type failure. Numeric NaN/Infinity stay
globally rejected at transport; their string representations reach comparator. Candidate narrow
TypedDict check is in pilot-contracts.md; generic nested primitive support alone
is not portability evidence. No production repair attempted at APC07.

### Refreshed G1 carrier repair

Transport QuantityValue is a closed value/semantic object: value JSON-finite scalar
str|int|float|bool|None,semantic string<=32; transport never imposes the four-domain
semantic enum. Comparison alone validates approved semantic meaning and units.
Required real captured→portable→Store→engine cases: wrapped0→unit_missing with
input state value;wrappedFalse→invalid_type/value;wrappedNone→null/null;
wrappedempty→empty/empty;gross/net/packaging semantic→semantic_mismatch/value.
All are unknown/review-only, source input retained, no proposed correction and no
whole-job rejection. Bool branch precedes finite numeric branch. Missing attribute
state remains distinct. Existing legacy string attribute admission unchanged.
Nested/list values,unknown wrapper keys,nonstring/overlong semantic and numeric
nonfinite remain malformed transport tests. Separate direct-comparator overlong
and nonfinite controls exercise defensive reasons without claiming portable entry.

## APC09 executable acceptance and raw-state authority refinement

Tests added before business code: test_profile_quantities.py,
test_profile_coverage_integration.py,test_profile_coverage_cli.py,small overlay
addition to inventory tests; shared synthetic factories profile_coverage_helpers.py.
Exact callable/ownership declarations in skeleton.md. No48-case generator yet.

Distinct support risk: selected source None/empty is UNKNOWN, so _supported None
must not erase raw empty→null or fabricate missing. Quantity comparison now has
optional raw_before/raw_after metadata inputs, still compares ONLY supported
before/after. Direct cases prove raw250L with supportedNone remains unknown and
normalized_afterNone; source-path cases prove projected None/empty/whitespace
states and unavailable diagnostics through real parser/portable/Store/engine.
Actual missing path alone uses missing sentinel. This does not upgrade expired,
LLM or truncated raw candidates to checked facts.

Report budget tests serialize actual multibyte envelopes at1MiB−1/at/+1 including
newline; separate injected resource-admission failure exercises existing root and
module single error envelopes (allowed), forbidding success payload. Report
fixture outcomes are committed legacy-shaped unavailable facts, not fake matcher
outputs. Opt-in SQL page test forbids _findings to catch whole-job materialization.
Existing valid create guard remains baseline; labelled corrupt persisted goal
reaches real missing-rule dereference and must fail safely after repair.

## Independent review refinements before corrective implementation

Long precision coefficient fixture ending890 expected a noncanonical fractional
trailingzero. Root independently approved ending891 so exact60-digit/precision6
assertion remains strong; original failure retained. Matcher priority clarification
approved: existing capacity conflict means identity_unresolved,not rewritten to
variant_specification; test must require conflict+different+review-only.

New wrapper ordering risk: same transport-valid QuantityValue with reversed dict
insertion order must produce identical matcher attributes; actual differing raw
quantities must still veto. Canonicalize only closed finite wrapper maps, preserve
old string and malformed-map behavior. Design/execute intended reorder red first.
Captured baseline metadata state observed without retained evidence_ids must be
not_recorded,never checked. Current overlay must include actual canonical profile
record digest; default baseline bytes unchanged.

Additional narrow ordering/error boundary cases before repair: Variant.attributes
contains the same admitted carrier,so variant_options must ignore wrapper key
insertion order while preserving old string normalization. Current overlay with
missing refrigerator profile must reject InventoryError(invalid_selection),
not leak runtime MaintenanceError; baseline inventory remains independent.


### APC14 additional source-boundary checks (designed before execution)

Beyond the fixed48cases, five bounded checks target distinct interactions:
(1) equivalent duplicate declarations must preserve BOTH label/value evidence
pairs; risk is incomplete provenance despite correct values. (2) competing raw
attribute vs projected capacity and top-level vs property Model must reject the
field rather than pick a winner; risk is source conflict hidden by projection.
(3) a native Shopify object carrying SchemaOrg-looking properties must serialize
identically with capability on/off; risk is expanding the five unaudited lanes.
(4) subprocesses with hash seeds1and26 must yield byte-identical portable records;
risk is set iteration affecting support/attribute ordering across cache/replay.
(5) controlled temporary ml exponent fault must break the exact500ml=0.5L
assertion, then restore policy; risk is an insensitive conversion assertion.
No persistent mutation or production file edit; bound each subprocess10s,one
worker,<=64KiB output. These checks are prepared,not yet executed/reviewed.


Completed replay amendment (root approved): a completed refrigerator job reopened
with changed selected normalization must reject actual engine.resume with
profile_mismatch before source work and preserve job,findings and snapshot.
Existing cancelled/failed invalid_state precedence remains. Unrelated registry
addition must still allow exact read-only completed replay. This closes the
completed Store.begin early-return bypass; no recheck API is introduced.


Full-gate readiness synchronization repair (existing case only): repeated process
cancellation fixture currently polls300x5ms,an independent1.5s window inside the
unchanged3s OperationContext. macOS spawned module imports can exceed that window
before controlled resolver readiness. Replace only readiness polling bound with
context.deadline minus existing0.3s cleanup reserve and stop if task.done. Retain
existing5ms cooperative poll,3iterations,3s operation,0.3s cleanup and all barrier,
CancelledError,late-reply and zero-process assertions. Expected: fixture reaches
real child readiness within existing budget or fails with bounded diagnostic;no
production timeout or safety threshold extension. Run this isolatedcaseonce.
