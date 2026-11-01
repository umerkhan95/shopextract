"""Real normalized unknown stock must survive the existing native transport."""
import json
from decimal import Decimal
import pytest
from tests.test_adapter_coverage import product,parent
from shopextract._models import Product,Variant
from shopextract._portable import product_to_record,product_from_record

@pytest.mark.parametrize('stock',[None,False,True])
def test_normalized_variant_stock_portable_roundtrip(stock):
 child={'id':2,'price':'1'}
 if stock is not None:child['is_in_stock']=stock
 p=product(parent(variants=[child]));assert p.variants[0].in_stock is stock
 restored=product_from_record(json.loads(json.dumps(product_to_record(p))))
 assert restored==p and restored.variants[0].in_stock is stock
 assert restored.evidence_contract.to_dict()==p.evidence_contract.to_dict()
 assert restored.variants[0].evidence_contract.to_dict()==p.variants[0].evidence_contract.to_dict()
 if stock is None:assert all(o.state.value!='observed' for o in restored.variants[0].evidence_contract.observations if o.field_path=='/in_stock')


def test_legacy_variant_constructor_defaults_and_positions():
 assert Variant().in_stock is True
 assert Variant('V','Title',Decimal('1'),None,False).in_stock is False


def test_invalid_variant_stock_text_still_rejected():
 p=Product(variants=[Variant(in_stock='unknown')])
 with pytest.raises(ValueError):product_to_record(p)
