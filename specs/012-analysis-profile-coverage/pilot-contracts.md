# Refrigerator pilot contract — approved APC07–10

Author /root/coverage_author,2026-10-25. Pilot G1/G2/G3 and later bounded
implementation amendments are recorded in reviews.md. Implementation/offline
verification completed; required live capture remains blocked as recorded in
evidence/pilot-live-discovery.json. This contract does not claim live coverage.

## Finite policy and physical quantity meaning

`refrigerator-v1` contains exactly9 fields: existing common description/title/
price/currency definitions unchanged, plus attributes/capacity,width,height,depth,
model. No weight inheritance. Model uses existing exact text identity_variant.
Four quantities use identity_variant and the following immutable records:

| Field | kind | normalization | required wrapper semantic | canonical unit |
| --- | --- | --- | --- | --- |
| attributes/capacity | volume | volume_total_l_v1 | total_volume | L |
| attributes/width | length | length_width_m_v1 | product_width | m |
| attributes/height | length | length_height_m_v1 | product_height | m |
| attributes/depth | length | length_depth_m_v1 | product_depth | m |

Distinct axis policy IDs allow compare_field itself to reject width as height;
axis safety must not depend only on caller field names. FieldRule remains exactly
kind/role/normalization. Store and maintenance-profiles JSON schema add exactly
these allowed kind/normalization combinations. Existing text/exact,
decimal/decimal,mass/mass_kg,3 built-in definitions and custom-profile record
formats/results stay unchanged. Existing *-v1 validation/name collisions remain.
New quantities may be used by explicit trusted custom profiles under these same
semantics; no arbitrary normalization or automatic category selection.

Carrier: `{"value":"250 L","semantic":"total_volume"}` under attributes/capacity;
closed two-key mapping. `value` is a JSON-finite scalar
(str|int|float|bool|None), never mapping/list; `semantic` is a bounded string
(max32 characters), not an enum at the transport layer. Comparator validates the
four exact approved meanings above. This distinction lets captured unknown/invalid
quantities remain portable facts and produce review-only diagnostics instead of
rejecting the whole job. Negative/finite numeric/bool/null values and gross/net/
packaging semantic strings are transport-valid, comparison-invalid or unavailable.
Global JSON-finite guards still reject numeric NaN/Infinity; their string forms
reach comparator. Extra keys/nested values/nonstring semantic remain malformed
transport and reject before persistence.
Each normalized wrapper and its label/value source selections must have real
observed support. Raw attributes/capacity='250 L' or width='60 cm' alone lacks
semantic authority. Existing raw dictionary admission does not grant meaning.
Product and Variant attributes type annotations add a QuantityValue TypedDict
union with existing str; constructor field order/defaults unchanged. Existing evidence primitive codecs support nested mappings, but the actual seventh
carrier control FAILED product_to_record at product/attributes/capacity because
strict portable type validation enforces the old string annotation. Therefore
add narrow QuantityValue TypedDict handling to the existing _portable._check_type:
exact required value/semantic keys, JSON-finite scalar value and bounded semantic
string, no unknown keys; no change to
legacy primitive validation. Product/Variant union and portable-product JSON schema
add exactly this closed shape. Source evidence/identity integrity validation stays
unchanged. Add explicit old-string, valid-wrapper and malformed-transport rejection plus invalid-value wrapper roundtrip
acceptance before implementing. This is a typed serialization seam requiring
G1/G2 review, not demonstrated existing wrapper portability. No new companion or
policy engine.
Other legacy dict values retain existing runtime behavior; annotation widening
must not silently tighten unrelated attribute admission.

Supported unit spellings are exact ml,L and mm,cm,m. Outer/number-unit ASCII
whitespace may be stripped; grammar unsigned digits with optional fractional
part, no exponent/grouping/comma/range. Zero valid. String value at most128 characters; semantic at most32. Those are carrier
resource bounds, not a scalar validity test. A128-character string reaches
comparator;129 characters is an explicit direct-parser input_too_long case and
malformed transport at portable admission (both stages are tested). Transform decimal coefficient/exponent by exact
powers of10 (ml:-3,mm:-3,cm:-2), using Decimal tuple/exponent construction or
integer digit formatting. Never apply default-context division/normalize to long
coefficients; long exact inputs must remain exact under a deliberately tiny
Decimal precision. Canonical finite decimal output has no exponent or insignificant
fractional zeros. Never use tolerance, net/gross/freezer equivalence or packaging
measurement conversions. Policy identifiers cannot change their meaning later.

