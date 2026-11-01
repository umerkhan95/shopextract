# Behavior/test design before breakdown

Scenario IDs and exact expected outcomes: spec.md. Distinct uncovered risk:
Field presence overstating factual/merchant eligibility, export aliases, false equivalence and biased stats. Actual validators/XML/matching/analyze-file paths, not static expected reports.

Fixture author uses tiny sanitized saved audit sources plus deterministic factories
seed0. Mock external HTTP/DNS/clocks/library boundaries only; actual algorithms,
normalizers,encoders,CLI/tool/persistence paths execute. Design all new edge cases
before tests/fixes; retain accepted native/freeProductGroup/empty-normalize controls.

Acceptance/stress cap64 concrete cases per child,one worker,120s subprocess,
1MiB ordinary input (child02 byte-boundary fixtures up to32MiB+1),256MiB target
retained test memory,stop first unexpected failure and one diagnosed repair.
Enumerate exact collected cases before red run;64 is maximum,not promised coverage.
Save one smoke before expansion. Distinct missing/null/empty/zero/conflict and
just-below/at/above limits from SCs are separate assertions; seed variation is not
new coverage. Independent reviewer checks fixture realism and real-path execution.

Live plan: local-file command behavior live N/A; actual source capture from preceding child reused, provenance labelled. Destination listing approval untested/not claimed; no feed upload.
Offline: focused acceptance/affected checks then configured scripts/run_tests.py
240s-family/480s-total (never increase). Prior timeout does not satisfy this gate;
record unrun families and unknown failure nodes honestly. Separate synthetic
mechanism,stress and actual live evidence; inconclusive live is never a pass.

G1 repair SC-D5: execute each15-row condition-table fixture using real validator
and feed projection; baselineB exact corefixture fixed in spec. Assert exact ruleID,
severity,subset_status and identifier_exists mapping,not only issue counts. Include
new/used/refurbished versusunknown,media brand exception,assigned/absent/unknown
identifiers,US ads versusPK free-listing variants and unsupported apparel branch.
Allrows cumulative; passing one row never overrides another error/needs_context.
Each unsupported branch must remain visibly unassessed,not generic eligibility.

G2 concrete additions BEFORE executablefixtures:15table rows+6coreinvalidcases
(negative/nonfinite/placeholder/noID/stockunknown/unsupportedcurrencycontract);
4feedcases(vendor+canonicalIDstable,unknownstockomission+flag,missingIDskip,CLIcounts);
7matchingcases(3incompatiblepairs acrossfuzzy+duplicates,oneexactGTINpositive);
3statscases(dedup,4-waystock,empty);1exportserializerinstrumentation requestscoped
(singleproduct once,exactsidecarreload). Total36 boundedtests,existingatomicfailure
controls reused. Unknownstock is coreerror blockedGoogle but lowlevel projection
still omitsavailability (assertprojection directly); operation success !=eligibility.
Title-only unresolvedsimilarity remains candidate; incompatible auditedcolor/function/
quantity cues veto candidatepair. Conditionalrules use explicitbaseline/tablecontext,
not country/category guessing. Profileoneproduct0.389s saved;no performanceSLAclaim.

Pre-review refinement:all15conditionrows execute realvalidate ANDto_feed(context) consumers in addition sharedassessment,assert same ruleIDs/subsetstatus andblockeditemretention parity. Onepresence-rich explicitpolicyrawtypewebsite negativecontrol blocksproduct_evidence. Total37cases (prior36initialred saved);no extra merchantrequests.

G2 repair design BEFORE tests:7newcases,total44. CapturedWoo validpriceUSD/image/
description/ID but absentstock normalizes scalarTrue compatibility;portableCLI
analyze-file mustunknown1/in0,validate mustmissing_availability blocked,feedCLI
mustretained0/skipped1+availabilityissue. This isolates unsupporteddefaultstock
without relying absentcurrency. FlatbaselineCLIvalidate withmissingcontext must
serialize needs_context,rulesversion,nonemptyunassessed_checks,issue ruleIDs.
Twoexports of SAMEProduct afterprice/titlemutation require secondsnapshot exact
newvalues+evidence,not staleidentitycache. InvalidproducerNaN andtamperedretained
pointer reject beforewrite,preserve BOTHpriorCSV/sidecarbytecontents. Realwriter/
codec/load/CLI,serializerinstrumentationcallsthrough. Existingatomicreplacement
control tests/test_cli_analysis.py::test_export_replace_rollback retained.

