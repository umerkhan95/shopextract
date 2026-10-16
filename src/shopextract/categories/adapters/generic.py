"""Translate captured generic declarations without inferring taxonomy or ancestry."""
from urllib.parse import urlsplit

from ..._normalization import Normalizer
from ..contracts import AdapterContext, CategoryFactBinding, CategoryObservation, CategoryTerm, CategoryTermRef
from ..evidence import source_fact
from ..helpers import merchant_scope, observation_id, nonblank_text


def _uri(value):
    if isinstance(value, str) and not any(c.isspace() for c in value):
        try:
            parsed = urlsplit(value)
            return parsed.scheme in ('http', 'https', 'urn') and bool(parsed.netloc or parsed.path)
        except ValueError:
            pass
    return False


def _state(selected):
    value = selected.value
    if not selected.present:
        return 'missing'
    if value is None:
        return 'null'
    if value == '' or value == []:
        return 'empty'
    return 'present'


def observe_categories(raw: dict, *, context: AdapterContext) -> tuple[CategoryObservation, ...]:
    """Consume parser-retained fields only; no requests, mapper, or path splitting."""
    owner = merchant_scope(context.scope)
    trace = Normalizer(raw)
    method = (raw.get('_capture') or {}).get('method')
    carrier = raw.get('category_declarations')
    if raw.get('_source') == 'google_feed':
        # Legacy parsed feeds lack presence metadata; do not bless collapsed defaults.
        fields = [('google:product_category', 'standard', '/category_declarations/google_product_category'),
                  ('google:product_type', 'custom_type', '/category_declarations/product_type')]
    elif 'og:title' in raw or 'product:category' in raw or method == 'opengraph':
        pointer = '/category_declarations/product:category' if isinstance(carrier, dict) else '/product:category'
        fields = [('opengraph:product_category', 'merchant', pointer)]
    elif 'category' in raw or method == 'json_ld' or '@type' in raw:
        fields = [('schema.org:category', 'merchant', '/category')]
    else:
        # CSS requires its existing exact DOM capture. LLM remains unsupported in
        # source_fact even when it supplies this custom declaration.
        fields = [('generic:product_type', 'custom_type', '/product_type')]

    result = []
    remaining_terms, remaining_refs = context.limits.terms, context.limits.relation_refs
    for namespace, kind, pointer in fields:
        selected = trace.select(pointer)
        state = _state(selected)
        value = selected.value
        is_og = namespace == 'opengraph:product_category'
        # A Google standard field is non-repeated; a repeated field is malformed.
        malformed = namespace == 'google:product_category' and isinstance(value, (dict, list))
        values = value if isinstance(value, list) and not malformed else [value]
        groups = {}
        partial = False
        reason = ''
        for index, entry in enumerate(values):
            if state != 'present' or malformed:
                break
            if remaining_terms <= 0 or remaining_refs <= 0:
                partial, reason = True, 'category_budget_reached'
                break
            leaf = f'{pointer}/{index}' if isinstance(value, list) else pointer
            term_namespace, term_kind = namespace, kind
            native = label = None
            facets = []
            if isinstance(entry, str) and entry.strip():
                if namespace == 'google:product_category':
                    if entry.isascii() and entry.isdecimal():
                        native = entry
                        facets.append(('native_id', leaf))
                    else:
                        # Preserve the entire declared standard path representation.
                        # No taxonomy lookup, segment IDs, or parent edges are invented.
                        facets.append(('raw_path', leaf))
                elif namespace == 'schema.org:category' and _uri(entry):
                    native = entry
                    facets.append(('native_id', leaf))
                else:
                    label = entry
                    facets.append(('label', leaf))
            elif isinstance(entry, dict) and namespace == 'schema.org:category':
                types = entry.get('@type', [])
                types = [types] if isinstance(types, str) else types
                is_code = isinstance(types, list) and any(t in ('CategoryCode', 'https://schema.org/CategoryCode', 'http://schema.org/CategoryCode') for t in types)
                if is_code:
                    term_kind = 'structured_code'
                    code_set = entry.get('inCodeSet')
                    context_pointer = leaf + '/inCodeSet'
                    if isinstance(code_set, dict):
                        code_set = code_set.get('@id')
                        context_pointer += '/@id'
                    if _uri(code_set):
                        term_namespace = code_set
                        facets.append(('code_context', context_pointer))
                    code = entry.get('codeValue')
                    if isinstance(code, str) and code.strip():
                        native = code
                        facets.append(('native_id', leaf + '/codeValue'))
                elif isinstance(entry.get('@id'), str) and entry['@id'].strip():
                    native = entry['@id']
                    facets.append(('native_id', leaf + '/@id'))
                if isinstance(entry.get('name'), str) and entry['name'].strip():
                    label = entry['name']
                    facets.append(('label', leaf + '/name'))
            elif is_og and entry in ('', None):
                # Empty declaration remains visible in the collection state fact.
                continue
            if not facets or (native is None and label is None and not any(f == 'raw_path' for f, _ in facets)):
                partial, reason = True, 'category_source_malformed'
                continue
            merchant = None if term_kind == 'standard' else owner
            ref = CategoryTermRef(term_namespace, None, native, merchant)
            facts = tuple(source_fact(raw, path, binding=CategoryFactBinding(facet, term=ref),
                                      convert=nonblank_text, operation='Retain declared category ' + facet + ' verbatim')
                          for facet, path in facets)
            group = groups.setdefault((term_namespace, term_kind), {})
            # Label-only refs are intentionally distinct by their exact raw label;
            # duplicate declarations retain every source pointer/evidence fact.
            key = (ref, label, entry if any(f == 'raw_path' for f, _ in facets) else None)
            previous = group.get(key)
            group[key] = CategoryTerm(ref, label, (previous.facts if previous else ()) + facts)
            remaining_terms -= 1
            remaining_refs -= 1
        if malformed:
            state = 'malformed'
        if partial and not groups and reason == 'category_source_malformed':
            state = 'malformed'
        if not groups:
            groups[(namespace, kind)] = {}
        for (term_namespace, term_kind), terms in groups.items():
            relation = 'memberships' if isinstance(value, list) else 'label'
            completeness = 'unknown'
            if state in ('present', 'empty') and not is_og and method != 'llm':
                completeness = 'complete'
            if partial:
                completeness = 'partial'
            why = reason or ('category_declarations_completeness_unknown' if is_og else
                'category_source_' + state if state not in ('present', 'empty') else '')
            if context.native_errors:
                completeness, why = ('partial' if terms else 'unknown'), 'category_source_error'
            result.append(CategoryObservation(
                observation_id(context.scope, term_namespace, relation, pointer), context.scope,
                relation, term_kind, state, completeness, tuple(terms.values()), (),
                (source_fact(raw, pointer, binding=CategoryFactBinding('source_state')),), why))
    return tuple(result)
