"""P0 acceptance: real Click entry point, deterministic native service boundary."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from jsonschema import Draft202012Validator

import shopextract
from shopextract import cli
from shopextract._models import Platform

P0 = Path(__file__).resolve().parents[1] / "specs/011-cli-feature-parity/p0"
URL = "https://fixture.invalid/product"


@pytest.fixture
def native(monkeypatch):
    calls = []

    async def detect(url, **kwargs):
        calls.append((url, kwargs))
        return SimpleNamespace(platform=Platform.SHOPIFY, confidence=0.9,
                               signals=["synthetic platform marker"])

    monkeypatch.setattr(shopextract, "detect", detect)
    for name in ("SHOPEXTRACT_CONFIG", "SHOPEXTRACT_OUTPUT_FORMAT", "SHOPEXTRACT_DIAGNOSTICS"):
        monkeypatch.delenv(name, raising=False)
    return calls


def invoke(argv, env=None):
    return CliRunner().invoke(cli.main, argv, env=env or {})


def envelope(result, code=None):
    # Fail explicitly for absent root controls, not a secondary JSONDecodeError.
    assert "No such option: --output-format" not in result.output, result.output
    assert "No such option: --config" not in result.output, result.output
    assert result.stdout.strip().startswith("{"), result.output
    value = json.loads(result.stdout)
    Draft202012Validator(json.loads((P0 / "response.schema.json").read_text())).validate(value)
    if code is not None:
        assert value["error"]["code"] == code
    return value


def test_legacy_command_options_and_defaults():
    expected = {"extract", "detect", "discover", "compare", "snapshot", "changes",
                "history", "analyze", "validate"}
    assert expected <= set(cli.main.commands)
    def option(command, name):
        return next(p for p in cli.main.commands[command].params if p.name == name)
    assert option("extract", "max_urls").default == 20
    assert set(option("extract", "max_urls").opts) == {"--max", "-n"}
    assert option("extract", "fmt").default == "json"
    assert list(option("extract", "fmt").type.choices) == ["csv", "json"]
    assert option("discover", "max_urls").default == 100
    assert option("analyze", "max_urls").default == 20
    assert option("compare", "stores").multiple and option("compare", "stores").required
    assert [p.name for p in cli.main.commands["history"].params] == ["domain", "product", "db", "canonical_id"]
    assert option("validate", "marketplace").default == "google_shopping"


def test_legacy_detect_stays_native_json(native):
    result = invoke(["detect", URL])
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout) == {"platform": "shopify", "confidence": 0.9,
                                       "signals": ["synthetic platform marker"]}
    assert native == [(URL, {})]


def test_machine_detect_uses_one_complete_envelope(native):
    result = invoke(["--output-format", "json", "detect", URL])
    assert result.exit_code == 0, result.output
    value = envelope(result)
    assert value["ok"] is True and value["completeness"] == "complete"
    assert value["data"]["platform"] == "shopify"
    assert native == [(URL, {})]


def test_machine_missing_argument_is_structured_before_dispatch(native):
    result = invoke(["--output-format", "json", "detect"])
    assert result.exit_code == 2
    value = envelope(result, "E_USAGE")
    assert value["data"] is None and value["error"]["retryable"] is False
    assert native == []


@pytest.mark.parametrize("content", [b"{}", b"[]", b'{"schema_version":true}',
    b'{"schema_version":1,"unknown":0}', b'{"schema_version":1,"schema_version":1}',
    b'{"schema_version":1,"output_format":NaN}', b'\xef\xbb\xbf{"schema_version":1}', b'\xff'])
def test_strict_config_rejected_before_dispatch(tmp_path, native, content):
    path = tmp_path / "cli.json"
    path.write_bytes(content)
    result = invoke(["--output-format", "json", "--config", str(path), "detect", URL])
    assert result.exit_code == 2
    envelope(result, "E_CONFIG")
    assert native == []


@pytest.mark.parametrize("size,valid", [(65535, True), (65536, True), (65537, False)])
def test_config_byte_cap(tmp_path, native, size, valid):
    path = tmp_path / "cli.json"
    body = b'{"schema_version":1}'
    path.write_bytes(body + b" " * (size - len(body)))
    result = invoke(["--output-format", "json", "--config", str(path), "detect", URL])
    assert result.exit_code == (0 if valid else 2), result.output
    envelope(result, None if valid else "E_CONFIG")
    assert len(native) == (1 if valid else 0)


@pytest.mark.parametrize("explicit,file_mode,env_mode,expected_json", [
    (None, "json", "legacy", True), ("legacy", "json", "json", False),
    (None, None, "json", True), ("json", "legacy", "legacy", True)])
def test_format_precedence(tmp_path, native, explicit, file_mode, env_mode, expected_json):
    path = tmp_path / "cli.json"
    settings = {"schema_version": 1}
    if file_mode is not None:
        settings["output_format"] = file_mode
    path.write_text(json.dumps(settings))
    args = ["--config", str(path)]
    if explicit is not None:
        args += ["--output-format", explicit]
    result = invoke(args + ["detect", URL], {"SHOPEXTRACT_OUTPUT_FORMAT": env_mode})
    assert result.exit_code == 0, result.output
    value = json.loads(result.stdout)
    assert ("schema_version" in value) is expected_json
    assert native == [(URL, {})]


def test_invalid_overridden_env_is_still_error(native):
    result = invoke(["--output-format", "json", "detect", URL],
                    {"SHOPEXTRACT_OUTPUT_FORMAT": "invalid"})
    assert result.exit_code == 2
    envelope(result, "E_CONFIG")
    assert native == []


@pytest.mark.parametrize("first,second,json_expected", [("json", "legacy", True),
                                                        ("legacy", "json", False)])
def test_repeated_format_first_occurrence_routes_error(native, first, second, json_expected):
    result = invoke(["--output-format", first, "--output-format", second, "detect", URL])
    assert result.exit_code == 2
    if json_expected:
        envelope(result, "E_USAGE")
    else:
        assert not result.stdout.strip()
        assert "No such option" not in result.stderr
    assert native == []


@pytest.mark.parametrize("argv", [["--version", "--help"], ["--help", "--version"],
    ["--output-format", "invalid", "--help"],
    ["--config", "missing.json", "detect", "--help"]])
def test_recognized_help_bypasses_config_env(argv, native, monkeypatch):
    original = Path.open
    def guarded(path, *args, **kwargs):
        assert path.name != "missing.json", "help must not read selected config"
        return original(path, *args, **kwargs)
    monkeypatch.setattr(Path, "open", guarded)
    result = invoke(argv, {"SHOPEXTRACT_CONFIG": "missing.json",
                           "SHOPEXTRACT_OUTPUT_FORMAT": "invalid"})
    assert result.exit_code == 0, result.output
    assert "Usage:" in result.stdout and "Options:" in result.stdout
    assert native == []


def test_option_looking_operand_after_sentinel_is_native_url(native):
    result = invoke(["detect", "--", "--help"])
    assert result.exit_code == 0, result.output
    assert native == [("--help", {})]


def test_machine_internal_failure_sanitizes_exception(native, monkeypatch):
    async def broken(*args, **kwargs):
        raise RuntimeError("SECRET-provider-token")
    monkeypatch.setattr(shopextract, "detect", broken)
    result = invoke(["--output-format", "json", "detect", URL])
    assert result.exit_code == 1, result.output
    envelope(result, "E_INTERNAL")
    assert "SECRET-provider-token" not in result.output
    assert "Traceback" not in result.output


def test_invalid_explicit_format_uses_valid_env_for_error(native):
    result = invoke(["--output-format", "invalid", "detect", URL],
                    {"SHOPEXTRACT_OUTPUT_FORMAT": "json"})
    assert result.exit_code == 2
    envelope(result, "E_USAGE")
    assert native == []


@pytest.mark.parametrize("argv", [["--help", "unknown"], ["--version", "unknown"],
                                  ["--", "--help"]])
def test_unknown_command_stays_usage_error_before_bootstrap(native, argv):
    result = invoke(argv)
    assert result.exit_code == 2, result.output
    assert native == []


@pytest.mark.parametrize("invalid", [False, True])
def test_selected_config_is_read_once_success_and_parse_failure(tmp_path, native, monkeypatch, invalid):
    path = tmp_path / "selected.json"
    path.write_text("{broken" if invalid else '{"schema_version":1,"output_format":"json"}')
    original = Path.open
    attempts = []
    def tracked(selected, *args, **kwargs):
        if selected == path:
            attempts.append(selected)
            assert len(attempts) == 1, "selected config reread during routing"
        return original(selected, *args, **kwargs)
    monkeypatch.setattr(Path, "open", tracked)
    result = invoke(["--config", str(path), "detect", URL],
                    {"SHOPEXTRACT_OUTPUT_FORMAT": "json"})
    assert result.exit_code == (2 if invalid else 0), result.output
    envelope(result, "E_CONFIG" if invalid else None)
    assert len(attempts) == 1
    assert len(native) == (0 if invalid else 1)


def test_selected_config_failed_open_is_not_retried(tmp_path, native, monkeypatch):
    path = tmp_path / "unreadable.json"
    original = Path.open
    attempts = []
    def denied(selected, *args, **kwargs):
        if selected == path:
            attempts.append(selected)
            raise PermissionError("SECRET-unreadable-path")
        return original(selected, *args, **kwargs)
    monkeypatch.setattr(Path, "open", denied)
    result = invoke(["--output-format", "json", "--config", str(path), "detect", URL])
    assert result.exit_code == 2
    envelope(result, "E_CONFIG")
    assert len(attempts) == 1 and native == [] and not path.exists()
    assert "SECRET" not in result.output


@pytest.mark.parametrize("failure_kind", ["config", "internal"])
def test_quiet_preserves_machine_errors(tmp_path, native, monkeypatch, failure_kind):
    args = ["--output-format", "json", "--diagnostics", "quiet"]
    if failure_kind == "config":
        path = tmp_path / "invalid.json"
        path.write_text('{"schema_version":true}')
        args += ["--config", str(path)]
    else:
        async def broken(*args, **kwargs):
            raise RuntimeError("SECRET-native-error")
        monkeypatch.setattr(shopextract, "detect", broken)
    result = invoke(args + ["detect", URL])
    assert result.exit_code == (2 if failure_kind == "config" else 1)
    envelope(result, "E_CONFIG" if failure_kind == "config" else "E_INTERNAL")
    assert not result.stderr and "SECRET" not in result.output


@pytest.mark.parametrize("mode", ["normal", "quiet"])
def test_real_diagnostic_helper_and_public_discover_consumer(native, monkeypatch, mode):
    from io import StringIO
    from shopextract._cli_core import CliSettings, emit_diagnostic, emit_response, make_response
    diagnostic = StringIO()
    data = StringIO()
    emit_diagnostic("synthetic progress", CliSettings("json", mode), diagnostic)
    emit_response(make_response([]), data)
    assert bool(diagnostic.getvalue()) is (mode == "normal")
    assert json.loads(data.getvalue())["data"] == []
    async def discover(url, **kwargs):
        return ["https://fixture.invalid/a", "https://fixture.invalid/b"]
    monkeypatch.setattr(shopextract, "discover", discover)
    result = invoke(["--diagnostics", mode, "discover", URL])
    assert result.exit_code == 0, result.output
    assert result.stdout.splitlines() == ["https://fixture.invalid/a", "https://fixture.invalid/b"]
    assert ("2 URLs discovered" in result.stderr) is (mode == "normal")


def test_option_looking_config_operand_is_not_help(tmp_path, native, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = invoke(["--config", "--help", "detect", URL])
    assert result.exit_code == 2
    assert "Usage:" not in result.stdout and not result.stdout
    assert "config" in result.stderr.lower() and native == []


def test_help_overrides_repeated_options_without_config_or_env_read(native, monkeypatch):
    import os
    from shopextract import _cli_core
    def prohibited(*args, **kwargs):
        raise AssertionError("bootstrap attempted config/env read")
    monkeypatch.setattr(_cli_core, "select_config", prohibited)
    original = os._Environ.__getitem__
    def guarded(env, key):
        if key.startswith("SHOPEXTRACT_"):
            prohibited()
        return original(env, key)
    monkeypatch.setattr(os._Environ, "__getitem__", guarded)
    result = invoke(["--output-format", "json", "--output-format", "legacy", "--help"])
    assert result.exit_code == 0, result.output
    assert "Usage:" in result.stdout and "--config" in result.stdout
    assert native == []


@pytest.mark.parametrize("args,json_expected", [
    (["--output-format", "json", "detect", "--version"], True),
    (["--output-format", "invalid", "--output-format", "json", "detect", URL], False)])
def test_remaining_bootstrap_error_routes(native, args, json_expected):
    result = invoke(args)
    assert result.exit_code == 2, result.output
    if json_expected:
        envelope(result, "E_USAGE")
    else:
        assert not result.stdout and "Error:" in result.stderr
    assert native == []


def test_settings_and_selected_file_do_not_leak_between_invocations(tmp_path, native):
    path = tmp_path / "settings.json"
    path.write_text('{"schema_version":1,"output_format":"json"}')
    runner = CliRunner()
    first = runner.invoke(cli.main, ["--config", str(path), "detect", URL])
    second = runner.invoke(cli.main, ["detect", URL])
    assert first.exit_code == second.exit_code == 0
    envelope(first)
    assert "schema_version" not in json.loads(second.stdout)
    assert len(native) == 2


@pytest.mark.parametrize("exception,code,exit_code,retryable", [
    (TimeoutError("SECRET-timeout"), "E_TIMEOUT", 1, True),
    (ImportError("SECRET-dependency"), "E_DEPENDENCY", 1, False),
    (KeyboardInterrupt(), "E_CANCELLED", 130, False)])
def test_public_native_failure_classes_and_settings_reset(native, monkeypatch, exception,
                                                          code, exit_code, retryable):
    async def fail(*args, **kwargs):
        raise exception
    original = shopextract.detect
    monkeypatch.setattr(shopextract, "detect", fail)
    result = invoke(["--output-format", "json", "detect", URL])
    assert result.exit_code == exit_code, result.output
    value = envelope(result, code)
    assert value["error"]["retryable"] is retryable
    assert "SECRET" not in result.output and "Traceback" not in result.output
    monkeypatch.setattr(shopextract, "detect", original)
    legacy = invoke(["detect", URL])
    assert legacy.exit_code == 0 and "schema_version" not in json.loads(legacy.stdout)


def test_real_emitter_broken_stream_fallback_and_settings_reset(native, monkeypatch):
    from functools import partial
    from shopextract import _cli_core
    class BrokenStream:
        def write(self, value):
            raise BrokenPipeError("SECRET-broken-stream")
        def flush(self):
            pass
    original = _cli_core.emit_response
    monkeypatch.setattr(_cli_core, "emit_response", partial(original, stream=BrokenStream()))
    result = invoke(["--output-format", "json", "detect", URL])
    assert result.exit_code == 1, result.output
    assert not result.stdout and "cannot write CLI response" in result.stderr
    assert "SECRET" not in result.output and "Traceback" not in result.output
    monkeypatch.setattr(_cli_core, "emit_response", original)
    legacy = invoke(["detect", URL])
    assert legacy.exit_code == 0 and "schema_version" not in json.loads(legacy.stdout)


@pytest.mark.parametrize("case", ["missing-url", "bad-integer", "missing-path", "valid-deferred"])
def test_phase_gate_follows_click_argument_validation(tmp_path, native, monkeypatch, case):
    attempts = []
    def prohibited(*args, **kwargs):
        attempts.append(args)
        raise AssertionError("native adapter must not run")
    monkeypatch.setattr(cli, "_extract", prohibited)
    monkeypatch.setattr(cli, "_discover", prohibited)
    monkeypatch.setattr(cli, "_validate_file", prohibited)
    # A controlled callback failure verifies validation precedes invocation.
    from shopextract._cli_core import CoreCommand
    import click
    def rejected(url):
        from shopextract._cli_core import CliFailure
        raise CliFailure('E_OPERATION', 'Controlled unavailable operation.')
    temporary = CoreCommand('deferred-test', callback=rejected, params=[click.Argument(['url'])])
    monkeypatch.setitem(cli.main.commands, 'deferred-test', temporary)
    commands = {"missing-url": ["extract"],
                "bad-integer": ["discover", URL, "--max", "bad"],
                "missing-path": ["validate", str(tmp_path / "missing.json")],
                "valid-deferred": ["deferred-test", URL]}
    result = invoke(["--output-format", "json", *commands[case]])
    assert result.exit_code == (1 if case == "valid-deferred" else 2), result.output
    envelope(result, "E_OPERATION" if case == "valid-deferred" else "E_USAGE")
    assert attempts == [] and native == []


def test_cli_failure_allows_runtime_traceback():
    from shopextract._cli_core import CliFailure
    failure=CliFailure('E_USAGE','Synthetic invalid input')
    try:raise failure
    except CliFailure as caught:trace=caught.__traceback__
    failure.__traceback__=trace
    assert failure.__traceback__ is trace and failure.code=='E_USAGE'


def test_cli_failure_survives_execution_context():
    from shopextract._cli_core import CliFailure
    from shopextract._execution import ExecutionPolicy,current_policy,execution_policy
    prior=current_policy();failure=CliFailure('E_USAGE','Synthetic invalid input')
    with pytest.raises(CliFailure) as caught:
        with execution_policy(ExecutionPolicy()):raise failure
    assert caught.value is failure and current_policy() is prior
