# INT-10: Workflow recipes, compatibility matrix and release verification

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#72](https://github.com/umerkhan95/shopextract/issues/72).
Related planned work: [INT-01 / #63](https://github.com/umerkhan95/shopextract/issues/63), [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73).

Status: planned; researched2026-10-24. Owner: integration/release maintainer.
Dependencies: INT-10a recipe-definition subset consumes reviewed spec.md and existing
tool contracts, so it can precede INT-11/local #24 skills. INT-10b executable recipes,
compatibility and release consumes implemented INT-01..09 and INT-11..25 only for
enabled rows; no cycle back from skill pack to final release. #27 only
for optional outbound delivery. Covers FR01/12/15, SC01/12/15 and platform SC05..11.

## Outcomes and recipe boundaries

Deliver versioned, importable examples showing real user goals in each implemented
connector, without implying every core Python feature already has a remote tool.
Baseline uses only discover/extract/match/changes/evidence/job_status/job_result/
job_cancel. Capability discovery and completed-job listing come from service control
plane. Every recipe preflights capability/version/scopes and exits explicitly if an
operation is absent. It cannot install dependencies, request extra credentials or
write merchant catalogs merely because a source page suggests it.

First executable recipes: bounded store extraction plus inspectable source evidence;
supplier catalog matching with uncertain/conflict review; reliable changes review
between two operator-granted existing captures. A schedule may submit another bounded
extraction but this does not create history or verify a reliable commercial transition.
Continuous monitoring requires separately designed fresh capture/scheduler/history
extension. Feed preparation, general analytics, taxonomy/category maintenance and
correction jobs are documented deferred recipes until typed tool surfaces exist.
Define each missing extension owner/risk/tests before enabling; a Python API presence
alone is not integration availability.

## Construction and release strategy

Use service schemas and fixture manifests as common reference, platform-native import
formats and concise setup instructions. Keep credentials/endpoints placeholders with
validation; exports/screenshots contain no secrets. Separate examples for MCP model
orchestration versus deterministic automation, with bounded polling and deferred job
continuation. Preserve service result evidence/uncertainty instead of model commentary
as a source of truth. Notification/destination writes require explicit configured
workflow actions; this epic does not send messages or mutate merchant stores.

Compatibility matrix records client/runtime/package/service/schema/protocol versions,
credential mode, scopes, private live result, known limits and date. State columns:
documented → implemented → mechanism-tested → private-live-compatible → submitted →
accepted/published. Different states cannot be collapsed into “supported.” Docs-only
completion means planning artifacts reviewed, not connectors shipped.

Platform distribution follows respective [n8n submission](https://docs.n8n.io/connect/create-nodes/deploy-your-node/submit-community-nodes.md),
[ChatGPT submission](https://developers.openai.com/plugins/deploy/submission),
[Zapier visibility](https://docs.zapier.com/integrations/quickstart/private-vs-public-integrations),
[Make visibility](https://developers.make.com/custom-apps-documentation/create-your-first-app/app-visibility)
and [Pipedream action lifecycle](https://pipedream.com/docs/components/contributing/actions-quickstart).
No acceptance date is promised. Pin and test new versions before public metadata
changes; retain old schemas while workflows or approved host metadata use them.

## Acceptance and future evidence

- [ ] Every enabled recipe imports/runs through the actual implemented adapter, preserves exact data and stops at declared budget.
- [ ] Missing export/analytics/capture capability produces explicit unsupported state and documents the prerequisite, not a fake feed or successful monitoring result.
- [ ] Side effects, secret setup, owner mapping, retry/commit-sequence checkpoint/expiry behavior are visible to workflow users.
- [ ] Independent matrix review matches actual saved mechanism/live runs, with blocked/inconclusive/pending states retained.
- [ ] Docs links, issue dependency mapping, sample redaction and package contents pass checks; final reviewer confirms no connector/publication claims from planning alone.

Future acceptance reuses scenario-specific synthetic/stress results instead of broad
repeated sweeps. Each platform begins with one saved small smoke; unavailable account
access blocks live compatibility while controlled real-path tests remain required.
