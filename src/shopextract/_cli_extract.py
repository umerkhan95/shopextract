"""Explicit P1 Click bindings; native algorithms and portable codecs own facts."""
from __future__ import annotations

import asyncio
import contextlib
import math
import os
import re
import sys
from dataclasses import asdict
from pathlib import Path

import click

from ._cli_core import CliFailure, emit_response, make_response
from ._cli_data import (atomic_json, extraction_data, products_from_value,
                        raw_records, read_json_file)
from ._execution import ExecutionPolicy, LLMBudget, execution_policy
from ._models import Platform
from ._outcomes import assess_extraction_outcome


def execution_options(llm=True):
    options = [click.option('--timeout', type=float, default=None, help='Operation deadline seconds (0,300], bounded default30.'),
               click.option('--browser/--no-browser', default=None, help='Explicit browser activation; bounded default off.')]
    if llm:
        options += [click.option('--allow-llm', is_flag=True, help='Explicitly enable bounded inference; providers may bill timed-out work.'),
                    click.option('--llm-model', default='openai/gpt-4o-mini'),
                    click.option('--llm-key-env', default='SHOPEXTRACT_LLM_API_KEY'),
                    click.option('--llm-temperature', type=float, default=0.2),
                    click.option('--llm-max-calls', type=click.IntRange(1, 10), default=1),
                    click.option('--llm-max-output-tokens', type=click.IntRange(1, 4096), default=512),
                    click.option('--llm-max-input-bytes', type=click.IntRange(1, 32768), default=8192)]
    def decorate(function):
        for option in reversed(options):
            function = option(function)
        return function
    return decorate


def explicit_controls():
    ctx = click.get_current_context()
    from click.core import ParameterSource
    old = {'url', 'max_urls', 'fmt', 'output_path'}
    return any(p.name not in old and ctx.get_parameter_source(p.name) == ParameterSource.COMMANDLINE
               for p in ctx.command.params)


def validate_timeout(value):
    value = 30.0 if value is None else value
    if not math.isfinite(value) or not 0 < value <= 300:
        raise CliFailure('E_USAGE', 'Timeout must be finite and greater than zero, at most300 seconds.')
    return value


def validate_max(value):
    if type(value) is not int or not 1 <= value <= 1000:
        raise CliFailure('E_USAGE', 'Max must be an integer from1 to1000.')
    return value


def validate_url(url):
    from urllib.parse import urlsplit
    parsed = urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
        raise CliFailure('E_USAGE', 'Expected an HTTP(S) URL without embedded credentials.')
    return url


def _browser_preflight():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            if not Path(playwright.chromium.executable_path).is_file():
                raise ImportError()
    except Exception:
        raise CliFailure('E_DEPENDENCY', 'Browser unavailable; install/configure Playwright Chromium yourself, then retry --browser.') from None


def policy_options(options, secrets=()):
    timeout = validate_timeout(options.get('timeout'))
    allow = options.get('allow_llm', False)
    ctx = click.get_current_context()
    from click.core import ParameterSource
    if not allow and any(name.startswith('llm_') and ctx.get_parameter_source(name) == ParameterSource.COMMANDLINE for name in options):
        raise CliFailure('E_USAGE', 'LLM options require explicit --allow-llm.')
    temperature = options.get('llm_temperature', 0.2)
    if not math.isfinite(temperature) or not 0 <= temperature <= 2:
        raise CliFailure('E_USAGE', 'LLM temperature must be finite, from0 to2.')
    model = options.get('llm_model', 'openai/gpt-4o-mini')
    if not re.fullmatch(r'[A-Za-z0-9_]+/[^\s]+', model):
        raise CliFailure('E_USAGE', 'Model must include provider/model without whitespace.')
    variable = options.get('llm_key_env', 'SHOPEXTRACT_LLM_API_KEY')
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', variable):
        raise CliFailure('E_USAGE', 'LLM key environment variable name is invalid.')
    if options.get('browser'):
        _browser_preflight()
    budget = None
    if allow:
        key = os.environ.get(variable, '')
        if not key and not model.startswith(('ollama/', 'ollama_chat/')):
            raise CliFailure('E_USAGE', 'Set the named LLM credential environment variable before --allow-llm.')
        budget = LLMBudget(model, key, temperature, options['llm_max_calls'],
                           options['llm_max_output_tokens'], options['llm_max_input_bytes'])
        secrets = (*secrets, key)
    return ExecutionPolicy(bool(options.get('browser')), budget, tuple(secrets)), timeout


