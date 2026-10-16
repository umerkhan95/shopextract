# Reliable change detection: mechanism/stress plan — review pending

Date: 2026-10-16. Author: design delegate. Scope: merged PR #48; existing live
Shopify/Magento/Woo smoke passed but observed no actual commercial changes.
Updated workflow requires synthetic mechanism checks as a separate evidence class.
This plan and scenario-matrix.md are the ONLY artifacts authored at this stage.
No generator, tests, runtime monkeypatch, network or inference has been executed.
Do not execute before an independent reviewer approves this plan.

## Coverage-gap rationale

Reviewed the saved SC01–18 suite and current reliable.py. Existing tests cover
single transitions, basic evidence/replay, separate expiry, tiny over-limit
constants, initial/recheck races and first-invocation rollback. They do not jointly
exercise a realistic mixed catalog through native normalization, a succession of
unverified rechecks, pending-state update rollback, terminal results after both
expiry and restart, exact budget inclusivity, or generated permutations against
an independently specified expected event set. Extra seed counts alone do not
count as distinct coverage. Matrix SM01–09 names each uncovered interaction.

## Real execution paths and independent oracle

After approval author reusable tests/test_reliable_changes_stress.py and one
sequential driver under this artifact directory. Fixtures are deterministic,
synthetic native Shopify product/variant payloads with realistic IDs, SKU, prices,
ISO currency, options and availability. Source URLs use reserved synthetic
https://synthetic.example; method synthetic_fixture; fixed UTC source/capture
times, no real observed-at claim. Explicit field/attribute evidence follows the
existing TrustContract schema; maintain schema-valid Product scalar types.
Use real capture -> normalize -> save_snapshot -> load_snapshot -> reliable_changes
-> qualified get_evidence. Product warranty/pack-size attributes use explicitly
labelled synthetic contract augmentation where native format has no mapping.
No expected report is returned from a fake and no duplicate diff algorithm.

Each scenario carries a handwritten action manifest: entity logical key,
record-local field path, exact typed old/new value, expected state/reason and
membership result. Generator applies those predefined actions; it does not derive
expected behavior from production output/helper functions. Independent oracle
compares exact sets of (logical product key, logical variant key or None, kind,
field path, state, old value, new value); normalize values with test-owned explicit
Decimal literals, not production equivalence/threshold helpers. Canonical IDs
map back through retained external_id/variant_id fields; independently assert IDs
remain stable across captures. Compute expected event-set equality, publication
counts, reasons, source pointer/time references and deterministic sort order.
Budget byte length may be measured from a known valid stored payload solely to
set exact byte boundaries; never use observed event decisions as oracle input.

## Bounded execution order and resources

1. Run one SM01 smoke using two products, two variants each; save smoke.json and
   compact fixture manifest before expanding. Timeout 60 seconds for smoke phase.
2. Execute SM02–08 once each, including table-driven exact-boundary subcases,
   then SM09 seeded stress: 16 sequential batches, seeds 1701 and 2909, eight
   batches each. Targeted and stress phase together timeout 60 seconds.
3. Total <=24 fixture batches (one smoke + seven targeted + sixteen stress),
   <=20 products per batch, <=4 variants per product, <=6 snapshots per batch,
   <=2 MiB serialized input per batch (sum raw snapshots/manifests). Generated
   stress varies order, titles, action placement and partial-coverage context,
   not arbitrary random values. Fixed manifest schedule guarantees each selected
   action interaction is exercised, with separate counts by interaction.
4. One process, sequential datasets/SQLite connections; no contention expansion,
   inference, network, installs, uv or dependency resolution. Existing .venv/bin/python
   with PYTHONPATH=src; OMP_NUM_THREADS=2, OPENBLAS_NUM_THREADS=2,
   MKL_NUM_THREADS=2, NUMEXPR_NUM_THREADS=2, TOKENIZERS_PARALLELISM=false.
   Total wall ceiling 180 seconds (both timed phases <=120 seconds total); no
   unbounded reruns. Subprocess driver may enforce each phase timeout, strictly
   one active child at a time. This is not a local model experiment.
5. On first genuine failure stop expansion, save current seed/action manifest,
   smallest already-known failing batch (no unbounded shrinker), expected/actual
   event delta and bounded traceback. Diagnose once; source repair requires its
   own test/review before proceeding. Record completed counts; do not restart
   completed batches. Token counters unavailable: record limitation, no quota claim.

## Assertion sensitivity and review

SM08 intentionally disables only the currency gate via scoped runtime monkeypatch
on reliable._currency_reason. The real capture/persistence/comparison/publication
paths still run against a separate disposable DB. A pending-with-currency_mismatch
assertion MUST fail under this injected defect; record detected/killed, restore
patch in finally/context and rerun the same invariant normally. If injected
breakage escapes detection, validation fails. Expected caught assertion is labelled
fault-detection evidence, never a genuine production failure or production pass.
No patched source ships; no mocking of normal report construction or ledger.

Save configuration/seeds, smoke, per-scenario results and compact summary under
this directory; ignore raw payload/SQLite databases. Keep reusable tests separate
from generated data. Root coordinator owns spec/task/verification updates and
independent final review. Do not alter existing docs-only working-tree changes.
Report separately: synthetic mechanism coverage, bounded stress outcome, and
unchanged actual-live commercial-change limitation. A pass is evidence only for
these scenarios/resource bounds, not production capacity or change frequency.
