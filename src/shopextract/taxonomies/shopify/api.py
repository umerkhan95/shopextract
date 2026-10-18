"""Ergonomic orchestration over the existing capture, category mapper and binder."""
from ..._models import Platform, ExtractionResult, ExtractionTier
from ..._normalize import normalize
from ...categories.api import _observe_categories, _bind_categories
from ...categories.contracts import CategoryScope, CategoryLimits, CategorizedExtractionResult
from .identity import NAMESPACE
from .loader import load_shopify_taxonomy
from .options import shopify_taxonomy_options


def normalize_with_shopify_taxonomy(raw, *, platform, shop_url, taxonomy=None,mappings=(),allow_unknown_source_version=False):
    taxonomy=taxonomy or load_shopify_taxonomy()
    scope=CategoryScope(platform,shop_url)
    product=normalize(raw,platform,shop_url)
    if product is None:return None
    observations=_observe_categories(raw,platform,scope,CategoryLimits())
    ids=set(target for rule in mappings for target in rule.target_ids)
    for observation in observations:
        for term in observation.terms:
            if term.ref.namespace==NAMESPACE and term.ref.native_id:
                node=taxonomy.category(term.ref.native_id)
                if node is not None:ids.add(node.short_id)
    options=shopify_taxonomy_options(scope,category_ids=sorted(ids),mappings=mappings,
        allow_unknown_source_version=allow_unknown_source_version,taxonomy=taxonomy)
    return _bind_categories(product,observations,options)


async def extract_with_shopify_taxonomy(url, *, taxonomy=None,mappings=(),allow_unknown_source_version=False,
                                      max_products=20,storefront=None):
    from ..._extract import _try_api_extraction
    from urllib.parse import urlsplit
    taxonomy=taxonomy or load_shopify_taxonomy()
    if type(max_products) is not int or not 1<=max_products<=100:raise ValueError('max_products must be 1..100')
    parts=urlsplit(url)
    # The caller configures merchant identity, including any store basepath.
    shop_url=url.rstrip('/')
    shopify_taxonomy_options(CategoryScope(Platform.SHOPIFY,shop_url),taxonomy=taxonomy,
        category_ids=tuple(t for rule in mappings for t in rule.target_ids),mappings=mappings)
    native=await _try_api_extraction(url,Platform.SHOPIFY,max_products=max_products,
        category_mode=True,include_categories=True,shopify_storefront=storefront)
    result=ExtractionResult(platform=Platform.SHOPIFY,tier=ExtractionTier.API,catalog_complete=False)
    if native is None:
        result.errors.append('Native source unavailable')
        return CategorizedExtractionResult(result,(),tuple(result.errors))
    result.raw_products=native.products
    companions=tuple(v for raw in native.products if (v:=normalize_with_shopify_taxonomy(raw,
        platform=Platform.SHOPIFY,shop_url=shop_url,taxonomy=taxonomy,mappings=mappings,
        allow_unknown_source_version=allow_unknown_source_version)) is not None)
    result.products=[v.product for v in companions]
    result.catalog_complete=native.complete and len(companions)==len(native.products)
    if native.error:result.errors.append(native.error)
    return CategorizedExtractionResult(result,companions,tuple(result.errors))
