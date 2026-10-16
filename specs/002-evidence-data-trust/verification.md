# Verification — issue #34

Baseline: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_models.py -q`
Result: 26 passed. Initial invocation without PYTHONPATH could not import the
checkout; corrected once with explicit src path. No inference or crawl required.
Session token counters are not exposed by the available tools; no quota estimate
is inferred. Scope is bounded to contracts, offline fixtures and compatibility.

## Final verification

Command: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_evidence_contracts.py tests/test_models.py tests/test_normalize.py tests/test_identity_matching.py tests/test_export.py tests/test_snapshot_completeness.py tests/test_extract.py tests/test_monitor.py tests/test_compare.py tests/test_quality.py -q`
Result: **241 passed**, 0.91 seconds. `git diff --check` passed.

Contract checks include missing/zero/false, nested field/collection coverage, escaped
pointers, score semantics, Decimal/UTC/tag collision round trips, unavailable states,
malformed schema/IDs/time/state/reference rejection, retained alternatives, mutation
validation and legacy constructor/asdict/canonical identity compatibility.

Spec/plan/tasks consistency review: all four #34 acceptance scenarios map to named
fixtures; the field matrix accounts for every current Product/Variant dataclass field.
FR-01/02/06 contract deliverables are complete; FR-03/04/05/07 implementations and
SC-01–04 end-to-end proof remain unchecked in dependent tickets. Constitution and
three local planning templates initialized without user configuration changes.

Fixture correction: normalize takes a dict, not a list. The existing non-product gate
requires a positive price, image or identifier; using a SKU permits the missing-price
fixture while retaining compatibility. The initial fixture failures were corrected;
no normalizer behavior was changed.

Limitations: source capture authenticity/calibration artifacts are caller responsibilities;
production capture byte limits, automatic extractor coverage, SQLite evidence storage,
retention, source precedence and full Product bundle export await #35–#39. A pre-existing
requests dependency-version warning appears at startup; it did not affect the checks.
No local inference, live crawl, parallel agent, install or broad research was performed.
Actual session token counters are unavailable; no fixed quota claim is made.

## P2 review follow-up

Both findings reproduced with targeted fixtures before changing production code:
9 failures exposed Enum codec bypasses and conflicting-state validated confidence.
The codec now recursively encodes Enum values before other type handling, preserving
Decimal/UTC tagging, raw-map escaping and rejection of nonfinite/unsupported values.
Validated confidence is accepted only for observed support; conflicting and other
unavailable states reject it on construction and after mutation during serialization.

Added 12 regression cases under `test_enum_values_use_recursive_codec`,
`test_enum_values_cannot_bypass_validation`, and
`test_only_observed_state_accepts_validated_confidence`.
The same affected-suite command above now passes **253 tests**, 0.98 seconds.
`git diff --check` passed. Public contract wording updated; component boundaries
unchanged. No agents or inference processes launched. Actual session token counters
remain unavailable.
