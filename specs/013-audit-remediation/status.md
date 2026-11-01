> Draft delivery: `fix/audit-remediation-main` integrates the remediation onto
> `origin/main` (`319ee9b`), excluding the unrelated refrigerator commits. User
> requested push/PR publication; labels remain unrequested. See `delivery.md` for
> current integration checks. Historical full-run and live evidence below belongs
> to the earlier development baseline, not this integrated PR tree.

# Audit remediation — implementation and final verification

User authorized all fixes2026-11-01. Branch fix/audit-remediation, HEAD90d5bd1;
Original development baseline retained below. Preserve unrelated specs012 edits. Primary /root,
author /root/audit_research, independent reviewer /root/audit_plan_review,
sequential gates. Draft commit/push/PR authorized by the latest user request; no labels requested.

## CURRENT resume point — do not restart passed work
All seven children and integration amendments are implemented and functionally
reviewed. Latest source change fixes decoded-response header copying in discovery;
3 real gzip cases plus35 affected controls passed6.09s. Latest source full driver5
TIMED OUT239.16s at80% (all completed nodes passed), at restore-GTIN timeout
control. Oracle/maintenance NOT RUN in5. Earlier driver4 passed2229 cases344.10s
before the narrow compression fix, so it is NOT a latest-source full pass.
No further source edits/speculative sweeps or merchant requests. Independent final assessment confirmed functionalPASS and G4/latest-source
full-resource/finalPENDING (reviews.md). All282 manifest hashes matched. No new
source blockers found; further optimization/sweeps not warranted by unproven host
cause. A separately authorized unchanged rerun requires demonstrated settled activity.
Only authorized Khaadi retry remains gated on fresh offlinegreen; not attempted.
One post-timeout process snapshot shows unrelated host activity, not proven cause;
no other process was modified. Browser merchant live still blocked as below.

## Completed functional scope
- 01 truthful outcomes, HTTP/product admission, Woo later404 retention.
- 02 exact contextual money/ISO registry, bounded compact roundtrip; rendered-money
  zero/symbol/conflict repairs. Native constructors preserved.
- 03 bounded shared browser-free HTML parser, DOM/JSON-LD ownership, browser gapfill.
- 04 Woo variants/brands/details, Shopify identifiers, Magento capabilities/detection;
  nullable Variant stock portable/defaultTrue unchanged (5+110 checks).
- 05 destination subset/feed/source-aware identifiers, match/duplicate vetoes,
  category/unknown-stock statistics, per-export validated snapshot reuse.
- 06 lazy imports/native HTTP defaults, prefetch/retry deadlines, timeout recovery,
  bounded discovery worker/robots/redirects/stdout/stable ordering. Recovery adds
  time after source cancellation; no whole-CLI wallclock/RAM guarantee.
- 07 bounded informational readiness; no Google approval/ACP certification claim.
- Integration: category namespace/cache compatibility, isolated category1MiB
  publication vs catalog32MiB/1M nodes, correct capability metadata, model-stop
  priority without promoting partial source coverage, immutable projection reuse.

## Verification evidence and exact limits
Driver4 passed2229 tests344.10s: main2099/oracle24/maintenance106. It predates
compression fix; does NOT establish latest full-source pass. Latest driver5 timed out; current full-source gate remains pending.
Earlier failed/timeout reports preserved, not re-labelled. Most recent historical
Allbirds25 products/265 variants ALL fields/entire contracts/source values,
analyzer and CSV+sidecar reload passed original30s after projection optimization.
See02-money-roundtrip/actual-audit-roundtrip.json. Claim A01–A35 mapping:
claim-coverage.md; detailed commands/results/reviews in verification.md/reviews.md.

Actual HTTP live after driver4: Allbirds200→2partial; Woo200/per_page2→2partial;
Naheed product200→1; Naheed missing404→no product/error. One request each, all four
assertions pass. Khaadi robots200 once then unavailable policy: inconclusive,
no forbidden request/emission. Original observation preserved separately; exact
cause not attributed. Primary authorized one retry only after latest offlinegreen;
aggregate first+retry<=5 requests. Browser merchant live remains BLOCKED: one
local SDK inspection found page hook but no supported service-worker configuration
before context creation, so global request counting unproven. Offline deterministic
browser admission/merge mechanisms passed; no uncounted browser live claim.

## Usage and repository state
No local inference/model launch, paid API, upload or parallel delegated work.
Actual session usage counters unavailable: primary tool/get_goal check returned
null goal/remainingTokens/completionBudgetReport; evidence/usage-milestone-runtime.json.
No quota percentage estimated. Reuse saved evidence. Source/tests remain unchanged after driver5. Final diff-check passed; current282
source/test/docs hashes saved in evidence/final-source-manifest.json.
