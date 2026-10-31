"""Private shared CLI configuration, bootstrap and single-response policy."""
from __future__ import annotations

import asyncio
import contextvars
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import click


@dataclass(frozen=True)
class CliSettings:
    output_format: str = "legacy"
    diagnostics: str = "normal"


@dataclass
class CliFailure(Exception):
    code: str
    message: str


@dataclass(frozen=True)
class ConfigSource:
    path: Path | None = None
    values: Mapping[str, object] | None = None
    failure: CliFailure | None = None


@dataclass(frozen=True)
class BootstrapScan:
    command_path: tuple[str, ...] | None
    help_target: tuple[str, ...] | None
    version_requested: bool
    explicit_options: tuple[tuple[str, str | None], ...]
    usage_error: str | None


_SETTINGS = contextvars.ContextVar("shopextract_cli_settings", default=CliSettings())
_CHOICES = {"output_format": ("legacy", "json"), "diagnostics": ("normal", "quiet")}
_ROOT = {"--config": "config", "--output-format": "output_format", "--diagnostics": "diagnostics"}
_ENV = {"output_format": "SHOPEXTRACT_OUTPUT_FORMAT", "diagnostics": "SHOPEXTRACT_DIAGNOSTICS"}
_EXITS = {"E_USAGE": 2, "E_CONFIG": 2, "E_PARTIAL": 3, "E_VALIDATION": 4, "E_CANCELLED": 130}
_CODES = {"E_OPERATION", "E_INTERNAL", "E_DEPENDENCY", "E_TIMEOUT", *_EXITS}


def settings() -> CliSettings:
    return _SETTINGS.get()


def scan_bootstrap(argv: Sequence[str], root: click.Group) -> BootstrapScan:
    options = []; path = []; current = root; help_target = None
    version = False; error = None; terminated = False; i = 0
    while i < len(argv):
        token = argv[i]
        if token == "--" and not terminated:
            terminated = True; i += 1; continue
        key, equal, attached = token.partition("=")
        if not terminated and not path and key in _ROOT:
            value = attached if equal else argv[i+1] if i+1 < len(argv) else None
            options.append((_ROOT[key], value)); i += 1 if equal else 2; continue
        if not terminated and token == "--help":
            help_target = tuple(path); i += 1; continue
        if not terminated and not path and token == "--version":
            version = True; i += 1; continue
        if not terminated and token.startswith("-") and token != "-":
            lookup = {alias: p for p in current.params if isinstance(p, click.Option)
                      for alias in (*p.opts, *p.secondary_opts)}
            param = lookup.get(key); compact = False
            if param is None and len(token)>2 and not token.startswith("--"):
                param = lookup.get(token[:2]); compact = param is not None and not param.is_flag
            if param is None:
                error = "Unknown command option."
            elif not param.is_flag and not equal and not compact:
                i += param.nargs
            i += 1; continue
        if isinstance(current, click.Group):
            if token in current.commands:
                path.append(token); current = current.commands[token]; terminated = False
            else:
                error = "Unknown command or option."
        i += 1
    return BootstrapScan(tuple(path) if path else None, help_target, version, tuple(options), error)


def _reject_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key")
        result[key] = value
    return result


def read_cli_config(path: Path) -> Mapping[str, object]:
    try:
        with path.open("rb") as stream:
            raw = stream.read(65537)
        if len(raw) > 65536 or raw.startswith(b"\xef\xbb\xbf"):
            raise ValueError("encoding or size")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_reject_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError("nonfinite")))
        if not isinstance(value, dict) or set(value) - {"schema_version", *_CHOICES}:
            raise ValueError("object or keys")
        if type(value.get("schema_version")) is not int or value["schema_version"] != 1:
            raise ValueError("version")
        for name, choices in _CHOICES.items():
            if name in value and (not isinstance(value[name], str) or value[name] not in choices):
                raise ValueError("setting")
        return value
    except (OSError, ValueError, UnicodeError, RecursionError):
        raise CliFailure("E_CONFIG", "Cannot read a valid CLI config; use schema_version 1 and documented settings.") from None


