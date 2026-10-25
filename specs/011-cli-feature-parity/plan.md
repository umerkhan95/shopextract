# Implementation plan — full CLI feature parity

Roadmap authored before implementation; full P0–P5 delivery is now authorized.
Behavior/test design precedes task breakdown. Commands remain proposed until
their phase ships; current delivery and exact evidence are recorded in status.md
and the p0/…p5/ child slices. P0–P4 have independent final PASS. P5 implementation, configured full-suite/wheel checks and independent whole-feature FINAL PASS are complete.

## Constitution check

Preserve constructors, identity, extraction defaults and feed contracts. Use
existing supported facts/evidence semantics; no inferred support from missing
values. MIT/self-hosted, no paid service gate. Sequential review agents, one active
delegate, no inference. Implementation followed separately reviewed phase contracts; historical planning approval alone did not authorize runtime completion.

## Delivery phases

| Phase | Deliverable / user outcome | Depends on | Exit criterion |
| --- | --- | --- | --- |
| P0 | Freeze capability manifest; machine I/O/error/config contracts; legacy baseline; help structure | G1 planning review | SC01–03/09/10 contracts and red tests agreed |
| P1 | Complete extraction front door: single/store/feed, normalize/quality, native options | P0 | SC04 + full machine output, controlled transport parity |
| P2 | Offline pipelines: identity/matching/evaluation, comparison, full stats, competitive analysis, validation/images/duplicates, all supported exports | P0; P1 for live URL workflows | SC05/05b + fixture roundtrips and error paths |
| P3 | Monitoring/trust: DB selection, canonical history, bounded watch, reliable recheck/replay, field resolution, snapshot/evidence/bundle/retention/migration | P0; P1 for fresh capture workflows | SC06/06b/09b through real state paths |
| P4 | Category workflows: six platform adapters, scoped mapping/config, portable records, Woo tree/linking, policy review | P0/P1/P3 | SC07 including partial/cyclic/foreign-scope cases |
| P5 | Root maintenance and MCP/tools entry points; session-safe foreground tools; packaged help/examples/final parity audit | P0; P3/P4 for integrated acceptance | SC08/08b/10 and every coverage row delivered |

Deliver sequentially; dependencies permit future reprioritization, not parallel
agents. Each phase is a reviewable child slice with its own G1/G2/G3, red tests,
offline/mechanism/stress evidence, live applicability and final review. Start P0,
then P1; do not implement the entire matrix as one patch. Time estimates wait for
P0's exact manifest and reviewed seams; no unsupported delivery date is promised.

## Architecture and decisions

Keep `cli.py:main` stable as registration boundary; proposed `cli_commands/`
modules own extraction, catalogs, monitoring/evidence, categories and operations.
Small shared CLI I/O/config/lifecycle utilities serve concrete command consumers.
Domain logic stays in existing APIs. Maintenance and MCP wrappers reuse their
native services/config validators and retain module invocations. Imports are lazy
where optional dependencies permit; root help never starts a runtime.

Machine mode uses versioned JSON envelopes, stdout data only, stderr diagnostics,
explicit partial/error statuses. Artifact format uses `--format`; response format
uses `--output-format`. stdin `-` accepted for schema-defined file inputs; explicit
file output uses a safe staged write contract. No per-command duplicate business
logic. Config files cannot grant ToolRuntime origins beyond trusted operator scope.
See research.md for lifecycle, LLM budgeting and multi-file recovery decisions
that must be resolved at affected design gates. Skeleton/components are future
stage artifacts; none are approved by this plan.

## Required gates

G1 reviews behavior/tests/tasks/research/coverage/plan; recorded in reviews.md.
G2 requires typed seams and genuine executable red evidence; G3 checks reuse and
refined skeleton. Implementation waits for G3. Final review checks actual diff,
all FR/SC evidence, help/docs and limitations. Review passage is an engineering
gate and does not need routine user confirmation.

## Verification and handoff

Use test-design.md's finite smoke, 24-case stress and <=30-request live ceilings.
Run focused CLI tests and affected library regressions then repository-required
checks per slice. Save exact commands/config/source revision, synthetic provenance,
counts and red/green results. Retain separate mechanism/stress/live outcomes.
Planning completion never means CLI parity implemented or verified. Resume via
status.md; future public API additions update coverage before parity is claimed.

## P0 contract-freeze design slice

P0 core contracts, schemas, legacy baseline and classified manifest are in
[p0/plan.md](p0/plan.md). P0 runtime and all independent gates including final
review passed; see [p0/status.md](p0/status.md). P1 extraction and P2 analysis/
export also passed final review. Later phase grammar remains reserved until
its own actual gates; current delivery/resume is [status.md](status.md).
