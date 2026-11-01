# G2 documentary skeleton and intended-red evidence

2026-11-01; G1 PASS prerequisite. No production/stubs/components in this stage.
Skeleton defines additive monetary context,private bounded compact codec/limits,
reader and opt-in CLI seams. Tests use real Normalizer,normalize,capture,portable
extraction_data,reader and Click API transport; no duplicate parsing/hydration.
Missing private codec is an intended declared-interface gap inside tests,not a
collection failure. Existing source functionality remains callable.

First smoke `red-smoke.log`: missing Shopify currency remainsUSD,1 intended
failure/35 deselected,0.42s. Initial `red-full.log/json`:36 collected,31 intended
failures/5 controls pass1.81s. Designed then added actual CSS context and compact
CLI seams to prevent helper-only coverage; final `red-final.log/json`:39 collected,
34 intended failures/5 passing controls,2.17s pytest,120s sequential subprocess cap.

| Group | Count |
| --- | ---: |
| Missing/null/empty/explicit currency |4|
| Direct Product constructor default |1|
| Contextual/ambiguous/three-decimal CSS parser |7|
| Malformed/nonfinite/negative amount |3|
| Explicitzero diagnostic/support |1|
| Actual capture+variant+portable compact roundtrip |1|
| Repeated-ref expanded bytes/nodes/depth edges |9|
| Dangling/hash/nested/self/cross/duplicate refs |6|
|32MiB wire -1/at/+1 +compliant5.4MiB legacy |4|
| Actual CSS normalizer and opt-in CLI integration |3|

Passing controls: explicitUSD,directProductUSD,malformed grouping/nonfinite
rejected,and oversized reader rejection. Parser optional currency/locale and
compact module are absent,as expected. New normalization/CLI seams fail intended
price/default/unknown-option assertions. Expanded nodes118 while wire nodes43;
expanded depth6 while wire depth5,so narrowed limits genuinely test expansion.
Fixture target max32MiB+1,retained-memory target256MiB (not measured guarantee),
seed0,one worker,no inference/merchant requests. Currency fixtures distinguish
PKR authority from Rs rupee-family prefix and preserve three-decimal precision.

Command prefix PYTHONPATH=src OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
MKL_NUM_THREADS=2 TOKENIZERS_PARALLELISM=false .venv/bin/python -m pytest
 tests/test_money_roundtrip.py -q --tb=short. G2 independent review next; components
only afterG2,thenG3 before business logic. Full-driver/live gates not run or waived.

G2 blocker repair designed before25 additions; final64-case ceiling retained.
`g2-integration-red.log/json`:14 intended failures/11 controls pass,39 deselected,
3.37s,120s ceiling. Ten separate native/schema/OG/feed dispatcher branches each
exercise missing and explicitUSD with exact path/support expectations; valid10
controls pass. Lowercase,invalid,conflicting source currency cases fail intended
scalar/support assertions. Full compact CLI->reader->products->downstream/literal
provenance/filesystem atomic path fails missing--compact option as designed.
Malformed compact export target-preservation control passes. Existing Shopify/CSS
expectations strengthened with source-pointer checks; no production/components02.
Full64-file green is not claimed; independent G2 re-review next.

## Implemented focused evidence and remaining real-source gap

AfterG3 first green1pass63deselected1.48s;`acceptance-green.*`64pass2.59s.
`affected.*`203pass4fail6.28s: reviewed no-locale CSS contract,knownHTTP status
missing in two old browser fixtures,and old1MiB edge. Designed disposition before
changes; kept monetary/redirect support assertions and supplied explicit locale/
status; updated exact32MiB edges. `focused-final.*`:271pass7.94s,120s ceiling.
No full-driver/live run while native generic import blocker remains.

Implemented shared currency/context parser,private bounded compact codec with
capture hash/literal escaping and expansion preflight,reader/full response/native
product/downstream integration,atomic CLI --compact output,advertised32MiB cap.
No03 code or unrelated destination work. Exact unknown-code semantic coverage
is limited to source-code lexical validation here; destination ISO policy is later
validation scope,not evidence of platform acceptance.

PRIMARY DISCOVERED REAL ROUNDTRIP GAP: actual saved Allbirds5,425,392bytes has
~193k nodes,so current100k ceiling still rejects it. Synthetic compliant5.4MiB
fixture does NOT prove that real sample roundtrip. Caps not blindly relaxed.
node-budget-amendment.md proposes1M catalog nodes with preparse lexical/token/
depth budgets and independent actual-source/adversarial tests BEFORE code change.
Review/evidence pending;02 not complete despite271 focused passes. Prior full-suite
and live gates remain pending. Original actual-source count evidence owned by
primary,forthcoming; no repeated large-file read here.

