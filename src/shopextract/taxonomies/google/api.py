"""Google classification through existing capture, mapper and strict binder."""
from dataclasses import dataclass
from hashlib import sha256
import json
from ..._models import Platform
from ..._normalize import normalize
from ...categories.api import _observe_categories, _bind_categories
from ...categories.contracts import CategoryScope, CategoryLimits, CategorySelector, MappingRule
from .contracts import GoogleTaxonomyIntegrityError
from .loader import load_google_taxonomy
from .options import NAMESPACE, google_taxonomy_options


def normalize_with_google_taxonomy(raw, *, platform=Platform.GENERIC, shop_url='',
                                   taxonomy=None, mappings=(), crosswalk=None,
                                   allow_unknown_source_version=False):
    taxonomy = taxonomy or load_google_taxonomy()
    if type(allow_unknown_source_version) is not bool:
        raise TypeError('Expected explicit boolean source version permission')
    if crosswalk is not None:
        from .crosswalk import ShopifyGoogleCrosswalk
        if not isinstance(crosswalk, ShopifyGoogleCrosswalk):
            raise TypeError('Expected validated ShopifyGoogleCrosswalk')
        if crosswalk.target_catalog_fingerprint != taxonomy.manifest.fingerprint:
            raise GoogleTaxonomyIntegrityError('Crosswalk target catalog differs')
    scope = CategoryScope(platform, shop_url)
    # Validate trusted supplied mappings and scope before normalization.
    rules = list(mappings)
    ids = {target for rule in rules for target in rule.target_ids}
    google_taxonomy_options(scope, category_ids=ids, mappings=rules, taxonomy=taxonomy)
    product = normalize(raw, platform, shop_url)
    if product is None:
        return None
    observations = _observe_categories(raw, platform, scope, CategoryLimits())
    generated = {}
    for observation in observations:
        for term in observation.terms:
            source_version = term.ref.taxonomy_version
            if source_version is None and not allow_unknown_source_version:
                continue
            candidates = []
            if term.ref.namespace == NAMESPACE:
                if source_version not in (None, taxonomy.manifest.version):
                    continue
                if term.ref.native_id is not None:
                    node = taxonomy.category(term.ref.native_id)
                    if node is not None:
                        candidates.append(('native_id', term.ref.native_id, (node.id,), 'google'))
                else:
                    for fact in term.facts:
                        if fact.binding.facet == 'raw_path' and isinstance(fact.raw_value, str):
                            node = taxonomy.resolve_path(fact.raw_value)
                            if node is not None:
                                candidates.append(('raw_path', fact.raw_value, (node.id,), 'google'))
            elif (crosswalk is not None and
                  term.ref.namespace == 'shopify:standard_product_taxonomy' and
                  source_version in (None, crosswalk.input_taxonomy.split('/', 1)[1]) and
                  isinstance(term.ref.native_id, str)):
                prefix = 'gid://shopify/TaxonomyCategory/'
                native = term.ref.native_id
                if native.startswith(prefix):
                    targets = crosswalk.rules.get(native[len(prefix):], ())
                    if targets:
                        candidates.append(('native_id', native, targets, 'shopify-google'))
            for facet, value, targets, route in candidates:
                key = (route, term.ref.namespace, source_version, facet, value)
                if key not in generated:
                    rule_id = sha256(json.dumps(key, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
                    version = (taxonomy.registry_version if route == 'google' else
                               taxonomy.registry_version + ':crosswalk-sha256:' + crosswalk.source_sha256)
                    rule = MappingRule(route + ':' + rule_id, version,
                        CategorySelector(term.ref.namespace, source_version, scope=scope,
                            allow_unknown_version=source_version is None, **{facet: value}), targets)
                    generated[key] = rule
                    ids.update(targets)
    options = google_taxonomy_options(scope, category_ids=ids,
        mappings=rules + sorted(generated.values(), key=lambda rule: rule.rule_id), taxonomy=taxonomy)
    return _bind_categories(product, observations, options)


@dataclass(frozen=True)
class GoogleClassification:
    status: str
    target_id: str | None
    candidate_ids: tuple[str, ...]
    reason: str


def effective_google_category(value, *, taxonomy):
    """Resolve at most one supported, nonpartial classification without mutation."""
    from ...categories.portable import categorized_product_to_record
    categorized_product_to_record(value)  # Validate original binding and owners.
    decisions = []
    candidates = set()
    ambiguous = False
    for decision in value.mappings:
        if decision.target_namespace != NAMESPACE:
            continue
        if decision.target_version != taxonomy.registry_version:
            raise GoogleTaxonomyIntegrityError('Classification target catalog differs')
        for target in decision.target_ids:
            if taxonomy.category(target) is None:
                raise GoogleTaxonomyIntegrityError('Classification target ID is unknown')
        if decision.target_ids and decision.status not in ('mapped', 'ambiguous'):
            raise GoogleTaxonomyIntegrityError('Unavailable classification has target candidates')
        decisions.append(decision)
        candidates.update(decision.target_ids)
        if decision.target_ids and (decision.partial or decision.status == 'ambiguous' or
                                    len(decision.target_ids) != 1):
            ambiguous = True
    ordered = tuple(sorted(candidates, key=int))
    if len(ordered) > 1 or ambiguous:
        return GoogleClassification('ambiguous', None, ordered, 'conflicting-multiple-or-partial-routes')
    if len(ordered) == 1:
        return GoogleClassification('mapped', ordered[0], ordered, 'unique-supported-target')
    if any(decision.status == 'unmapped' for decision in decisions):
        return GoogleClassification('unmapped', None, (), 'no-applicable-mapping')
    return GoogleClassification('unavailable', None, (), 'category-source-unavailable')
