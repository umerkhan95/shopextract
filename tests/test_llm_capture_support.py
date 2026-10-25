"""Model output cannot supply captured field or category facts."""
import pytest
from shopextract._capture import capture
from shopextract._normalize import normalize
from shopextract._models import Platform
from shopextract._evidence import SupportState


@pytest.mark.parametrize('method', ['llm', 'llm_bounded'])
def test_model_capture_remains_unsupported(method):
    raw = capture({'title': 'Invented refrigerator', 'price': '250', 'sku': 'invented',
                   'url': 'https://fixture.invalid/fridge'},
                  'https://fixture.invalid/fridge', method,
                  excerpt='<html>No product facts here.</html>')
    product = normalize(raw, Platform.GENERIC, 'https://fixture.invalid')
    assert product is not None
    observations = {fact.field_path: fact for fact in product.evidence_contract.observations}
    for path in ('/title', '/price', '/sku'):
        assert observations[path].state == SupportState.UNSUPPORTED
        assert observations[path].evidence_ids == []


@pytest.mark.parametrize('method', ['llm', 'llm_bounded'])
def test_model_categories_never_claim_complete(method):
    from shopextract.categories.adapters.generic import observe_categories
    from shopextract.categories.contracts import AdapterContext, CategoryScope
    raw = capture({'title': 'Invented', 'category': 'Refrigerators'},
                  'https://fixture.invalid/fridge', method)
    context = AdapterContext(CategoryScope(Platform.GENERIC, 'https://fixture.invalid'))
    observations = observe_categories(raw, context=context)
    assert observations
    assert all(item.completeness == 'unknown' for item in observations)
    assert all(fact.support == SupportState.UNSUPPORTED
               for item in observations for term in item.terms for fact in term.facts)
