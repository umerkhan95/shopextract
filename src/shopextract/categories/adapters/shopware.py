"""Translate returned Shopware category memberships and independent index facts."""
from ..._normalization import Normalizer
from ..contracts import AdapterContext, CategoryFactBinding, CategoryObservation, CategoryTerm, CategoryTermRef
from ..evidence import source_fact
from ..helpers import merchant_scope, observation_id, nonblank_text as _identifier, nonblank_text as _label

_NAMESPACE = 'shopware:category'




def observe_categories(raw: dict, *, context: AdapterContext) -> tuple[CategoryObservation, ...]:
    """No network, inferred ancestry, or changes to legacy normalization."""
    owner = merchant_scope(context.scope)
    remaining_terms = context.limits.terms
    remaining_refs = context.limits.relation_refs
    result = []
    for field, relation in (('categoryIds', 'memberships'), ('categoryTree', 'index'), ('categories', 'memberships')):
        pointer = '/' + field
        selected = Normalizer(raw).select(pointer)
        values = selected.value
        state = ('missing' if not selected.present else 'null' if values is None else
                 'malformed' if not isinstance(values, list) else 'empty' if not values else 'present')
        completeness = 'complete' if state in ('empty', 'present') else 'unknown'
        reason = '' if completeness == 'complete' else 'category_source_' + state
        terms, positions, edges, edge_facts = [], {}, [], []
        cap = min(remaining_terms, remaining_refs)
        parent_by_child = {}
        if isinstance(values, list):
            for index, entry in enumerate(values[:cap]):
                if remaining_terms <= 0 or remaining_refs <= 0:
                    completeness, reason = 'partial', 'category_budget_reached'
                    break
                leaf = f'{pointer}/{index}'
                native = label = None
                if field == 'categories' and isinstance(entry, dict):
                    try:
                        native = _identifier(entry.get('id'))
                    except ValueError:
                        pass
                    translated = entry.get('translated')
                    label_pointer = leaf + ('/translated/name' if isinstance(translated, dict)
                        and isinstance(translated.get('name'), str) and translated['name'].strip() else '/name')
                    try:
                        label = _label(Normalizer(raw).select(label_pointer).value)
                    except ValueError:
                        pass
                elif field == 'categories' and isinstance(entry, str):
                    label_pointer = leaf
                    try:
                        label = _label(entry)
                    except ValueError:
                        pass
                else:
                    try:
                        native = _identifier(entry)
                    except ValueError:
                        pass
                if native is None and label is None:
                    completeness, reason = 'partial', 'category_source_malformed'
                    continue
                ref = CategoryTermRef(_NAMESPACE, None, native, owner)
                facts = []
                if field != 'categories' or isinstance(entry, dict):
                    facts.append(source_fact(raw, leaf + ('/id' if field == 'categories' else ''),
                        binding=CategoryFactBinding('native_id', term=ref), convert=_identifier,
                        operation='Retain opaque Shopware category ID'))
                if field == 'categories':
                    facts.append(source_fact(raw, label_pointer,
                        binding=CategoryFactBinding('label', term=ref), convert=_label,
                        operation='Retain Shopware category label verbatim'))
                key = (ref, label)
                if key in positions:
                    at = positions[key]
                    terms[at] = CategoryTerm(ref, label, terms[at].facts + tuple(facts))
                else:
                    positions[key] = len(terms)
                    terms.append(CategoryTerm(ref, label, tuple(facts)))
                remaining_terms -= 1
                remaining_refs -= 1
                if field == 'categories' and isinstance(entry, dict) and native is not None:
                    parent = entry.get('parentId')
                    if isinstance(parent, str) and parent.strip():
                        if remaining_refs < 2:
                            completeness, reason = 'partial', 'category_budget_reached'
                            continue
                        parent_ref = CategoryTermRef(_NAMESPACE, None, parent, owner)
                        edge = (parent_ref, ref)
                        parent_by_child[native] = parent
                        if edge not in edges:
                            edges.append(edge)
                        edge_facts.extend((source_fact(raw, leaf + '/parentId',
                            binding=CategoryFactBinding('parent_id', edge=edge), convert=_identifier),
                            source_fact(raw, leaf + '/id',
                            binding=CategoryFactBinding('child_id', edge=edge), convert=_identifier)))
                        remaining_refs -= 2
            if len(values) > cap:
                completeness, reason = 'partial', 'category_budget_reached'
        if parent_by_child:
            known = {term.ref.native_id for term in terms}
            for child, parent in parent_by_child.items():
                if parent not in known:
                    completeness, reason = 'partial', 'category_parent_unavailable'
                visited = {child}
                cursor = parent
                for _ in range(context.limits.ancestry_depth):
                    if cursor in visited:
                        completeness, reason = 'partial', 'category_ancestry_invalid'
                        break
                    visited.add(cursor)
                    if cursor not in parent_by_child:
                        break
                    cursor = parent_by_child[cursor]
                else:
                    completeness, reason = 'partial', 'category_ancestry_depth_reached'
        if context.native_errors:
            completeness, reason = 'partial' if terms else 'unknown', 'category_source_error'
        # An index has no claim about the graph's completeness or an ordered path.
        if relation == 'index' and completeness == 'complete':
            completeness, reason = 'unknown', 'category_index_unexpanded'
        state_fact = source_fact(raw, pointer, binding=CategoryFactBinding('source_state'))
        result.append(CategoryObservation(observation_id(context.scope, _NAMESPACE, relation, pointer),
            context.scope, relation, 'merchant', state, completeness, tuple(terms), tuple(edges),
            (state_fact,) + tuple(edge_facts), reason))
    return tuple(result)