## Amendment G2 intended-red evidence; NO amendment production

Source registry URL pinned to SIX list-one. Web rendering failed XML content-type;
bounded SSL-verified urllib fallback10s/256KiB failed certificate-chain verification.
No insecure fetch/retry sweep. iso4217-source.json records BLOCKED,publication/hash
unknown; runtime table cannot be invented. Registry metadata/membership tests are
red pending verified source and future implementation.

New amendment17-case file after explicit design/skeleton: first registry smoke
2failed/15deselected1.49s; `amendment-red-full.*`16 intended failures/1 portable-node
alignment control pass5.39s,120s. Covers registry,ref slots,preparse shape/escape/
1Mnode/64depth edges,dense-input-before-decoder,real portable-shaped200k-node input,
native Woo default CLI cap compatibility. Provenance positions refined to actual
portable product.title/product.price/raw_data; focused `amendment-slots-red.log`
records3 intended failures/14 deselected (same3cases,no count increase).

`actual_audit_roundtrip.py` bounded30s diagnostic executed once with supplied
actual-audit-shape metadata: actual historical5.4MiB/25product/193134node Allbirds
reader returns E_USAGE,stored actual-audit-roundtrip.json. No raw capture copied
into Git or full file printed. This is current reproduction of remaining gap,
not live merchant evidence. No full-suite/live rerun or cap/scanner/registry/slot
production changes.03components independently authored;03production unchanged.


ISO SOURCE RESOLVED by primary:systemcurl defaultverifiedtrust (no-k),one diagnosed
TLS-stack repair; reuse savedXML/json,NOmorefetch. SIX publication2026-09-17,
178codes,47491bytes,SHA25633139b438657d1cee116ba737807ea71d19d6de4b90f799a09c56f0cc6a1b0ff.
Prior source-block notes are historical,not current blocker. Registry version/hash
must match this artifact; is_pricing_currency(code) is membership minusXXX(no
currency)/XTS(testing),which both remain unsupported for real price currency.
Metadata acceptance strengthened to these exact controls,17casecount unchanged;
registry/scanner/slot production still gated. No further source fetch/probe.

Last amendment G2 gap repaired in design/test only: direct compact dense-token
preflight BEFORE json.loads proof. `amendment-direct-codec-red.log`:1 intended
failure17deselected1.89s,actual full decoder boundary reached too early today.
Reader preflight alone no longer treated as codec coverage. Amendment now18cases;
prior17-case reds retained,no18-case green claimed. Actual-audit diagnostic script
now requires analyzer +CSV/evidence-sidecar export/reload and exact Decimal/variant/
evidence equality after reader passes. Enhanced script NOT executed against still
blocked real sample in this assignment; previous E_USAGE remains actual outcome.
No02amendment code or components before pendingG2/G3 review.

Amendment afterG3:18cases pass45.17s. Combined82 run hit its120s ceiling after
71 completed rows; no failure marker,actualaudit not launched. Diagnosed lexical
string scanning per-character Python loop dominated large32MiB boundary fixtures.
One repair uses stdlib compiled-regex search for quote/backslash/control boundaries,
retaining actual escape/token/depth logic and avoiding string-object allocation.
No test/budget relaxed. Native explicit-limit check also keeps original1MiB CLI
cap independently of catalog byte allowance (same reviewed isolation contract).

Amendment implemented after independentG3 PASS: immutable verifiedISO membership,
provenance-slot grammar and lexical preflight before both readers,1M catalog node
allowance with existing portable1M ceiling,nativeWoo1MiB defaults/checks isolated.
18amend tests pass45.17s. First82run timed out120s; one diagnosed string-scan repair
uses compiledregex search over quote/backslash/control boundaries (no allocation
of complete JSON tree,limits unchanged). Final82PASS59.17s.

Actual historical integration first30s timeout,preserved as failure; checkpoint
instrumentation located record-equality serialization. One minimal comparison
repair avoids re-running full product_to_record/trust validation: exact decoded
original value equality for ALL Product fields/variants plus entire encoded
contract dicts (including source values) is retained. Last30s run proves25product
reader+variant/evidence equality and analyzer25; still TIMEOUT during export.
CSV-sidecar reload remains UNVERIFIED; no budget increase or further retry loop.
Saved actual-audit-roundtrip.json checkpoints; final full roundtrip not claimed.
Reviewer must assess comparison equivalence;05export work may resolve cost.