G3interaction BEFORE code:2nativefeed+companioncases,total46. Mixedvalidstockobserved/
unsupporteddefaultstock products emitexactvalidsubset;allunsupporteddefaultstock
emit0items. Real load_evidence_sidecar verifies digest/order and restores EXACT
retainedProduct/variant/contracts (empty[] forallskipped). No rowcountonly proxy.
Nativefixtures capturedbefore normalization,notrecaptured mutatedproducer.
G3fixturestrengthening: mixedorder=[blocked(id2),valid(id3),valid(id1)] expected
exact[valid3,valid1],notprefix/sortedsubset. Same2cases,retainedindices[1,2];catches
snapshot[:retained_count] andidentitysorting shortcuts.

Implementation compatibility refinement BEFORE tests:2cases,total48. TypedProduct
WITHOUTcontract cannot authenticate constructor-defaultstock;analysisunknown1 and
Googleavailabilityunsupported despite otherwisepopulatedfields. Legacyexplicitdict
values remain supplied/unverified. Explicitprice0 is validobservedmoney (no automatic
invalid_price),subsetbaseline otherwisepasses;fullGoogleapprovalstillunassessed.
This preserves auditcaveatfreeproducts,notlistingapproval. No newnetwork/source.

Affecteddiagnosis BEFORE repair:267pass12fail20.28s. Two genuine compatibility
regressions:existing Google title/description length checks must remain;negative
amount issue keeps explicitnonnegative diagnostic. Otherfailures are oldfixtures
missing newlyrequiredID/currency/description/knownstock or sourcecontract. Keep
existingpayload/duplicate-ID/priceformat/GTINwarning assertions; enrich ONLY those
fixtures with valid explicitcore or actual captured nativefeedfacts. CSV/JSON custom
trustfixtures remainunchanged. Existingstats missingstock expectedin1 updates to
in0/unknown1 under reviewedbehavior (strengthened out0/totalreconciliation).
Two additionalriskcases (total50) BEFORE code: invalidGTIN 'abc' withassignedcontext
blocked invalid_gtin;conditioncontextused withfeednew blockedcondition_conflict.
ExistingvalidGTIN/refurbished controls retained. Reusevalidatedchecksum helper.

Conditiondiagnosis BEFORE minimalrepair:affected280pass1fail19.65s;actualnative
Product.condition is unsupported compatibility'NEW'. Treat unsupportedcondition as
ABSENT for destinationprojection,not contradicting capturednew context. Canonicalize
observed conditioncase only;never emit unsupporteddefault. Oneusedcontextnative
control (total51) requires missing_condition,not fictitiouscondition_conflict.
Existingmixedsubsetfixture detects falseblocking andretains exactsourcecontracts.

Functionalreview refinement BEFORE repair:6newcases,total57. TypedGTIN changedto
anotherchecksumvalidvaluewithoutsource andtypedMPNaddedwithoutsource cannot satisfy
assignedidentity;omit claim and explicitunsupported_gtin/mpn error. Existing valid
nativecapturedGTINpositive controls retained. Variantcontext string'true' (notbool)
needs_context/unsupported_rule_branch,nevergroupingpass. Zero testamendment aligns
inheritedSC05: observed/supplied0 NOTinvalid_money but zero_price_needs_context
warning/needs_context;addnativecapturedzeroobserved control. Idealo SKU-onlydict
mustretainwithTSVSKU despiteGooglemissing_id;nativecapturedSKU-only(IDs explicitly
cleared) companion exactProduct/contracts+SKUrowID mustreload. Googlepolicyremains
external/canonicalonly;SKU-onlynotGooglemanufacturerID. No limits/networkchanges.

Sourceprojectiondiagnosis BEFORE repair:111pass1fail1.27s. trust_view explicitly
separates authoritative resolved'value' from mutable scalar'legacy_value'; observed
state alone cannot authenticate later scalar mutation. Require exactcurrentvalue
agreement at scalarprojection boundary (not mutate globaltrustmodel). Add58thcase:
capturedstockFalse then scalarTrue =>analysisunknown,not fabricatedinstock.
Idealo SKU-onlyissues must also omit Googlemissing_id,not merelyretainwithfalseerror;
strengthenexisting2SKUcases,unchangedcount. Googleconditionalissuesremainunchanged.
