# Research and decisions

Author: task-breaker/research delegate, 2026-10-25. Read-only code inspection and saved evidence; no new executable tests, downloads, model calls or live requests. This document records planning decisions, not completed feature verification.

## Existing evidence and bounded questions

Sources inspected: `docs/development-workflow.md`, constitution, local plan/tasks templates; `maintenance/profiles.py`, `maintenance/store.py`, `maintenance/engine.py`, `categories/maintenance.py`, selected attribute trace locations in `_normalize.py`; `specs/007-open-taxonomy-evaluation/{research,verification,status}.md`. Paths above are relative to repository root. Source inspection date: 2026-10-25; prior evaluation date: 2026-10-17. No present-day external-source claims require a new download.

Reuse `artifacts/open-taxonomy-evaluation/sources.json`, `selected-reference.json`, `compatibility-results.json` and saved `el_electronics.yml`, `aa_apparel_accessories.yml`, `hg_home_garden.yml`, `attributes.yml`, `LICENSE`. The prior review records Shopify 2026-08 commit `2e9aa2e9b882383952c63d212add13eb80f46cf9`, five retained source files totaling 6,488,755 bytes and 12 passing bounded checks. These are historical results, not new-profile verification. Inventory author must verify recorded hashes before use; stop on mismatch instead of refreshing the corpus silently.

| Question | Observed evidence | Decision / remaining work |
| --- | --- | --- |
| Does broad category mapping imply detailed coverage? | Three built-ins; hardware RAM/storage/model are text identity rules, footwear has specific text rules; generic has common fields. Prior probe had only three target leaves. | Keep policy coverage independent of mapping and source attributes. Remaining profile count unknown until reviewed semantic inventory. |
| Can current engine normalize refrigerator units? | FieldRule and Store validator support only text/decimal/mass; mass normalizes g/kg. | Add new finite volume/length rules with exact Decimal arithmetic; retain all old rule definitions and behavior. Freeze names and serialization at G2. |
| Will new rules persist safely? | Store serializes definitions, rejects name collisions, requires versioned names ending `-v1`, compares stored definitions to registry on resume. | Keep refrigerator-v1 within current version naming; changing capabilities requires explicit versioned policy semantics, not changing old definitions. Source review confirms _validated stores only selected definitions and validate_profiles compares each persisted entry, not registry equality. Adding an unrelated profile must preserve old-job replay; changed selected definitions must still fail. Save a prior-registry fixture to verify this before shipping. No blanket mismatch bypass. |
| Does a binding select a profile? | category_review_reasons requires selected_profile and checks exact bindings; engine obtains selection from goal.profiles. | Preserve explicit selection; no resolver or implicit generic/ancestor fallback. |
| Do quantities reach real evidence paths? | `_normalize.py` traces attributes, with platform-specific seams and Schema.org additionalProperty handling. The saved probe did not prove refrigerator field extraction. | Audit one refrigerator capture-shaped fixture through actual capture/normalize/support/persistence first. Add only demonstrated extraction gaps; retain source pointers and semantic context. |
| Where to expose coverage? | Engine loops requested goal fields and applies stored field rules; Store.report pages findings with default 100 and limit 1000. | Add small diagnostics scoped to requested products/fields and report page; store full inventory separately. Inspect public operations and CLI adapters/schema before committing exact keys. The maintenance module CLI currently prints JSON without an output cap; the 1 MiB portable/category CLI limit is not an existing maintenance guarantee. Add a 1 MiB serialized ceiling for diagnostics-enabled report output, preserving legacy output when diagnostics are unused and existing report/evidence budgets; report-budget failure cannot publish partial success. |

## Alternatives and contracts

Do not create one profile per taxonomy leaf or platform: grouping requires identical reviewed comparison/identity semantics, not shared names alone. Do not generate operational rules from taxonomy attribute lists: numeric RAM is absent in the saved laptop leaf, and the refrigerator umbrella attribute is irrelevant. Keep unrelated inherited attributes unreviewed. Proposed future packs (apparel/cosmetics/furniture/electronics) are candidate work, with no promised counts.

Use existing CategoryProfile/FieldRule, comparison, category companion, Store, engine, matcher, report operations and CLI translation. Avoid a new analysis engine or generic policy framework. Inventory is an offline artifact/report pipeline; runtime registry retains its existing 1000-target cap. A job receives only an explicit selected subset.

The pilot scope is total capacity, product width/height/depth and exact model plus common fields. No tolerance, net/gross equivalence, packaging dimensions, categorical unit guesses or GB/GiB conversions. Structured source semantics must demonstrate the exact approved field meaning; an ambiguous label remains unknown. A quantity parser cannot recover missing semantic authority from text. Unit parsing failures retain raw state and a deterministic reason without changing old-profile result shapes when unused.

