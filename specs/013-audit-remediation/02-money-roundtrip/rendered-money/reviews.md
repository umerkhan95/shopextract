# Rendered-money independent review

## G1 — PASS

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed design before breakdown,
source discrepancy and existing shared Decimal/ISO contracts. No probes/tests/
network or author implementation. Exact precision/large-number/zero/PKR grouping
cases, ambiguous $/yen, supported context/conflict, malformed/negative and actual
browser/policy controls address distinct risks. Reusing conversion outcomes and
pinned registry rather than a second float/format parser is appropriate; no
product-admission weakening,constructor change or currency-from-domain assumption.

G2 must preserve raw candidate/excerpt and exact transformations: derived amount
is not an unlabelled direct source scalar. Exercise actual caller context/conflict
propagation,including explicit price0 versus a competing nonzero fallback and
explicit metadata/context code conflicting with rendered text. Use source presence
rather than `or` when zero is a supported monetary input. Existing supported
EUR/USD/GBP and ambiguous-symbol policy cases stay controls. These refine existing
zero/conflict requirements,not a new currency inference feature.

G2 named extraction/context interfaces plus executable intended-red acceptance
next; G3 and implementation/focused/full-driver/live/final gates pending.16-case
ceiling and one-worker/time bounds remain; no all-ISO-locale promise inferred.

## Reviewed SHA-256

```json
{
  "spec.md": "dc73ae3b8e0fbca9b353500e8a02e2c782c4bb86afa70d49e038ebfddc937231",
  "test-design.md": "7cb5f8f663a2b6027cf890f813b53aabd61604a6d436964d5b737e36b8782071",
  "tasks.md": "b371b7da47f0cf3b40f98bbef75ff5b77561bed9fd6f1b5d5896030406cbd614",
  "research.md": "efe6a439c6885f1390afdcd03b2d9862bf825888529f34501969de408e9ef04c",
  "plan.md": "470c79d1b268f97567001dc83c9de7c8c885567774918e4743a6308d2fa105f7"
}
```

## G2 — CHANGES REQUIRED, executable contract coverage

Reviewer `/root/audit_plan_review`,2026-11-01. Inspected documentary signatures,
real-path tests and saved bounded initial-red results. No source/tests/network/
probes. Initial small complete set is honestly labelled initial smoke,not a prior
single-case run.

Blocking SC-RM4 coverage gap: actual browser cases cover12.50 and0 without any
source-support assertion; the promised actual browser KWD1.234 exact amount and
source-supported currency/excerpt/transformation is absent. Add one designed
crawler-boundary precision fixture through actual normalization/evidence,assert
exact Decimal and full source pointer/value/excerpt; adjust small case ceiling
explicitly if needed. Direct md.extract precision alone cannot detect caller
rounding/support loss. Other16cases meaningfully exercise malformed/negative,
symbol ambiguity,actual CAD conflict,metadatazero presence and policy admission.
Named optional context interfaces and shared Decimal/ISO dependency are suitable.
No components/implementation before repaired G2.

Required additions must be designed before tests/repair,stay sequential/bounded,
retain existing assertions and save focused intended-red/control evidence. No
full-driver/live/final gate waived; actual audit export timeout remains unrelated
open verification.

```json
{
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/skeleton.md": "ec220361852c9ddf2561a49f219455c2c1bc4c561e7a30ba0a0a55451db45e41",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/spec.md": "dc73ae3b8e0fbca9b353500e8a02e2c782c4bb86afa70d49e038ebfddc937231",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/test-design.md": "7cb5f8f663a2b6027cf890f813b53aabd61604a6d436964d5b737e36b8782071",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/verification.md": "6cab6104afd182a9f15953c9718efce47fea47aa39ba37672b1385bf8766acf2",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/red.log": "5ddda64f3aa284363134ef3ee5ac6a55a17864a1e8297c818a317d3ac375776f",
  "tests/test_rendered_money.py": "6dfb7a84228866ca8ca1b9a4cb0fac281813796509a17d789a74cfa07ea93a20"
}
```

## G2 repair re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed designed additions and
actual focused intended-red/control evidence; no new probes/tests/network or
author source edits. Supersedes previous changes-required G2 for hashes below.

Rendered17 cases now include actual known200 browserKWD1.234 through shared
normalization plus observed price/currency evidence tied to original URL and
original KWD excerpt. This resolves prior helper-only precision/support gap.
Context/conflict/metadatazero/policy/largeDecimal controls remain intact.

Two-case smoke saved before combined44-case bounded run:33 intended failures/
11controls. Tests still exercise actual transport/normalization/browser/API/CLI
mechanisms; missing new interface/flag failure may precede later assertions,so
those must actually execute in green verification. No full44green claim.
Components/G3 next; no production,full-driver/live/final approval inferred. Actual
audit export timeout remains open separately.

