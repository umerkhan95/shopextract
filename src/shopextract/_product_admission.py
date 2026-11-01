"""Admission of generic product metadata, independent of monetary eligibility."""
from collections.abc import Mapping


def has_product_evidence(raw: Mapping[str, object]) -> bool:
    title = raw.get('name') or raw.get('og:title') or raw.get('title')
    if not isinstance(title, str) or not title.strip():
        return False
    types = raw.get('@type', ())
    if isinstance(types, str):
        types = (types,)
    if isinstance(types, (list, tuple)) and any(
            isinstance(t, str) and t.rstrip('/').rsplit('/', 1)[-1].rsplit(':', 1)[-1] in ('Product', 'ProductGroup')
            for t in types):
        return True
    og_type = raw.get('og:type')
    if isinstance(og_type, str) and og_type.strip().lower() == 'product':
        return True
    return any(raw.get(k) is not None and str(raw[k]).strip() for k in (
        'og:product_id', 'product:retailer_item_id', 'og:price:amount', 'product:price:amount'))


def crawl_document_allowed(result: object) -> bool:
    status = getattr(result, 'status_code', None)
    return (getattr(result, 'success', False) is True and type(status) is int
            and 200 <= status < 300)