def storefront_options(path, platform):
    if path is None:
        return None
    value = read_json_file(path)
    allowed = {'endpoint','access_token','protocol','token_type','customer_access_token','customer_id','capabilities'}
    if not isinstance(value, dict) or set(value) - allowed or any(not isinstance(v, str) for k,v in value.items() if k!='capabilities'):
        raise CliFailure('E_USAGE', 'Storefront config requires only documented native string options.')
    if 'capabilities' in value:
        from .extractors.magento_graphql import validate_capabilities
        try:validate_capabilities(value['capabilities'])
        except ValueError as exc:raise CliFailure('E_USAGE',str(exc)) from None
        if platform!='magento' or value.get('protocol','graphql')!='graphql':raise CliFailure('E_USAGE','Capabilities require Magento GraphQL only.')
    if 'endpoint' in value:
        validate_url(value['endpoint'])
    if 'protocol' in value and (platform != 'magento' or value['protocol'] not in ('rest','graphql')):
        raise CliFailure('E_USAGE', 'Storefront protocol requires explicit --platform magento and rest/graphql.')
    from .extractors._bigcommerce_auth import AUTH_OPTIONS, validate_auth
    if AUTH_OPTIONS.intersection(value):
        if platform != 'bigcommerce':
            raise CliFailure('E_USAGE', 'Storefront authentication context requires explicit --platform bigcommerce.')
        try:
            validate_auth(value.get('token_type','storefront'), value.get('access_token'), value.get('customer_access_token'), value.get('customer_id'))
        except ValueError:
            raise CliFailure('E_USAGE', 'Invalid BigCommerce authentication context.') from None
    return value


def emit_result(data, partial=False):
    failure = CliFailure('E_PARTIAL', 'Operation returned bounded or incomplete results; inspect metadata.') if partial else None
    emit_response(make_response(data, failure=failure))
    if partial:
        raise click.exceptions.Exit(3)


def run_operation(operation, policy, timeout, *, recover=None):
    async def run():
        with execution_policy(policy, timeout) as state:
            if recover is not None:
                from ._execution import ProgressCheckpoint
                state.progress=ProgressCheckpoint()
            try:
                result = await asyncio.wait_for(operation(), timeout)
            except asyncio.TimeoutError:
                if recover is not None:
                    checkpoint=state.progress.snapshot()
                    if checkpoint is not None:return recover(checkpoint),list(state.warnings)
                raise TimeoutError() from None
            return result, list(state.warnings)
    # stdout carries only the response; crawl4ai 0.8 progress lines otherwise land there.
    with contextlib.redirect_stdout(sys.stderr):
        return asyncio.run(run())


