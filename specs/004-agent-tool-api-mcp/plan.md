# Implementation plan — #24

State: ready for independent G1 review; no implementation authorization gate has passed.

## Constitution check

Opt-in versioned tools preserve legacy constructors/extraction/feed/matching/monitoring defaults. Real captured support and owner relationships remain authoritative. Native existing parsers/normalizer, identity matching, reliable changes and evidence persistence are reused. Official MCP v1 is MIT/Python >=3.10 compatible; no paid gate. Sequential agents/jobs, no inference, small smoke before deterministic bounded expansion. User authorization covers workflow review agents; no extra approval needed for routine gates.

## Architecture and decisions

See spec.md/test-design.md for FR/SC contracts and research.md for code/source evidence. Five reviewable slices in tasks.md: A contracts/session/jobs; B guarded sources/discovery/extraction; C matching/changes/evidence; D MCP/reference client; E docs/verification. Preserve all scope and create mapped child issues before implementation; local ticket drafts currently exist, no external mutations by design author.

MCP stdio uses optional mcp>=1.30,<2, validated at 1.30.0 on Python 3.10. Domain schema validation/envelopes shared with direct Python tools. HTTPX custom transport plus HTTPCore public network backend validates origins/redirects, connects to vetted IPs and retains original Host/TLS name. Native guarded extraction supports existing public API parsers and structured HTML; no implicit model/browser/network escape. Exact startup allowlists, enabled tools and configured capture aliases produce session-bound authority. Result-owned evidence and scoped configured captures feed real existing matching/change/evidence paths. Bounded ephemeral jobs/cursors are sufficient; no hosted auth/job platform.

Deadline/cancel cleanup uses async HTTP cancellation and at most one disposable worker for noncooperative synchronous existing algorithms; no cancellable-thread fiction. Integration process budget is therefore five (client/server/up to two resource trackers/one worker), no parallel model or job. Worker rollback/publication semantics must be explicit at G2; if a materially simpler implementation still meets exact hard deadline and cleanup contract, document/review it before use. Full subprocess source isolation is unnecessary; worker gets bounded captured data/configured domain arguments and no network input capability.

Proposed limit defaults and stdio-only transport are G1 decisions. All requirements remain proposed until reviewer verdict; implementation must not quietly relax them. Any material changed contract returns to design and affected gates.

## Required gates

G1: independent reviewer receives spec/test-design/tasks/research/plan/status, checks traceability, native-format support/security and realistic adverse cases. Save actual artifact digests, findings/dispositions/verdict in reviews.md; currently pending.
G2: after G1, author skeleton.md/interfaces and executable failing acceptance tests; record red result/reason before business logic. Reviewer validates typed schemas, SDK v1 signatures, pinned TCP/TLS seam, process cancellation/SQLite, evidence ownership and scenario exercise.
G3: author components.md/revised skeleton; separate reviewer checks reuse/coupling/lifecycle/failure invariants. Implementation starts only after actual pass and red evidence.
Final: independent reviewer assesses final diff, all FR/SC outcomes, offline/stress/live evidence and docs. No future verdict assumed.

## Verification and handoff

Follow test-design.md: smoke first; seed 24, fixed clock, up to 48 distinct bounded stress cases/120s/16MiB fixtures, one active job, at most 5 processes including support trackers only when reference client/server/worker required. Offline production paths, controlled network/clock/fault boundaries and critical negative controls precede public live client flow <=16 requests/120s. Record commands/environment/results in verification.md when executed. Preserve distinction between planned checks, deterministic mechanism/stress evidence, genuine protocol integration, actual public observations and unchanged commercial data. Missing required mechanism coverage blocks completion; access failure remains live blocked/inconclusive. Run affected compatibility checks then repository checks, runnable doc examples and package/license check. No commits/push/labels or unrelated history changes by this author.

## G1 revision response

