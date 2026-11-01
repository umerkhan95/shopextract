# Downstream documentary interfaces — G2 proposal

D1/D2 `validate/_destination.py:assess_google(product,*,context=None)->dict`
returns projection,issues[{rule_id,field,severity,message}],subset_status
(blocked/needs_context/subset_pass),id_source,unassessed_checks andrulesversion.
Canonicalprojection uses explicit external_id elsecanonical_product_id(labelderived),
vendorbrandfallback,knownstockonly,exactfinitepositiveamount+supportedISOcurrency.
Known nonproductrawadmission and unsupportedcontractfields block requiredfields.
Bare legacydict explicitvalues are supplied/unverified (assessment flags),never
verifiedsourceclaims. Missingcontext yieldsneeds_context,not universalapproval.

Existing validate(products,marketplace='google_shopping',*,context=None) reuses
projection/rules,extends ValidationIssue rule_id and ValidationReport subset_status,
unassessed_checks/rulesversion with compatibilitydefaults. Othermarketplaces keep
legacybehavior. Existing QualityScorer remains presence-only;docstrings/reportlabels
saypresence,not eligibility. `to_feed(...,context=None)` returns retained/skipped/issues
while fileformat stays XML/TSV; bothwriters usecanonicalprojection,omit unknownstock,
no defaultUSD/identifier_exists=no. Google blockeditems skipped;needs_context items
retainedwithissues. CLIexport propagates counts/issues separatelyfrom operationok.

D3 existing normalized_attributes/classify_match/fuzzy_match/find_duplicates share
conservative titlecolor/function/quantity vetoes. Fuzzy/title outputs remaincandidate
APIs; no constructor/APIreplacement. Exact supportedidentity controls retained.
D4 analyze_products/count_categories dedupe perproductlabels;CatalogStats adds
unknown_stock default0; missing/null/unobserveddefault stock unknown.

D5 measuredoneproduct export-profile.txt demonstrates duplicate bundle serialization,
not proven25recordtimeoutcause. Request-scoped preparedbundle reused only within
oneatomicexport;no globalcache/trustbypass. Native caller stillvalidated beforewrite;
CLI's loaded portableproducts trusted only via explicit internal validatedrecordseam.
Testinstrumentation counts actual serializers (wrappercallsthrough),plus lossless
actual25diagnostic underoriginal30sceiling afterfocusedgreen. Preserve rollback.

G2 clarification: `_bundle.PreparedEvidenceSnapshot` is private frozen dataclass
holding immutable validated bundle JSONbytes and frozen rowidentity/projectionkeys.
Factory `prepare_evidence_snapshot(products)` validates actual producer Product/
variant/contracts once and snapshots current invocation; callers cannot supply
"validated=True". Private sidecar construction accepts only this factoryoutput;
public create_evidence_sidecar still validates throughfactory. CLI redundantpreflight
is removed only when writerfactory validates before stagedfileeffects. New export
creates new snapshot,never reuses by objectidentity; snapshots do not hold mutable
liveproducts. No globalcache. Malformedproducer/tamperedpointer fails before either
target or sidecar replacement. Existingtypedidentity/projectionverification retained.

Stats/assessment accept Product|dict:typedproducts retain contract at CLI boundary,
contract-aware requiredstock uses actual trustview; no asdict-default leakage.
Legacy explicitdict values remain supplied/unverified. CLI whitelist adds new
reportfields; report consumers receive typedmodels,not discarded dynamiccontracts.
