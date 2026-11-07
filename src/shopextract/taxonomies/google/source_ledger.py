"""Disjoint source-category accounting over a validated active crosswalk."""
from dataclasses import dataclass

from .contracts import GoogleTaxonomyIntegrityError
from .crosswalk import ShopifyGoogleCrosswalk

SOURCE_STATUSES = ('mapped-single', 'mapped-multiple', 'explicit-upstream-unmapped',
                   'missing-rule', 'invalid-reference', 'version-unavailable')


@dataclass(frozen=True)
class SourceDisposition:
    source_id: str
    status: str
    target_ids: tuple[str, ...]
    reason: str


def audit_source_categories(crosswalk, source_catalog):
    if not isinstance(crosswalk, ShopifyGoogleCrosswalk):
        raise TypeError('Expected validated ShopifyGoogleCrosswalk')
    if (crosswalk.input_taxonomy != 'shopify/' + source_catalog.manifest.release or
            crosswalk.source_catalog_fingerprint != source_catalog.manifest.fingerprint):
        raise GoogleTaxonomyIntegrityError('Crosswalk source catalog differs')
    known = {node.short_id for node in source_catalog.iter_categories()}
    if (not set(crosswalk.rules) <= known or not crosswalk.explicit_exclusions <= known or
            set(crosswalk.rules) & crosswalk.explicit_exclusions):
        raise GoogleTaxonomyIntegrityError('Crosswalk source index is invalid')
    rows = []
    for source in sorted(known):
        targets = crosswalk.rules.get(source, ())
        if targets:
            status = 'mapped-single' if len(targets) == 1 else 'mapped-multiple'
            reason = 'validated-forward-rule'
        elif source in crosswalk.explicit_exclusions:
            status, reason = 'explicit-upstream-unmapped', 'explicit-source-exclusion'
        else:
            status, reason = 'missing-rule', 'no-rule-or-explicit-exclusion'
        rows.append(SourceDisposition(source, status, targets, reason))
    return tuple(rows)
