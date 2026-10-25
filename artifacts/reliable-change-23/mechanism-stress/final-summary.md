# Synthetic mechanism/stress result — incomplete bounded scope

23/24 planned logical batches passed: SM01–08 and15/16 seeded batches. Only
seed2909/index7 (20-product partial omission+replay) remains interrupted.31 total
fixture attempts include three diagnosed setup failures, two superseded
single-event boundary passes and three interrupted attempts; these are not added
to successful coverage. No production behavior mismatch was demonstrated.

Mechanism evidence includes six-event native capture/normalize smoke, repeated
unverified rechecks then confirmation, terminal expiry/restart, health interactions,
exact mixed-report entry N=7 and UTF-8 byte B=15,963 boundaries (N/B±1 cold and
persisted replay), real pending-ledger update rollback, and currency-gate fault
sensitivity detected/killed with restored normal checks. Two seeds1701/2909 drive
independent exact expected event-set manifests; existing feature tests were not rerun.

Final read-only standard-library owner audit PASS:23 saved reports,196 qualified
old/new/recheck owner references, zero DB writes. Product/variant IDs matched the
candidate, for all saved candidate references, regardless of state. Audit runtime0.191driver seconds
(0.053audit seconds). Original full-graph audit timed out and is not passed.

Charged cumulative execution173.914seconds<180: includes132.607 measured earlier
driver seconds, a20-second audit timeout with0.100s explicitly unmeasured overhead
reserve,21.016seconds last generator chunk and0.191seconds direct audit. The original
stress phase exceeded its intended cumulative60-second cap by about4seconds due
to omitted resume bookkeeping; this remains a recorded budget breach. Reviewed
continuations hard-stopped at their caps, and no automatic extra chunk ran.

Fixture corrections, each diagnosed once per blocker: SupportState enum typing;
documented unknown/valueNone membership-presence oracle with stronger references;
and explicit retention batch establishing complete expiry. Mixed boundary fixture
was separately reviewed and corrected; old results preserved as superseded.
Approved replay optimization retained full events equality and zero new_events
while avoiding redundant third-snapshot re-evaluation already covered elsewhere.

Reusable tests: tests/test_reliable_changes_stress.py declares24 pytest cases
(1smoke+7targeted+16seeded); collection was not run by this delegate after bounded
execution. Drivers/configuration/results are saved here; source production files
were unchanged. Raw payloads/DBs/per-invocation logs remain ignored under raw/.
No network, inference or dependency installation. Existing author/reviewer agents
were reused sequentially.
Actual live commercial-change observations remain separately inconclusive.
