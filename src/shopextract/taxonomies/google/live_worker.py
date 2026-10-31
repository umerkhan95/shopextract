"""Machine worker delegating extraction to the native Shopextract orchestrator."""
import asyncio
from contextlib import redirect_stdout
import json
import math
import sys

from ..._execution import ExecutionPolicy, execution_policy, safe_error
from ..._models import Platform
from .live_profile import in_scope


async def produce(payload):
    if (not isinstance(payload, dict) or set(payload) !=
            {'url', 'platform', 'shop_url', 'max_products', 'timeout'} or
            type(payload['max_products']) is not int or not 1 <= payload['max_products'] <= 4 or
            type(payload['timeout']) not in (int, float) or
            not math.isfinite(payload['timeout']) or not 0 < payload['timeout'] <= 120 or
            not in_scope(payload['url'], payload['shop_url'])):
        raise ValueError('Invalid production worker input')
    from ... import extract
    with execution_policy(ExecutionPolicy(browser=True, llm=None), payload['timeout']) as state:
        platform = None if payload['platform'] == 'auto' else Platform(payload['platform'])
        result = await asyncio.wait_for(extract(payload['url'], platform=platform,
            shop_url=payload['shop_url'], max_urls=1, include_categories=True), payload['timeout'])
        raw = result.raw_products[:payload['max_products']]
        return dict(schema_version=1, raw_products=raw, tier=result.tier.value, platform=result.platform.value,
            urls_attempted=result.urls_attempted, urls_succeeded=result.urls_succeeded,
            errors=[safe_error(str(e))[:240] for e in [*result.errors, *state.warnings]][:20],
            catalog_complete=result.catalog_complete,
            incompleteness_reasons=result.incompleteness_reasons[:20],
            truncated=len(raw) != len(result.raw_products),
            browser=dict(enabled=True, attempted=None),
            llm=dict(enabled=False, reason='no_configured_budget'))


def main():
    try:
        source = sys.stdin.buffer.read(65537)
        if len(source) > 65536:
            raise ValueError('Worker input too large')
        payload = json.loads(source)
        with redirect_stdout(sys.stderr):
            value = asyncio.run(produce(payload))
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False).encode()
        if len(encoded) > 1048576:
            raise ValueError('Worker result too large')
        sys.stdout.buffer.write(encoded)
    except Exception:
        # Native browser/provider diagnostics may contain sensitive source data.
        # The report gets an explicit failure, never a fabricated empty success.
        sys.stdout.write('{"error":"production_extraction_failed"}')
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
