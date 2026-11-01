# Behavior/test design before breakdown

Scenario IDs and exact expected outcomes: spec.md. Distinct uncovered risk:
Mis-scaled money, unsupportedUSD becomes fact, and oversized self-output; test actual normalizer/evidence/portable reader/export seams, not a duplicate parser.

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

Live plan: one saved Shopify domain,max3requests/2items/30s,zero retries; CSS monetary cases controlled offline when live locale inaccessible.
Offline: focused acceptance/affected checks then configured scripts/run_tests.py
240s-family/480s-total (never increase). Prior timeout does not satisfy this gate;
record unrun families and unknown failure nodes honestly. Separate synthetic
mechanism,stress and actual live evidence; inconclusive live is never a pass.

G1 repair SC-M5: tiny wire table large capture repeated many times: expanded
bytes/nodes/depth just below/at cap accepted,+1 rejected before hydration; same
capture referenced twice under cap retains equivalent support. Duplicate digest
keys,hash mismatch,danglingref and nested/self/cross-reference cycles rejected.
Count repeated occurrences even if objects stay shared; no allocation/serialization
before estimated limits checked. Legacy5.4MiB test uses known-compliant generated
fixture; saved audit data only asserted if separately inspected for all limits.

Executable G2 inventory: currency4 missing/null/empty/explicit +constructor1;
CSS monetary7 legitimate/context/ambiguity cases +3 rejected numeric cases;
zero outcome diagnostic1; compact actual evidence/variant roundtrip1;
expanded byte cap -1/at/+1 (3),node -1/at/+1 (3),depth -1/at/+1 (3),
malformed reference5 (dangling,hash,nested,self/cross cycles/duplicate keys split
per collected inventory); reader32MiB -1/at/+1 (3),compliant5.4MiB1. Final collected
count is recorded from pytest,not inferred from this provisional inventory.
Each fresh synthetic envelope canonicalized with declared JSON/hash convention.
Max per-case32MiB+1 input/256MiB retained memory target,120s sequential full new-file
run after one saved small smoke; stop on unexpected harness issue and repair once.

Integration seam completion before tests: two actual CSS normalize cases route
PKR-context3,720 and Rs.3,720(no currency authority) through production normalization,
expected price3720 and PKR/unsupported-empty currency respectively; direct parser
cases alone cannot detect forgotten context propagation. One real transport-backed
CLI extract --compact keeps existing schema1.0 outer response,data is catalog-1
object decodable to legacy product_count1; default output unchanged. This prevents
codec-only success with missing CLI integration. Actual final inventory39 cases.

G2 repair BEFORE tests (25 additions,final64-case ceiling): ten independent
normalizer branches Woo store/admin,Magento REST/GraphQL,Shopware store/legacy,
BigCommerce,schema,OG,feed each missing and explicitUSD (20). Missing ->empty,
unsupported+reason; explicitUSD ->observedUSD with exact field pointer. CSS lower
pkR ->PKR accepted/source /currency; invalidNOPE ->empty/rejected; conflicting
Shopify variantPKR vs productUSD ->empty/unsupported with both pointers (3).
Existing Shopify/CSS cases strengthened with support/path checks,not new counts.
One actual full compact CLI response ->bounded read_json_file ->products_from_value
->analyze-file roundtrip carries Decimal1.20,variant/evidence and a literal exact
$capture_ref map inside raw source and actual captured values; no direct-decode
substitute. Same integrated case injects os.replace filesystem failure after encode,
existing output sentinel preserved. One malformed compact input ->export to existing
sentinel rejects with E_USAGE before replacing target. These2 integration cases
complete25 additions. Filesystem/HTTP external boundaries only are injected; no
codec/projection/normalizer stubs. Existing byte/memory/120s bounds unchanged.

Affected compatibility disposition before repair: legacy CSS decimal-comma fixture
has no locale despite declared contextual contract; retain its29.99 assertion and
supply explicit price_locale=de-DE/currencyEUR,wire this source context through CSS
caller. Browser redirect provenance fixtures require knownstatus200 under child01
fail-closed gate; add status instead of weakening admission/support assertions.
Old fixed1MiB edge test updates to reviewed32MiB boundaries; independent exact
byte edges already anchor this contract. CLI advertised input cap follows actual
bound. No inference from DE title/domain; existing ambiguous cases stay rejected.

Amendment G2 inventory designed before tests:17 cases:registry2unknown+metadata1;
refs3forbidden slots;scanner escape/shape1,node hardbound3,depthbound3,dense input
before decoder1,portable-shaped>100k reader1,portable budget alignment1,native Woo
category CLI default1. Actualaudit roundtrip is separate bounded diagnostic using
primary hash/path metadata (not CI external-file test or skip). Existing literal
source ref roundtrip64-case coverage reused. Newfile120s,oneworker,max32MiB+1,
nodefixtures<=1M+1,seed0. Registry source retrieval currentlyblocked,recorded honestly.

Provenance-slot refinement before final assertions: forbidden refs go into actual
portable product.title/product.price and merchant raw_data attribute,not only
extra catalog-level keys; reuse real product_to_record constructor shape. All3
must reject in codec before downstream normalization/hydration,while existing
escaped raw lookalike roundtrip remains required. No new case count.


ISO SOURCE RESOLVED by primary:systemcurl defaultverifiedtrust (no-k),one diagnosed
TLS-stack repair; reuse savedXML/json,NOmorefetch. SIX publication2026-09-17,
178codes,47491bytes,SHA25633139b438657d1cee116ba737807ea71d19d6de4b90f799a09c56f0cc6a1b0ff.
Prior source-block notes are historical,not current blocker. Registry version/hash
must match this artifact; is_pricing_currency(code) is membership minusXXX(no
currency)/XTS(testing),which both remain unsupported for real price currency.
Metadata acceptance strengthened to these exact controls,17casecount unchanged;
registry/scanner/slot production still gated. No further source fetch/probe.

Last G2 repair BEFORE test: direct decode_compact_catalog receives valid compact
wire with>1M tiny JSON values but<32MiB. Instrument only full json.loads boundary
to raise if called; expected ValueError from actual lexical budget first. Reader
proof alone cannot certify this entry. New amendment count18,baseline64 unchanged;
120s ceiling. Actual-audit final diagnostic must additionally run analyzer and
CSV+evidence-sidecar export/reload,checking Decimal/variants/evidence equality;
reader-only success is insufficient. Do not rerun known blocked sample now.
