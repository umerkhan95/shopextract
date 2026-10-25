"""Captured bounded BigCommerce merchant membership connection; no inferred ancestry."""
from ..._normalization import Normalizer
from ..contracts import AdapterContext, CategoryObservation, CategoryTerm, CategoryTermRef
from ..native import native_source_fact as _fact
from ..helpers import merchant_scope, observation_id, native_id as _id, nonblank_text as _label

_NS = 'bigcommerce:category'




def observe_categories(raw: dict, *, context: AdapterContext) -> tuple[CategoryObservation, ...]:
    selected = Normalizer(raw).select('/categories')
    value = selected.value
    edges = value.get('edges') if isinstance(value,dict) else None
    state = ('missing' if not selected.present else 'null' if value is None else
             'malformed' if not isinstance(edges,list) else 'empty' if not edges else 'present')
    info = value.get('pageInfo') if isinstance(value,dict) else None
    next_page = info.get('hasNextPage') if isinstance(info,dict) else None
    complete = 'complete' if isinstance(edges,list) and next_page is False else 'partial' if next_page is True else 'unknown'
    reason = '' if complete == 'complete' else 'category_budget_reached' if next_page is True else 'completion_metadata_unavailable'
    if state in ('missing','null','malformed'):
        complete, reason = 'unknown', 'category_source_' + state
    facts = (_fact(raw,'/categories','source_state',context),
             _fact(raw,'/categories/pageInfo/hasNextPage','completion',context))
    terms, seen = [], {}
    cap = min(context.limits.terms,context.limits.relation_refs)
    for index, edge in enumerate((edges or [])[:cap] if isinstance(edges,list) else []):
        node = edge.get('node') if isinstance(edge,dict) else None
        if not isinstance(node,dict):
            complete, reason = 'partial','category_source_malformed'
            continue
        native = label = None
        try:
            native = _id(node.get('entityId'))
        except ValueError:
            pass
        try:
            label = _label(node.get('name'))
        except ValueError:
            pass
        if native is None and label is None:
            complete, reason = 'partial','category_source_malformed'
            continue
        ref = CategoryTermRef(_NS,None,native,merchant_scope(context.scope))
        pointer = f'/categories/edges/{index}/node'
        term_facts = (_fact(raw,pointer+'/entityId','native_id',context,ref,_id),
                      _fact(raw,pointer+'/name','label',context,ref,_label))
        if 'path' in node:
            term_facts += (_fact(raw,pointer+'/path','raw_path',context,ref,_label),)
        key = (ref,label)
        if key in seen:
            at = seen[key]
            old = terms[at]
            terms[at] = CategoryTerm(ref,label,old.facts+term_facts)
        else:
            seen[key] = len(terms)
            terms.append(CategoryTerm(ref,label,term_facts))
    if isinstance(edges,list) and len(edges) > cap:
        complete,reason = 'partial','category_budget_reached'
    relevant = any(e.path is None or not e.path or e.path[0] == 'categories' for e in context.native_errors)
    if relevant:
        complete,reason = ('partial' if terms else 'unknown'),'category_source_error'
    return (CategoryObservation(observation_id(context.scope,_NS,'memberships','/categories'),
        context.scope,'memberships','merchant',state,complete,tuple(terms),facts=facts,reason=reason),)
