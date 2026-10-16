# #39 bounded offline acceptance results

2026-10-16; Python 3.10 in repository `.venv`; no network/model/credentials.

- Small fixture execution first: feed zero/false observed, missing-price unsupported,
  nested price Decimal 1.2300, manufacturer attribute winner blue, restored GTIN.
- `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_evidence_trust_e2e.py`:
  **8 passed in 3.47s**. Actual names/requirement map is in shared tasks.md.
- `PYTHONPATH=src .venv/bin/python examples/evidence_trust.py --output-dir /tmp/shopextract-trust-20261016-39`:
  success; saved `evidence.db`, `evidence-bundle.json`, `report.json` there.
- Report: fixed UTC `2026-10-16T12:00:00.123456+00:00`; 81 Product/standalone
  Variant factual paths; observed 25, unknown 9, unsupported 47; all 25 observed
  paths dereferenced retained support and scoped storage lookups. Product paths
  include nested fields and standalone Variant scopes are deliberately counted
  separately. Counts are fixture state/retrieval coverage, not accuracy.

First integration run identified unsupported demo metadata keys, optional empty
variant-availability attachment mismatch, and a test expecting expiry on a fixture
that never captured evidence. Metadata/test corrected; persistence owner normalized
empty optional attachment behavior. Retest passed. The installed requests stack
prints a dependency-version warning; no network is used or needed by this workflow.

Guide/README and shared spec, plan, tasks, research, model and contract docs updated.
Public guide uses public export APIs and documents actual operating limits, scoped
lookup, row companion verification, retention unavailability versus secure erasure,
and confidence limitations. Parent owns affected aggregate/full offline suite.
