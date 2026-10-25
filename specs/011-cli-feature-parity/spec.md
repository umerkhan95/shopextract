# CLI feature parity — behavior specification

Feature, 2026-10-25. Goal: every supported user workflow in ShopExtract
must be usable from the installed `shopextract` command without writing Python.
The initial plan is complete; the user subsequently authorized full implementation,
integration, documentation and ticket updates. Phase-specific gates/evidence
record actual implementation status; planning PASS alone is not runtime approval.

## Outcomes and requirements

- FR01 Coverage: maintain `coverage.md` mapping existing public capabilities to
  proposed commands, current availability, phase and acceptance scenarios. Every
  top-level public callable and documented module workflow must be mapped or have
  an explicit rationale for being a data/helper interface rather than a command.
  Implemented capabilities are in scope; speculative ecosystem integrations from
  spec 010 remain dependencies, not promised CLI features.
- FR02 Compatibility: all nine existing root commands, arguments, option aliases
  and default behavior remain usable. Existing maintenance/tools module entry
  points remain usable. New behavior uses additive commands or explicit options.
- FR03 Automation: new data commands support `--output-format json`, a versioned
  JSON envelope, diagnostics on stderr and complete bounded results. Legacy
  commands opt into the same contract explicitly. JSONL is used for watch events;
  CSV/feed/Parquet are export payload formats, distinct from response formatting.
  No silent ten-product truncation in machine mode. Human output may preview only
  when total count and truncation are explicit. Proposed exit statuses: 0 success,
  1 operation failure, 2 usage/configuration error, 3 partial/incomplete result,
  4 validation rejection, 130 interruption. Legacy defaults retain current codes.
- FR04 Extraction: expose single-product, store and feed extraction, normalization,
  quality, platform selection, supported identifier/enrichment, browser/LLM,
  storefront and field-resolution options through existing APIs. Inspect actual
  signatures before adding flags; no arbitrary internal function execution.
- FR05 Offline workflows: expose identity matching/evaluation, catalog comparison,
  statistics, competitive analysis, marketplace validation, image checking,
  duplicates and supported exports. File/stdin pipelines preserve Decimal money,
  identifiers, variants, missing values and evidence according to native codecs.
- FR06 Monitoring and trust: expose explicit database selection, canonical-ID
  history, bounded watch, reliable changes/recheck/replay, snapshot save/load,
  evidence lookup, bundles/sidecars and retention. Prune defaults to dry-run;
  mutation requires explicit `--apply`. Identity migration has explicit DB and
  apply intent; do not claim preview support until a safe read-only preview exists.
- FR07 Categories: expose category extraction/normalization, native scopes,
  mapping with versioned rules/registries, category validation/portable records,
  WooCommerce tree retrieval, membership linking and local policy review.
- FR08 Operations: root `maintenance` wraps existing create/run/status/report/
  evidence/cancel/resume/retry behavior; root `tools serve` launches existing MCP
  stdio service. Tools schemas/bootstrap/operations are accessible through a
  bounded foreground `tools call` session with same-session submit/poll/page/
  evidence consumption. Handles are session-only, never durable CLI job IDs.
  Maintenance job IDs remain durable in their own database.
- FR09 Boundaries: validate input before side effects; expose API-supported caps,
  deadlines and cancellation. Secrets use environment/trusted configuration,
  never diagnostic output. CLI wrapper must retain each underlying surface's
  trust policy: operator CLI remains distinct from restricted ToolRuntime.
  Missing optional dependencies produce actionable errors. Never auto-install,
  auto-download a model or silently invoke paid inference.
- FR10 Discoverability: nested help, examples, file schemas, config precedence
  (explicit flags > trusted file > documented environment > existing defaults),
  migration notes and install smoke. All supported public additions update the
  coverage inventory and CLI acceptance checks.

## Acceptance scenarios

SC01 inventory completeness; SC02 legacy invocation compatibility; SC03 clean,
complete machine output; SC04 extraction/control fidelity; SC05 offline analysis,
matching and export fidelity; SC06 reliable monitoring/evidence state; SC07 category
scope/mapping/tree integrity; SC08 maintenance recovery and MCP session lifecycle;
SC09 failure/resource/security boundaries; SC10 installed help and discoverability.
Exact inputs, expected outcomes and verification distinctions: `test-design.md`.

## Boundaries and compatibility

Use the local templates and repository workflow. No extraction rewrite, new
daemon, remote job server, merchant write connector, hosted account, model benchmark
or integration implementation. Data models/enums/policies are input/output schemas;
DataFrame conversion is covered by export/table behavior, not a Python-object CLI.
Stable helper behaviors may be flags or report fields; record the mapping explicitly.
No automatic model downloads or paid calls. Push/PR publication is separate from
local implementation; preserve the existing dirty source dependencies.
