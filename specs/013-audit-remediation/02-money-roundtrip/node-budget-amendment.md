# Proposed behavior/test amendment — review required before code

Original scope: downstream must consume extraction's own bounded output. Current
approved100000-node limit is insufficient for actual saved25-item Allbirds output.
Primary's saved-source measurement (not repeated here):downstream/allbirds.json
5,425,392bytes,products168,935nodes plusraw_products24,178 (~193k before metadata).
Source root is parent audit research.md. Primary evidence/hash record forthcoming.
Current compliant5.4MiB synthetic pass proves byte handling only,not this real case.
Current02 completion/full verification is explicitly blocked on this gap.

## Proposed FR-M5 (not implemented/approved)

Raise catalog logical node ceiling to1,000,000,keep32MiB wire AND expanded bytes,
depth64,1000record ceilings. This accommodates measured sample and is a bounded
proposal for100-product verification,not a promise that every100-item catalog fits.
Before json.loads, perform incremental lexical budget/depth prescan (UTF8 bounded
bytes,quoted strings/escapes respected,strict constant/numeric grammar validated
by final decoder). Count containers/scalar values and a separate key/token ceiling
2,000,000; reject over1M values or depth64 before object allocation. No caps relaxed
without this prescan. Wire and expanded-reference limits both enforced; estimate
expanded reference cost before hydration,even repeated shared objects.

Existing32MiB JSON can contain millions of tiny tokens: post-parse node checks alone
are insufficient. Prescan must be shared by compact and legacy catalog readers;
outer schema1.0 overhead included. Existing duplicate-key/hash/cycle/reference
rules remain. No unconditional “large input succeeds” claim or unlimited memory.
Retained-memory256MiB remains verification target for defined fixtures,not proved
RSS guarantee; measure before claiming it. Other protected consumers remain scoped.

## Predesigned SC-M6 / independent expected outcomes

1. Actual saved25-item Allbirds full envelope:reader->products projection->real
   analyze/export roundtrip retains25 items,Decimal,variant identifiers/evidence;
   <=1M nodes/32MiB/depth64. Save hash/counts/minimal source report,not raw Git dump.
2. Deterministic realistic100-product provenance fixture within ceilings succeeds;
   just-below/at/above1M nodes,32MiB anddepth64 obey independent exact expectations.
3. Small-wire repeatedcapture refs amplifying to>1M nodes fail before hydration;
   valid repeat retains factual support. Existing compact corruption cases remain.
4.32MiB highly dense scalar/container JSON exceeding token/value ceiling rejects
   before full decoder allocation. Instrument decoder external seam or bounded
   memory observation to prove rejection order,not a fake replacement algorithm.
5. Escaped quotes/brackets/braces inside strings do not count as structure; UTF8,
   whitespace,number/literal boundaries and malformed JSON cannot bypass prescan.
6. Atomic output target and typed CLI errors preserved on preflight failure.

Budget:one saved small case first,then max12 independent scenario classes,seed0,
one subprocess/worker,120s total,32MiB+1 input; high-density memory cases isolated
with recorded peak. Stop first failure,one diagnosed repair. New G1/G2/G3 review
and red evidence required before changing current64-case expectations or caps.

## G2 exact scanner, registry, slots and consumer contracts

`_bounded_json.preflight_catalog_json(payload:bytes,*,max_bytes=33554432,
max_nodes=1000000,max_tokens=2000000,max_depth=64)->JSONShape` (frozen fields
nodes,keys,tokens,depth). Values count each container/scalar;keys count object keys;
tokens=nodes+keys. Rootdepth0 including scalar leaves. Strings honor escaping;
syntax still validated strictly by final decoder. Call scanner BEFORE json.loads
in compact AND legacy catalog readers; limits may narrow,not enlarge. Shared
portable validate_tree must receive same1M catalog ceiling; changing only CLI
counter cannot satisfy real roundtrip. General/native category limits stay within
own ceiling:default WooTreeLimits reused,never expanded by catalog MAX_BYTES.

Registry: proposed pinned SIX ISO4217 Maintenance Agency list-one,source URL in
iso4217-source.json. Web reader rejected XML; bounded10s/256KiB fallback encountered
certificate verification failure. Source publication/hash therefore BLOCKED,not
invented. `_currencies.REGISTRY_SOURCE/REGISTRY_VERSION/REGISTRY_SHA256` must name
verified bundled source before implementation; runtime offline membership rejects
QQQ/ZZZ even though3letters,accepts assignedUSD/PKR/KWD. No ISO source retry sweep.

Capture refs allowed ONLY raw_products[i]._capture,products[i].product.raw_data.
_capture,and those raw-root `_field_sources`/`_identifier_sources` provenance
capture slots. No references in titles,prices,identity,diagnostics or arbitrary
source dictionaries. Encode escapes literal source lookalikes unchanged,including
in approved source positions; decode rejects unescaped transport refs elsewhere
before hydration. Real full-envelope/literal/atomic64-case controls reused.

New executable amendment file is separate17-case bounded review slice (baseline64
retained,not claimed82green). Portable-shaped>100k fixture and real historical audit
diagnostic ensure observed gap addressed. No scanner/registry/slot/cap code yet.


ISO SOURCE RESOLVED by primary:systemcurl defaultverifiedtrust (no-k),one diagnosed
TLS-stack repair; reuse savedXML/json,NOmorefetch. SIX publication2026-09-17,
178codes,47491bytes,SHA25633139b438657d1cee116ba737807ea71d19d6de4b90f799a09c56f0cc6a1b0ff.
Prior source-block notes are historical,not current blocker. Registry version/hash
must match this artifact; is_pricing_currency(code) is membership minusXXX(no
currency)/XTS(testing),which both remain unsupported for real price currency.
Metadata acceptance strengthened to these exact controls,17casecount unchanged;
registry/scanner/slot production still gated. No further source fetch/probe.