Profile definition snapshots must capture unit policy meaning. Prefer explicit canonical unit/normalization identifiers in persisted rules over an undocumented global conversion table; G2 must establish how a later conversion-policy change triggers profile_mismatch. Category-policy mismatch stays separate. Original job snapshots remain immutable. Legacy serialized profiles, custom profiles/schema, collisions, portable category roundtrips, resume and recheck require red/green compatibility evidence. New additive report fields must not reinterpret legacy coverage.

Unsupported requested paths need a safe result even with strong identifiers and observed source values: inspect `engine._compare` before assuming absent rule handling is sufficient. Plan a distinct case where the selected profile lacks the requested field; it must remain unknown/review-only, never raise from reading a missing rule or propose a correction. Freeze unknown reason codes and checked-field semantics at G2. Checked means rule execution with sufficient supported inputs; attempted-but-invalid, missing, unsupported and not requested remain separate.

## Failure, recovery and resource limits

Source hash mismatch blocks inventory for that source; record it and continue independent reviewed sources, without claiming the original denominator. Semantic group uncertainty is review-pending, not an invented profile count. Incomplete extraction blocks only the unsupported lane, with explicitly narrower supported coverage. A required live seam that cannot be observed remains blocked even if synthetic checks pass. Stored policy mismatch fails closed; persistence failure retains prior committed report, retry is idempotent under unchanged snapshots.

Reuse test-design limits: seed 26; smoke first; 48 sequential mechanism/stress cases, 120 seconds including cleanup, per-case 10 seconds, one worker, 512 MiB driver memory ceiling, aggregate inputs 16 MiB, logs 256 KiB. Declare manifest before execution. Future live requests: at most three URLs/six total requests including redirects, 15 seconds/request, 90 seconds total, no automatic retries. Full final repository driver retains 240-second family/480-second overall ceilings. No model inference needed. One diagnosed repair per blocker, then record limitation.

Actual incremental uncached-input/output counters are unavailable to this assignment. Do not infer quota usage from file sizes or promise a percentage. Keep planning bounded and resume from saved artifacts.

### Binding semantic context and backward compatibility decision

A generic raw `capacity`/`width` key alone does not establish total-volume/product-dimension meaning. The pilot requires source evidence that explicitly identifies total volume or product dimension, or an adapter-specific reviewed contract that gives that exact semantic meaning. Missing context, gross/net ambiguity or package/product ambiguity remains unknown even if the number parses. Preserve the evidence pointer and approved semantic identifier through the support path; do not silently repurpose global attribute keys. G2 freezes the concrete carrier (existing support metadata if sufficient, otherwise an additive typed companion), exact identifiers and serialization; the evidence requirement itself is decided here.

Retain existing *-v1 profile naming validation in this pilot; no existing definition is rewritten. New volume/length normalization identifiers carry immutable version semantics (e.g. volume_l_v1/length_m_v1, exact spellings frozen at G2) in the persisted FieldRule record, so a policy semantic change must create a different identifier/profile definition and trigger existing mismatch behavior for affected jobs. Legacy custom rules continue to validate exactly as before. New identifiers are additive allowlist entries in both Store and CLI schema. No global conversion change may alter the meaning of an existing normalization identifier. A subsequent refrigerator-v2 naming extension is separate work unless needed to resolve a discovered blocker before implementation.

G1 admission clarification: Store._validated currently rejects fields absent from an explicitly selected profile. Preserve that invalid_argument contract. Test the defensive absent-rule engine guard using a labelled persisted legacy/corrupt-state fixture reaching the real comparison path; do not relax goal admission to make the fixture executable.

## APC07 bounded extraction audit and pilot contract candidate — 2026-10-25

Fresh pilot G1 pending. No production implementation or stubs. Source inspection
was bounded to six extractors, _schema_org.py, _normalize.py/_normalization.py,
_capture/_portable, maintenance engine/store, category review and both CLI report
adapters. Exact candidate contracts live in pilot-contracts.md; skeleton.md links
that interface candidate. Inventory acceptance does not approve pilot semantics.

Probe expected behavior and limits were saved first in evidence/pilot-audit-plan.md.
One generic HTML smoke ran and saved pilot-audit-smoke.json before native expansion:
actual SchemaOrgExtractor.extract_from_html retained total-capacity and model raw
values, but normalize produced attributes{}; quantity/model support unsupported,
common title observed. Real portable roundtrip, temporary Store checkpoint,
close/reopen and engine._supported exercised; no hand-built Product or fakeStore.

Then five actual native extractors processed one source-shaped synthetic product
each; ONLY httpx external transport controlled. Result6lanes/6controlledrequests,
0.477s, zero realnetwork/model calls. Evidence/pilot-audit-six-lanes.json and
pilot_extraction_audit.py retain exact shapes/reproduction. URL.synthetic-audit
invalid domain and receipt labels explicitly identify synthetic provenance;
real captured merchant facts/live availability are not claimed.

