# Behavior/test design before breakdown

Scenario IDs and exact expected outcomes: spec.md. Distinct uncovered risk:
Cross-variant identifier leakage, installation-specific GraphQL failure wiping core data, and absence represented as confident fact; controlled HTTP only, actual adapters/normalizers.

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

Live plan: one domain per changed adapter,first smoke<=3requests/2items/30s; only then max6requests/3items/45s peradapter.429/core-schema failures controlled offline; stop first unexpected result.
Offline: focused acceptance/affected checks then configured scripts/run_tests.py
240s-family/480s-total (never increase). Prior timeout does not satisfy this gate;
record unrun families and unknown failure nodes honestly. Separate synthetic
mechanism,stress and actual live evidence; inconclusive live is never a pass.

## Executable G2 inventory (19 cases)
Brand single/empty/conflict3;supplied childaliases2;duplicatechildID1;Woo publicdetail valid/wrongID/5boundary3;Shopify429/variantmismatch2;Magento capability supported/corefallback2;defaultcore1;publicAPI1;HTMLMagento/plainfallback2;CLI Woo/Magento2. Real paths,mockHTTP only. Existing Shopify/productID/GTIN controls and category tests reused during affected checks. Woo enrichment global20 ceiling documentary contract; stress coverage must be added before implementation if reviewer finds absent.

G2 refinement BEFORE tests: global20 means EXTRA DETAIL HTTP attempts, excluding base catalog fetches; five parents with5declaredIDs each =>first20details,all5base retained,fifth children absent,partial reason. Wrongparent_id rejects child despite matchingID. Missingchild stock isNone/unsupported,notFalse. Existing enrichment acceptance must normalize adapter output DIRECTLY and resolve observed childprice/stock/attributes evidence against actualdetailURL/rawvalues (no recapture). Invalid Magento capability, Woo enrichment onShopify API/CLI =>ValueError/usageerror BEFORE anyHTTP. Unknownoptionalfield then coreerror =>atmost2requests,no products anderror. Reuse existing Shopify identifier controls by exact collected paths recorded at implementation. Bounded total27cases,<=120s;17rendered.

Functional A1 refinement BEFORE tests:10cases. Detail JSONlist/null must retain1base,partialerror,no variants (shapevalidation before .get). Parent variations dict/string unsupportedcontainer =>no detailHTTP,retainbasepartialreason. DeclaredIDs empty/bool/path/query/zero/negative rejected BEFORErouteconstruction; onebasefetch only,retainedbase/error. Only positive integer (excludingbool) or nonempty decimalstring>0 routeIDs accepted;6invalidvariants distinct source types. ExistingvalidnumericID/global20/parent5 controls retained. Total37cases.
Portable interop BEFORE code:5 cases,37existing+5=42. Real capture→Woo normalization
→portableJSON→reload preserves None/False/True variantstock and entire product/
variant contracts. LegacyVariant() defaultTrue/positionalFalse preserved. Invalid
text stock rejected. Diagnostic unknown-stock-portability.json already proves
None currentlyfails at product/variants/0/in_stock; only nullable annotation needed.
