"""Build finite native category policies from the complete Google catalog."""
from ...categories.config import validate_options
from ...categories.contracts import CategoryOptions, CategorySelector, MappingRule, TargetRegistry
from .contracts import GoogleTaxonomyLookupError
from .loader import load_google_taxonomy

NAMESPACE = 'google:product_category'


def google_taxonomy_options(scope, *, category_ids, mappings=(),
                            allow_unknown_source_version=False, taxonomy=None):
    taxonomy = taxonomy or load_google_taxonomy()
    if type(allow_unknown_source_version) is not bool:
        raise TypeError('Expected explicit boolean source version permission')
    if isinstance(category_ids, (str, bytes)):
        raise TypeError('category_ids must be a sequence of IDs')
    selected = {}
    for key in category_ids:
        node = taxonomy.category(key)
        if node is None:
            raise GoogleTaxonomyLookupError('Unknown Google category: ' + key)
        selected[node.id] = node
        if len(selected) > 1000:
            raise GoogleTaxonomyLookupError('Selected category limit exceeded')
    rules = list(mappings)
    if allow_unknown_source_version:
        for key, node in sorted(selected.items(), key=lambda item: int(item[0])):
            for facet, value in (('native_id', key), ('raw_path', node.full_name)):
                rules.append(MappingRule('google-identity:' + facet + ':' + key,
                    taxonomy.registry_version,
                    CategorySelector(NAMESPACE, None, scope=scope,
                        allow_unknown_version=True, **{facet: value}), (key,)))
    result = CategoryOptions(scope,
        TargetRegistry(NAMESPACE, taxonomy.registry_version,
                       tuple(sorted(selected, key=int))), tuple(rules))
    validate_options(result)
    return result
