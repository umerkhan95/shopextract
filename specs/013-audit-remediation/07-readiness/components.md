# Readiness components — G3 proposal

`_readiness.readiness_report` is a pure bounded adapter over existing source_record,
Google assessment and currency/identifier validators. It uses typed Products when
available, preserving contracts; legacy explicit dictionaries remain supplied facts.
No extraction, clients, API keys, model or provider imports. Target metadata is a
literal registry pinned to saved primary sources and official-source-check.json.
Dates mean retrieval dates; source maturity and profile scope remain explicit.

Google reuses the limited catalog subset. Schema coverage inspects five modeled
areas and separates ProductGroup/variants without inherited group offers. OpenAI
maps the stable nine basic fields, accepts unknown availability, requires currency
and explicit seller context, and marks variant/grouping unassessed when present.
ACP always returns protocol-unassessed with RFCProposal maturity. `ready` applies
only to the named profile; merchant approval, ads and checkout remain unassessed.

The CLI loads bounded catalogs/context, validates the closed target/context fields,
and exposes source metadata and deterministic item ordering. The existing response
envelope owns operation success; --strict uses partial exit3 with the report retained.
Invalid arguments are usage errors. Record/variant report caps are explicit and
produce needs_context diagnostics rather than silent truncation. No mutable cache.

Twenty-four real CLI/helper cases cover positive and negative profiles, source
support, protocol limitations, deterministic order and zero-network boundaries.
User documentation/help must explain profile scope and link the official stable
OpenAI reference; no approval/certification claims or paid dependency requirements.

G3 numeric lifecycle: preflight caps top records1000, aggregate variant nodes100,
root-depth0/max8 and active-path cycles before profile evaluation. Whole preflight
failure emits no items, ready=false and exact omitted top-record count, with a
named needs_context diagnostic. CLI existing over1000 rejection remains E_USAGE.
Known scalar field bytes cap8192; aggregate profile projection plus report framing
has8MiB budget. Reports select only bounded profile fields, never raw_data/contracts.
A conservative preflight projection-byte estimate may reject oversized reports;
output accounting also reserves framing before append. No unbounded sorting/copy.

Resource clarification: aggregate report/projection bytes mean JSON-encoded UTF8
including escaping and framing,not only raw source-string lengths. Estimate this
before assessment/materialization and keep emitted report within8MiB; overflow
returns explicit needs_context/no assessed items under the reviewed contract.

Compatibility amendment (authoritative before code): source preflight cap1000
aggregate variant nodes/depth64,not100/depth8. Raw provenance is not an assessed
variant graph. Schema assessment separately caps100variantnodes/depth8,keeps top
reports and explicit omitted coverage. Native25/265 shallowvariant catalog passes
input preflight regardless original provenance depth11. OpenAI grouping remains
unassessed without discarding base items. No larger wire/node budgets introduced.