Quantity compare results retain existing comparison/normalized_before/
normalized_after/trace keys and add `input_states` and `input_reasons` mappings
with before/after entries. Only new quantity kinds add these keys. State enum:
missing,null,empty,value; absent path uses a private missing sentinel passed only
to new quantity comparison, never serialized. Null remains explicit None;
whitespace string is empty. For a transport-valid wrapper, input_states describe
its inner value: None→null, empty/ASCII-whitespace string→empty, every other
finite scalar→value (including0 andFalse). An entirely absent attribute remains
missing; unwrapped explicit None remains null. Validate presence/state before
quantity syntax. For nonempty values compare semantic first (missing marker→
semantic_missing, unapproved meaning→semantic_mismatch), then bool→invalid_type,
finite numeric→unit_missing, then string syntax/unit checks. BoolFalse must never
reach numeric handling; numeric0 is value/unit_missing rather than missing/null.
Reasons, in deterministic validation order:
missing,null,empty,input_too_long,invalid_type,semantic_missing,semantic_mismatch,
non_finite,negative,range,unit_missing,unit_incompatible,unit_unsupported,
invalid_syntax; valid input reason null. Direct comparison malformed wrappers invalid_type;
transport rejects those before jobs. Bare nonempty strings semantic_missing; incompatible known physical units get
unit_incompatible, unrecognized/localized units unit_unsupported. Bool is
invalid_type, never0. Wrapped NaN/Infinity strings get non_finite. Direct compare nonfinite numeric
control also gives non_finite with safe typed snapshot, but nonfinite numeric
transport cannot enter portable jobs. Finite numeric value gives unit_missing. Missing semantic key gets
semantic_missing, extra keys invalid_type. Safe raw snapshots preserve invalid
nonfinite values as typed repr records, never NaN JSON literals. Trace includes
normalization ID, both original wrapper snapshots, canonical unit and exact
normalized values; source pointers remain in existing evidence/support payloads.
Any invalid/absent side gives unknown, never equality/correction.

## One demonstrated extraction seam

Actual APC07 smoke and five native adapter audit are saved in evidence/. Generic
SchemaOrg parser retains explicit additionalProperty+model but normalization drops
all5 selected attributes. This is the only proposed extraction change. Native5
lanes remain explicitly unavailable for these selected fields, not implemented
via guessed dimensions/metafields/custom attributes or changed native queries.
Source transport controlled only; these are synthetic mechanism observations,
not successful live refrigerator captures.

Add an explicit keyword `include_refrigerator_attributes=False` to normalize
and category normalization wrapper; defaults/feed/extract APIs retain previous
outputs. Only trusted MaintenanceEngine jobs whose persisted selected definitions
include refrigerator-v1 enable the capability through ToolRuntime→GuardedSources
→domain parse→normalize. Private worker payload boolean is parent-owned, never a
public tool/user-source directive. Recreate the same flag for resume/recheck;
Engine already creates/closes a runtime per run. Selected definitions are already
part of source cache identity; add an immutable capability version1 tag only for
enabled jobs so old-cache keys remain unchanged. Default-false tests must prove
old hardware model/attributes are byte-for-byte unchanged on the same raw source.
No global enrichment, automatic profile selection or new Product constructor field.

Within the opted-in generic SchemaOrg path add only these projections:

- Approved capacity labels: Total capacity,Total volume,Total refrigerator capacity.
- Approved dimensions: Product width,Product height,Product depth.
- Model: top-level model string or additionalProperty label Model.

Match labels by strip/collapse ASCII whitespace+casefold, no substring/localized
matching. A declaration may use name or propertyID; if both are nonblank, both
must resolve to the same approved field. Unsupported/contradictory label cannot
be hidden by the other. Values must already include approved units; do not infer
units from vague labels, unitCode or native dimension units. Generic Capacity,
Width,Net capacity,Gross capacity,Freezer capacity,Package width remain unapproved.
Native SchemaOrg quantitative objects/top-level width/height/depth are out of
scope in this first seam. Real source shape outside the alias contract remains
unavailable rather than guessed.

