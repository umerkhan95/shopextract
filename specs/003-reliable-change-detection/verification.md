# Final verification summary — 2026-10-16

Final state: **95 focused / 726 full-suite tests passed**; independent final review
PASS, synthetic end-to-end demo PASS, bounded live pipeline smoke PASS.
Actual live commercial change: **inconclusive** (equal captured values).
Final logs: final-focused.log, final-full-tests.log, final-example.log and
final-live-replay.log under artifacts/reliable-change-23/.

The following sections preserve stage evidence, including superseded red and green
counts. Pending statements below describe their historical stage, not final status.

## Stage verification evidence — 2026-10-16

## Existing baseline and skeleton regression

Command: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_monitor.py tests/test_snapshot_completeness.py -q`

Baseline: 39 passed (coordinator), artifacts/reliable-change-23/baseline.log.
After declaration/tests: 39 passed in 1.35 seconds,
artifacts/reliable-change-23/skeleton-regressions.log. No business logic added.

## Acceptance red before implementation

Command: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_reliable_changes.py -q --tb=short`

87 failed, all at `NotImplementedError: Reliable change reports are not implemented`
in declaration stub reliable_changes. No collection/fixture failures; this is the
intended absent behavior, not an accepted pass. Named SC01–18 tests cover fields,
evidence, identity, health, thresholds, explicit rechecks, currency, replay,
rollback, races, expiry, resource bounds and unrelated legacy isolation.
Saved artifacts/reliable-change-23/red.log. No xfail/skip masking.

Fixture repair before final red: set PYTHONPATH=src to match repository baseline;
keep Product scalar fields type-valid while graph normalized values exercise
adversarial typed observations; custom fault exception prevents the missing stub
from being mistaken for injected RuntimeError. These repair test setup, not
requirements. The final saved red log contains only missing-behavior failures.

G2/G3, new acceptance green, broader offline checks and bounded live checks remain
pending. No live requests or inference performed. Dependency warning about host
requests versions appears in logs but did not affect the baseline or test setup.
Actual usage counters unavailable; no quota percentage inferred.

## G2 corrections and re-review evidence

87 acceptance cases now include exact dictionary-key/type assertions and ordering,
explicit product/variant currency reason checks, currency-candidate rechecks,
unsupported rechecks/additions, same-domain corrupt legacy isolation, missing
canonical identity and nonfinite stored graph rollback, exact qualified recheck
references/source timestamps, and barrier-synchronized initial/recheck publishers.
Final red still fails only at missing-business stub; no fixture defects. This file
is available to the independent G2 reviewer; G2 remains pending re-review.

## Reviewed health refinement red
Command: `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_reliable_changes.py -k failure_reasons --tb=short`
3 intended missing-behavior failures, 87 deselected, before health implementation;
artifacts/reliable-change-23/health-red.log. Delta independently reviewed and passed.

## Implementation and offline green
- Focused: `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_reliable_changes.py`: **90 passed**; implementation-focused.log.
- Affected regressions: **292 passed**; implementation-regression.log.
- Full suite: `PYTHONPATH=src .venv/bin/python -m pytest -q`: **721 passed**, 17.22 seconds; full-tests.log.
- `PYTHONPATH=src .venv/bin/python examples/reliable_changes.py`: passed; example.log. Synthetic capture -> normalization -> storage -> warranty/price decisions -> explicit recheck -> qualified lookup -> replay.
- `git diff --check`: passed. All logs under artifacts/reliable-change-23/.
- Tests used OMP/BLAS/MKL thread caps of two, tokenizer parallelism disabled; no inference.

## Live pipeline smoke
Command: `PYTHONPATH=src .venv/bin/python artifacts/reliable-change-23/live_check.py`.
**Passed**: exactly 2 sequential requests, no retries/redirects/browser. Each response
8048 bytes; 2 products and 2 variants per capture. 103 retained source lookups per
capture round-tripped exact source URL/time/pointer values. Canonical product IDs
persisted. Partial scope produced no removal alerts. Replayed report had zero new
events. 0 observed change candidates/events; 4 unsupported-field diagnostics.
Actual live commercial-change validation is **inconclusive** because both captures
had equal values. Threshold/recheck/field-change correctness is supported by the
designed offline tests and separately labelled synthetic example, not fabricated
live mutations. No expanded crawl or repeated sweep.
Evidence: live/summary.json, live.log and live_check.py; captured responses and DB
remain local in live/. Final independent review pending.

## Environment note
An accidental `uv run` attempted dependency downloads before tests; it was stopped,
its generated uv.lock removed, and all completed checks used the existing .venv.
No project dependency changes. Existing requests dependency warning persisted
without check failures. Actual session token counters unavailable at milestones.

## Final-review regression red before repairs
`pytest -q tests/test_reliable_changes.py -k 'invalid_domain or oversized_ledger' --tb=short`:
3 failed, 2 passed, 90 deselected. Saved final-findings-red.log before fixes.
Oversized-ledger test uses SQLite text_factory to reject materializing corrupt
report text before a byte-limit decision; asserts no committed DB changes.
Domain cases assert ValueError plus unchanged DB for invalid input.

## Final post-review checks
95 focused passed in 9.03s. Full suite **726 passed in 17.56s**.
Final synthetic example passed. Final code replayed saved live captures with zero
new events; this was offline replay, **zero additional network requests**.
Independent review PASS and artifact digests recorded in reviews.md.
`git diff --check` passed. No remaining code/verification blockers in planned scope.
Delivery tracking: #23 and child issues remain open until PR review/merge.

## Additional live checks requested before merge
Native Magento GraphQL and Woo Store API: **PASS**, exactly 4 additional sequential
requests, no retries/errors/redirects, 20-second whole-request and 1 MiB caps.
Each capture retained 2 products (Magento up to 4 variants/product). Price,
currency and stock observed for every product; 318 qualified source URL/time/
pointer checks passed. Shared identities stable, both live comparisons/replays
0 events/0 new events. Labelled offline-derived partial omissions: 0 removals.
Actual commercial change remains inconclusive because source values did not change.
New plan, driver and summaries: artifacts/reliable-change-23/additional-live/.
Independent review PASS; no runtime source changes after final offline checks.
Across initial Shopify and additional native platforms: 6 requests, 524 evidence
round-trips. Raw responses/SQLite remain local and ignored.
