# Implementation plan — issue #23

## Constitution check

Opt-in Python report supplements preserved legacy APIs/models/feeds. Reuse MIT
local SQLite, identity, portable typed values and trust resolution. Evidence
supports every observed field; unknown/default scalars never become facts.
Sequential delegates, <=3 live requests, no local model or new paid dependency.

## Reviewed interface

`reliable_changes(domain, *, previous_snapshot_id, current_snapshot_id,
recheck_snapshot_id=None, db_path=DEFAULT_DB_PATH) -> dict`.
Policy version reliable-change-v1 is fixed in first release; no ambiguous mutable
caller thresholds. Explicit snapshot IDs avoid inferred latest-pair races.

Dictionary report with explicit typed-codec serialization; avoid new public dataclasses.
Nested schema sketch: EvidenceReference(snapshot_id,
record_key, observation_id, evidence_ids); ValueSide(state observed/absent/unknown,
value, references, coverage metadata); ReliableChange(candidate_id/event_id,
kind field_changed/product_added/product_removed, state confirmed/pending/rejected,
reason, canonical IDs, field_path, old/new sides, optional recheck side).
ReliableChangeReport(report_id, policy_version, supplier, snapshot IDs,
status/reason, candidates, events, new_events, diagnostics). events contains only
confirmed candidates; new_events is a per-invocation publication subset. Exact
serialization/schema keys belong in skeleton.md after G1, not implementation.

One new narrow monitor module owns evaluation + ledger transaction; existing
connection-owned loader extraction and separation of bounded schema DDL from legacy
backfill belong in monitor/evidence.py. Reliable comparisons require persisted
selected identities and never migrate unrelated history. Reuse scoped
identity, resolve_fields, typed encoding and equivalence. Additive versioned
ledger has unique supplier/pair/policy key. Freeze diagnostic and selected facts
at first evaluation; report returned as detached dictionaries. Mutable pending outcomes only change through valid explicit
recheck. Persist values/qualified references, not duplicate source payloads.

## Gates and verification

G1/G2/G3 and final independent review passed; artifact digests and findings are
recorded in reviews.md. Behavior/test design preceded breakdown/research; code
skeleton and executable red tests preceded component review and implementation.
Child issues #45, #46 and #47 were linked before production implementation.
Definitions/limits remain in research.md, scenario design in test-design.md.

Existing baseline: 39 passed. Designed acceptance: initial 87 red plus 3 health
delta red; final-review regression red found two contract bugs. Final checks:
95 focused and 726 full-suite tests passed, synthetic e2e passed. Bounded live
pipeline smoke passed with 2 requests; actual live commercial-change validation
is inconclusive because captures had equal values. Final code replayed saved
live captures offline, without further requests. See verification.md for logs.
Session counters unavailable; no quota percentage inferred.
