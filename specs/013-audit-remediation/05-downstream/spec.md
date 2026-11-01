# 05-downstream — behavior specification

2026-11-01; implementation authorized umbrella-wide; this assignment DESIGN ONLY.
AR15/16; parent FR05/07,SC05/08/09/10/11. Eligibility/feeds,matching and statistics as separate substeps.

## Outcomes and requirements
FR-D1: keep presence score explicitly presence-only; add rule issues for unsupported/default fields,invalid money,placeholder images,product evidence and destination conditions. Google validation requires actual ID,title,description,link,image,amount/currency,availability; supported brand/identifier/condition and variant rules follow pinned G1 conditions. Missing country/category context ->needs_context, never complete eligibility. No network image approval claim.
FR-D2: shared canonical feed projection uses vendor as brand fallback; stable item ID is supported external_id or existing canonical_product_id (label derived canonical,not manufacturer). If neither, item ineligible; never title/price hash as manufacturer ID. Unknown stock omitted/flagged, never in stock. Export returns retained/skipped counts/issues; ok means operation success only, destination eligibility separate. Default file syntax unchanged.
FR-D3: fuzzy match and title duplicates are candidates, not identity confirmations. Reuse identity conflict checks including explicit/inferred title color,function and quantity; contradictory500ml/1L,shampoo/conditioner,taupe/white not automatically paired. Compatible supported identity positive control required; report precision sample and accepted count separately.
FR-D4: category counts count each label once/product across category_path/product_type; stock true/false/unknown separate and totals reconcile. Existing model stock constructors remain; dictionary missing/null and unsupported defaults are unknown in analysis projection.

## Acceptance scenarios
SC-D1: presence-rich policy/negative price cannot be destination eligible; missingGTIN not automatically identifier_exists=no; conditional brand/condition rules and unknown context explicit.
SC-D2: vendor->g:brand; canonical ID stable after price/title changes; missing both IDs blocks item; unknown currency/stock not invented; XML/validator issue parity and partial export counts.
SC-D3: three reviewed incompatible audit pairs rejected as identity/duplicate acceptance; compatible exact identifier positive control; similar but unresolved titles remain candidates, not merged.
SC-D4: one product[A,A]+product_typeA countsA1; missing/null/true/false stock ->unknown2/in1/out1; zero products yields0 totals without assumed availability.

## Boundaries and compatibility
Child01 functional review passed; full-driver/live gate remains pending. Preserve
constructors,identity,default feed syntax. No production/tests changed here.
Each numbered substep gets executable red tests and independent gates before code.

## G1 concrete Google subset contract
Rule set `google-catalog-subset-2026-11-01`,sourceG1 sections Brand,GTIN,MPN,
Identifier exists,Condition,Item group ID,Gender,Color,Size. Evaluate all applicable
rows cumulatively. `subset_pass` is never full Merchant Center eligibility.
Required context: destination,country,condition,category class,variant flag and
identifier_status(present/absent/unknown for applicable GTIN/MPN assignment,explicit supported declaration). Absent
identifier declaration is unknown,not evidence of genuine nonassignment. Baseline
fixtureB: valid core fields+USD10+explicitstock,US shopping_ads,new,general,
nonvariant,assigned validGTIN and brandAcme,identifier_status=present.

| Rule | Fixture change from B | Exact diagnostic / subset outcome |
| --- | --- | --- |
| G-ID1 | none | no identifier issue;subset_pass |
| G-ID2 | GTIN explicitly unassigned,brand+assigned manufacturerMPN present | no identifier issue;subset_pass |
| G-ID3 | identifier_status=absent,GTIN/MPN absent,brandAcme present,identifier_exists=no | explicit no assignment retained;no missingGTIN error;subset_pass |
| G-ID4 | identifier_status=unknown,GTIN/MPN absent | identifiers_need_context;needs_context;do not emit identifier_exists=no |
| G-ID5 | assignedGTIN supplied plus identifier_exists=no | contradictory_identifiers error;blocked |
| G-BR1 | new/general and brand absent | missing_brand error;blocked |
| G-BR2 | category books/movie/music and brand absent | no brand error;other checks apply |
| G-CO1 | explicitused/refurbished and condition supplied | no condition issue;other checks apply |
| G-CO2 | caller statesused but feed condition absent | missing_condition error;blocked |
| G-CO3 | conditionunknown | condition_need_context;needs_context;never assume new |
| G-V1 | US variants,groupID absent | missing_item_group_id error;blocked |
| G-V2 | US variants,groupID stable,group title consistent,color differentiates and supplied | no grouping issue;other checks apply |
| G-V3 | free_listings variants,countryPK,groupID absent | missing_item_group_id error;blocked |
| G-AP1 | US shopping_ads clothing category1604,age_group/gender/color/size absent | apparel_profile_not_implemented needs_context (not subset_pass) |
| G-U1 | unsupportedcountry/category/destination or missingcontext | unsupported_rule_branch needs_context;no universal-valid fallback |

Initial supported region for nonapparel grouping ads isUS; free-listing grouping
rule supported independently. Other country/category variants explicitly needs_context
until separately designed. Shipping,tax,certification,account,landing-page/image
access and specialized apparel rules are unassessed; expose unassessed_checks,
never Google-approved/complete eligibility. RuleIDs/version/issue severities above
are executable expectations,not placeholders for implementing every Google rule.

D5 verification refinement: one measured source-backed duplicate serialization
mechanism may be repaired with per-export validated bundle reuse; no global cache,
no trust validation bypass or budget increase. Existing validated-load seam may be
used only within same invocation. Preserve atomicrollback and exact full Product/
variant/entireevidence sidecarreload. Actualaudit30s aggregate diagnostic remains
pending until observedpass;oneproduct0.389s is not proof of wholecatalogcause.
