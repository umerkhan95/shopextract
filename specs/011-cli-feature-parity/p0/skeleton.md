# P0 typed skeleton — G2 candidate

G1 PASS retained; this document declares future seams only. No public production
stub or business implementation is introduced. Author /root/cli_p0_author.

## Ownership and typed declarations

`cli.py` keeps `main` and the nine registered legacy commands. A private
`_cli_core.py` owns shared parsing/config/response policy; domain commands continue
calling native services. Do not add public constructor/workflow APIs for helpers.
A small Click Group subclass at the root owns bootstrap and exception routing.

```python
OutputFormat = Literal["legacy", "json"]
Diagnostics = Literal["normal", "quiet"]
ErrorCode = Literal["E_OPERATION", "E_INTERNAL", "E_DEPENDENCY", "E_TIMEOUT",
                    "E_USAGE", "E_CONFIG", "E_PARTIAL", "E_VALIDATION", "E_CANCELLED"]

@dataclass(frozen=True)
class CliSettings:
    output_format: OutputFormat = "legacy"
    diagnostics: Diagnostics = "normal"

@dataclass(frozen=True)
class BootstrapScan:
    command_path: tuple[str, ...] | None
    help_target: tuple[str, ...] | None
    version_requested: bool
    explicit_options: tuple[tuple[str, str | None], ...]  # ordered, keep duplicates
    usage_error: str | None  # sanitized diagnostic, not arbitrary exception text

@dataclass(frozen=True)
class CliFailure(Exception):
    code: ErrorCode
    message: str  # sanitized at construction/boundary

class ErrorRecord(TypedDict):
    code: ErrorCode
    message: str
    retryable: bool

class Response(TypedDict):
    schema_version: Literal["1.0"]
    ok: bool
    data: object | None
    warnings: list[dict[str, str]]
    error: ErrorRecord | None
    completeness: Literal["complete", "partial", "unavailable"]

def scan_bootstrap(argv: Sequence[str], root: click.Group) -> BootstrapScan: ...
def read_cli_config(path: Path) -> Mapping[str, object]: ...
@dataclass(frozen=True)
class ConfigSource:
    path: Path | None
    values: Mapping[str, object] | None
    failure: CliFailure | None  # retain one failed attempt; never reread on error

def select_config(scan: BootstrapScan, env: Mapping[str, str],
                  cwd: Path) -> ConfigSource: ...
def resolve_settings(scan: BootstrapScan, env: Mapping[str, str],
                     source: ConfigSource) -> CliSettings: ...
def error_output_format(scan: BootstrapScan, env: Mapping[str, str],
                        source: ConfigSource) -> OutputFormat: ...
def make_response(data: object | None, *, failure: CliFailure | None = None,
                  warnings: Sequence[Mapping[str, str]] = ()) -> Response: ...
def emit_response(response: Response, stream: TextIO) -> None: ...
def emit_diagnostic(message: str, settings: CliSettings, stream: TextIO,
                    *, essential: bool = False) -> None: ...
def failure_exit(failure: CliFailure) -> int: ...
```

`make_response` must enforce contracts.json's exact error/retryable/completeness
combinations; E_PARTIAL requires non-null data. Serialization accepts supported
JSON primitives and native typed codecs at later phase boundaries, rejecting
unsupported values/nonfinite floats. Never `default=str` arbitrary objects.
`emit_response` writes one document plus LF; output failure is best-effort sanitized
stderr and exit 1. A response does not contain an exit field: `failure_exit` derives
it from the same fixed contract table, preventing contradictory duplicated state.

## Integration and flow

1. Root Group scans actual tokens against Click registrations without callback
   execution; skip operands, honor `--`, root-only version and nested help. B01–B15
   in contracts.json are the authoritative order/recognition/routing contract.
2. Unknown command/option spelling routes usage first. Otherwise recognized help
   wins over version in either order and bypasses config/env reads and validation.
   No optional runtime imports, network, models, DB or output writes in bootstrap.
3. Normal path selects one config file; read <=65,537 bytes (one-byte over-cap
   detection), strict UTF-8/no BOM/duplicate keys/nonfinite values, exact closed
   schema. Validate selected file and documented present env even when overridden.
   Merge flags > file > env > defaults. Cache one selected-file attempt/result for
   this invocation so error representation does not reread it.
4. Usage/config errors select representation by first explicit format occurrence,
   then valid file/env/default fallback. Later duplicates cannot choose format.
   This fallback never hides the validation failure or dispatches a command.
5. Store immutable settings in Click context; legacy callbacks preserve existing
   command args/options/native calls/default output. Machine branches use the
   shared envelope emitter rather than capturing/parsing legacy stdout. Initial
   core tests exercise existing detect result projection only; later domain
   serializers/flags/payloads require their affected-phase contracts.
6. Native failures translate at root boundary to sanitized CliFailure. Internal
   tracebacks and secrets never become user output; KeyboardInterrupt maps 130,
   known missing optional dependency/timeout operation failure maps 1. No automatic
   retry or unbounded lifecycle is introduced. Later phase job/runtime ownership
   must receive its own reviewed cancellation design.

## Test seams and limits

`tests/test_cli_core.py` invokes the real public `cli.main` using Click CliRunner.
Only `shopextract.detect` (external/native service boundary) is replaced with a
small deterministic async fixture or failure, so parser/config/emitter/bootstrap
remain real. No replacement config parser/emitter/reference implementation is
used. A subprocess driver caps the whole initial focused run at 30 seconds;
imports failing or unavailable dependencies cannot count as intended red.
Legacy registration/default checks and real detect output are separate from
missing-feature checks. P1 full extraction payload/11-product native codec
acceptance remains in its phase; no premature exact extraction schema is implied.

G2 independent review pending. Components/G3 and all production changes follow
G2, not this document. No code stub returns fabricated success.

G3 refinement: emit_diagnostic is a small CLI-owned stderr helper for existing
extract summaries/discover counts. It gates nonessential progress under quiet;
it does not receive raw exceptions and cannot suppress an envelope error record.
No ambient LLM activation change is introduced in P0; affected new extraction
workflows require P1 reviewed activation/budget controls, not env-only consent.

Final review F1 refinement: CoreGroup.command_class uses a small CoreCommand
subclass. Its invoke runs after Click validates the domain command context and
before callback/native execution, so temporary deferred-machine availability
checks cannot hide missing/type/file E_USAGE errors. `_MACHINE_COMMANDS` contains
canonical command-path tuples; extend only with affected-phase reviewed payload
bindings. This refines the existing validation-before-dispatch order, not grammar.
