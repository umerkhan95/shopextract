# P0: CLI core contract freeze

Design slice, 2026-10-25. This specifies future behavior; it implements no runtime.
Parent FR01–03/09/10 and SC01–03/09/10 apply. Independent G1 passed; see reviews.md for the reviewed revision.

## Outcomes and requirements

- **P0-FR01 / baseline:** `command-baseline.json` freezes all nine existing command
  names, argument order, aliases, defaults, choices and required/multiple options.
  Existing invocations without new opt-in controls retain output, library dispatch,
  default database and exit behavior. In particular extract stdout's ten-item preview
  and validate's historical issue-report exit 0 remain legacy behavior. Fixes to
  those behaviors require machine mode or an affected-phase contract change.
- **P0-FR02 / grammar:** only new P0 syntax is root options, before the command:
  `shopextract [--config PATH] [--output-format legacy|json]
  [--diagnostics normal|quiet] COMMAND [ARGS]`. Options are singleton; repetition
  is usage error (2). `--help`/`--version` retain Click spelling. `--format/-f`
  and `--output/-o` remain artifact controls of extract, not envelope controls.
  There is no `config` command, after-command global option, JSONL, implicit stdin,
  new alias, or reserved-command placeholder in P0. For usage-error representation, first explicit format occurrence wins if valid;
  invalid/missing first value falls back to validated file, then env, then legacy.
  Later duplicates never change the selected error representation. Future watch streaming grammar
  must receive its own freeze; this contract governs single-response commands.
- **P0-FR03 / machine I/O:** json emits exactly one UTF-8 JSON document plus LF on
  stdout, with keys defined by `response.schema.json`. No preview truncation,
  banners, progress or log lines appear there. `data` contains the full native result represented losslessly, or null if no
  usable result exists. Success has `ok=true`, `error=null`, `completeness="complete"`; failure has
  `ok=false`, null data and a structured error; partial has `ok=false`, usable
  data, error E_PARTIAL and `completeness="partial"`. Failure completeness is
  `"unavailable"`. Envelope schema_version is the string `"1.0"`. Warnings never silently convert failure
  to success. Empty successful results are empty collections, not partial/error.
  Partial is only legal where native results expose incomplete work; P0 creates no
  fabricated partial result. Domain payload schemas belong to P1–P5 and must be
  frozen before binding their native results; envelope schema alone proves no parity.
- **P0-FR04 / errors:** `contracts.json` freezes statuses, exit codes and stable
  generic error codes. Known expected errors have actionable sanitized messages;
  no traceback, credentials, config contents or raw exception text are emitted.
  Native business/validation findings remain data unless a later phase explicitly
  defines failure criteria. Quiet suppresses nonessential stderr diagnostics only;
  it cannot suppress JSON errors. Legacy invocation behavior stays historical.
  Machine usage/config validation finishes before network, model, DB, output-file
  writes or optional-runtime startup. An emission failure/broken stdout cannot be
  guaranteed to produce valid JSON; exit 1, best-effort sanitized stderr.
- **P0-FR05 / config:** `config.schema.json` is the entire accepted CLI config.
  Strict JSON object, UTF-8 (no BOM), <=65,536 bytes; duplicate keys, NaN/Infinity,
  unknown keys at any level, wrong types and unsupported versions are rejected.
  Schema version is required integer 1 (boolean true is invalid). Empty object is
  invalid; optional settings omitted inherit defaults. Empty PATH/env values are
  errors, not absence. `--config PATH` overrides `SHOPEXTRACT_CONFIG`; no discovery
  or merge of files, no includes, interpolation, executable config or stdin `-`.
  Relative file path resolves against cwd. Config is read-only, once per command.
  Setting precedence: explicit root option > selected trusted file > documented environment
  (`SHOPEXTRACT_OUTPUT_FORMAT` / `SHOPEXTRACT_DIAGNOSTICS`) > legacy/normal defaults. Validate
  all selected file keys and present recognized env values even if overridden;
  an invalid lower-precedence setting cannot be silently hidden. Unknown environment
  variables are ignored. No credentials, domain flags, trusted origins, model or
  browser activation can be set through this schema. Future version/extension
  requires schema revision and affected review; reserved phase config is rejected.
- **P0-FR06 / bootstrap:** recognized root/nested `--help` and root `--version` exit 0 before
  config/env validation or file reads, and never start network/models/browser/DB/
  ToolRuntime/maintenance/optional engines. Help wins over invalid declared root values/duplicates and over version in
  either token order; unknown commands or unknown option spellings remain usage
  errors. Actual token recognition and all routing cases are frozen by the
  `bootstrap` and `bootstrap_cases` tables in contracts.json. Option operands and
  tokens after `--` are never recognized as help/version options. Help/version
  always use their historical text output even with `--output-format json`.
  Runtime imports necessary for current package startup are not a promise of
  import-free root help. No new dependency installation is part of P0.
- **P0-FR07 / inventory:** `capability-manifest.json` classifies every local public
  definition and public method, package re-export and saved AST inventory entry.
  Command workflows, schema/data contracts, composed helpers, implementation
  helpers and Python-only extensions are distinct. Public helper spelling alone
  does not imply a standalone user workflow. In-memory DataFrame objects, callback
  predicates/alert registration, Investigator/FailureHook/transport/resolver/clock
  injection remain Python-only. CLI watch events support consumers; no declarative
  alert rule language is added. Category config/codec helpers compose named parent
  workflows; native signature inspection remains required at each affected phase; this
  inventory does not claim to save complete callable signatures. Native
  functions remain available regardless of CLI classification.

## Acceptance scenarios

P0-SC01 legacy parser/baseline; P0-SC02 complete machine envelope and streams;
P0-SC03 error/exit routing; P0-SC04 strict config and precedence; P0-SC05 help
activation; P0-SC06 inventory completeness/classification. Exact cases and expected
outcomes are in `test-design.md`, before task breakdown.

## Boundaries and compatibility

P0 freezes core grammar and classification, not every later command. Manifest
`grammar_state=reserved` records a target command family only; no P1–P5 argument,
flag, domain schema, retry/cancellation, payload codec or availability contract is
approved here. Those phases must resolve native signatures and parent research
questions at their G1, then G2/G3 before code. Exact integer/boolean/null types,
Decimal as exact decimal string, enum values, ISO-8601 datetime with native offset,
ordered lists and string-key mappings are machine serialization invariants; reject
nonfinite numbers and unsupported values rather than stringify arbitrary objects.
Native evidence/category codecs take precedence and require phase-specific schemas.
No new runtime tests or business implementation precede this slice's G1.

## Workflow

See `tasks.md`, `research.md`, `plan.md`, `status.md`, `verification.md`. Independent
reviewer must record G1 verdict with digests; author cannot approve own contracts.
