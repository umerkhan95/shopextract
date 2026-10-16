"""Reviewed native field declarations; producer queries remain owned by extractors.

G3 implementation composes these finite selections into separate opt-in templates.
Guard imports producer-owned complete constants; it never maintains a second query.
"""
BIGCOMMERCE_CATEGORY_SELECTION = '''categories(first:20) {
  pageInfo { hasNextPage endCursor }
  edges { node { entityId name path } }
}'''
MAGENTO_CATEGORY_SELECTION = 'categories { uid name }'

# Operation metadata is allowed only to downgrade completeness, never support a fact.
CATEGORY_DIAGNOSTICS_KEY = '_category_diagnostics'


from .contracts import NativeCategoryError


def localize_category_errors(errors: tuple[NativeCategoryError, ...], *,
                             product_path: tuple[str | int, ...]) -> tuple[NativeCategoryError, ...]:
    """Strip this product prefix; keep global/ancestor errors, exclude other siblings."""
    result = []
    for error in errors:
        path = error.path
        if path is None or product_path[:len(path)] == path:
            result.append(NativeCategoryError(None, error.code))
        elif path[:len(product_path)] == product_path:
            result.append(NativeCategoryError(path[len(product_path):], error.code))
    return tuple(result)


def native_body(response, *, include_categories=False):
    """Opt-in preserves native errors+data; ordinary helper behavior is unchanged."""
    if not include_categories:
        from ..extractors._storefront import json_body
        return json_body(response)
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError('Native GraphQL response must be an object')
    errors = []
    reported = data.get('errors') or []
    if not isinstance(reported,list):
        reported = [{}]
    if len(reported) > 100:
        errors.append(NativeCategoryError(None,'native_error_budget_reached'))
    for error in reported[:99 if errors else 100]:
        path = error.get('path') if isinstance(error, dict) else None
        if not isinstance(path, list) or len(path) > 32 or any(type(p) not in (str, int) for p in path):
            path = None
        elif any(isinstance(p, str) and len(p) > 128 for p in path):
            path = None
        code = (error.get('extensions') or {}).get('code', 'native_source_error') if isinstance(error, dict) else 'native_source_error'
        if not isinstance(code, str) or not code.isascii() or len(code) > 64:
            code = 'native_source_error'
        errors.append(NativeCategoryError(tuple(path) if path else None, code))
    if not isinstance(data.get('data'), dict):
        raise ValueError('Native GraphQL data unavailable')
    result = dict(data)
    result['_category_errors'] = tuple(errors)
    return result


def attach_category_diagnostics(raw, errors, *, product_path):
    localized = localize_category_errors(tuple(errors), product_path=tuple(product_path))
    if localized:
        raw[CATEGORY_DIAGNOSTICS_KEY] = [dict(path=list(e.path) if e.path is not None else None, code=e.code) for e in localized]
    return raw


def native_source_fact(raw, pointer, facet, context, ref=None, convert=None, operation=''):
    """Reject failed GraphQL facets before the shared source-support bridge.

    Paths are already product-local. Ancestor/global errors reject affected child
    facets, while descendant errors also invalidate a parent aggregate, never siblings.
    """
    from .contracts import CategoryFactBinding
    from .evidence import source_fact
    tokens = tuple(int(p) if p.isdecimal() else p for p in pointer.strip('/').split('/'))
    failed = any(error.path is None or tokens[:len(error.path)] == error.path
                 or error.path[:len(tokens)] == tokens for error in context.native_errors)
    if failed:
        def rejected(value):
            raise ValueError('Native category field failed')
        convert = rejected
    return source_fact(raw, pointer, binding=CategoryFactBinding(facet, term=ref),
                       convert=convert, operation=operation)
