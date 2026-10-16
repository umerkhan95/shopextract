"""Captured Magento UID/name memberships; no inferred taxonomy ancestry."""
from ..._normalization import Normalizer
from ..contracts import (
    AdapterContext, CategoryObservation, CategoryTerm, CategoryTermRef,
)
from ..native import native_source_fact
from ..helpers import merchant_scope, observation_id, nonblank_text as _opaque_text


_NAMESPACE = 'magento:category'



def observe_categories(raw: dict, *, context: AdapterContext) -> tuple[CategoryObservation, ...]:
    """Retain independently supported facets and bounded unordered memberships."""
    selected = Normalizer(raw).select('/categories')
    state_fact = native_source_fact(raw, '/categories', 'source_state', context)
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

    terms, positions = [], {}
    if isinstance(value, list):
        cap = min(context.limits.terms, context.limits.relation_refs)
        for index, entry in enumerate(value[:cap]):
            if not isinstance(entry, dict):
                completeness, reason = 'partial', 'category_source_malformed'
                continue
            pointer = f'/categories/{index}'
            native_id, label = None, None
            try:
                native_id = _opaque_text(entry.get('uid'))
            except ValueError:
                completeness, reason = 'partial', 'category_source_malformed'
            try:
                label = _opaque_text(entry.get('name'))
            except ValueError:
                pass  # CategoryInterface.name is nullable; UID remains usable.
            if native_id is None and label is None:
                completeness, reason = 'partial', 'category_source_malformed'
                continue
            ref = CategoryTermRef(_NAMESPACE, None, native_id, merchant_scope(context.scope))
            facts = (
                native_source_fact(raw, pointer + '/uid', 'native_id', context, ref,
                            convert=_opaque_text, operation='Retain opaque Magento category UID'),
                native_source_fact(raw, pointer + '/name', 'label', context, ref,
                            convert=_opaque_text, operation='Retain Magento category name verbatim'),
            )
            key = (ref, label)
            if key in positions:
                at = positions[key]
                terms[at] = CategoryTerm(ref, label, terms[at].facts + facts)
            else:
                positions[key] = len(terms)
                terms.append(CategoryTerm(ref, label, facts))
        if len(value) > cap:
            completeness, reason = 'partial', 'category_budget_reached'
    relevant_errors = tuple(error for error in context.native_errors
                            if error.path is None or not error.path or error.path[0] == 'categories')
    if relevant_errors:
        completeness, reason = 'partial' if terms else 'unknown', 'category_source_error'
        if state == 'empty':
            # A failed selection returning [] cannot claim an observed empty membership set.
            state = 'malformed'
    return (CategoryObservation(
        observation_id(context.scope, _NAMESPACE, 'memberships', '/categories'),
        context.scope, 'memberships', 'merchant', state, completeness,
        terms=tuple(terms), facts=(state_fact,), reason=reason),)
