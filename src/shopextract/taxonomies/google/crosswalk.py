"""Strict explicit directional Shopify-to-Google crosswalk loading."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
from types import MappingProxyType

from .contracts import GoogleTaxonomyIntegrityError
from .source_document import decode_source_document as _decode

MAX_SOURCE_BYTES = 8 * 1024 * 1024


@dataclass(frozen=True)
class ShopifyGoogleCrosswalk:
    input_taxonomy: str
    output_taxonomy: str
    source_sha256: str
    source_catalog_fingerprint: str
    target_catalog_fingerprint: str
    rules: object
    explicit_exclusions: frozenset[str]
    duplicate_rows: int = 0


def load_shopify_google_crosswalk(source_file, *, source_catalog, target_catalog,
                                 expected_sha256):
    if not isinstance(expected_sha256, str) or not re.fullmatch('[0-9a-f]{64}', expected_sha256):
        raise GoogleTaxonomyIntegrityError('Expected crosswalk SHA256 is required')
    with Path(source_file).open('rb') as handle:
        data = handle.read(MAX_SOURCE_BYTES + 1)
    if len(data) > MAX_SOURCE_BYTES:
        raise GoogleTaxonomyIntegrityError('Crosswalk source byte limit exceeded')
    actual = sha256(data).hexdigest()
    if actual != expected_sha256:
        raise GoogleTaxonomyIntegrityError('Crosswalk source SHA256 differs')
    value = _decode(data)
    keys = {'input_taxonomy', 'output_taxonomy', 'rules', 'unmapped_product_category_ids'}
    if not isinstance(value, dict) or set(value) != keys:
        raise GoogleTaxonomyIntegrityError('Invalid crosswalk root fields')
    if (value['input_taxonomy'] != 'shopify/' + source_catalog.manifest.release or
            value['output_taxonomy'] != 'google/' + target_catalog.manifest.version):
        raise GoogleTaxonomyIntegrityError('Crosswalk catalog version pair differs')
    if not isinstance(value['rules'], list) or not isinstance(value['unmapped_product_category_ids'], list):
        raise GoogleTaxonomyIntegrityError('Crosswalk rules and exclusions must be arrays')
    rules = {}
    duplicates = 0
    for row in value['rules']:
        if (not isinstance(row, dict) or set(row) != {'input', 'output'} or
            not isinstance(row['input'], dict) or set(row['input']) != {'product_category_id'} or
            not isinstance(row['output'], dict) or set(row['output']) != {'product_category_id'}):
            raise GoogleTaxonomyIntegrityError('Invalid crosswalk row fields')
        source = row['input']['product_category_id']
        targets = row['output']['product_category_id']
        if not isinstance(source, str) or not source or source_catalog.category(source) is None:
            raise GoogleTaxonomyIntegrityError('Unknown crosswalk source category')
        if source_catalog.category(source).short_id != source:
            raise GoogleTaxonomyIntegrityError('Crosswalk source requires canonical short ID')
        if not isinstance(targets, list) or not targets:
            raise GoogleTaxonomyIntegrityError('Crosswalk targets must be a nonempty array')
        for target in targets:
            if (not isinstance(target, str) or not re.fullmatch('[0-9]+', target) or
                    target_catalog.category(target) is None):
                raise GoogleTaxonomyIntegrityError('Unknown crosswalk target category')
        if len(set(targets)) != len(targets):
            raise GoogleTaxonomyIntegrityError('Duplicate crosswalk target ID')
        targets = tuple(sorted(targets, key=int))
        if source in rules:
            if rules[source] != targets:
                raise GoogleTaxonomyIntegrityError('Conflicting duplicate crosswalk source row')
            duplicates += 1
        rules[source] = targets
    exclusions = set()
    for source in value['unmapped_product_category_ids']:
        if (not isinstance(source, str) or not source or source_catalog.category(source) is None or
                source_catalog.category(source).short_id != source or source in exclusions or source in rules):
            raise GoogleTaxonomyIntegrityError('Invalid or conflicting crosswalk source exclusion')
        exclusions.add(source)
    return ShopifyGoogleCrosswalk(value['input_taxonomy'], value['output_taxonomy'], actual,
        source_catalog.manifest.fingerprint, target_catalog.manifest.fingerprint,
        MappingProxyType(dict(sorted(rules.items()))), frozenset(exclusions), duplicates)
