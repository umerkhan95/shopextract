# Inventory reusable components — finalized APC04

Author: /root/coverage_author, 2026-10-25. Independent inventory G2/G3 passed with digests in reviews.md. This
finalizes status metadata only; approved component behavior is unchanged. Pilot component lifecycle is recorded below.

| Existing component | Reuse and consumer | Boundary |
| --- | --- | --- |
| maintenance.profiles.profile / immutable FieldRule | Inventory serializes exact existing rule definitions for the two reference profiles | No change to existing profiles; presence does not mean checked coverage |
| categories.config.validate_options and runtime_record | Existing runtime admission; independent999/1000/1001 regression | Inventory is offline metadata; never auto-register4125 nodes or invent bindings |
| categories._codec.canonical / wire | Runtime contracts continue unchanged; profile rules may use dataclasses.asdict for primitive inventory projection | Avoid passing a large inventory through runtime category limits or typed companion constructors |
| taxonomies.shopify.build optional PyYAML setup | Reuse declared taxonomy-build extra and lazy safe_load dependency pattern | Different pinned three-branch files; do not invoke full-release preparation/download/publish |
| hashlib / json / pathlib | Five-file integrity and deterministic report assembly | Source pins are fixed reviewed constants; no mutation or inferred source refresh |
| saved007 sources.json + selected-reference.json | Provenance and cross-check reference semantics | Historical data, not present extraction/live evidence; fixture pins independently frozen in tests |

One narrow new owner, `maintenance.inventory`, combines verified metadata with
three explicit baseline policy assessments. It does not create an analysis
engine, profile resolver or family classifier. Inventory errors are local
ValueError subclasses with stable diagnostic codes, not API error envelopes.

Lifecycle: hash/size verification → safe parsing and duplicate/link validation →
explicit selection → immutable current-profile projection → sorted primitive
result. Failure produces no partial result and no files; coordinator saves the
smoke/full result only after success. Report-size cap is checked before return.
Parsed corpus is released after building one result; no global cache or mutable
registry state. Inputs can be reordered without changing output.

The runtime category codec/config validator continue to own the only trusted
bindings, policy digests and portable source-support contracts. A metadata locator
is not an Evidence pointer. Extraction stays `not_audited` until APC07 establishes
actual raw→normalization→support→Store paths. Later pilot/report work must reuse
Store/engine/matcher after its own fresh G1/G2/G3; this draft grants no approval.

## G2 portability repair

SOURCE_PINS is an immutable size/hash configuration map; build_inventory reads
this same authority. Fresh-checkout pytest substitutes only the map for a7-node
synthetic source-shaped fixture. It does not replace reading, hashing, parsing,
validation, profiling or ordering. Optional PyYAML remains supplied by existing
taxonomy-build setup. No new public pin-override parameter is added.

Actual retained raw corpus is not a pytest fixture or repository dependency.
The separate explicit retained_inventory_acceptance.py driver verifies pinned
upstream source identity and actual denominator without skips; its successful
run remains a required APC05/06 gate. Tiny synthetic and actual retained evidence
are separately labelled; production algorithm is shared, not duplicated.

## Pilot reusable components — finalized APC10

Inventory finalized above remains historical. Pilot candidate reuses FieldRule/
profile comparison; existing ConversionOutcome.record_inputs; capture support and
resolution; portable type/finite-tree guards; category companion/config/bindings;
selected-definition/category snapshots; matcher/engine; Store checkpoint and
committed findings; root response builder and module envelope. No new quantity
policy engine, persistence table, Product constructor field or source classifier.

QuantityValue is an explicit additive typed carrier consumed by normalized
attributes,portable transport and quantity comparison; source semantic authority
comes from retained label/value inputs, not TypedDict membership alone. Existing
strict type checker adds its narrow closed-shape branch; no generic arbitrary
nested attribute allowance. Invalid finite captured facts remain transportable,
while parser/comparison diagnostics reject their quantity meaning.

New shared module: maintenance.reporting.encode_coverage_response,
a stdlib-only actual-envelope UTF8/newline resource preflight used by Python
report boundary and both CLI adapters. It accepts an already constructed envelope,
never imports CLI or duplicates error-response semantics. SQL report paging reuses
existing finding/advisory tables and immutable snapshots; no new storage lifecycle.
Old output paths untouched unless --coverage/new profile capability is selected.

DefaultFalse source opt-in flows through existing engine/runtime/source/worker
owners; engine derives it from stored selected profile definitions at each run,
resume and recheck. Add capability version only to enabled cache scopes. No raw
source/public tool flag can grant policy selection. Raw candidate state helper
never supplies comparison authority; support expiry/LLM/truncation still vetoes.

Implementation ownership is frozen by skeleton.md. Independent pilot G2 and G3
passed with recorded digests in reviews.md; component metadata is finalized here.
APC11–13 implementation now awaits its independent implementation checkpoint;
this status does not preempt APC14 coverage review or verification gates.
