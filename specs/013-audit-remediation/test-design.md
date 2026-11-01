# Behavior and test design (before task breakdown)

Written before tasks. SC/FR definitions and exact expectations are in spec.md.

| Scenarios | Distinct risk / current coverage gap | Planned real-path verification |
| --- | --- | --- |
| SC01–02 | Unknown completion and successful HTTP error documents; generic metadata mistaken for product identity | Controlled transport + production CLI/extractor, with empty/capped/terminal/error fixtures and legitimate free product counterexample |
| SC03 | Failure after prior success and fetch limits interact | Mock only transport; real Woo loop/extract/CLI, 100 then404; terminal99/100/101, item limits1/99/100/101, timeout after batch |
| SC04–05 | Thousand-fold money error versus unsupported compatibility values | Production normalizers and evidence encoder; explicit PKR/USD/EUR contexts, ambiguous input, zero/missing/null/empty/negative/NaN |
| SC06–07 | Nested and variant data lose ownership or get fabricated | Small sanitized saved source fixtures through actual structured/normalization paths; root/@graph equivalence, cyclic links, real/lazy/placeholder images,429 and optional attribute rejection |
| SC08 | Export and validator disagree on canonical fields and destination conditions | Real export XML + validator roundtrip with supported/unsupported ID/brand/price/currency/stock; country/category conditional cases |
| SC09 | Similarity mistaken for identity despite incompatible product variants | Reviewed audit pairs through real match/duplicate paths; incompatible color/function/quantity plus supported positive identity control |
| SC10 | Categories and availability are biased by defaults | Real analyze-file path with repeated category and true/false/missing/null stock |
| SC11–12 | Size, stdout and deadline constraints fail across feature seams | Production CLI controlled server, cap−1/cap/cap+1, remaining deadline below/at retry delay, cancellation cleanup, disallowed URL; stable ordering under shuffled completion |
| SC13 | Historical evidence becomes an unsupported current claim | Hash and summarize saved audit files; record current revision, method and confidence per finding |

## Diagnostic verification now
First saved smoke calls current Normalizer.money(css=True) and QualityScorer.
This demonstrates current behavior; it is not green acceptance evidence. Additional
bounded diagnostic probes may exercise CLI, normalizers, JSON-LD and analysis.
Expected diagnostic results are the audit claims; remediation acceptance outcomes
above are independently derived requirements. No source patching or tests rewritten
to match observed behavior.

## Red-test plan for child slices
Before production changes each child author adds executable tests for its SCs,
saves intended failures and passes G2/G3 review. Existing relevant regressions must
be inventoried; do not count repeated numeric examples as distinct failure coverage.
Missing mechanisms cannot be tested by replacing the mechanism with a fake.

## Synthetic and stress plan for implementation
Deterministic factories, seed0; max24 scenario classes,128 cases total per slice,
max8MiB per ordinary fixture (large-input boundary slice may use cap+1 only),
sequential one worker,120s diagnostic ceiling; full repository driver limits stay
480s total/240s family or narrower. Save one smoke before expansion, stop on first
unexpected failure, diagnose once, retain smallest fixture. Coverage reviewer checks
variant linkage, honest outcome state and budget transitions. Byte/memory boundary
limits must be finalized per slice rather than treating these as a scale guarantee.

## Bounded live plan for implementation
After offline green: one read-only smoke on one audit domain (max3 requests,
5 products,30s outer process deadline,zero retries), save result before expansion.
Then at most one domain per affected adapter,10 requests/10 items/60s per domain,
sequential, obey robots policy and stop on first unexpected result. Pin URLs and
assertions in each child before requests. Transient404/429/deadline cases use
controlled transport mechanism tests; label live observations separately. Planning
itself requires no fresh live requests and cannot establish present store behavior.
