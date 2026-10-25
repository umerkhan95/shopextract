"""Shared provenance/source handling for additive safe native reports."""
from ._models import SourceStatus
from ._execution import safe_error


def source_status(store, result):
    return SourceStatus(store, bool(result.products or result.raw_products or result.catalog_complete is True),
                        result.catalog_complete, [safe_error(e) for e in result.errors])


def observed_currency(product, raw):
    value = raw.get('currency') if isinstance(raw, dict) else None
    if isinstance(value, str) and value.strip():
        return value.strip().upper()
    contract = getattr(product, 'evidence_contract', None)
    if contract is not None:
        from ._evidence import trust_view
        # A scalar constructor default never supplies observed provenance.
        view = trust_view(product, contract)
        field = view.get('/currency', {})
        if isinstance(field, dict) and field.get('state') == 'observed':
            value = field.get('value')
            if isinstance(value,str) and value.strip():
                return value.strip().upper()
    return None
