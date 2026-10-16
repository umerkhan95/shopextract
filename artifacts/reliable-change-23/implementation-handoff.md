# Implementation handoff — issue #23

Source files:
- src/shopextract/monitor/reliable.py: bounded opt-in field/membership/recheck engine, typed codec, snapshot-time resolution, selected refs, atomic versioned SQLite report publication and rollback seam.
- src/shopextract/monitor/evidence.py: default-preserving optional backfill flag and connection-owned _load_snapshot extraction.
- src/shopextract/monitor/__init__.py: explicit reliable_changes export.

Checks: acceptance 90 passed (implementation-focused.log); affected acceptance/legacy/evidence/identity/resolution regressions 292 passed (implementation-regression.log). The final focused rerun includes resolution_context diagnostics for competing supported field observations. No test assertions changed by implementer. Captures bounded before graph/portable decode; existing retained fragment/product budgets rechecked. Health complete requires flag true and empty incompleteness reasons. No migration, backfill, history scan, network recheck, callback, or new dependency in API.

Review note: product membership presence side uses unknown value plus selected captured refs and coverage, avoiding invented scalar values; absence uses explicit absent. Reviewer should confirm this presentation against dictionary contract.

Limits: no live run performed by implementer; coordinator owns live/full-suite/docs and final independent review. Session token counters unavailable. Initial mistaken uv run triggered downloads/resolution; process stopped, generated uv.lock removed, tests use existing .venv/bin/python + PYTHONPATH=src. Existing dependency RequestsDependencyWarning persists. No commits, pushes, issue edits or child agents.
