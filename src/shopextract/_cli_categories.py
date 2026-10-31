"""Explicit bounded category CLI; native libraries own facts, mapping and trees."""
from __future__ import annotations

import functools
import json
from dataclasses import replace
from urllib.parse import urlsplit, unquote

import click

from ._cli_core import CliFailure, CoreCommand, emit_response, make_response
from ._cli_data import (read_json_file, raw_records, categorized_from_value, atomic_json,
                        MAX_BYTES, MAX_RECORDS, category_policy_from_value)
from ._cli_extract import run_operation, validate_timeout, validate_url, storefront_options, execution_options, policy_options
from ._cli_monitor import check_destination
from ._execution import ExecutionPolicy
from ._portable import product_to_record


def encoded(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')


def bound(value, *, newline=False):
    if len(encoded(value)) + int(newline) > MAX_BYTES:
        raise CliFailure('E_USAGE','Category result exceeds CLI1MiB; reduce input or limits.')


def category_output(data, *, partial=False, validation=False, failure=False, warnings=()):
    response=make_response(data,warnings=warnings)
    code='E_OPERATION' if failure else 'E_VALIDATION' if validation else 'E_PARTIAL' if partial else None
    if code:
        response.update(ok=False,error=dict(code=code,message='Inspect category outcome and reasons.',retryable=False),
                        completeness='partial' if partial else 'unavailable')
    bound(response,newline=True)
    emit_response(response,compact=True)
    if code:raise click.exceptions.Exit(1 if failure else 4 if validation else 3)


def write_artifact(value,path):
    bound(value)
    atomic_json(path,value,compact=True)


def sources(destination,*paths):
    if paths.count('-')>1:
        raise CliFailure('E_USAGE','Only one input may read stdin.')
    if destination=='-':
        raise CliFailure('E_USAGE','Omit --output for response stdout; artifact outputs require a path.')
    check_destination(destination,*paths)


def native_errors(function):
    @functools.wraps(function)
    def wrapped(*args,**kwargs):
        try:return function(*args,**kwargs)
        except CliFailure:raise
        except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError):
            raise CliFailure('E_USAGE','Invalid category config, scope, record or native limits; consult category schema.') from None
    return wrapped


def options_file(path):
    from .categories._codec import typed
    from .categories.contracts import CategoryOptions
    from .categories.config import validate_options
    options=typed(CategoryOptions,read_json_file(path));validate_options(options)
    return options


def runtime_file(path):
    from .categories.config import runtime_from_record
    return runtime_from_record(read_json_file(path))


def categorized_file(path, *, runtime=None):
    data=read_json_file(path);values=categorized_from_value(data)
    policy=category_policy_from_value(data,values)
    if policy is not None:
        from .categories.config import runtime_record
        if runtime is None or policy['config']!=runtime_record(runtime):
            raise CliFailure('E_USAGE','Policy-bearing records require matching policy review or catalog export; use bare records for transforms.')
    return values


def require_scope(values,options,*,digest=False):
    from .categories.config import options_digest
    expected=options_digest(options) if digest else None
    if any(v.scope!=options.scope or digest and v.config_digest!=expected for v in values):
        raise CliFailure('E_USAGE','Category records differ from trusted scope or policy.')


def category_data(values,**metadata):
    from .categories.portable import categorized_product_to_record
    return dict(products=[product_to_record(v.product) for v in values],
        categorized_products=[categorized_product_to_record(v) for v in values],product_count=len(values),**metadata)


def publish(values,destination,**metadata):
    data=category_data(values,**metadata)
    bound(data)
    if destination:
        write_artifact(data['categorized_products'],destination)
        category_output(dict(output=destination,product_count=len(values)))
    else:category_output(data)


def remap(values,options):
    from .categories.mapping import map_categories
    from .categories.config import options_digest
    from .categories.portable import bind_product
    require_scope(values,options)
    return [bind_product(v.product,v.scope,v.observations,map_categories(v.observations,options=options),
        options_digest(options),limits=options.limits) for v in values]


def tree_file(path):
    from .categories.woo_tree import woo_tree_from_record
    value=read_json_file(path)
    if isinstance(value,dict) and 'data' in value:
        if value.get('schema_version')!='1.0' or not isinstance(value['data'],dict):raise ValueError()
        value=value['data']['tree']
    return woo_tree_from_record(value)


def tree_publish(tree,destination):
    from .categories.woo_tree import woo_tree_to_record
    record=woo_tree_to_record(tree)
    data=dict(tree=record,outcome=tree.outcome,reasons=list(tree.reasons),node_count=len(tree.nodes),
        confirmed_empty=tree.confirmed_empty)
    # Validate complete response first, even when only an artifact will be written.
    bound(data)
    if destination:
        write_artifact(record,destination)
        data=dict(output=destination,outcome=tree.outcome,reasons=list(tree.reasons),node_count=len(tree.nodes),confirmed_empty=tree.confirmed_empty)
    category_output(data,partial=tree.outcome=='partial',failure=tree.outcome in ('unavailable','malformed'))


