# Epic #22 scope and execution

GitHub source: https://github.com/umerkhan95/shopextract/issues/22
Issue snapshots saved locally on 2026-10-16 in `issues/`.

| Ticket | Initial state | Scope | Dependencies |
|---|---|---|---|
| #34 | Closed | Evidence/unknown/score contracts and shared specifications | None |
| #35 | Closed | Capture and normalization provenance across adapters | #34 |
| #36 | Closed | Deterministic field authority, freshness, retained conflicts | #34,#35 |
| #37 | Open; next | Atomic evidence persistence/retrieval, restart, conservative migration, explicit bounded retention | #34,#35 |
| #38 | Open | Typed lossless bundles, strict loading, compatible feed/CSV companions, scoped references | #35,#36,#37 |
| #39 | Open | Offline E2E acceptance, compatibility checks, operating/migration/API documentation | #36,#37,#38 |

Research roles: persistence, portability, verification. Each produced a cited report.
Skeleton owners: skeleton_persistence, skeleton_portability, research_portability
(third owner after its research role). Each created skeletons and separately reviewed
them against all completed reports.
Separate implementation owners: implement_persistence (#37), implement_portability
(#38), skeleton_portability in a new implementation turn (#39, whose skeleton was
owned by research_portability). Each ticket has a different implementer from its
own skeleton owner. Runtime agent capacity required phased role reuse.

No inference, live crawl, external publication, ticket closure or Git push is part
of this local implementation. Acceptance requires actual saved tests, not skeletons.
Retention expiry is support unavailability, not a secure erase guarantee for all
legacy/capture copies. Portable integrity digests are not authenticity or accuracy.