def select_config(scan: BootstrapScan, env: Mapping[str, str], cwd: Path) -> ConfigSource:
    values = [v for k, v in scan.explicit_options if k == "config"]
    path = values[0] if values else env.get("SHOPEXTRACT_CONFIG")
    if path is None and not values:
        return ConfigSource()
    if not path or path == "-":
        return ConfigSource(failure=CliFailure("E_CONFIG", "Config path must be a nonempty file path."))
    selected = Path(path)
    selected = selected if selected.is_absolute() else cwd / selected
    try:
        return ConfigSource(selected, read_cli_config(selected))
    except CliFailure as exc:
        return ConfigSource(selected, failure=exc)


def error_output_format(scan: BootstrapScan, env: Mapping[str, str], source: ConfigSource) -> str:
    if scan.command_path == ("tools", "serve"):
        return "legacy"
    if scan.command_path in _ENVELOPE_COMMANDS or scan.command_path and scan.command_path[0] in {"maintenance","tools","capabilities","schema","taxonomy"}:
        return "json"
    explicit = next((v for k, v in scan.explicit_options if k == "output_format"), None)
    if explicit in _CHOICES["output_format"]:
        return explicit
    value = source.values.get("output_format") if source.values else None
    if value in _CHOICES["output_format"]:
        return value
    value = env.get(_ENV["output_format"])
    return value if value in _CHOICES["output_format"] else "legacy"


def resolve_settings(scan: BootstrapScan, env: Mapping[str, str], source: ConfigSource) -> CliSettings:
    seen = set(); explicit = {}
    for name, value in scan.explicit_options:
        if name in seen:
            raise CliFailure("E_USAGE", "Root options may be supplied only once.")
        seen.add(name)
        if name in _CHOICES and value not in _CHOICES[name]:
            raise CliFailure("E_USAGE", "Invalid root option value.")
        if value is None:
            raise CliFailure("E_USAGE", "Root option requires a value.")
        explicit[name] = value
    if source.failure:
        raise source.failure
    environment = {}
    for name, variable in _ENV.items():
        if variable in env:
            if env[variable] not in _CHOICES[name]:
                raise CliFailure("E_CONFIG", "Invalid documented CLI environment setting.")
            environment[name] = env[variable]
    merged = {"output_format": "legacy", "diagnostics": "normal", **environment,
              **{k: v for k, v in (source.values or {}).items() if k in _CHOICES},
              **{k: v for k, v in explicit.items() if k in _CHOICES}}
    return CliSettings(**merged)


def make_response(data=None, *, failure: CliFailure | None = None, warnings=()):
    if failure is None:
        return dict(schema_version="1.0", ok=True, data=data, warnings=list(warnings),
                    error=None, completeness="complete")
    if failure.code not in _CODES or (failure.code == "E_PARTIAL" and data is None):
        raise ValueError("invalid CLI response invariant")
    partial = failure.code == "E_PARTIAL"
    return dict(schema_version="1.0", ok=False, data=data if partial else None,
                warnings=list(warnings), error=dict(code=failure.code, message=failure.message,
                retryable=failure.code == "E_TIMEOUT"), completeness="partial" if partial else "unavailable")


def emit_response(response, stream=None, *, compact=False):
    encoded = json.dumps(response, ensure_ascii=False, allow_nan=False, separators=(',', ':') if compact else None)
    click.echo(encoded, file=stream)


def emit_diagnostic(message, configuration=None, stream=None, *, essential=False):
    configuration = configuration or settings()
    if essential or configuration.diagnostics != "quiet":
        click.echo(message, file=stream, err=stream is None)


def failure_exit(failure):
    return _EXITS.get(failure.code, 1)


def emit_success(data):
    emit_response(make_response(data))


# New workflow errors default to the versioned response; legacy defaults remain explicit.

_ENVELOPE_COMMANDS = {(name,) for name in ("extract-one", "feed", "normalize", "quality",
    "compare-catalogs", "match", "match-gtin", "match-pair", "match-evaluate", "analyze-file", "duplicates", "export")}
_ENVELOPE_COMMANDS |= {(group, child) for group, children in {
    "identity": ("assign", "inspect"), "stats": ("distribution", "outliers", "brands"),
    "competitive": ("position", "gaps", "brands"), "images": ("check",)}.items() for child in children}
_ENVELOPE_COMMANDS |= {(group,) for group in ('identity','stats','competitive','images')}


