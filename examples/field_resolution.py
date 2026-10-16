"""Offline, fixed-time field authority demonstration; no network or model calls."""
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
import json
from uuid import NAMESPACE_URL, uuid5

from shopextract import (Evidence, FieldObservation, Product, TrustContract,
                        classify_match, resolve_fields, resolution_references)

AS_OF = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)


def demonstrate():
    evidence, observations = [], []
    def add(label, path, value, role):
        eid='e_'+str(uuid5(NAMESPACE_URL,'fixture/evidence/'+label))
        oid='o_'+str(uuid5(NAMESPACE_URL,'fixture/observation/'+label))
        evidence.append(Evidence(eid,'https://'+role+'.example/catalog',AS_OF,
            'offline_fixture',retained_data={'value':value},pointer='/value',source_role=role))
        observations.append(FieldObservation(oid,path,'observed',value,value,[eid]))
    add('supplier-color','/attributes/color','red','supplier')
    add('manufacturer-color','/attributes/color','blue','verified_manufacturer')
    add('supplier-price','/price',Decimal('80.00'),'supplier')
    add('manufacturer-list-price','/price',Decimal('120.00'),'verified_manufacturer')
    add('stock-a','/in_stock',True,'supplier')
    add('stock-b','/in_stock',False,'supplier')
    observations.append(FieldObservation('o_'+str(uuid5(NAMESPACE_URL,'fixture/missing-gtin')),
        '/gtin','unknown',reason='GTIN absent from both fixture sources'))
    p=Product(title='Offline product',price=Decimal('80'),currency='EUR',attributes={'color':'red'})
    original=TrustContract(evidence,observations)
    p.evidence_contract=resolve_fields(original,as_of=AS_OF)
    view=p.trust_view()
    assert view['/attributes/color']['value']=='blue'
    assert view['/price']['value']==Decimal('80.00')
    assert view['/in_stock']['state']=='conflicting' and view['/in_stock']['value'] is None
    assert view['/gtin']['state']=='unknown' and not original.resolutions
    decision=classify_match(p,Product(title='Offline product'))
    return {'as_of':AS_OF.isoformat(), 'fields':resolution_references(p.evidence_contract),
            'matching':asdict(decision), 'retained_contract':p.evidence_contract.to_dict()}


if __name__=='__main__':
    print(json.dumps(demonstrate(),indent=2,ensure_ascii=False))