```json
{
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/spec.md": "dc73ae3b8e0fbca9b353500e8a02e2c782c4bb86afa70d49e038ebfddc937231",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/test-design.md": "4f10a91e7f2fb8b2ea2a8610272bf73d2e144fdf9ff4116fd11048aa2c9efaee",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/skeleton.md": "ec220361852c9ddf2561a49f219455c2c1bc4c561e7a30ba0a0a55451db45e41",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/verification.md": "e8addd3f460588a5a17cd23bdaba1df6d21b8279042cd2ae5a694d74cc02d719",
  "tests/test_rendered_money.py": "bf071c77469161a8a071ab49280f8daaad0e26b08b9a698a8ae37d7ff0a315f2",
  "specs/013-audit-remediation/04-adapter-coverage/repair-red.log": "cd7641b9943f450aa7d1bf39f167ef804c07eeb2a69348bea33b0b0047fc7dcc",
  "specs/013-audit-remediation/04-adapter-coverage/repair-smoke.log": "2d8be81f7c55083a97a6fa2d6db676f9358f718da9da5c1f0434ffa8c0ac02e5"
}
```

## G3 — PASS, shared components and ownership

Reviewer `/root/audit_plan_review`,2026-11-01; no source implementation, probes/
tests/network. Reviewed against latest approved executable G2 contracts.

Tokenizer discovery delegates monetary semantics to shared Decimal/registry;
whole-token validation,exactzero/context authority/conflict and actual rendered
capture remain separate responsibilities. Unified owns admission/unique owner and
missing-field merge; no constructor/default or alternate pricing engine. Minor
reviewer wording clarification includes captured structured-offer as well as
metadata context,as existing G2 skeleton requires; do not discard competing
authorities or infer context from generic page text/domain.

Implementation may proceed sequentially against accepted tests; functional/full-
driver/live/final remain pending. Original actualaudit export timeout stays open.
No future verdict or observed-source fidelity is assumed from documentary design.

```json
{
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/components.md": "49c175f353da76f27d6358429c936a4c39dab04e921c18fa0374b59b4c73aea9",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/skeleton.md": "ec220361852c9ddf2561a49f219455c2c1bc4c561e7a30ba0a0a55451db45e41",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/spec.md": "dc73ae3b8e0fbca9b353500e8a02e2c782c4bb86afa70d49e038ebfddc937231",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/test-design.md": "4f10a91e7f2fb8b2ea2a8610272bf73d2e144fdf9ff4116fd11048aa2c9efaee",
  "tests/test_rendered_money.py": "bf071c77469161a8a071ab49280f8daaad0e26b08b9a698a8ae37d7ff0a315f2"
}
```

## Functional review — CHANGES REQUIRED, authority/token interactions

Reviewer `/root/audit_plan_review`,2026-11-01. Inspected actual token/Decimal/ISO
implementation and browser consumer plus saved108pass scope. No new probes/tests/
network/source edits. Exact Decimal replaces float,valid KWD/large integer/zero
mechanisms and actual source support are meaningful improvements. Fixture URL and
retained source_excerpt correction is honest,not a precision expectation weakened.
Three uncovered interactions block functional PASS:

| Finding | Severity | Required disposition |
| --- | --- | --- |
| _SYMBOL_TO_CODE still maps bare£ toGBP (and bare₩ toKRW) without captured authority; explicit FKP/KPW context then becomes a false conflict | Blocking ambiguous-symbol authority | Apply existing ambiguous-symbol rule generically,not only dollar/yen. Predesign bare/context/explicitISO controls for pound and won; no inferred pricing currency from bare ambiguous symbol. Preserve explicitGBP/USD/EUR and known-context positives. |
| _PRICE_RE amount stops at whitespace; e.g. EUR1 234,50 is matched as EUR1 and accepted before examining remaining numeric chunk | Blocking magnitude/token regression | Preserve supported locale-aware whitespace grouping or reject the whole ambiguous/malformed token; never accept a numeric prefix as full price. Prior regex recognized grouped spaces. Add exact grouped-space and malformed-space controls through shared conversion/actual parser,including nonbreaking-space if supported explicitly. |
| Browser detects conflicting authorities but leaves an existing structured offer.priceCurrency unchanged; writes only when field missing | Blocking conflict projection | Add Product with preexistingCAD offer plus metadataUSD/explicit conflicting rendered code. Outcome must retain original competing source values but emit unresolved/unsupported currency with diagnostic,not a single observedCAD scalar. Existing bare-offer conflict fixture cannot catch this branch. |

A minor efficiency issue is repeated markdown extraction before owner/context,then
with context and again without; reviewed components intend one candidate discovery
per result. Reuse extracted candidate/authority data where practical without a new
parser framework; do not weaken authority/precision controls for speed.

Design exact cases before repair. Keep additions bounded/sequential and save smoke
then affected results; no broad source/model/test sweep. Existing108pass is scoped
evidence,not a final/all-ambiguity verdict. Full-driver/live and actualaudit export
timeout remain pending separately.