Use Normalizer.record_inputs with exact label(s) and value pointers to construct
wrappers, preserving conversion history. Container outcome plus explicit child
outcomes must not be overwritten by record_nested; unrelated raw attributes
remain unchanged. When raw attributes and projected field coexist, identical
explicit wrapper inputs may retain all contributing pointers; conflicting or
ambiguous values fail closed with rejected ConversionOutcome and captured raw
sources retained. Duplicated equivalent declarations retain every input pointer;
conflicting declarations must never pick last/first silently. Model conflicts
between top-level/additionalProperty likewise unavailable. Evidence support,
LLM/truncation/expiry protections continue through existing capture/resolve/
portable/Store paths. No taxonomy value becomes a product fact.

## Explicit binding, identity and snapshots

Trusted per-product goal.profiles selection remains required. Refrigerator also
requires enabled persisted category policy, unambiguous exact mapping to
hg-11-7-41 in shopify:product-taxonomy@2026-08, and exact binding to refrigerator-v1.
No config gives category_policy_missing and needs_review, even if quantity agrees.
Missing binding/profile/mapping, partial/multiple competing targets and conflicts
retain existing category_* / profile_binding_missing reasons. An exact binding
never selects policy. Unselected refrigerator-looking product stays review-only.

Refrigerator-specific conflict veto checks known contradictory baseline/supplier
labels (hardware/electronics/footwear/boots/shoes) even though current
_category_conflict ignores nonold profiles. An anchored Boots product cannot
borrow refrigerator coverage. Unknown labels cannot grant validity; exact scoped
mapping/binding remains required. Old3 profile legacy no-config behavior unchanged.
GTIN/MPN/variant conflict and unsupported identity stay authoritative. Capacity, dimension or model difference remains needs_review,never a proposed
correction. Existing matcher conflicts keep identity_unresolved priority; only an
otherwise exact matcher lets the domain rule give variant_specification. Agreeing quantities cannot override matcher/category veto.
Absent rule guard precedes role dereference: new goals still reject invalid_argument;
labelled legacy/corrupt-state engine fixture gives unsupported_field/review-only.

Persist new rule definitions through existing selected-definition snapshot.
Store.validate_profiles must compare selected stored definitions on resume AND
recheck/retry before any mutation; adding unrelated registry entries cannot
invalidate old jobs. A new normalization identifier/definition for a selected
policy triggers profile_mismatch, never updates old snapshot. Existing category
policy mismatch behavior remains separate. No new coverage table/checkpoint
budget/schema migration: immutable selected profiles+goal+committed findings
already retain the required facts. Quantity-only input state/reasons are committed
inside the existing finding comparison payload and existing transaction.

## Opt-in page diagnostics and output budget

Python/public operation: `MaintenanceStore.report(job_id,offset=0,limit=100,
include_profile_coverage=False)`; public CLI/module CLI add `report --coverage`.
Existing report fields/defaults unchanged. Limits1..1000,offset>=0;0 and1001 reject.
SQL LIMIT/OFFSET ordered by existing finding ordinal/id must page findings before
materialization; current _findings()[slice] is an audited boundedness gap. Reuse
existing advisory overlay for just selected finding IDs. Do not load all findings
or return whole taxonomy per request.

With opt-in add root `profile_coverage` exactly:

```
{schema_version:1,scope:'finding_page',offset:int,limit:int,finding_count:int,
 products:[{product_key,selected_profile,profile_definition_digest,
 configured_fields:[],requested_fields:[],page_fields:[],checked_fields:[],
 unavailable_fields:[],invalid_fields:[],unsupported_fields:[],unrequested_fields:[],
 not_recorded_fields:[],field_diagnostics:[{field,outcome,reason,input_states,
 input_reasons,blockers,baseline_basis}]}]}
```

