"""Explicit Google taxonomy integration; no catalog or network I/O on import."""


def parse_google_taxonomy(*args, **kwargs):
    from .source import parse_google_taxonomy as operation
    return operation(*args, **kwargs)


def prepare_google_taxonomy(*args, **kwargs):
    from .prepare import prepare_google_taxonomy as operation
    return operation(*args, **kwargs)


def prepare_google_snapshot(*args, **kwargs):
    from .source_snapshot import prepare_google_snapshot as operation
    return operation(*args, **kwargs)


def load_google_taxonomy(*args, **kwargs):
    from .loader import load_google_taxonomy as operation
    return operation(*args, **kwargs)


def google_taxonomy_options(*args, **kwargs):
    from .options import google_taxonomy_options as operation
    return operation(*args, **kwargs)


def normalize_with_google_taxonomy(*args, **kwargs):
    from .api import normalize_with_google_taxonomy as operation
    return operation(*args, **kwargs)


def load_shopify_google_crosswalk(*args, **kwargs):
    from .crosswalk import load_shopify_google_crosswalk as operation
    return operation(*args, **kwargs)


def audit_source_categories(*args, **kwargs):
    from .source_ledger import audit_source_categories as operation
    return operation(*args, **kwargs)


def effective_google_category(*args, **kwargs):
    from .api import effective_google_category as operation
    return operation(*args, **kwargs)


def __getattr__(name):
    if name in {'GoogleTaxonomy', 'GoogleCategory', 'GoogleCounts', 'GoogleManifest',
                'GoogleSourceProvenance', 'GoogleTaxonomyError', 'GoogleTaxonomyIntegrityError',
                'GoogleTaxonomyLookupError', 'GoogleTaxonomyPublicationError',
                'GoogleTaxonomyDependencyError'}:
        if name == 'GoogleTaxonomy':
            from .catalog import GoogleTaxonomy
            return GoogleTaxonomy
        from . import contracts
        return getattr(contracts, name)
    if name == 'GoogleClassification':
        from .api import GoogleClassification
        return GoogleClassification
    if name == 'ShopifyGoogleCrosswalk':
        from .crosswalk import ShopifyGoogleCrosswalk
        return ShopifyGoogleCrosswalk
    if name == 'SourceDisposition':
        from .source_ledger import SourceDisposition
        return SourceDisposition
    raise AttributeError(name)


__all__ = [
    'parse_google_taxonomy', 'prepare_google_taxonomy', 'load_google_taxonomy',
    'prepare_google_snapshot',
    'google_taxonomy_options', 'normalize_with_google_taxonomy',
    'load_shopify_google_crosswalk', 'audit_source_categories',
    'effective_google_category', 'GoogleClassification', 'ShopifyGoogleCrosswalk',
    'SourceDisposition', 'GoogleTaxonomy', 'GoogleCategory', 'GoogleCounts',
    'GoogleManifest', 'GoogleSourceProvenance', 'GoogleTaxonomyError',
    'GoogleTaxonomyIntegrityError', 'GoogleTaxonomyLookupError',
    'GoogleTaxonomyPublicationError',
    'GoogleTaxonomyDependencyError',
]