def _scope_path(path):
    """Reject ambiguous paths before the HTTP stack/server normalizes them."""
    for _ in range(4):
        decoded=unquote(path,errors='strict')
        if decoded==path:break
        path=decoded
    else:
        raise CliFailure('E_USAGE','Category store paths have excessive URL encoding.')
    if '\\' in path or any(segment in ('.','..') for segment in path.split('/')):
        raise CliFailure('E_USAGE','Category store paths cannot contain traversal segments.')
    return path.rstrip('/')


def register(main):
    @main.group('categories',cls=click.Group)
    def categories():
        """Native scoped category records, mappings, trees and local policy review."""

    def option_input(function):return click.option('--options','options_path',required=True,help='Exact native CategoryOptions JSON.')(function)
    def destination(function):return click.option('--output','destination',help='Atomic native artifact file; omit for response stdout.')(function)

    @categories.command('normalize',cls=CoreCommand)
    @click.argument('file')
    @option_input
    @destination
    @click.option('--restore-short-gtin',is_flag=True)
    @native_errors
    def normalize(file,options_path,destination,restore_short_gtin):
        from .categories.api import normalize_with_categories
        sources(destination,file,options_path);options=options_file(options_path)
        records=raw_records(read_json_file(file));values=[]
        for raw in records:
            value=normalize_with_categories(raw,options.scope.platform,options.scope.store_url,
                category_options=options,restore_short_gtin=restore_short_gtin)
            if value is not None:values.append(value)
        publish(values,destination,input_count=len(records),dropped_count=len(records)-len(values))

    @categories.command('extract',cls=CoreCommand)
    @click.argument('url')
    @option_input
    @destination
    @click.option('--storefront-config',type=click.Path(),help='Bounded native storefront endpoint/auth JSON.')
    @click.option('--enrich-identifiers',is_flag=True)
    @click.option('--restore-short-gtin',is_flag=True)
    @click.option('--max-products',type=click.IntRange(1,1000),default=20,show_default=True)
    @click.option('--source-mode',type=click.Choice(['native','production']),default='production',show_default=True)
    @execution_options()
    @native_errors
    def extract(url,options_path,destination,max_products,timeout,storefront_config,enrich_identifiers,restore_short_gtin,source_mode,**execution):
        from .categories.api import extract_with_categories
        sources(destination,*[p for p in (options_path,storefront_config) if p is not None]);options=options_file(options_path)
        api=storefront_options(storefront_config,options.scope.platform.value)
        validate_url(url)
        if source_mode=='native' and execution.get('allow_llm'):
            raise CliFailure('E_USAGE','Native category mode does not support LLM; select production.')
        secrets=tuple(v for k,v in (api or {}).items() if k in ('access_token','customer_access_token','customer_id'))
        policy,timeout=policy_options(dict(execution,timeout=timeout),secrets)
        source,scope=urlsplit(url),urlsplit(options.scope.store_url)
        prefix=_scope_path(scope.path)
        source_path=_scope_path(source.path)
        if (source.scheme,source.netloc)!=(scope.scheme,scope.netloc) or not (source_path==prefix or source_path.startswith(prefix+'/')):
            raise CliFailure('E_USAGE','Extraction URL differs from category store origin/base path.')
        result,warnings=run_operation(lambda:extract_with_categories(url,category_options=options,source_mode=source_mode,max_urls=max_products,api_options=api,
            enrich_identifiers=enrich_identifiers,restore_short_gtin=restore_short_gtin),policy,timeout)
        data=category_data(result.products,catalog_complete=result.result.catalog_complete,
            incompleteness_reasons=list(result.result.incompleteness_reasons),
            input_count=len(result.result.raw_products),dropped_count=len(result.result.raw_products)-len(result.products))
        if not result.products:raise CliFailure('E_OPERATION','No usable category products; source unavailable or normalization failed.')
        bound(data)
        if destination:
            write_artifact(data['categorized_products'],destination)
            data=dict(output=destination,product_count=len(result.products),catalog_complete=result.result.catalog_complete,
                incompleteness_reasons=list(result.result.incompleteness_reasons))
        category_output(data,partial=not result.result.catalog_complete or bool(result.diagnostics),warnings=warnings)

    @categories.command('map',cls=CoreCommand)
    @click.argument('file')
    @option_input
    @destination
    @native_errors
    def mapping(file,options_path,destination):
        sources(destination,file,options_path)
        options=options_file(options_path);values=categorized_file(file)
        publish(remap(values,options),destination)

    @categories.command('validate',cls=CoreCommand)
    @click.argument('file')
    @option_input
    @native_errors
    def validate(file,options_path):
        from .categories.mapping import map_categories
        from .categories.validation import validate_observations
        sources(None,file,options_path);options=options_file(options_path);values=categorized_file(file)
        require_scope(values,options,digest=True)
        for value in values:
            validate_observations(value.observations,options.limits)
            if value.mappings!=map_categories(value.observations,options=options):raise ValueError()
        category_output(dict(valid=True,product_count=len(values)))

    @categories.group('record',cls=click.Group)
    def record():
        """Create/reload native bound categorized records."""
    @record.command('create',cls=CoreCommand)
    @click.argument('file')
    @option_input
    @destination
    @native_errors
    def create(file,options_path,destination):
        sources(destination,file,options_path)
        options=options_file(options_path);publish(remap(categorized_file(file),options),destination)
    @record.command('load',cls=CoreCommand)
    @click.argument('file')
    @destination
    @native_errors
    def load(file,destination):
        sources(destination,file);publish(categorized_file(file),destination)

    @categories.group('tree',cls=click.Group)
    def tree():
        """Opt-in bounded Woo tree acquisition and captured membership lookup."""
    @tree.command('fetch',cls=CoreCommand)
    @option_input
    @destination
    @click.option('--limits','limits_path',help='Exact native WooTreeLimits JSON with reduced ceilings.')
    @click.option('--timeout',type=float,default=30.,show_default=True)
    @native_errors
    def fetch(options_path,destination,limits_path,timeout):
        from .categories.woo_tree import fetch_woocommerce_category_tree,WooTreeLimits,_validate_limits
        from .categories._codec import typed
        sources(destination,*[p for p in (options_path,limits_path) if p is not None])
        options=options_file(options_path);timeout=validate_timeout(timeout)
        limits=WooTreeLimits(response_bytes=MAX_BYTES,retained_bytes=MAX_BYTES)
        if limits_path:
            data=read_json_file(limits_path)
            if not isinstance(data,dict) or type(data.get('seconds')) not in (int,float):raise ValueError()
            data=dict(data,seconds=float(data['seconds']));limits=typed(WooTreeLimits,data)
        _validate_limits(limits)
        if limits.retained_bytes>MAX_BYTES or limits.response_bytes>MAX_BYTES:raise ValueError()
        limits=replace(limits,seconds=min(limits.seconds,timeout))
        value,_=run_operation(lambda:fetch_woocommerce_category_tree(options.scope,limits=limits),ExecutionPolicy(),timeout)
        tree_publish(value,destination)

    @tree.command('load',cls=CoreCommand)
    @click.argument('file')
    @destination
    @native_errors
    def tree_load(file,destination):
        sources(destination,file);tree_publish(tree_file(file),destination)
    @tree.command('export',cls=CoreCommand)
    @click.argument('file')
    @click.option('--output','destination',required=True)
    @native_errors
    def tree_export(file,destination):
        sources(destination,file);tree_publish(tree_file(file),destination)
    @tree.command('link',cls=CoreCommand)
    @click.argument('tree_path')
    @click.argument('file')
    @destination
    @native_errors
    def link(tree_path,file,destination):
        from .categories.woo_tree import link_tree_memberships
        from .categories._codec import wire
        sources(destination,tree_path,file);tree=tree_file(tree_path);values=categorized_file(file)
        if any(v.scope!=tree.scope for v in values):raise CliFailure('E_USAGE','Tree and product category scopes differ.')
        links=[wire(link) for v in values for link in link_tree_memberships(tree,v.observations)]
        data=category_data(values,links=links,tree_outcome=tree.outcome,tree_reasons=list(tree.reasons))
        if destination:
            write_artifact(data,destination)
            data=dict(output=destination,link_count=len(links),tree_outcome=tree.outcome,tree_reasons=list(tree.reasons))
        category_output(data,partial=tree.outcome=='partial',failure=tree.outcome in ('unavailable','malformed'))

    @categories.group('policy',cls=click.Group)
    def policy():
        """Deterministic local policy identity and review reasons; no advisor."""
    @policy.command('inspect',cls=CoreCommand)
    @click.option('--config','config_path',required=True,help='Exact native CategoryRuntimeConfig JSON.')
    @native_errors
    def inspect(config_path):
        from .categories.maintenance import category_policy_digest
        from .categories.config import runtime_record,options_digest
        config=runtime_file(config_path)
        category_output(dict(config=runtime_record(config),policy_digest=category_policy_digest(config),options_digest=options_digest(config.options)))
    @policy.command('review',cls=CoreCommand)
    @click.argument('file')
    @click.option('--config','config_path',required=True)
    @click.option('--profile',help='Operator-selected profile identifier; no automatic selection.')
    @native_errors
    def review(file,config_path,profile):
        from .categories.maintenance import category_policy_digest,category_review_reasons
        from .categories.config import runtime_record
        sources(None,file,config_path);config=runtime_file(config_path);values=categorized_file(file,runtime=config)
        require_scope(values,config.options,digest=True)
        reasons=[list(category_review_reasons(v,selected_profile=profile,config=config)) for v in values]
        data=category_data(values,review_reasons=reasons,policy_digest=category_policy_digest(config),config=runtime_record(config))
        category_output(data,validation=any(reasons))
