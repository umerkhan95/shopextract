# 07-readiness — behavior specification

2026-11-01; implementation authorized umbrella-wide; this assignment DESIGN ONLY.
AR17; parent FR05/08,SC08/13. Opt-in local informational readiness command, not submission/certification.

## Outcomes and requirements
FR-Q1: add readiness FILE --target google_shopping|schema_org|openai_discovery|acp --country/--category optional. Reuse child05 issues/projection, no extraction/network calls. Report schema_version,rule_set/source_date,provenance,summary and per-item missing/unsupported/invalid/needs_context checks. Return machine operation success for valid input even if not ready; --strict returns existing partial exit3 with retained report on blockers; invalid input E_USAGE/E_OPERATION unchanged.
FR-Q2: Google target is scoped data eligibility diagnostics, not account/shipping/tax/landing-page/approval proof. schema_org target states model-coverage profile (name,url,image,identifier,offer coverage) and never invents universal mandatory schema.org fields. ProductGroup/variants reported separately.
FR-Q3: openai_discovery targets stable O1 nine fields with brand/vendor and explicit seller context; unknown availability allowed,unknown currency not. Missing seller_name needs input,never fabricated from domain. acp reports unsupported_protocol_assessment/needs_context with RFCProposal metadata,not ACP-ready: local product data cannot verify checkout/payment/auth/protocol integration. No certification claims or fabricated ACP readiness score.

## Acceptance scenarios
SC-Q1: complete Google data without destination context ->needs_context; invalid currency and missing ID blockers; --strict partial data retained; nonstrict report exits0 but ready=false.
SC-Q2: schema partial Product has explicit coverage gaps,not invalid vocabulary; ProductGroup variants separated, no group-price fabrication.
SC-Q3: OpenAI nine-field valid fixture inclavailabilityunknown accepted for discovery profile; missing seller/brand fails; supplied sellercontext preserved and no merchant inference.
SC-Q4: --target acp always states protocol not assessed and RFCproposal provenance, even perfect catalog; report deterministic on reordered inputs and no network; invalid target rejected before reads.

## Boundaries and compatibility
Child01 functional review passed; full-driver/live gate remains pending. Preserve
constructors,identity,default feed syntax. No production/tests changed here.
Each numbered substep gets executable red tests and independent gates before code.

Concreteprofilecontract: reportassessment_scope names limitedGooglecatalogsubset,
schema_model_coverage,openai_basic_product_fields orunsupported_protocol_assessment.
`ready` applies ONLY namedprofile,nevermerchantapproval/checkout. Googlecontext can
be supplied by optionalbounded --context JSONfile (closedexisting05contextfields),
--country/--category override; --seller-name explicit OpenAIsellercontext. No domain
inference. OpenAIstablebasic9fields currentofficialcheck saved2026-11-01;whenvariants
arepresent,variant/grouping unassessed =>needs_context/readyfalse even9basicfieldspass.
Schema rawProductGroup coverage/hasVariant entries separate,noinheritedgroupprice.
Per-itemdeterministicsortbyexplicititemidentity/sourceURL;no timestamps/randomscore.

Bounded helper contract (amended before production):1000 top records and1000
aggregate source variant nodes. Source variant graph depth64 and active-path cycle
guard apply independently of CLI reader; raw provenance/evidence is never traversed
by profile assessment. Assessed schema variant coverage is capped at100 nodes and
depth8(root0),retaining top-item reports with explicit unassessed/omitted coverage.
Source-cap overflow returns ready=false,needs_context and no assessed items; summary
states omitted top records. CLI over1000 records remains E_USAGE. A normal native
25-product/265-variant catalog is valid input,not an input-shape usage error.
Known scalar profile fields cap8192 UTF-8 bytes. Escaped JSON report/projection
budget8MiB includes framing reserve; overflow is explicit needs_context,never silent
truncation. Reports never copy raw_data/contracts. Reader32MiB/1Mnodes/depth64 remains
separate. These bounds supersede the initial100-source-variant proposal.