Sort products by product_key,field lists lexically; page findings preserve existing
order. Configured fields come only from stored selected definition; requested
from persisted goal; page_fields only fields represented in this finding page.
Unrequested=configured minus goal requested. Classify only page_fields. Checked
requires retained rule, nonunknown comparison and adequate baseline
observed-or-explicitly-supplied/supplier observed support. Rule execution can be
checked while identity/category blockers still forbid correction; include those
blockers. Unsupported=absent rule; unavailable=missing/null/empty/unsupported/
expired/conflicting support; invalid=sufficient source support but invalid
quantity/value/semantic parse. Priority unsupported→unavailable→invalid→checked.
Unknown legacy evidence not sufficient to classify is not_recorded; never invent
missing-vs-null distinction or actual execution. Quantity input details are
persisted; legacy absent details use unknown marker only. `baseline_basis` is
captured/supplied from goal. No job-wide checked total inferred from a page.
No findings means products empty and finding_count0, not full checked coverage.

Public root CLI already caps all envelopes1MiB after PR97; reuse that cap. Module
CLI adds1MiB cap only for --coverage (legacy output unchanged). Both diagnostics
paths pre-serialize their actual envelope in UTF-8 including newline, then emit
once; exact <=1048576 succeeds,plus1 fails before any success-payload byte (the existing single error envelope is still emitted). API bounds the
report payload and adapters independently check their larger actual envelope.
Failure is resource_limit at Python boundary and existing E_OPERATION/exit1 at
root CLI; module CLI existing error envelope/exit2. Existing report interfaces
have no file destination, so no new file export is added here. If shared artifact
helpers are exercised, preflight precedes atomic_json/replace; shell redirection
itself is outside application control. Test stdout atomicity explicitly and
retain existing file helper atomicity regressions; do not invent a report-file
replacement API to satisfy a hypothetical path.

## Fresh inventory overlay and retained baseline

Keep original saved inventory-smoke/coverage-matrix bytes reproducible as dated
baseline. Extend inventory with an explicit current-policy overlay option, default
baseline unchanged, producing schema_version2 with baseline digest and selected
profile definition digest. Only exact reviewed refrigerator reference receives
profile refrigerator-v1 and policy_coverage implemented_selected_fields; selected
field list exactly9 and whole_family_coverage incomplete. Its semantic review
remains pending until independently accepted; bindings/extraction/job checked/live
states remain separately unavailable/not_audited or explicitly cited evidence.
No overlay may change baseline pending counts into implemented family totals.
APC17 saves current overlay+human summary; public helper must not silently keep
claiming refrigerator missing after requesting current-policy view. Exact overlay
interface freezes at pilot G2; this is the G1 observable behavior decision.

## Bounded verification and live target prerequisite

Manifest evidence/pilot-case-manifest.json names48 deterministic risks/outcomes
before fixture code:12 valid quantities/fields,12 invalid/state semantics,6 real
adapter paths,8 binding/identity/partial interactions,4 replay/fault and6 registry/
order boundaries. Seed26; one worker,120s total/percase10s,512MiB ceiling,
25products/job,16requested fields,64KiB/payload,2MiB/registry,16MiB total,
256KiB logs. Save one synthetic complete refrigerator smoke first. Preserve real
matcher/engine/Store; control only external transport/clocks/injected faults.
One diagnosed repair then affected rerun or limitation; full configured driver
required after focused/mechanism success. Distinct report pagination101findings,
1MiB−1/at/+1 UTF8,conversion assertion-sensitivity and old3/customschema admission
checks run as separately bounded acceptance suites, not silently stuffed into48.

No concrete public refrigerator URL was found in retained discovery by root;
APC16 is unready, not waived. Permitted discovery after offline success: at most2
web searches and6 result URLs inspected as search metadata only, targeting a
public refrigerator merchant/manufacturer page likely to expose approved labels.
Do not guess product URLs. Record exact discovered URL/domain/search origin and
expected label/value pointers before HTTP. If no suitable URL, required live seam
remains blocked. If found, product HTTP budget remains <=3URLs/6requests including
redirects,15s/request,90s total,zero automatic retries,one worker; no authentication,
store writes or anti-bot circumvention. Start1capture/save before expansion,stop
on denial/unexpected behavior. Discovery requests/accounting are separately
reported; they are not fabricated source captures. No commercial mutation required.