| Lane | Source capture and relevant fields | Actual current result / disposition |
| --- | --- | --- |
| Generic SchemaOrg | _schema_org.extract_from_html captures additionalProperty/name,value plus model; _normalize_schema_org only uses additionalProperty for identifiers | Observed title; all5 selected attrs unsupported despite retained source; one demonstrated normalization seam |
| Shopify | ShopifyExtractor.extract captures public products.json with title/variants; no requested metafield query | Observed title; all5 attrs unsupported; unavailable lane, no new native request |
| Woo | WooCommerceExtractor.extract captures prices and source attributes list | Attributes list not normalized into approved semantic dictionary; all5 unsupported; no guessed term/unit projection |
| Magento | MagentoGraphQLExtractor.extract captures sku/name and controlled custom_attributes sample | Native normalizer uses selected custom attributes for identifiers, not approved refrigerator semantics; all5 unsupported |
| Shopware | ShopwareExtractor.extract captures width/height/length/customFields plus context | Raw dimensions retained but units/product conventions not approved at this seam; all5 unsupported; native values not guessed |
| BigCommerce | BigCommerceExtractor.extract captures fixed published query product fields | Query has no quantity/model field; all5 unsupported; no pretend custom fields |

All6 lane paths include real normalize→product_to/from_record→Store checkpoint/
reopen→Engine._supported; title observed and selected quantities/model unsupported.
Native response samples may include optional fields not guaranteed by current
queries; they demonstrate normalization unavailability, not live schema field
availability. No production extraction change outside generic opt-in justified.

Code findings resolved in candidate design: Product/Variant attributes annotation
is dict[str,str], so wrapper needs additive TypedDict union without constructor
changes. The seventh control proves strict portable validation currently rejects
nested wrapper despite primitive codec support; candidate adds narrow closed-wrapper
validation and coherent JSON schema, with old-string validation unchanged. record_inputs can
bind both semantic label and value to a wrapper; record_nested skips an already
recorded child, preventing accidental rewrite. _supported resolves retained
observations/evidence and rechecks freshness. Existing _compare can dereference
rule_value['role'] after a missing rule; guard must precede that path. Existing
_category_conflict ignores new profile names; fridge wrong-Boots case needs explicit
veto plus mandatory persisted exact category policy/binding. Old3 behavior stays.

Store selected-definition fingerprints already include kind/normalization/role;
versioned axis-specific IDs freeze semantic meaning without new serialization
keys. Preserve old3 definitions and custom rule admission; add only new allowed
combinations. No new transactional diagnostics table is needed: report derives
coverage from immutable goal/selected-definition snapshots and committed findings,
plus new quantity-only input state/reason keys. This removes migration/checkpoint
ownership surface. Report currently materializes all _findings before slicing;
opt-in page diagnostics must page SQL before advisory overlay. Existing root CLI
already has universal1MiB cap after PR97; module CLI cap only --coverage is new.

Original baseline inventory must remain reproducible; APC17 additionally saves a
current-policy overlay with selected9-field implementation rather than whole-family
coverage. No retrospective conversion of pending rows into reviewed totals.

Concrete live URL is not yet known from retained discovery. Candidate contract
bounds later search to2queries/6result metadata candidates, then exact URL and
expected sourcefields must be declared BEFORE the original <=6 product requests.
No guessed URL/capture or waived live gate. This assignment performs no searches,
network,models or downloads. Counter telemetry remains unavailable.

Carrier control after6-lane audit (seventh product, predeclared separately)
FAILED at real product_to_record: ValueError Invalid type at
product/attributes/capacity. Strict _portable._check_type enforces dict[str,str];
primitive nested support alone does not establish portable compatibility. Receipt
evidence/pilot-carrier-control.json records blocked stage and proposed typed
repair. No production repair attempted. Additive annotation, narrow closed
TypedDict validation and portable-product JSON schema need independent review
and failing acceptance tests before implementation. No constructor field added.

Compatibility refinement: generic enrichment must be explicitly opted-in, default
False, only through trusted persisted refrigerator-profile selection in maintenance.
Propagate capability via existing per-run ToolRuntime/GuardedSources/domain path;
selected definitions/capability tag version1 separate cache meaning. Default old
hardware model capture cannot silently improve. Root CLI already caps1MiB after
PR97; moduleCLI --coverage must preflight its actual legacy-style envelope.

Refreshed G1 carrier repair: transport wrapper value admits JSON-finite scalar
str/int/float/bool/None and bounded semantic string; allowed domain meanings
remain comparator authority. This preserves real unknown source facts for review
without whole-job type rejection. Typed codec remains closed and rejects nested/
list/extra-key/nonfinite numeric payloads. Exact priority/null/empty semantics and
real engine roundtrip cases are updated in pilot-contracts.md/test-design.md.
No production/stub changes or extra probes for this repair.
