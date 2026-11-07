"""Opt-in bounded wait for an HTTP 429 that carries Retry-After.

Observed 2026-11-07: Powerhouse and Telemart (Shopify) answered /products.json
with 429 and Retry-After 60; extract failed in under a second with
retry_after_seconds 60 and no way to wait it out.
"""

import json

import pytest
from click.testing import CliRunner

from shopextract._cli_extract import wait_out_rate_limit
from shopextract._execution import ExecutionPolicy, execution_policy
from shopextract._models import ExtractionResult, Product


def limited(retry_after=0.01):
    return ExtractionResult(catalog_complete=False, incompleteness_reasons=["rate_limited"],
                            retry_after_seconds=retry_after)


def attempts(*results):
    calls = []
    async def attempt():
        calls.append(1)
        return results[len(calls) - 1]
    return attempt, calls


async def run(attempt, max_wait, timeout=30):
    with execution_policy(ExecutionPolicy(), timeout) as state:
        result = await wait_out_rate_limit(attempt, max_wait)
        return result, list(state.warnings)


@pytest.mark.asyncio
async def test_without_the_option_a_429_is_returned_at_once():
    attempt, calls = attempts(limited())
    result, warnings = await run(attempt, None)
    assert len(calls) == 1 and result.incompleteness_reasons == ["rate_limited"] and warnings == []


@pytest.mark.asyncio
async def test_retry_after_within_the_cap_waits_and_retries_once():
    recovered = ExtractionResult(products=[Product(title="Fridge")])
    attempt, calls = attempts(limited(), recovered)
    result, warnings = await run(attempt, 60)
    assert len(calls) == 2 and result is recovered
    assert warnings == ["rate_limited: waited 0.01s for Retry-After, then retried once"]


@pytest.mark.asyncio
async def test_a_second_429_is_reported_not_retried_again():
    attempt, calls = attempts(limited(), limited())
    result, _ = await run(attempt, 60)
    assert len(calls) == 2 and result.incompleteness_reasons == ["rate_limited"]


@pytest.mark.asyncio
@pytest.mark.parametrize("retry_after, max_wait, timeout, why", [
    (61, 60, 300, "Retry-After 61s exceeds --wait-rate-limit 60s"),
    (None, 60, 300, "source sent no Retry-After"),
    (60, 120, 30, "does not fit the remaining"),
])
async def test_waits_that_are_unknown_too_long_or_past_the_deadline_are_refused(retry_after, max_wait, timeout, why):
    attempt, calls = attempts(limited(retry_after))
    result, warnings = await run(attempt, max_wait, timeout)
    assert len(calls) == 1 and result.incompleteness_reasons == ["rate_limited"]
    assert len(warnings) == 1 and why in warnings[0]


@pytest.mark.asyncio
async def test_products_or_other_failures_are_never_retried():
    partial = ExtractionResult(products=[Product(title="A")], incompleteness_reasons=["rate_limited"],
                               retry_after_seconds=0.01)
    blocked = ExtractionResult(incompleteness_reasons=["blocked"], retry_after_seconds=0.01)
    for first in (partial, blocked):
        attempt, calls = attempts(first)
        result, _ = await run(attempt, 60)
        assert len(calls) == 1 and result is first


def test_cli_rejects_a_wait_above_120_seconds():
    from shopextract.cli import main
    result = CliRunner().invoke(main, ["--output-format", "json", "extract", "https://fixture.invalid",
                                       "--wait-rate-limit", "121"])
    assert result.exit_code == 2


def test_cli_passes_the_wait_to_extraction(monkeypatch):
    from shopextract import _cli_extract
    from shopextract.cli import main
    seen = {}
    async def fake(attempt, max_wait):
        seen["max_wait"] = max_wait
        return ExtractionResult(products=[Product(title="A", product_url="https://fixture.invalid/a")],
                                catalog_complete=True)
    monkeypatch.setattr(_cli_extract, "wait_out_rate_limit", fake)
    result = CliRunner().invoke(main, ["--output-format", "json", "extract", "https://fixture.invalid",
                                       "--wait-rate-limit", "60", "--timeout", "90"])
    assert seen == {"max_wait": 60}, result.output
    assert json.loads(result.output)["ok"] is True
