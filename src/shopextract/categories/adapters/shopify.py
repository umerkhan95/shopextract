"""Translate captured Shopify declarations without requesting category enrichment."""
from ..._normalization import Normalizer
from ..contracts import (AdapterContext, CategoryFactBinding, CategoryObservation,
                         CategoryTerm, CategoryTermRef)
from ..evidence import source_fact
from ..helpers import merchant_scope, observation_id

CUSTOM = 'shopify:product_type'
STANDARD = 'shopify:standard_product_taxonomy'
COLLECTION = 'shopify:collection'


def _text(value):
    if not isinstance(value, str) or not value:
        raise ValueError('Expected nonempty Shopify text')
    return value


def observe_categories(raw: dict, *, context: AdapterContext) -> tuple[CategoryObservation, ...]:
    """Keep custom type, standard taxonomy and collections as separate relations.

    Only supplied raw declarations are translated. In particular, public products.json
    does not imply availability of either GraphQL category or collection fields.
    """
    selected = Normalizer(raw)
    owner = merchant_scope(context.scope)
    remaining = min(context.limits.terms, context.limits.relation_refs)
    result = []

    def affected(pointer):
        tokens = tuple(pointer.lstrip('/').split('/'))
        return any(error.path is None or not error.path or
                   tuple(str(v) for v in error.path)[:len(tokens)] == tokens or
                   tokens[:len(error.path)] == tuple(str(v) for v in error.path)
                   for error in context.native_errors)

    def fact(pointer, facet, term=None, convert=None):
        def rejected(value):
            raise ValueError('Shopify category source error')
        return source_fact(raw, pointer, binding=CategoryFactBinding(facet, term=term),
                           convert=rejected if affected(pointer) else convert)

    def emit(namespace, relation, kind, pointer, state, completeness, terms=(), facts=(), reason=''):
        result.append(CategoryObservation(
            observation_id(context.scope, namespace, relation, pointer), context.scope,
            relation, kind, state, completeness, tuple(terms), facts=tuple(facts), reason=reason))

    # product_type is one merchant-defined string, including any literal separators.
    pointer = '/product_type'
    value = selected.select(pointer)
    state = ('missing' if not value.present else 'null' if value.value is None else
             'empty' if value.value == '' else 'present' if isinstance(value.value, str) else 'malformed')
    terms = []
    reason = ''
    completeness = 'unknown'
    if state == 'present' and remaining > 0:
        ref = CategoryTermRef(CUSTOM, None, None, owner)
        terms.append(CategoryTerm(ref, value.value, (fact(pointer, 'label', ref, _text),)))
        remaining -= 1
        completeness = 'complete'
    elif state == 'present':
        reason, completeness = 'category_limit_reached', 'partial'
    if affected(pointer):
        reason, completeness = 'category_source_error', 'partial' if terms else 'unknown'
    emit(CUSTOM, 'label', 'custom_type', pointer, state, completeness, terms,
         (fact(pointer, 'source_state'),), reason)

    # GraphQL category is a Standard Product Taxonomy node, never a custom label.
    pointer = '/category'
    value = selected.select(pointer)
    state = ('missing' if not value.present else 'null' if value.value is None else
             'present' if isinstance(value.value, dict) else 'malformed')
    terms, reason, completeness = [], '', 'unknown'
    if state == 'present':
        node = value.value
        native_id = node.get('id')
        label = node.get('name')
        valid_id = isinstance(native_id, str) and bool(native_id)
        valid_label = isinstance(label, str) and bool(label)
        if not valid_id:
            state, reason = 'malformed', 'invalid_standard_category_id'
        if (valid_id or valid_label) and remaining > 0:
            ref = CategoryTermRef(STANDARD, None, native_id if valid_id else None, None)
            terms.append(CategoryTerm(ref, label if valid_label else None, (
                fact(pointer + '/id', 'native_id', ref, _text),
                fact(pointer + '/name', 'label', ref, _text))))
            remaining -= 1
            completeness = 'complete' if valid_id else 'unknown'
        elif valid_id or valid_label:
            reason, completeness = 'category_limit_reached', 'partial'
    if affected(pointer):
        reason, completeness = 'category_source_error', 'partial' if terms else 'unknown'
    emit(STANDARD, 'memberships', 'standard', pointer, state, completeness, terms,
         (fact(pointer, 'source_state'),), reason)

    # Collections are a paginated merchandising membership connection, not ancestry.
    pointer = '/collections'
    value = selected.select(pointer)
    state = ('missing' if not value.present else 'null' if value.value is None else
             'present' if isinstance(value.value, dict) else 'malformed')
    terms, reason, completeness = [], '', 'unknown'
    facts = [fact(pointer, 'source_state')]
    if state == 'present':
        edges = value.value.get('edges')
        completion_pointer = pointer + '/pageInfo/hasNextPage'
        completion = selected.select(completion_pointer)
        facts.append(fact(completion_pointer, 'completion'))
        if isinstance(completion.value, bool):
            completeness = 'partial' if completion.value else 'complete'
            reason = 'category_budget_reached' if completion.value else ''
        else:
            reason = 'completion_metadata_unavailable'
        if not isinstance(edges, list):
            state, reason, completeness = 'malformed', 'invalid_collection_connection', 'unknown'
        else:
            state = 'present' if edges else 'empty'
            seen = {}
            # Inspect at most the configured number of source entries, even duplicates.
            cap = remaining
            for index, edge in enumerate(edges[:cap]):
                node = edge.get('node') if isinstance(edge, dict) else None
                if not isinstance(node, dict):
                    state, reason, completeness = 'malformed', 'invalid_collection_node', 'partial'
                    continue
                native_id, label = node.get('id'), node.get('title')
                valid_id = isinstance(native_id, str) and bool(native_id)
                valid_label = isinstance(label, str) and bool(label)
                if not valid_id:
                    state, reason, completeness = 'malformed', 'invalid_collection_id', 'partial'
                if not (valid_id or valid_label):
                    continue
                ref = CategoryTermRef(COLLECTION, None, native_id if valid_id else None, owner)
                path = f'{pointer}/edges/{index}/node'
                node_facts = (fact(path + '/id', 'native_id', ref, _text),
                              fact(path + '/title', 'label', ref, _text))
                key = ref, label if valid_label else None
                if key in seen:
                    old = terms[seen[key]]
                    terms[seen[key]] = CategoryTerm(ref, old.label, old.facts + node_facts)
                else:
                    seen[key] = len(terms)
                    terms.append(CategoryTerm(ref, label if valid_label else None, node_facts))
            if len(edges) > cap:
                reason, completeness = 'category_limit_reached', 'partial'
    if affected(pointer):
        reason, completeness = 'category_source_error', 'partial' if terms else 'unknown'
    emit(COLLECTION, 'memberships', 'merchandising', pointer, state, completeness,
         terms, facts, reason)
    return tuple(result)
