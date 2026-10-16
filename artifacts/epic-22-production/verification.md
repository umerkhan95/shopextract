# Epic #22 — research, implementation and verification

Date: 2026-10-16. Local branch: `evidence-trust-storage-exports`.

## Scope and ticket status

Next actionable ticket was [#37](https://github.com/umerkhan95/shopextract/issues/37),
under [Evidence & Data Trust #22](https://github.com/umerkhan95/shopextract/issues/22).
#34–#36 were already closed. This session implemented the remaining local scope:

| Ticket | Result | Main implementation |
|---|---|---|
| #37 | Atomic typed evidence storage, scoped retrieval, conservative additive migration, explicit bounded pruning and expiry | `src/shopextract/monitor/evidence.py`, snapshot integration |
| #38 | Strict lossless Product/Variant bundles, expiry metadata, digest-bound CSV/feed companions and compatible default exports | `src/shopextract/_portable.py`, `export/_bundle.py` |
| #39 | Runnable offline trust workflow, acceptance fixtures, public documentation and specification traceability | `examples/evidence_trust.py`, `tests/test_evidence_trust_e2e.py`, `docs/evidence-trust.md` |

GitHub issues were read and saved; no remote issue closure, push or PR was performed.
The original untracked artifacts were preserved.

## Research and handoff

Three research roles saved cited reports: [persistence](research-persistence.md),
[portability](research-portability.md), [verification](research-verification.md).
Sources include Buneman et al. (ICDT 2001), Green et al. (PODS 2007), RO-Crate,
W3C PROV-DM, RFC 8259/6901/8785, official SQLite documentation, and research on
calibration and abstention. Reports distinguish source results from project
engineering decisions; this code does not claim PROV/RO-Crate conformance or
statistical guarantees inherited from those papers.

Three skeleton owners created interfaces, then separately reviewed against all
completed research reports. Three implementation roles followed, with a different
implementer from each ticket's skeleton owner. Runtime capacity required phased
role reuse; details are in [scope.md](scope.md). No local model was launched.

## Changes and integration review

Dynamic evidence attachments were previously omitted by snapshot `asdict()`.
They now persist explicitly alongside compatible monitoring JSON, within the same
transaction as identity aliases and snapshot data. Payload hashes verify stored
bytes; owner/snapshot scopes prevent ambiguous lookup of local evidence IDs.

Retention defaults to dry-run and reference protection. Explicit expiry removes
available support, retains tombstones and downgrades dependent observations and
selected resolutions. Bundle reload and subsequent persistence preserve expiry.
Integration review corrected inconsistent multi-query reads, microsecond retention
cutoffs, repeated expiry metadata and same-path export/sidecar overwrites.

## Executed verification

All test invocations used `PYTHONPATH=src .venv/bin/python -m pytest`.
Initial collection without PYTHONPATH was diagnosed once and repaired; no install
or repeated environment repair was needed.

| Check | Actual result | Saved output |
|---|---|---|
| Initial monitor/export/evidence baseline | 74 passed | `baseline.log` |
| Bundle/export focused tests | 43 passed | `portability-tests.log` |
| Persistence plus affected regressions | 178 passed | `persistence-tests.log` |
| Offline E2E acceptance | 8 passed (implementation owner) | `verification-e2e.md` |
| Full offline suite: `PYTHONPATH=src OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 TOKENIZERS_PARALLELISM=false .venv/bin/python -m pytest tests -q` | **631 passed in 8.24s** | `full-tests.log` |
| `git diff --check` | Passed | Coordinator check |

Focused counts overlap and must not be added. The full result includes the new
rollback, migration, precise cutoff, shared-reference retention, corrupt import,
sidecar and end-to-end tests.

Standalone offline example: **81 factual owner paths**, with all **25 observed
paths independently retrievable** (9 unknown and 47 unsupported). The E2E report
records the actual command and saved output directory.

## Operating limits and evidence boundaries

SQLite busy wait is bounded to five seconds. Serialized snapshots are capped at
16 MiB; bundle input at 64 MiB, 100,000 records, depth 64 and 1,000,000 nodes.
Capture limits remain 4096 bytes per fragment and 65536 bytes per product support.
Pruning inspects one bounded batch (default 100, maximum 1000); protected prefixes
may remain eligible on later calls. No automatic pruning or total database size
guarantee is provided.

Expiry guarantees support unavailability, not secure erasure: compatibility raw
data, prior exports and backups can retain source copies. Digests do not prove
authenticity. Fixture coverage is not population accuracy or calibrated confidence.
No live crawl, model experiment, load test or operating-system crash/power-loss
fault injection was performed; SQLite durability depends on its documented
filesystem guarantees. The saved offline tests substantiate the local acceptance
criteria, without establishing every production deployment condition.

## User-requested live follow-up

Five bounded live cases passed across four platform families, including the public
`snapshot()` API. All 696 scoped capture retrievals passed; restart, bundles,
sidecars and expiry/resave passed. Full offline rerun: 631 passed in 8.29s.
See `artifacts/live-evidence-trust/review.md` for the recorded commands and limits.
