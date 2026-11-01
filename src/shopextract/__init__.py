"""shopextract -- Extract, compare, and monitor product data from any e-commerce store.

Public API:
    detect(url) -> PlatformResult
    discover(url, ...) -> list[str]
    extract(url, ..., llm_api_key=, llm_model=) -> ExtractionResult
    extract_one(url, ..., llm_api_key=, llm_model=) -> dict
    from_feed(feed_url, ...) -> ExtractionResult
    compare(query, stores) -> ComparisonResult
    compare_catalogs(store_a, store_b) -> CatalogDiff
    fuzzy_match(products_a, products_b) -> list[tuple]
    match_gtin(gtin, products) -> list[dict]
    snapshot(url) -> int
    changes(domain) -> list[Change]
    price_history(domain, product_title) -> list[tuple]
    watch(url) -> AsyncGenerator[Change]
    analyze(url) -> CatalogStats
    analyze_products(products) -> CatalogStats
    price_distribution(products) -> dict[str, int]
    outliers(products) -> list[dict]
    brand_breakdown(products) -> dict[str, float]
    price_position(my_product, competitors) -> PricePosition
    assortment_gaps(my_store, competitors) -> AssortmentGaps
    brand_coverage(catalogs) -> dict[str, dict[str, int]]
    validate(products, marketplace) -> ValidationReport
    check_images(products) -> list[ImageIssue]
    find_duplicates(products, method, threshold) -> list[tuple]
    to_csv(products, path) -> None
    to_json(products, path, indent) -> None
    to_feed(products, path, format) -> None
    to_dataframe(products) -> pandas.DataFrame
    to_parquet(products, path) -> None"""
from importlib import import_module as _import_module

_EXPORTS = {'detect': ('._detect', 'detect'),
 'discover': ('._discover', 'discover'),
 'extract': ('._extract', 'extract'),
 'extract_one': ('._extract', 'extract_one'),
 'from_feed': ('._extract', 'from_feed'),
 'ResolutionPolicy': ('._resolution', 'ResolutionPolicy'),
 'resolve_fields': ('._resolution', 'resolve_fields'),
 'resolution_references': ('._resolution', 'resolution_references'),
 'Evidence': ('._models', 'Evidence'),
 'FieldObservation': ('._models', 'FieldObservation'),
 'FieldResolution': ('._models', 'FieldResolution'),
 'SupportState': ('._models', 'SupportState'),
 'TrustContract': ('._models', 'TrustContract'),
 'ValidatedConfidence': ('._models', 'ValidatedConfidence'),
 'factual_paths': ('._models', 'factual_paths'),
 'trust_view': ('._models', 'trust_view'),
 'AssortmentGaps': ('._models', 'AssortmentGaps'),
 'CatalogDiff': ('._models', 'CatalogDiff'),
 'CatalogStats': ('._models', 'CatalogStats'),
 'Change': ('._models', 'Change'),
 'ChangeType': ('._models', 'ChangeType'),
 'ComparisonResult': ('._models', 'ComparisonResult'),
 'ExtractionResult': ('._models', 'ExtractionResult'),
 'ExtractionTier': ('._models', 'ExtractionTier'),
 'ExtractorResult': ('._models', 'ExtractorResult'),
 'ImageIssue': ('._models', 'ImageIssue'),
 'Match': ('._models', 'Match'),
 'NewProduct': ('._models', 'NewProduct'),
 'Platform': ('._models', 'Platform'),
 'PlatformResult': ('._models', 'PlatformResult'),
 'PriceChange': ('._models', 'PriceChange'),
 'PricePosition': ('._models', 'PricePosition'),
 'Product': ('._models', 'Product'),
 'RemovedProduct': ('._models', 'RemovedProduct'),
 'ValidationIssue': ('._models', 'ValidationIssue'),
 'ValidationReport': ('._models', 'ValidationReport'),
 'Variant': ('._models', 'Variant'),
 'assign_identity': ('.identity', 'assign_identity'),
 'migrate_snapshot_identities': ('.identity', 'migrate_snapshot_identities'),
 'MatchDecision': ('.compare.identity_match', 'MatchDecision'),
 'MatchRelation': ('.compare.identity_match', 'MatchRelation'),
 'classify_match': ('.compare.identity_match', 'classify_match'),
 'match_products': ('.compare.identity_match', 'match_products'),
 'normalized_attributes': ('.compare.identity_match', 'normalized_attributes'),
 'normalize': ('._normalize', 'normalize'),
 'QualityScorer': ('._quality', 'QualityScorer'),
 'analyze': ('.analyze', 'analyze'),
 'analyze_products': ('.analyze', 'analyze_products'),
 'assortment_gaps': ('.analyze', 'assortment_gaps'),
 'brand_breakdown': ('.analyze', 'brand_breakdown'),
 'brand_coverage': ('.analyze', 'brand_coverage'),
 'outliers': ('.analyze', 'outliers'),
 'price_distribution': ('.analyze', 'price_distribution'),
 'price_position': ('.analyze', 'price_position'),
 'compare': ('.compare', 'compare'),
 'compare_catalogs': ('.compare', 'compare_catalogs'),
 'evaluate_matching': ('.compare', 'evaluate_matching'),
 'fuzzy_match': ('.compare', 'fuzzy_match'),
 'match_gtin': ('.compare', 'match_gtin'),
 'to_csv': ('.export', 'to_csv'),
 'to_dataframe': ('.export', 'to_dataframe'),
 'to_feed': ('.export', 'to_feed'),
 'to_json': ('.export', 'to_json'),
 'to_parquet': ('.export', 'to_parquet'),
 'changes': ('.monitor', 'changes'),
 'price_history': ('.monitor', 'price_history'),
 'snapshot': ('.monitor', 'snapshot'),
 'watch': ('.monitor', 'watch'),
 'EvidenceLookup': ('.monitor.evidence', 'EvidenceLookup'),
 'PruneReport': ('.monitor.evidence', 'PruneReport'),
 'get_evidence': ('.monitor.evidence', 'get_evidence'),
 'load_snapshot': ('.monitor.evidence', 'load_snapshot'),
 'prune_evidence': ('.monitor.evidence', 'prune_evidence'),
 'save_snapshot': ('.monitor.evidence', 'save_snapshot'),
 'create_evidence_bundle': ('.export._bundle', 'create_evidence_bundle'),
 'create_evidence_sidecar': ('.export._bundle', 'create_evidence_sidecar'),
 'load_evidence_bundle': ('.export._bundle', 'load_evidence_bundle'),
 'load_evidence_sidecar': ('.export._bundle', 'load_evidence_sidecar'),
 'read_evidence_bundle': ('.export._bundle', 'read_evidence_bundle'),
 'write_evidence_bundle': ('.export._bundle', 'write_evidence_bundle'),
 'check_images': ('.validate', 'check_images'),
 'find_duplicates': ('.validate', 'find_duplicates'),
 'validate': ('.validate', 'validate')}

