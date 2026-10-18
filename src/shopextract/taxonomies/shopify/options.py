"""Construct finite existing category policies from selected catalog identities."""
from ...categories.config import validate_options
from ...categories.contracts import CategoryOptions, CategorySelector, MappingRule, TargetRegistry
from .contracts import TaxonomyLookupError
from .identity import NAMESPACE
from .loader import load_shopify_taxonomy


def shopify_taxonomy_options(scope, *, category_ids, mappings=(), allow_unknown_source_version=False, taxonomy=None):
    taxonomy=taxonomy or load_shopify_taxonomy()
    if type(allow_unknown_source_version) is not bool:raise TypeError('Expected explicit boolean version permission')
    if isinstance(category_ids,(str,bytes)):raise TypeError('category_ids must be a sequence of IDs')
    selected={}
    for key in category_ids:
        node=taxonomy.category(key)
        if node is None:raise TaxonomyLookupError('Unknown category: '+key)
        selected[node.short_id]=node
        if len(selected)>1000:raise TaxonomyLookupError('Selected category limit exceeded')
    ids=tuple(sorted(selected))
    rules=list(mappings)
    if allow_unknown_source_version:
        for short in ids:
            rules.append(MappingRule('shopify-identity:'+short,taxonomy.registry_version,
                CategorySelector(NAMESPACE,None,scope=scope,native_id=selected[short].id,allow_unknown_version=True),(short,)))
    result=CategoryOptions(scope,TargetRegistry(NAMESPACE,taxonomy.registry_version,ids),tuple(rules))
    validate_options(result)
    return result
