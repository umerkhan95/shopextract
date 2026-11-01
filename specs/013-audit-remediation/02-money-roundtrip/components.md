# Money/roundtrip components — G3 ready

G2 PASS prerequisite; documentation only, no02 business code. Independent reviewer
next. Currency normalization and compact transport are separate bounded substeps.

| Owner | Reuse / consumers | Boundary and error contract |
| --- | --- | --- |
| Normalizer / conversion outcomes | Existing selection,source paths,accepted/rejected observations; every native/schema/OG/CSS/feed branch | Shared contextual money/currency conversion; missing/invalid/conflicting currency unsupported empty string,constructor defaults preserved; accepted zero diagnostic separate from eligibility |
| Pure compact codec / CompactLimits | Existing JSON-compatible extraction_data and portable capture/evidence values | Canonical hashing,explicit reference encoding/escaping,duplicate/hash validation,wire AND per-occurrence expanded budgets before hydration; ValueError on malformed/over-limit input |
| Existing capture/portable identity | Actual captured source values,Decimal encoding,variant IDs,evidence and ordering | Codec roundtrip preserves exact values/support; digest does not confer factual authority; literal reserved source maps escaped and recovered unchanged |
| CLI data consumer | Existing read_json_file/products_from_value/load_catalog | Recognize full response/nested compact envelope,validate before product projection; same source accepted by downstream analyze/export; existing E_USAGE mapping |
| CLI extraction output | Existing make_response and atomic_json | --compact opt-in only; schema1.0 outer envelope preserved; encoding/validation before replacement; filesystem failure cleans temp and preserves original target |

Codec state is per call: immutable limits,local capture table and precomputed cost
metadata; no global cache,network,worker or recursion through unvalidated refs.
Count expanded occurrences even if shared objects avoid copies; serialization also
obeys expanded bound. Limits may narrow,never exceed32MiB/100000nodes/depth64/
1000records. Reject nested transport references/cycles/dangling/duplicate digests;
source lookalikes are escaped data,not transport. Hash before reconstruction.

No duplicated destination validator or new identity scheme. Monetary errors remain
inspectable conversion outcomes; CLI/API field transport unchanged except explicit
unsupported normalized currency and opt-in compact data. Shared caller context
owns warnings; no parser guesses merchant country or manufacturer identifiers.
Components/G3 apply only to reviewed02 contracts; no implementation yet.

## Amendment components — G3 requested after amendment G2 PASS

- `_bounded_json` owns pure UTF8 lexical preflight/JSONShape. Shared legacy catalog
  reader and direct compact decoder call it BEFORE full decoder. Bounded values,
  keys/tokens,bytes/depth are distinct; strict json.loads remains grammar authority.
- Catalog allowance1M nodes/32MiB is explicit,not an increase of protected native
  limits. Reuse portable validation with existing normal default or explicit catalog
  allowance only where necessary. Native Woo tree retains valid native defaults;
  category options do not derive transport budget from catalog byte constant.
- `_currencies` bundles verified saved SIX publication2026-09-17 and sourceSHA;
  immutable pricing membership excludesXXX/XTS. No runtime network/XML dependency.
  Existing currency outcome owner reuses membership without overriding conflict
  handling or source paths. Raw invalid source code remains inspectable.
- Existing compact codec owns approved provenance-path grammar plus escaping.
  Reject unescaped reference outside capture slots before hydration; literal source
  maps stay escaped values. Existing hash/cost model reused,expanded occurrences
  counted under1M/32MiB/depth64 before reconstruction. No second serializer/cache.
- CLI reader scopes enlarged catalog allowance; existing helpers still own record
  projection/typed errors/atomic output. Preflight and downstream failures never
  replace target. Actual audit final diagnostic must pass analyzer+CSV-sidecar
  reload preserving Decimal/variants/evidence; reader-only pass insufficient.

State is per-call bounded counters/table plus immutable bundled currency data.
No added threads/processes or inference. ValueError/CLI E_USAGE error projection
unchanged. Amendment82 combined acceptance cases (64baseline+18new),oneworker,
120s focused ceilings; full/live remain later gates. No amendment production yet.

The original100000-node paragraph above records the pre-amendment component
contract; this reviewed amendment supersedes it for catalog paths only. The final
amendment executable inventory is18cases plus64baseline,not17.
