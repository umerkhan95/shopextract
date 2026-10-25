# Implementation plan — G1 candidate, 2026-10-17

Constitution check: existing Product/Variant/identity/default exports preserved;
source evidence separate from derived mapping; MIT/self-hosted exact rules and supplied
registry; no provider spend, paid dependency or inferred taxonomy/profile authority.
Design and test matrix precede this plan/tasks; independent gates remain pending.

## Architecture decisions for review
Use one explicit categorized wrapper layer around ordinary Product/extraction result,
one typed source observation contract, one deterministic mapping engine and one
version-one companion codec. Reuse capture/Normalizer/SupportState/portable storage/
maintenance jobs and guarded transport. See spec FR09–14 and research decisions1–9.
Native adapters translate only; common owner owns normalization/core, codec, security,
tool child-process format/cache/maintenance. Keep module responsibilities/interfaces
in skeleton.md after G1, then components.md after G2; do not implement a framework now.

Concrete acquisition: default native query unchanged; BigCommerce optional first20
CategoryConnection selection, Magento optional categories{uid name}, Shopware returned
categoryIds/index, Shopify public custom type, Woo product_cat, generic retained feed/
JSON-LD/OG declarations. No tree request or category followup; partial source stays partial.
Store/catalog and assignment channel/locale separate from vocabulary namespace/version.
Unknown values never default into source facts. Exact mapping sets require equality;
conflicts remain ambiguous. Immutable companion binding rejects mutated Product even
at encoding. Config/schema/scope/profile-binding digests isolate category-mode caches.
Maintenance retains explicit configured profile and all matcher/field safeguards;
category mode missing/ambiguous adds review; ordinary legacy jobs unchanged.

## Gates and next actions
G1: independent reviewer checks actual spec/test/tasks/research/plan files and schema
proofs; record digest/findings/verdict. None passed yet. Then shared skeleton + intended
red acceptance failures; G2 independent review. Reusable model/refined skeleton; G3
independent review. Author resolves blocking findings and rereviews affected artifacts.
Implement T09–12 only after all gates and corresponding red checks; platform authors
acknowledge direct consultation and common contract before code. No duplicated mapper
or producer/security query bodies. Sequential test/driver processes under user limits.

## Verification and handoff
C01–24 independently designed mechanisms, bounded fixtures/seed26/100 fixed invocations/
120s, source evidence and actual production paths; ordinary44 normalization baseline
is reusable compatibility evidence only. Stop/save first failure, one repair/blocker.
Then affected regressions/required repository checks and <=12 actual live HTTP calls,
explicit sources/access prerequisites, no fallback model or recursive crawl. Missing
native access remains blocked/inconclusive with separate real-path synthetic proof.
Final reviewer checks diff/gates/mechanism/live evidence; remaining access limitations
must be explicit. No push/PR/Git/publication requested in this design assignment.


G1 error revision: implement the opt-in native errors+data contract before declaring
C03/C06/C10 green. Preserve valid product siblings and captured supported category leaves;
category errors/unknown completion cannot become complete/empty. Rejection/access denial
retains explicit unavailable/source diagnostics with no category-triggered fallback
request. Shared owner handles common parsing seam; default helper behavior remains
compatible. These are bounded variants of existing cases, not expanded research/sweeps.
