"""Strict bound companion projection into contextual metadata; no new observations."""
from ...categories.portable import categorized_product_to_record
from .contracts import CategorySchema, ProductTaxonomySchema, TaxonomyIntegrityError
from .identity import NAMESPACE


def schema_for(taxonomy,value):
    categorized_product_to_record(value)
    resolved={};unresolved=[]
    for decision in value.mappings:
        if decision.status!='mapped':
            unresolved.append(decision);continue
        if decision.target_namespace!=NAMESPACE or decision.target_version!=taxonomy.registry_version:
            raise TaxonomyIntegrityError('Mapped taxonomy identity differs from catalog')
        for target in decision.target_ids:
            node=taxonomy.category(target)
            if node is None:raise TaxonomyIntegrityError('Mapped target absent from catalog')
            resolved[node.id]=CategorySchema(node,taxonomy.attributes_for(node.id))
    return ProductTaxonomySchema(taxonomy.registry_version,tuple(resolved[k] for k in sorted(resolved)),tuple(unresolved))