_ENVELOPE_COMMANDS |= {(name,) for name in ('watch','snapshot-save','snapshot-load','resolve','evidence')}
_ENVELOPE_COMMANDS |= {('identity','migrate'),('evidence','inspect'),('evidence','get'),('evidence','prune'),('evidence','bundle'),('evidence','sidecar')}
_ENVELOPE_COMMANDS |= {('evidence',group,action) for group in ('bundle','sidecar') for action in ('create','load')}


_ENVELOPE_COMMANDS |= {('categories',),('categories','record'),('categories','tree'),('categories','policy')}
_ENVELOPE_COMMANDS |= {('categories',name) for name in ('extract','normalize','map','validate')}
_ENVELOPE_COMMANDS |= {('categories',group,name) for group,names in {
    'record':('create','load'),'tree':('fetch','link','load','export'),'policy':('inspect','review')}.items() for name in names}


_ENVELOPE_COMMANDS |= {(name,) for name in ("maintenance","tools","capabilities","schema")}


class CoreCommand(click.Command):
    def invoke(self, ctx):
        # All shipped commands have native contracts; Click validates before callbacks.
        return super().invoke(ctx)


class CoreGroup(click.Group):
    """Bootstrap before Click eager options, then centralized machine failures."""
    command_class = CoreCommand

    def main(self, args=None, prog_name=None, complete_var=None, standalone_mode=True, **extra):
        import os
        argv = list(sys.argv[1:] if args is None else args)
        scan = scan_bootstrap(argv, self)
        source = ConfigSource(); environment = {}; configuration = CliSettings()
        token = None
        try:
            if scan.usage_error is None and (scan.help_target is not None or scan.version_requested):
                bootstrap_args = [*scan.help_target, "--help"] if scan.help_target is not None else ["--version"]
                return super().main(bootstrap_args, prog_name, complete_var, standalone_mode, **extra)
            environment = {name: os.environ[name] for name in ("SHOPEXTRACT_CONFIG", *_ENV.values()) if name in os.environ}
            protocol = scan.command_path == ("tools", "serve")
            source = ConfigSource() if protocol else select_config(scan, environment, Path.cwd())
            if scan.usage_error:
                raise CliFailure("E_USAGE", scan.usage_error)
            configuration = CliSettings() if protocol else resolve_settings(scan, environment, source)
            token = _SETTINGS.set(configuration)
            cleaned = []; i = 0
            while i < len(argv):
                key, equal, _ = argv[i].partition("=")
                if key in _ROOT:
                    i += 1 if equal else 2
                else:
                    cleaned.extend(argv[i:]); break
            result = super().main(cleaned, prog_name, complete_var, standalone_mode=False, **extra)
            if standalone_mode and isinstance(result, int) and result:
                raise SystemExit(result)
            return result
        except (Exception, KeyboardInterrupt) as exc:
            if isinstance(exc, CliFailure):
                failure = exc
            elif isinstance(exc, click.ClickException):
                failure = CliFailure("E_USAGE", "Invalid command arguments; consult command --help.")
            elif isinstance(exc, (KeyboardInterrupt, click.Abort)):
                failure = CliFailure("E_CANCELLED", "Command interrupted.")
            elif isinstance(exc, (TimeoutError, asyncio.TimeoutError)):
                failure = CliFailure("E_TIMEOUT", "Operation timed out.")
            elif isinstance(exc, ImportError):
                failure = CliFailure("E_DEPENDENCY", "A required optional dependency is unavailable; install the documented extra.")
            else:
                failure = CliFailure("E_INTERNAL", "Command failed unexpectedly.")
            mode = error_output_format(scan, environment, source)
            try:
                if mode == "json":
                    emit_response(make_response(failure=failure))
                elif isinstance(exc, click.ClickException):
                    exc.show()
                else:
                    click.echo(f"Error: {failure.message}", err=True)
                code = failure_exit(failure)
            except (OSError, ValueError, TypeError):
                code = 1
                try:
                    click.echo("Error: cannot write CLI response.", err=True)
                except OSError:
                    pass
            if standalone_mode:
                raise SystemExit(code)
            return code
        finally:
            if token is not None:
                _SETTINGS.reset(token)