__all__ = ['ResolutionPolicy',
 'resolve_fields',
 'resolution_references',
 'Evidence',
 'FieldObservation',
 'FieldResolution',
 'SupportState',
 'TrustContract',
 'ValidatedConfidence',
 'factual_paths',
 'trust_view',
 'evaluate_matching',
 'assign_identity',
 'migrate_snapshot_identities',
 'MatchDecision',
 'MatchRelation',
 'classify_match',
 'match_products',
 'normalized_attributes',
 'detect',
 'discover',
 'extract',
 'extract_one',
 'from_feed',
 'normalize',
 'compare',
 'compare_catalogs',
 'fuzzy_match',
 'match_gtin',
 'EvidenceLookup',
 'PruneReport',
 'save_snapshot',
 'load_snapshot',
 'get_evidence',
 'prune_evidence',
 'create_evidence_bundle',
 'load_evidence_bundle',
 'write_evidence_bundle',
 'read_evidence_bundle',
 'create_evidence_sidecar',
 'load_evidence_sidecar',
 'snapshot',
 'changes',
 'price_history',
 'watch',
 'analyze',
 'analyze_products',
 'price_distribution',
 'outliers',
 'brand_breakdown',
 'price_position',
 'assortment_gaps',
 'brand_coverage',
 'validate',
 'check_images',
 'find_duplicates',
 'to_csv',
 'to_json',
 'to_feed',
 'to_dataframe',
 'to_parquet',
 'AssortmentGaps',
 'CatalogStats',
 'CatalogDiff',
 'Change',
 'ChangeType',
 'ComparisonResult',
 'ExtractionResult',
 'ExtractionTier',
 'ExtractorResult',
 'ImageIssue',
 'Match',
 'NewProduct',
 'Platform',
 'PlatformResult',
 'PriceChange',
 'PricePosition',
 'Product',
 'RemovedProduct',
 'ValidationIssue',
 'ValidationReport',
 'Variant',
 'QualityScorer']
__version__ = '0.1.2'


def __getattr__(name):
    try:
        module, attribute = _EXPORTS[name]
    except KeyError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
    value = getattr(_import_module(module, __name__), attribute)
    globals()[name] = value
    return value


def __dir__():
    return sorted(set(globals()) | set(_EXPORTS))

# These inexpensive package/function names collide with child module attributes.
# Bind actual functions up front so normal submodule imports cannot replace them.
for _name in ('analyze', 'compare', 'validate'):
    __getattr__(_name)
del _name
