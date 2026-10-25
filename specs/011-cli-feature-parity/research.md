# Bounded repository research

Date: 2026-10-25. Sources: current local code/docs, not external API claims.
No web research or model inference needed for this planning request.

## Observed facts

- `pyproject.toml` registers `shopextract.cli:main`, Click >=8, Python >=3.10.
- `src/shopextract/cli.py` and saved real `--help` show nine root commands.
  Extraction stdout mixes summary text with only the first ten products;
  validation is text, discovery is line-based, changes emits separate objects.
  README's blanket claim that all defaults are JSON is inaccurate today.
- Root `__init__.py`, module exports and docs expose substantially more behavior
  than CLI flags. See `coverage.md` and `evidence/surface-inventory.json`.
- Maintenance already has a separate argparse CLI, durable SQLite jobs, trusted
  profiles and origins. Reuse its engine and validation rather than shelling out
  to parse human output or creating a second job scheduler.
- Tools already have a module CLI for MCP, strict ToolRuntime schemas and
  session-scoped handles. Root CLI integration must not imply persistent tool jobs
  or reuse maintenance IDs for ephemeral runtime handles.
- Storefront API overrides and LLM parameters already exist on extract; generic
  extraction can perform browser/LLM fallback. Reusing the public API does not by
  itself provide a hard wall-time or disable paid fallback. New machine/config
  modes require an explicit activation policy and bounded execution design.
- Feed export supports Google Shopping XML and idealo TSV; Amazon/eBay are
  validation targets, not existing export formats. Parquet depends on an engine
  checked separately; help must work without activating optional engines/MCP.
- Existing data/evidence/category codecs preserve contracts that generic
  `str()`/dataclass dumps can lose. Reuse native codecs, add CLI-only representations
  with explicit schemas where a native codec is absent.

## Decisions and alternatives

Keep Click and additive root groups; avoid framework replacement and flattening
every helper into a new command. Retain legacy defaults while offering explicit
machine output. JSON envelopes wrap reports; artifact payload serialization stays
separate. CLI command modules call shared library services. Only genuinely common
input/output/config/cancellation code is shared; no new generic workflow framework.
Use foreground bounded calls for ToolRuntime; a durable tool daemon/HTTP jobs
service belongs to spec 010 and is not needed for CLI parity.

## Open engineering decisions before affected G2/G3

1. Exact schemas for matching files, category config and policy inputs: derive
   from native contracts and validate before side effects.
2. Cancellation across async APIs, browser children and synchronous serializers:
   define owned subprocess boundaries where cooperative cancellation is insufficient.
3. Keep legacy implicit LLM behavior only on legacy paths; new workflows require
   explicit `--allow-llm` and trusted credentials, with a configured timeout/cost cap.
   Never assume a provider-specific cost estimator exists. Block enabling that
   mode until an enforceable budget contract is designed.
4. Durable migration preview must avoid opening/mutating the real database in a
   purported dry run. Initial command may require explicit `--apply` only.
5. Atomic export plus sidecar replacement: stage validated files; define recovery
   for failure between replacements. Do not promise filesystem-wide atomicity.

## Limits and evidence

One 20-second-cap help probe executed, exit 0, saved before inventory expansion.
No network, suite, installs, models or stress runs. Actual session token counters
are not exposed by available tools; record unavailable, no quota inference.
Many unrelated working-tree edits/artifacts predate this plan; only new
`specs/011-cli-feature-parity/` files belong to this task. Recheck source revision
and exact signatures before implementation, especially evolving tool code.

## Implementation interaction notes (2026-10-25)

- New CLI extraction cannot disable ambient LLM fallback merely by passing an
  empty llm_api_key: native extract resolves provider/environment keys. P1 must
  design an explicit additive activation guard and enforceable budget boundary
  before claiming advanced-option parity; legacy calls retain existing defaults.
- P3 adds database/canonical history controls. Legacy baseline assertions must
  preserve positional argument order while allowing reviewed additive options;
  update their expectation through P3 design rather than treating added --db as
  a compatibility failure or silently weakening tests.
- P5 discovery should enumerate installed Click commands/parameters without
  starting runtimes, and publish actual packaged input/output schemas.

- Native `compare_catalogs(store_a, store_b)` accepts store URL strings, not two
  offline catalogs. Competitive price_position/assortment_gaps also fetch native
  competitor stores; brand_coverage consumes catalog mappings. P2 must retain
  those input distinctions and bound implicit nested extraction/LLM behavior,
  not rename files as URLs or fabricate an offline native API. Native signature
  snapshot: evidence/native-signatures.json (AST-only, selected reads preferred).

- P0 bootstrap scans the existing one-level root commands. When P2/P3/P4/P5
  register nested command groups, their reviewed skeleton must extend scan_bootstrap
  to traverse installed Click groups, retain the full command/help path and use
  each child's option arity; otherwise valid nested --config/--db flags are
  mistaken for unknown root-command flags. Add real nested-help/operand tests
  before changing the shared scanner at that affected gate.

- P3 native price_history currently converts stored Decimal text to float and
  migrates identity rows when called. Machine history needs a reviewed exact-money
  extension/reuse contract while preserving default float legacy output; it must
  not stringify an already-rounded float and claim losslessness. Native watch
  is infinite and yields only changes, so CLI bounds must cover unchanged stores
  too, close the generator and bound nested snapshot extraction policy.

- P2 comparison/competitive safety: native compare._build_result ranks all matches
  by price without currency grouping; price_position reduces competitor records
  to floats and loses currency context. The CLI must not expose mixed-currency
  cheapest/rank claims. Design an additive native-safe mode or report grouping
  before implementation, keeping legacy behavior explicit; filtering after
  currency provenance has already been discarded is insufficient. Native stats
  derive floats; distinguish native approximate aggregates from exact retained
  product money rather than claim rounded floats recover source precision.
