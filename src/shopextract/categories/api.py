"""Category binding over compatible native sources or opt-in production extraction."""
from dataclasses import replace
from importlib import import_module
from typing import Any
from .._models import Platform, ExtractionResult, ExtractionTier
from .._normalize import normalize
from .config import validate_options, options_digest
from .contracts import (AdapterContext, CategoryError, CategoryOptions, CategorizedProduct,
                        CategorizedExtractionResult, NativeCategoryError)
from .mapping import map_categories
from .portable import bind_product


def normalize_with_categories(raw: dict, platform: Platform = Platform.GENERIC,
                              shop_url: str = '', *, category_options: CategoryOptions,
                              restore_short_gtin: bool = False) -> CategorizedProduct | None:
    validate_options(category_options)
    if platform != category_options.scope.platform:
        raise CategoryError('Category platform differs from source scope')
    product = normalize(raw, platform, shop_url or category_options.scope.store_url,
                        restore_short_gtin=restore_short_gtin)
    if product is None:
        return None
    observations = _observe_categories(raw, platform, category_options.scope, category_options.limits)
    return _bind_categories(product, observations, category_options)


def _observe_categories(raw, platform, scope, limits):
    """Shared bounded source translation; taxonomy helpers derive finite policy from it."""
    method = (raw.get('_capture') or {}).get('method', '')
    generic = (method.startswith(('json_ld','opengraph','css','llm','feed_')) or
               raw.get('_source') == 'google_feed' or 'offers' in raw or 'og:title' in raw or
               'Product' in str(raw.get('@type','')))
    name = 'generic' if generic else platform.value
    errors = []
    for error in raw.get('_category_diagnostics', [])[:100]:
        path = error.get('path') if isinstance(error,dict) else None
        code = error.get('code','native_source_error') if isinstance(error,dict) else 'native_source_error'
        errors.append(NativeCategoryError(tuple(path) if isinstance(path,list) else None, str(code)[:64]))
    context = AdapterContext(scope, limits, tuple(errors))
    adapter = import_module('.adapters.' + name, __package__)
    observations = adapter.observe_categories(raw, context=context)
    remaining = limits.terms
    bounded = []
    for observation in observations:
        terms = observation.terms[:remaining]
        clipped = len(terms) != len(observation.terms)
        remaining -= len(terms)
        bounded.append(replace(observation, terms=terms, completeness='partial' if clipped else observation.completeness,
                               reason='category_budget_reached' if clipped else observation.reason))
    observations = tuple(bounded)
    return observations


def _bind_categories(product, observations, category_options):
    """Bind once using the existing mapper, digest and evidence contract."""
    mappings = map_categories(observations, options=category_options)
    return bind_product(product, category_options.scope, observations, mappings,
                        options_digest(category_options), limits=category_options.limits)


def _validate_production_source(url: str, store_url: str) -> None:
    """Validate selected input scope before extraction; no redirect guarantee."""
    from urllib.parse import urlsplit, unquote
    from ..tools.security import normalized
    from ..tools.contracts import ToolError
    try:
        target, origin, _, _ = normalized(url)
        source, expected_origin, _, _ = normalized(store_url)
        if origin != expected_origin:
            raise ValueError()
        def source_path(value):
            path = urlsplit(value).path
            for _ in range(3):
                decoded = unquote(path,errors='strict')
                if decoded == path:
                    break
                path = decoded
            if unquote(path,errors='strict') != path or '\\' in path or any(part in ('.','..') for part in path.split('/')):
                raise ValueError()
            return path.rstrip('/')
        path, base = source_path(target), source_path(source)
        if base and path != base and not path.startswith(base + '/'):
            raise ValueError()
    except (ValueError, TypeError, ToolError):
        raise CategoryError('Category production source differs from store scope') from None


