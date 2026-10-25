# P0 reusable components — G3 candidate

Author `/root/cli_p0_author`, 2026-10-25. G1/G2 PASS remain recorded in reviews.md.
This document owns reuse/boundary decisions; no production implementation added.

| Component / owner | Reuse and concrete consumers | Responsibility / error contract |
| --- | --- | --- |
| Existing Click command declarations, cli.py | Existing nine command callbacks, Click argument/option conversion and help formatting, existing console entry point | Preserve names/aliases/defaults/native dispatch; reuse Click errors for recognized domain parsing after bootstrap. Group subclass adds the frozen root ordering, not a second domain parser. |
| Bootstrap scanner, private _cli_core.py | Inspect actual Click registered params and commands; root help/version, normal dispatch, machine usage routing | Track ordered explicit options without losing repetitions; skip declared operands and honor --. Recognize spelling/path before eager help. No env/config/native runtime work until bootstrap decision; no command callback execution to discover grammar. |
| Strict config source + settings, private _cli_core.py | stdlib JSON decoding, pathlib bounded binary read, immutable ConfigSource; success settings resolution and failure output routing | One selected-file attempt per invocation, <=65,537 bytes read for cap detection. Keep strict decoder/schema failure on ConfigSource; both resolver/error selector consume it. No config discovery/merge/plugin loader. Validate documented env and selected file even when overridden. No reusable generic application config framework. |
| Envelope/error emitter, private _cli_core.py | stdlib JSON encoder with allow_nan=False, Click streams, fixed contracts.json policy; success/usage/config/internal-failure branches | Single response+LF; exact retryable/completeness/error invariants and exit policy. Sanitize at exception boundary; no arbitrary exception message/default=str. Quiet gates nonessential CLI diagnostics; it cannot hide machine error records. Broken stdout is best-effort stderr/exit1. |
| Native service adapters, existing cli.py bodies | Existing detect/discover/extract/compare/snapshot/changes/history/analyze/validate services and native result projections | Legacy remains old flow. Explicit machine branch calls native services directly and emitter once; never parse/capture legacy text as data. Core detect projection in tests reuses existing fields. Other domain codecs/expanded payloads/flags freeze at affected phase, not a shared reflection serializer. |
| Native portable codecs, existing _portable/_evidence/category modules | P1–P5 native evidence/category and typed report consumers, per-phase reviewed adapters | Reserve actual binding to phase schemas. Reuse supported codecs instead of flattening evidence or arbitrary dataclass dumps; preserve identity/missing support. No new duplicate codec/model hierarchy in P0. |

## Cohesion and lifecycle

The small shared core serves three current needs: root bootstrap/settings, command
response emission and errors. Domain services do not depend on it. Click context
owns immutable settings plus the single ConfigSource for one invocation; nothing
is cached globally or written to user config. No owned background thread, process,
async loop or tool runtime is added. Existing asyncio.run native dispatch stays
within each synchronous command; future phase lifecycle contracts own cancellation
of browser/tool/job resources. Bootstrap does not instantiate those components.

The fixed runtime contract table belongs to `_cli_core.py`; tests compare public
responses to checked-in schemas/contracts. Runtime must not depend on files under
specs/ or on development-only jsonschema. For the three-key flat config, explicit
strict type/key validation is sufficient, with tests enforcing published schema;
no new runtime dependency or duplicated domain schema engine is justified.

No common file writer, generic request router, plugin system, generic native
object serializer or future-domain command framework is needed for these core
consumers. Root registrations can later move into domain modules only when those
phase seams are reviewed; this stage does not preempt that structure.

## Verification ownership and reviewed gaps

D3 initial public-CLI red evidence is reused, not rerun. D7-gap design in
test-design.md covers successful/failed single-read, quiet/error streams and B
cases missing from the first 32 checks before adding those tests. Fixture author
uses actual production loader/bootstrap/emitter once implemented, mocks only
native external results or deliberate I/O failures. Independent reviewer checks
these cases and limits before stress execution. Existing red is sufficient to
begin implementation after G3; expanded final coverage still blocks completion.

G3 independent review pending; author does not approve own component model.

Final F1 refinement: CoreCommand.invoke owns the temporary machine-availability
check after Click argument conversion and before native callback invocation.
CoreGroup remains bootstrap/settings/error owner. This reuses Click lifecycle
rather than duplicating argument validators or inserting per-domain guards.
