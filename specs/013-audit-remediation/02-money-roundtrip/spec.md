# 02-money-roundtrip — behavior specification

2026-11-01; implementation authorized umbrella-wide; this assignment DESIGN ONLY.
AR12; parent FR03/06,SC04/05/11. Supported amounts/currencies and bounded extraction-to-downstream roundtrip.

## Outcomes and requirements
FR-M1: preserve Product/Variant constructors, including direct Product.currency defaultUSD. Normalizers emit empty currency string when source absent/rejected, with unsupported observation and diagnostic; no literal unknown ISO value. Explicit valid source code remains uppercase. Never infer country from domain. Shopify may use captured cookie/explicit currency/page currency declaration; conflicting evidence stays unresolved, not overwrite.
FR-M2: shared monetary parser strips known symbols/prefixes, validates grouping; comma-only three-digit grouping is thousands only with explicit compatible locale/currency or Rs-prefix context (PKR-context3,720 ->3720); context-free3,720 remains unresolved (three-decimal currencies exist). Decimal comma one/two fractional digits requires compatible locale; mixed separators use last separator as decimal only with valid grouping (3.720,00 ->3720.00). Rs. indicates rupee family, not uniquely PKR: accepted amount3720, currency unknown unless explicitPKR context. Ambiguous/malformed grouping rejected, never observed zero. Explicit finite zero retained with eligibility diagnostic; negatives/nonfinite rejected.
FR-M3: downstream read cap32MiB, records1000,depth64/node100000 unchanged. Add opt-in extract --compact catalog-v1 envelope deduplicating identical capture bodies by digest without losing required provenance; downstream readers accept it and legacy output. Default formats unchanged. Over-cap rejects before parse; no silent truncation; failed atomic write preserves target.

## Acceptance scenarios
SC-M1: missing/null/empty/USD-source currency -> unsupported empty/unsupported empty/unsupported empty/observedUSD respectively; direct Product() stillUSD.
SC-M2: explicitPKR-context3,720/Rs.3,720/3,720.00/3.720,00 ->3720/3720/3720/3720; context-free3,720 unresolved, explicitPKR suppliesPKR while Rs. alone does not. Three-decimal currency/locale context retains appropriate decimal precision rather than applying PKR grouping.
SC-M3: 1,23,4/NaN/negative reject, explicit0 observed with flag; price rejection distinct from missing.
SC-M4: a compliant5.4MiB legacy extraction within record/node/depth bounds reads successfully; the saved Allbirds file is not promised to satisfy those other bounds without inspection;32MiB-1/at/+1 boundary, over records/nodes reject. Compact duplicate-capture roundtrip preserves exact Decimal,variant IDs,trust support and ordering; dangling/hash-mismatched refs reject.

## Boundaries and compatibility
Child01 functional review passed; full-driver/live gate remains pending. Preserve
constructors,identity,default feed syntax. No production/tests changed here.
Each numbered substep gets executable red tests and independent gates before code.

## G1 expansion-budget repair
FR-M4: wire AND expanded logical tree budgets each32MiB canonical UTF8JSON,
100000nodes,depth64,1000products. Compute expanded cost before allocation, counting
repeated references for every occurrence (shared Python identity is not a limit
bypass). Capture table digest keys unique; verify canonical content hashes before
resolution. References target table entries only; nested references in capture
bodies/cycles,danglingrefs,duplicate keys/hash mismatches reject. Preserve valid
repeated refs when expanded budget fits; reject repeated-ref amplification over
any expanded bound. No recursive hydration before validation. Downstream output
serialization obeys same expanded bound; atomic targets preserved on rejection.