async def extract_with_categories(url: str, *, category_options: CategoryOptions,
                                  source_mode: str = 'native',
                                  **extraction_options: Any) -> CategorizedExtractionResult:
    """Bind native source categories, optionally using the full production chain.

    Native remains the compatible source-specific default. Production delegates
    tier selection to extract(); the caller's execution policy controls browser
    and inference eligibility. Neither mode guesses missing source categories.
    """
    validate_options(category_options)
    if source_mode not in ('native', 'production'):
        raise CategoryError('Unknown category extraction source mode')
    allowed = {'platform','max_urls','shop_url','llm_api_key','llm_model','llm_temperature',
               'enrich_identifiers','restore_short_gtin','api_options'}
    if set(extraction_options) - allowed:
        raise CategoryError('Unknown category extraction option')
    if source_mode == 'native' and extraction_options.get('llm_api_key'):
        raise CategoryError('Category mode uses native/static sources only')
    platform = extraction_options.get('platform') or category_options.scope.platform
    if platform != category_options.scope.platform:
        raise CategoryError('Category extraction platform scope mismatch')
    maximum = extraction_options.get('max_urls',20)
    if type(maximum) is not int or maximum <= 0:
        raise CategoryError('max_urls must be positive')
    shop = extraction_options.get('shop_url') or category_options.scope.store_url
    api_options = extraction_options.get('api_options')
    if api_options is not None and (not isinstance(api_options,dict) or
            set(api_options) - {'endpoint','access_token','protocol','token_type','customer_access_token','customer_id'} or
            any(not isinstance(v,str) for v in api_options.values())):
        raise CategoryError('Invalid storefront API options')
    if source_mode == 'production':
        from .._extract import extract
        from .._scope import catalog_scope
        if catalog_scope(shop,platform) != catalog_scope(category_options.scope.store_url,platform):
            raise CategoryError('Category extraction shop scope mismatch')
        _validate_production_source(url, category_options.scope.store_url)
        kwargs = dict(extraction_options)
        kwargs.update(platform=platform,shop_url=shop,include_categories=True)
        result = await extract(url,**kwargs)
    elif platform == Platform.GENERIC:
        from ..extractors._storefront import request
        from ..extractors.feed import GoogleFeedExtractor
        from ..extractors.unified import UnifiedCrawlExtractor
        import httpx
        async with httpx.AsyncClient(timeout=30) as client:
            response = await request(client,'GET',url)
        kind = response.headers.get('content-type','')
        if url.lower().endswith(('.xml','.csv','.tsv')) or 'xml' in kind or 'csv' in kind:
            parser = GoogleFeedExtractor._parse_xml if 'xml' in kind or url.lower().endswith('.xml') else GoogleFeedExtractor._parse_csv
            raw = parser(response.text,str(response.url),include_categories=True)
        else:
            raw = UnifiedCrawlExtractor._extract_structured_from_html(response.text,str(response.url),include_categories=True)
        result = ExtractionResult(raw_products=raw[:maximum], platform=platform, catalog_complete=False,
                                  incompleteness_reasons=['catalog_coverage_unverified'])
    else:
        from .._extract import _try_api_extraction
        native = await _try_api_extraction(url,platform,max_products=maximum,
            enrich_identifiers=extraction_options.get('enrich_identifiers',False), api_options=api_options,
            include_categories=category_options.limits.terms > 0, category_mode=True)
        if native is None:
            result = ExtractionResult(platform=platform,catalog_complete=False,errors=['Native source unavailable'])
        else:
            result = ExtractionResult(raw_products=native.products[:maximum], platform=platform,
                tier=ExtractionTier.API, catalog_complete=native.complete,
                incompleteness_reasons=[] if native.complete else [native.completeness_reason or 'source_incomplete'],
                errors=[native.error] if native.error else [])
    companions = []
    for raw in result.raw_products:
        value = normalize_with_categories(raw,platform,shop,category_options=category_options,
            restore_short_gtin=extraction_options.get('restore_short_gtin',False))
        if value is not None:
            companions.append(value)
    result.products = [v.product for v in companions]
    if len(companions) != len(result.raw_products):
        result.catalog_complete = False
        result.incompleteness_reasons.append('normalization_dropped_records')
    return CategorizedExtractionResult(result, tuple(companions), tuple(result.errors))
