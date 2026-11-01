# Documentary skeleton — G2 ready after executable reds

G1 PASS. No production stubs/business logic. Components follow independent G2.

- `_normalization.Normalizer.money` retains existing parameters and adds optional
  keyword-only currency:str|None=None,locale:str|None=None. CSS callers pass actual
  explicit context; source selection/conversion outcomes remain owner of support.
  Shared private monetary conversion returns finite Decimal or rejection; no
  guessing USD/PKR from missing inputs. Zero accepted with diagnostic reason.
- `_normalize` adapters use supported currency or empty string; constructor defaults
  unchanged. Explicit conflicts unsupported, actual field paths retained.
- `_compact_catalog.CompactLimits` frozen limits: max_wire_bytes=33554432,
  max_expanded_bytes=33554432,max_nodes=100000,max_depth=64,max_records=1000.
  Per-call limits may narrow,not enlarge ceilings.
- `_compact_catalog.encode_compact_catalog(data:dict,*,limits:CompactLimits=...) -> bytes`
  takes existing JSON-compatible extraction_data; emits canonical UTF8 catalog-v1.
- `_compact_catalog.decode_compact_catalog(payload:bytes,*,limits:CompactLimits=...) -> dict`
  validates duplicate keys,digests,wire and logical expanded budgets before hydration;
  returns equivalent legacy data. ValueError for invalid/over-budget inputs; CLI
  translates to existing E_USAGE,never partial fabricated records.
- Wire shape: {schema_version:'catalog-1',data:<catalog>,captures:{sha256:<capture>}};
  capture references are exact {$capture_ref:sha256} objects at captured provenance
  positions. Canonical hash uses sorted keys,ensure_asciiFalse,compact separators,
  allow_nanFalse. Capture-table nested transport references forbidden; no external
  resolution/network. Raw source values that resemble reserved tags require escaping
  at encoder,not interpretation as a network/location reference.
- `_cli_data.read_json_file` enforces32MiB wire/node/depth ceilings and recognizes
  opt-in catalog envelope before existing record projection. Default legacy formats
  preserved; `extract --compact` calls codec before atomic write/stdout. Compact
  validation error leaves existing output target untouched.

Dependency: pure codec/limits -> existing portable/evidence JSON shapes; CLI
consumes it,not inverse. No browser/model imports. Exact source facts/identity/order
must survive roundtrip; hashing does not create observed support. No new defaults
on Product/Variant constructors. Test fixtures use actual capture/normalize/portable
paths and labelled synthetic transport payloads,not a duplicate implementation.

G2 repaired consumer seams: full schema1.0 CLI envelope contains catalog-1 data;
read_json_file/products_from_value must accept/decode this nested compact form
before canonical product projection,then existing load_catalog/downstream commands
reuse it. No caller-required direct decode workaround. Decoder/encoder distinguish
literal source $capture_ref maps from transport tags by escaping reserved source
values; actual captured provenance must roundtrip exactly. Atomic replacement
failure preserves target and cleans temporary output; input validation precedes
output creation. Currency conversion is shared across every dispatcher branch;
record actual source pointers for lowercase normalization/conflict/rejection.

## Amendment skeleton — independent G2/G3 required, not implemented

New pure `_bounded_json.JSONShape(nodes:int,keys:int,tokens:int,depth:int)` and
`preflight_catalog_json(payload:bytes,*,max_bytes=33554432,max_nodes=1000000,
max_tokens=2000000,max_depth=64)->JSONShape` as exact contract in amendment.
Scanner reused by legacy/compact consumers BEFORE full JSON decoder; byte/value/
key/depth bounds precede allocation,strict JSON decoder still authoritative for
syntax. CompactLimit's catalog nodes and _portable.validate_tree bound align1M;
expanded cost remains before hydration. Separate catalog allowances from native
category payload limits; Woo tree default uses valid native limits,not global
catalog MAX_BYTES. No enlargement of native's8MiB hard ceiling.

New `_currencies` bundled offline registry defines REGISTRY_SOURCE,REGISTRY_VERSION,
REGISTRY_SHA256 and currency membership; verified official source required before
production. Current ISO fetch blocked (iso4217-source.json),no guessed table/version.
Normalizer.currency reuses registry for membership as well as source conflict and
uppercase handling. No network at normalization time.

Codec ref admission receives traversal path: only documented capture/provenance
slots permitted; escaped literal source dictionaries remain data even in a capture
body. Validate slot before reference expansion. Existing canonical hashing/escape
and cost model reused,not a second serializer. New17-case amendment +historical
actual-audit diagnostic,baseline64 unchanged; no new code until reviewed gates.


ISO SOURCE RESOLVED by primary:systemcurl defaultverifiedtrust (no-k),one diagnosed
TLS-stack repair; reuse savedXML/json,NOmorefetch. SIX publication2026-09-17,
178codes,47491bytes,SHA25633139b438657d1cee116ba737807ea71d19d6de4b90f799a09c56f0cc6a1b0ff.
Prior source-block notes are historical,not current blocker. Registry version/hash
must match this artifact; is_pricing_currency(code) is membership minusXXX(no
currency)/XTS(testing),which both remain unsupported for real price currency.
Metadata acceptance strengthened to these exact controls,17casecount unchanged;
registry/scanner/slot production still gated. No further source fetch/probe.

Last G2 direct-entry proof: decode_compact_catalog must invoke actual lexical
preflight BEFORE json.loads,independently of read_json_file integration. New
amendment acceptance18cases; last test instruments full decoder boundary and fails
if dense wire reaches allocation. No scanner/registry/slot production added.
