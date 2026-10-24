# INT-07: Zapier actions and completed-job polling trigger

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#69](https://github.com/umerkhan95/shopextract/issues/69).
Related planned work: [INT-01 / #63](https://github.com/umerkhan95/shopextract/issues/63).

Status: planned; researched2026-10-24. Owner: Zapier integration maintainer.
Dependency: INT-01; #27 only for optional later signed push, never merchant-write
approval for polling. Covers FR09/04/14, SC09/04/14.

## Build and authenticate

Use the [Platform CLI framework](https://docs.zapier.com/integrations/build-cli/overview)
with a versioned integration definition, authentication module, creates/actions and
polling triggers. Current docs recommend `zapier-platform`; do not copy obsolete
binary/version snippets blindly. Pin tested CLI/core/Node versions during child setup.
Use platform HTTP helpers and automated fixtures, with a stable shared service
contract rather than copying Python core code into action scripts.

Configure OAuth if shared service supports it, otherwise scoped self-service API
bearer key for private setup. [Authentication guidance](https://docs.zapier.com/integrations/build/auth)
requires an account test and favors OAuth; public publication cannot depend on users
emailing maintainers for API access. Service base URL is validated and tied to stored
credentials; merchant URLs remain ordinary extraction inputs and never receive them.
Missing/revoked token and wrong-owner objects fail without revealing private handles.

## Action and trigger contracts

Provide Submit Job, Get Job Status, Get Result Page and Cancel Job; operation choices
use eight existing capabilities only. Submit returns job identity promptly. A workflow
can continue from a separate completed-job trigger/status action instead of holding
execution open. [Operating constraints](https://docs.zapier.com/integrations/build/operating-constraints)
state30seconds for polling/actions including requests and scripting; configure a
lower internal admission/request deadline with headroom, not a30second sleep.
Recheck payload and account-rate limits before implementation.

[Polling dedup](https://docs.zapier.com/integrations/build/deduplication) expects
newest-first arrays and stable primary keys, normally `id`; automatic full pagination
cannot be assumed. Trigger IDs use completion identities, not product IDs (a product
may participate in several jobs). Use service monotonic commit-sequence ordering/filtering and explicit
retention-gap error. Pause/reactivation resets can change platform dedup state; document
at-least-once workflow behavior, never guarantee all-time exactly-once delivery.
Commercial-change triggers/fresh captures remain deferred; granted capture review is
an explicit manual operation.

## Acceptance and future tests

- [ ] Correct private credentials pass account test; invalid scope/base URL/token fail without forwarding secrets.
- [ ] Slow source job returns accepted identity before action budget; pending status differs from completed empty result.
- [ ] Newest-first completed list produces stable unique IDs; repeated polls and response loss do not resubmit work. Late equal-timestamp/lower-ID and backward-clock commits retain discoverability by sequence.
- [ ] More than one retained page, checkpoint older than journal, restart and429 follow explicit bounded/gap behavior; never silently drop backlog.
- [ ] Decimal text/variants/evidence/completeness survive action fields and trigger payloads; cancellation returns authoritative state.

Use real CLI handler execution and shared service persistence with controlled clock/
transport only; save smoke then bounded mechanism/fault cases. Future private live
smoke: one action/two polls, ≤12service calls/two products/120seconds, source cap6.
[Private/public states](https://docs.zapier.com/integrations/quickstart/private-vs-public-integrations)
are separate; private invitation does not mean app-directory approval. Developer access,
public API onboarding, version promotion and review remain prerequisites. This planning
slice creates no integration, installation, test Zap or public submission.

Journal sequence/checkpoints remain decimal text or opaque tokens across JavaScript
outputs; never cast to Number. SC04/14 test9007199254740993 losslessly.
