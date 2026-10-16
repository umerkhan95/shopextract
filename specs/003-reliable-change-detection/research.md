# Bounded production research — 2026-10-16

Scope: existing repository contracts, no external/current factual claims. No
network, inference or new code. Sources inspected once; reuse this summary.

| Question | Local source / finding | Decision |
| --- | --- | --- |
| Existing compatibility seam? | monitor/changes.py exposes legacy changes/price_history; watch.py imports legacy changes | New monitor/reliable.py and explicit reliable_changes export; do not change existing watchers/default feed/CLI behavior |
| Matching ownership? | identity.py identifies persistent products and variants, rejects duplicate anchors; title bridge is conservative legacy migration | Reuse existing persisted canonical IDs, validate uniqueness. No new title matching or identity algorithm. Missing selected canonical identity is an explicit migration-required error; do not migrate history inside this API |
| Supported field source? | _resolution.py resolve_fields applies authority/freshness; resolution_references and trust_view aggregate competing evidence | Resolve graph at snapshot.created_at; select resolution.selected_observation_id and ONLY that observation's evidence_ids for event side refs. Preserve other candidates separately as diagnostics; never treat aggregated trust_view evidence as selected support |
| Time correctness? | snapshots created_at is UTC capture/persist time; source evidence has its own observed_at; fixture NOW elsewhere may differ | Fixtures set snapshot created_at to fixed T0/T1/T2 after save. Source evidence times <= respective capture time within policy window. Future/stale boundary fixtures intentional, never accidentally Jan evidence under October capture |
| Atomic multi-snapshot evidence? | evidence.load_snapshot opens a connection and _get_connection initializes schemas in a write transaction | Extract existing body into private connection-owned loader, public load_snapshot retains signature. Reliable entry opens one initialize=False connection, BEGIN IMMEDIATE, runs bounded DDL only (extract evidence schema DDL from legacy backfill, preserving existing default backfill for callers), reads metadata + all snapshots + evidence through same connection; persist ledger then commit. Never call public load_snapshot/get_evidence within held write transaction (second initialization could block itself) |
| Race/lock recovery? | snapshot._get_connection sets sqlite timeout/busy_timeout five seconds, FK ON; saves use BEGIN IMMEDIATE | Same bounded transaction policy, unique comparison key and publication state, rollback on any exception. Read <=3 explicitly selected snapshots and their graphs; never invoke migrate_snapshot_identities or legacy backfill. Selected legacy identity-free rows fail explicitly; unrelated history remains untouched. no network or user callbacks in transaction, no implicit retry. Race test uses independent connections, not model processes |
| Storage bounds? | evidence._prepare rejects >16MiB serialized snapshots, product evidence 64KiB, fragment 4KiB | Preserve limits; validate direct snapshot/record lengths before decode. No unbounded history scan. Generated candidates + diagnostics <=10,000, stored report <=16MiB; overflow explicit ValueError/rollback, no truncation. Event serialization uses existing typed encode_value/decode_value, no lossy Decimal float conversion |
| Equivalent normalized values? | _resolution._equivalent_key distinguishes bool/number, handles NFC, mappings/lists conservatively | Reuse helper with narrow internal import rather than copy. Field validators separately enforce price/currency/stock/quantity semantics; parent selected currency qualifies variant price |
| Rechecks/dedup? | No persistent reliable report ledger currently exists | Add versioned additive ledger, frozen report payload + pending state + unique comparison key. Stable candidate ID derives comparison key/entity/field/type; stable event ID derives candidate. Per-call new_events derived atomically from newly confirmed transitions. Pending may recheck, terminal immutable; no exactly-once external delivery claim |
| Report expiry? | evidence._owner_graph reconstructs retained graph plus expiry tombstones; prune_evidence can remove payloads | Initial computation needs retained selected support. Persist selected values/references and outcome, not source payload copy. Replay frozen historical report after pruning; lookup shows expired. Report support means support at computation, never implies permanent retention. No bypass of retention or recomputation changing published events |

## Resolved boundaries and residual limits

Known equal scopes required even for field comparisons; stronger than legacy API
but opt-in explicit. Snapshot order is (created_at, id), so equal timestamps use ID.
An invalid recheck fails whole invocation before schema/ledger changes commit.
Terminal candidates ignore later valid recheck values; history immutable. A new
comparison can represent a later real reversal. A pending unverified recheck may
be retried with a later valid snapshot; record attempted recheck metadata without
publishing. report_id identifies pair/policy, not current invocation.

Catalog completeness cannot establish variant completeness: variant field diffs
supported, variant membership diagnostics only. Removal old product need not have
an observed price; preserve unknown price as unknown, with old identity/presence
and selected available evidence. New presence needs one supported tracked field.
Overlapping manual historical pairs remain separate comparisons; callers wanting
continuous monitoring must supply successive pairs and deduplicate stable IDs.
Public live endpoint availability remains unverified until designed live phase.

G1 correction: price rechecks require supported candidate-matching currency, including inherited parent currency for variants. Equal scalar price with changed/unknown currency remains pending. Add SC12 unrelated-history isolation and SC14 recheck-currency regressions.
