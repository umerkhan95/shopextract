"""Exact legacy projection oracle; no performance wallclock assertion."""
import copy
import json
from dataclasses import asdict
from datetime import datetime,timezone
from decimal import Decimal
import pytest
from shopextract._models import Product,Platform
from shopextract._evidence import encode_value
from shopextract._portable import product_to_record,product_from_record


def test_native_projection_exact_all_fields_and_contracts():
 from tests.test_adapter_coverage import parent,URL
 from shopextract._capture import capture
 from shopextract._normalize import normalize
 raw=parent(variants=[{'id':2,'sku':'V2','prices':{'price':'0','currency_code':'KWD','currency_minor_unit':3},'is_in_stock':False,'attributes':{'color':'Blue'}}])
 product=normalize(capture(raw,URL,'projection_fixture'),Platform.WOOCOMMERCE,URL)
 assert len(product.variants)==1
 record=product_to_record(product)
 assert json.dumps(record['product'],ensure_ascii=False)==json.dumps(encode_value(asdict(product)),ensure_ascii=False)
 assert record['evidence_contract']==encode_value(asdict(product.evidence_contract))
 assert record['variant_contracts']==[encode_value(asdict(v.evidence_contract)) for v in product.variants]
 restored=product_from_record(record)
 assert restored==product and restored.evidence_contract.to_dict()==product.evidence_contract.to_dict()
 assert [v.evidence_contract.to_dict() for v in restored.variants]==[v.evidence_contract.to_dict() for v in product.variants]


def test_immutable_leaves_do_not_deepcopy(monkeypatch):
 from shopextract._evidence import _record_values
 original=copy.deepcopy;calls=[]
 def spy(value,*a,**kw):calls.append(type(value));return original(value,*a,**kw)
 monkeypatch.setattr(copy,'deepcopy',spy)
 value={'list':['x',1,False,None,Decimal('0.001'),datetime(2026,1,1,tzinfo=timezone.utc),Platform.GENERIC]}
 actual=_record_values(value)
 assert actual==value and actual is not value and actual['list'] is not value['list'] and calls==[]
 class MutableText(str):pass
 text=MutableText('source');text.state=['original']
 copied=_record_values(text)
 assert calls and copied==text and copied is not text
 copied.state.append('changed');assert text.state==['original']


def test_projection_mutable_isolation():
 from shopextract._evidence import _record_values
 p=Product(raw_data={'nested':[{'value':'source'}]})
 projected=_record_values(p);projected['raw_data']['nested'][0]['value']='changed'
 assert p.raw_data=={'nested':[{'value':'source'}]} and projected['scraped_at']==p.scraped_at


def test_unsupported_portable_values_still_rejected():
 for p in (Product(in_stock='unknown'),Product(raw_data={'value':object()}),Product(price=Decimal('NaN'))):
  with pytest.raises(ValueError):product_to_record(p)
 from dataclasses import replace
 from tests.test_reliable_changes import product
 p=product();c=p.evidence_contract
 object.__setattr__(c,'schema_version',2)
 with pytest.raises(ValueError):product_to_record(p)
 cycle={};cycle['self']=cycle
 with pytest.raises(ValueError):product_to_record(Product(raw_data=cycle))