```json
{
  "src/shopextract/extractors/_markdown_price.py": "3c26040f1245d645cca89c12040d75af57bdb0ca1e7205294d198d4c060b6f0b",
  "src/shopextract/extractors/unified.py": "f0ec441b8c1bc34ff927c976fcc3711c061df2f9cff47adde80d55ad6e9a9428",
  "tests/test_rendered_money.py": "07c26569fec041790ebb8ea316f812e6732b46ef359717b707527f4b5c7bf511",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/spec.md": "dc73ae3b8e0fbca9b353500e8a02e2c782c4bb86afa70d49e038ebfddc937231",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/components.md": "49c175f353da76f27d6358429c936a4c39dab04e921c18fa0374b59b4c73aea9",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/verification.md": "04df6441b07aabf45a7a5cc686f5988f562c395bf316741d73bcdaeb2bb0cbad",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/green.log": "03717583dae4332857e2160dabf97efd5a1939ac2c0bd33a31148f6d5be1e882"
}
```

## Functional seven-case repair re-review — CHANGES REQUIRED, OG conflict projection

Reviewer `/root/audit_plan_review`,2026-11-01. Inspected revised code and7added
case expectations with saved179pass. No new probes/tests/network/source edits.
Bare pound/won authority and whole-space-group magnitude findings are resolved
in designed cases. Existing schema-offer conflict clears scalar while original
capture stays intact; price/source support controls pass.

The same currency-conflict blocker remains in separately implemented OG branch:
when owner is OG,existing product:price:currency/og:price:currency is never cleared
on conflicting authority; code only fills a missing value. A pure OG product CAD
plus captured metadata USD can remain observedCAD despite conflict diagnostic.
Add one exact OG owner/capture-retention case and apply unresolved currency
projection there too; schema-only repair does not establish dispatcher parity.

Also source-authority comparisons use raw set/string equality after shared
Normalizer correctly canonicalizes codes. Agreed usd versusUSD can become a false
conflict/blank scalar via len(set(authorities)) or explicit!=context. Canonicalize
valid codes consistently before authority comparison (retain original source
values),and add one lowercase-agreement control. This reiterates accepted source
uppercase semantics rather than adding another inference policy.

Repeated candidate discovery remains a documented minor efficiency limitation,
not a falsely passed single-parse guarantee. Keep next repair focused/bounded;
179pass is scoped saved coverage,not final dispatcher/conflict completion.
Full-driver/live and actualaudit export timeout remain open.

```json
{
  "src/shopextract/extractors/_markdown_price.py": "41b6e4ab3979ca5a7eee133e50a73f09108f303bbbb8f412e0d5d3357f48b5e8",
  "src/shopextract/extractors/unified.py": "de5db1c9881ce418a9bc2fdd438313fd00dfcd80eb93b15e78e012ec58071f76",
  "src/shopextract/_normalization.py": "49e65c22b52a0537f0175f6690c468f95024f485a4bcb4e62336d6258133fdd9",
  "tests/test_rendered_money.py": "85403e12c99aac0e9b80d79eeed8dbe93f4d15ead332f61f61c3e167ac5e7f2e",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/functional-green.log": "db2cb342ddac8b8b6dbcba50557c4a3b317580cf8521b9d19c90db5bea6ce5e5",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/verification.md": "44e1fb21ee74304ae09074077d3bf166ed5deb6a8bab69d085e6bd0503318a06"
}
```

## Focused OG/canonical-authority functional re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01; inspected two designed added
cases,actual repair and saved2red/78green evidence. No probes/tests/network/source
edits by reviewer. Prior OG conflict and lowercase-agreement blockers resolved:
OG owned currencies clear on unresolved authority,original capture retainsCAD;
source authority strings canonicalize before equality/uniqueness so usd/USD
agreement preservesUSD without false conflict. Existing schema/OG zero/ownership,
ambiguous symbols,whole-token and precision controls remain in focused set.

Functional PASS for reviewed rendered-money contract under stated cases. Current
26rendered+52HTML=78pass; prior179pass is historical still-applicable coverage,
not a new181-case run. Repeated candidate discovery remains minor documented
efficiency limitation,not a single-parse guarantee. No new scope/probe expansion.

Full-driver/live/final and actualaudit export/sidecar timeout remain open. This
focused functional pass does not certify full audit completion or unlimited locale
coverage. Author may proceed to next independently gated adapter substep.

```json
{
  "src/shopextract/extractors/unified.py": "38e36c6c72c3bfcbe4fa42e02a7ee8584c4b13664c41c241093fa513c9c1c84e",
  "src/shopextract/extractors/_markdown_price.py": "41b6e4ab3979ca5a7eee133e50a73f09108f303bbbb8f412e0d5d3357f48b5e8",
  "src/shopextract/_normalization.py": "49e65c22b52a0537f0175f6690c468f95024f485a4bcb4e62336d6258133fdd9",
  "tests/test_rendered_money.py": "ab9a87e56dbe47eb27621519f2fdb107231ad591096a6a164140ca6ff339f444",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/og-red.log": "03022f90c8ec6f1f25dbbfb6c2e15275251129a8233380e87da1004ba1e2cf1e",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/og-green.log": "e6b2842087d526285f4ead4b78ca89304f2cd831297c946eeabdd91469936df3",
  "specs/013-audit-remediation/02-money-roundtrip/rendered-money/verification.md": "d92a9dce9279d0cc554c60bb60c81e74bbc16a867d2d9918c70e7fbaf4530fbd"
}
```
