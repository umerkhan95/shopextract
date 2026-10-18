"""Explicit offline Shopify metadata API; build and network imports stay opt-in."""
from .contracts import (AttributeExtension,AttributeRecord,CategoryAttributeBinding,CategoryRecord,
    CategorySchema,TaxonomyError,TaxonomyIntegrityError,TaxonomyLookupError,TaxonomyPublicationError,ValueRecord)
from .loader import load_shopify_taxonomy
from .contracts import ProductTaxonomySchema
from .options import shopify_taxonomy_options
from .api import normalize_with_shopify_taxonomy, extract_with_shopify_taxonomy