Pending rereview of G1-01–04. Adopt owned resolver subprocess with <=2s deadline/<=1s cleanup grace, serialized with domain worker; fail server admission closed on unreaped child. Adopt identity-only response encoding and <=64KiB raw reads, reject compressed responses before decode. Count full retained graph under 4MiB/job and 32MiB/session, release with handle invalidation. Discovery outputs policy-screened eligible URLs and separate rejected_source diagnostics; extraction still revalidates DNS. Test-design R1–R8 replace eight less distinct cases within existing 48, with original boundary/address risks retained as parameterized assertions. These tighten mechanisms without removing any epic capability or adding a decompression/resolver framework. Await independent revised-artifact G1 verdict; no code yet.

Implementation pause at native Shopware security amendment: existing native extractor needs canonical read-only product-search POST, beyond GraphQL-only wording. Exact NativeReadPolicy/route/body/zero-byte denial cases are in spec/test-design/skeleton. Coordinator requires a separate affected security review before enabling the allowance. Preserve saved ten-test domain smoke; other native modes/MCP/docs/stress are still incomplete. No stress/live execution has occurred.

Current bounded implementation checkpoint: A–D code and E runnable docs/reference client saved; focused20/affected187 checks passed as recorded in verification.md, but full feature completion is not claimed. Native5 real parser/evidence and real MCP flow smoke passed separately. Concrete48-case manifest/fixtures/driver are ready for independent mechanism coverage review; stop before stress/public live/full-suite expansion. After approval execute bounded driver, diagnose at most one repair per blocker, then full repository check under180s explicit subprocess timeout. Live assigned separately by coordinator. Scope/gates remain mandatory.

MC repair refinement: exact row mappings replace blanket claims; same dispatcher/guard/job branches remain active under surgical test-only faults. New interaction fixtures replace weaker cases inside48. Driver actual fixture ledger and full source/test/helper/environment identity enforce bounded honest resumes; preflight14,490,163 bytes, cumulative16MiB. Tracker measurement supersedes earlier process estimates: maximum5 including caller/server support trackers and one active auxiliary worker; library does not kill shared interpreter tracker. Request corrected coverage plus affected process-budget review before stress/fullsuite/live. CI extras now required across supported Python matrix; no CI pass claimed.

### F02 affected plan — review pending

Canonical behavior/seams are spec.md F02 amendment, skeleton.md and components.md; acceptance B01–B08 in test-design.md. Sequence: affected G1 contract review → corrected G2 async/worker/resource interfaces and representative normal/oversize reds → affected G3 reuse/lifecycle review → one bounded implementation slice → focused normal/oversize/item/aggregate/busy/cancel/admission/legacy checks <=45s. Migrate all direct/MCP bootstrap consumers/examples together; retain capture/evidence owners. No F02 implementation before independent affected review. F01 separate focused red/green is saved. Existing stress/live receipts remain closed/unchanged; no broad regression/fullsuite until assigned.

F02 final verification ceiling declared before execution (2026-10-16): after unchanged B05/B06 ownership checks pass, run the full repository suite ONCE with a240-second total subprocess deadline. Prior suite took169.29s; eight new real SQLite/killable-worker capture cases add approximately20s in saved focused execution, so the old180-second ceiling no longer leaves sufficient startup/cleanup margin. Keep finite240s ceiling, numerical workers capped2, no parallel test workers, log<=1MiB and owned process-group cleanup. Ordinary full-suite evidence remains separate from closed stress/live receipts; no further sweep. Required CI pytest deadline follows this same240s finite bound.

### Discovery timeout follow-up bounded plan — review pending

Author D01/D02 expectations then representative reds (<=10s total) → independent affected review → smallest lazy child-fetch implementation → affected focused checks within new45s execution budget. No research/model/fullsuite/old stress resume. Any later public retry needs offlinegreen/review and separate90s/8request receipt; only Bliss World, existing default30s job timeout, no blanket120s inflation. Old receipts and813-pass historical result preserved. Current assignment ends after design/red.