def extract_store(url, max_urls, fmt, output_path, options):
    from . import extract
    validate_url(url); validate_max(max_urls)
    if fmt != 'json':
        raise CliFailure('E_USAGE', 'Bounded machine extraction supports --format json; use export for other formats.')
    if options.get('shop_url'):
        validate_url(options['shop_url'])
    if options.get('enrich_variants') and options.get('platform')!='woocommerce':
        raise CliFailure('E_USAGE','Variant enrichment is only supported with explicit WooCommerce platform.')
    api = storefront_options(options.get('storefront'), options.get('platform'))
    secrets = tuple(v for k,v in (api or {}).items() if k in ('access_token','customer_access_token','customer_id'))
    policy, timeout = policy_options(options, secrets)
    async def operation():
        result = await extract(url, max_urls=max_urls,
            platform=Platform(options['platform']) if options.get('platform') else None,
            shop_url=options.get('shop_url'), enrich_identifiers=options.get('enrich_identifiers',False),
            restore_short_gtin=options.get('restore_short_gtin',False), api_options=api,
            **({'enrich_variants':True} if options.get('enrich_variants') else {}))
        return extraction_data(result)
    data, warnings = run_operation(operation, policy, timeout, recover=extraction_data)
    data['errors'].extend(warnings)
    partial = assess_extraction_outcome(product_count=len(data['products']),
        catalog_complete=data['catalog_complete'], errors=data['errors'],
        incompleteness_reasons=data['incompleteness_reasons']) != 'complete'
    if partial and not data['products']:
        raise CliFailure('E_OPERATION', 'No usable products were extracted; source failed or was incomplete.')
    if options.get('compact'):
        from ._compact_catalog import encode_compact_catalog
        import json
        data=json.loads(encode_compact_catalog(data))
    if output_path:
        failure = CliFailure('E_PARTIAL', 'Operation returned bounded or incomplete results; inspect metadata.') if partial else None
        atomic_json(output_path, make_response(data, failure=failure))
    emit_result(data, partial=partial)


def discover_urls(url, max_urls, platform, options):
    from . import discover
    validate_url(url); validate_max(max_urls)
    policy, timeout = policy_options(options)
    async def operation():
        return await discover(url, max_urls=max_urls, platform=Platform(platform) if platform else None, timeout=timeout)
    urls, _ = run_operation(operation, policy, timeout)
    emit_result({'urls':urls,'count':len(urls),'catalog_complete':None,
                 'incompleteness_reasons':list(getattr(urls,'reasons',['discovery_coverage_unverified'])),
                 'request_count':getattr(urls,'request_count',None)}, partial=True)


def extract_single(url, options):
    from . import extract_one
    from ._evidence import encode_value
    validate_url(url)
    policy, timeout = policy_options(options)
    product, warnings = run_operation(lambda: extract_one(url), policy, timeout)
    if not product:
        raise CliFailure('E_OPERATION', 'No product extracted from the page.')
    emit_result({'product':encode_value(product)}, partial=bool(warnings))


def extract_feed(url, shop_url, max_products, timeout):
    from . import from_feed
    validate_url(url); validate_max(max_products)
    if shop_url:
        validate_url(shop_url)
    async def operation():
        result = await from_feed(url, shop_url=shop_url or '')
        if len(result.products) > max_products:
            result.products = result.products[:max_products]
            result.raw_products = result.raw_products[:max_products]
            result.catalog_complete = False
            result.incompleteness_reasons.append('product_budget_reached')
        return extraction_data(result)
    data, _ = run_operation(operation, ExecutionPolicy(), validate_timeout(timeout))
    if not data['products']:
        raise CliFailure('E_OPERATION', 'No usable products were extracted; source failed or was incomplete.')
    emit_result(data, partial=assess_extraction_outcome(product_count=len(data['products']),
        catalog_complete=data['catalog_complete'], errors=data['errors'],
        incompleteness_reasons=data['incompleteness_reasons']) != 'complete')


def normalize_file(path, platform, shop_url, restore_short_gtin):
    from . import normalize
    from ._portable import product_to_record
    if shop_url:
        validate_url(shop_url)
    records = raw_records(read_json_file(path))
    products=[]; dropped=[]
    for index, record in enumerate(records):
        product = normalize(record, platform=Platform(platform), shop_url=shop_url or '', restore_short_gtin=restore_short_gtin)
        if product is None:
            dropped.append(index)
        else:
            products.append(product_to_record(product))
    emit_result({'products':products,'product_count':len(products),'dropped_indices':dropped})


def quality_file(path):
    from . import QualityScorer
    value = read_json_file(path)
    if isinstance(value, dict) and 'data' in value or isinstance(value, list) and any(isinstance(v,dict) and 'schema_version' in v and 'product' in v for v in value):
        records = [asdict(p) for p in products_from_value(value)]
    else:
        records = raw_records(value)
    scorer = QualityScorer()
    emit_result({'scores':[scorer.score_product(p) for p in records],
                 'batch_score':scorer.score_batch(records),'product_count':len(records)})
