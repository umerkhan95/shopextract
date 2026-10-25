"""Strict explicit category companion envelope around the unchanged Product codec."""
import copy
from .._portable import product_to_record, product_from_record, validate_tree
from ._codec import wire, typed, canonical, digest
from .contracts import (CategorizedProduct, CategoryError, CategoryScope,
                        CategoryObservation, MappingDecision, CategoryLimits)
from .validation import validate_observations

_KEYS = {'schema_version','product','scope','observations','mappings','config_digest','original_binding'}


def _payload(value):
    validate_observations(value.observations)
    observations = {o.observation_id: o for o in value.observations}
    if len(observations) != len(value.observations):
        raise CategoryError('Duplicate category observation identity')
    for decision in value.mappings:
        typed(MappingDecision, wire(decision))
        observation = observations.get(decision.observation_id)
        if observation is None or (decision.term is not None and decision.term not in {t.ref for t in observation.terms}):
            raise CategoryError('Dangling category mapping source')
        if decision.status in ('mapped','ambiguous') and not decision.target_ids:
            raise CategoryError('Mapped category requires target candidates')
        if any(p not in {f.pointer for t in observation.terms for f in t.facts} for p in decision.source_pointers):
            raise CategoryError('Dangling category mapping facet')
    if any(o.scope != value.scope for o in value.observations):
        raise CategoryError('Category assignment scope mismatch')
    if value.product.platform != value.scope.platform:
        raise CategoryError('Category Product platform mismatch')
    if type(value.schema_version) is not int or value.schema_version != 1:
        raise CategoryError('Unsupported category version')
    if not isinstance(value.config_digest, str) or len(value.config_digest) != 64:
        raise CategoryError('Invalid category config digest')
    return dict(schema_version=1, product=product_to_record(value.product), scope=wire(value.scope),
        observations=wire(value.observations), mappings=wire(value.mappings), config_digest=value.config_digest)


def bind_product(product, scope, observations, mappings, config_digest, *, limits=None):
    limits = limits or CategoryLimits()
    snapshot = copy.deepcopy((product, scope, observations, mappings))
    product, scope, observations, mappings = snapshot
    value = CategorizedProduct(product, scope, observations, mappings, config_digest, '')
    payload = _payload(value)
    binding = digest(payload)
    result = CategorizedProduct(product, scope, observations, mappings, config_digest, binding)
    if len(canonical(dict(payload, original_binding=binding)).encode()) > limits.record_bytes:
        raise CategoryError('Category companion byte cap exceeded')
    return result


def categorized_product_to_record(value: CategorizedProduct) -> dict:
    try:
        payload = _payload(value)
        if digest(payload) != value.original_binding:
            raise CategoryError('Category original binding changed')
        result = dict(payload, original_binding=value.original_binding)
        if len(canonical(result).encode()) > 262144:
            raise CategoryError('Category companion byte cap exceeded')
        return result
    except (ValueError, TypeError, AttributeError, RecursionError) as error:
        raise CategoryError(str(error)) from error


def categorized_product_from_record(record: dict) -> CategorizedProduct:
    try:
        if not isinstance(record,dict) or set(record) != _KEYS:
            raise CategoryError('Malformed category envelope fields')
        if type(record['schema_version']) is not int or record['schema_version'] != 1:
            raise CategoryError('Unsupported category envelope version')
        validate_tree(record, encoded=True)
        if len(canonical(record).encode()) > 262144:
            raise CategoryError('Category envelope byte cap exceeded')
        value = CategorizedProduct(product_from_record(record['product']), typed(CategoryScope,record['scope']),
            tuple(typed(CategoryObservation,o) for o in record['observations']),
            tuple(typed(MappingDecision,m) for m in record['mappings']),
            record['config_digest'], record['original_binding'])
        categorized_product_to_record(value)
        return value
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError) as error:
        raise CategoryError(str(error)) from error


def validate_categorized_products(records, *, options, maximum):
    """Validate fresh/cache worker records against their trusted parent policy.

    Consume the same strict companion decoder before a result can be accepted or
    persisted. The child-supplied digest never substitutes for actual scope checks.
    """
    from .config import options_digest
    if not isinstance(records, list) or len(records) > maximum:
        raise CategoryError('Invalid category product collection')
    expected = options_digest(options)
    for record in records:
        value = categorized_product_from_record(record)
        if value.config_digest != expected or value.scope != options.scope:
            raise CategoryError('Category source policy differs')
