# #38 portability skeleton and handoff

Skeleton only; every API intentionally raises NotImplementedError. No existing
export defaults, public exports or persistence behavior changed.

- `src/shopextract/_portable.py`: `product_to_record` / `product_from_record`;
  one versioned codec shared by export and SQLite. Typed product data and aligned
  variant attachments remain separate from already encoded TrustContract maps.
- `src/shopextract/export/_bundle.py`: create/load dictionary bundle, read/write
  bounded JSON files, create/verify digest-bound feed sidecars. Envelope versions
  and bounded validation are explicit; stable identity/fallback rules documented
  at interface level, with collision handling required before implementation.
- Implementer integration outside these owned files: expose opt-in public APIs;
  wire SQLite to the shared record codec; add optional CSV/feed companion paths;
  preserve default output bytes; add scoped evidence references to match reports.

Required tests: nested conflicting Product/Variant semantic round trip; Decimal
`1.2300`, UTC microseconds, literal `$type` maps; full contract equality; legacy
missing/unsupported and expired evidence; duplicate keys/IDs, unknown versions,
invalid tags/platform/model fields, naive/nonfinite values, depth/size limits,
misaligned variants, dangling references and retained pointer errors. Sidecars:
verify every row, duplicate marketplace IDs, wrong digest and mapping corruption.
Run affected export/evidence/monitor/report regressions with offline fixtures.

Research basis: `research-portability.md`; no claim of PROV/RO-Crate/JCS/BagIt
conformance. Retained content travels within existing capture caps; remote-only
URLs do not become locally archived evidence. Import does not refresh evidence
or turn raw rule/model scores into validated confidence.

## Separate research review (completed after skeleton creation)

Reviewed portability, persistence and verification reports together. Confirmed
codec reuse, dynamic attachments, separate versioning, typed semantic comparisons,
strict loading and default feed compatibility. Added explicit scoped reference
contract (`product/N`, `product/N/variant/M`) alongside bundle stable record keys;
SQLite owner location does not replace portable identity. Added retention warning
to shared codec: missing payload tombstones cannot become malformed Evidence or
revived observations. Implementer must integrate storage availability with trust
inspection and exported reports; historical freshness and retention differ.

Cross-owner APIs agreed by parent: persistence `save_snapshot`/`load_snapshot`
will share product record codec; `get_evidence` accepts snapshot_id and record_key
scope. #39 must use final public APIs and compare every factual path plus actual
retrievability. Tests listed above are planned, not executed. Skeleton validation:
`python3 -m py_compile src/shopextract/_portable.py src/shopextract/export/_bundle.py`
passed. No implementation tests are claimed.
