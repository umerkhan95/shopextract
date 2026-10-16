"""Translate captured Woo product categories into unordered merchant memberships."""
from ..._normalization import Normalizer
from ..contracts import (
    AdapterContext, CategoryFactBinding, CategoryObservation, CategoryTerm, CategoryTermRef,
)
from ..evidence import source_fact
from ..helpers import merchant_scope, observation_id, native_id as _native_id, nonblank_text as _label


_NAMESPACE = 'woocommerce:product_cat'




def observe_categories(raw: dict, *, context: AdapterContext) -> tuple[CategoryObservation, ...]:
    """Use retained source facets only; legacy category_path is untouched."""
    selected = Normalizer(raw).select('/categories')
    state_fact = source_fact(raw, '/categories', binding=CategoryFactBinding('source_state'))
    value = selected.value
    if not selected.present:
        state, completeness, reason = 'missing', 'unknown', 'category_source_missing'
    elif value is None:
        state, completeness, reason = 'null', 'unknown', 'category_source_null'
    elif not isinstance(value, list):
        state, completeness, reason = 'malformed', 'unknown', 'category_source_malformed'
    elif not value:
        state, completeness, reason = 'empty', 'complete', ''
    else:
        state, completeness, reason = 'present', 'complete', ''

    terms = []
    positions = {}
    if isinstance(value, list) and value:
        cap = min(context.limits.terms, context.limits.relation_refs)
        for index, entry in enumerate(value[:cap]):
            pointer = f'/categories/{index}'
            native = None
            label = None
            if isinstance(entry, dict):
                try:
                    native = _native_id(entry.get('id'))
                except ValueError:
                    pass
                try:
                    label = _label(entry.get('name'))
                except ValueError:
                    pass
            elif isinstance(entry, str):
                try:
                    label = _label(entry)
                except ValueError:
                    pass
            if native is None and label is None:
                completeness, reason = 'partial', 'category_source_malformed'
                continue
            ref = CategoryTermRef(_NAMESPACE, None, native, merchant_scope(context.scope))
            facts = []
            if isinstance(entry, dict):
                # Preserve rejected/missing ID and label independently of usable siblings.
                facts.append(source_fact(raw, pointer + '/id',
                    binding=CategoryFactBinding('native_id', term=ref), convert=_native_id,
                    operation='Retain opaque Woo category ID as text'))
                facts.append(source_fact(raw, pointer + '/name',
                    binding=CategoryFactBinding('label', term=ref), convert=_label,
                    operation='Retain Woo category label verbatim'))
            else:
                facts.append(source_fact(raw, pointer,
                    binding=CategoryFactBinding('label', term=ref), convert=_label,
                    operation='Retain legacy Woo category label verbatim'))
            key = (ref, label)
            if key in positions:
                at = positions[key]
                old = terms[at]
                terms[at] = CategoryTerm(ref, label, old.facts + tuple(facts))
            else:
                positions[key] = len(terms)
                terms.append(CategoryTerm(ref, label, tuple(facts)))
        if len(value) > cap:
            completeness, reason = 'partial', 'category_budget_reached'
    if context.native_errors:
        completeness, reason = 'partial' if terms else 'unknown', 'category_source_error'
    return (CategoryObservation(
        observation_id(context.scope, _NAMESPACE, 'memberships', '/categories'),
        context.scope, 'memberships', 'merchant', state, completeness,
        terms=tuple(terms), facts=(state_fact,), reason=reason),)
