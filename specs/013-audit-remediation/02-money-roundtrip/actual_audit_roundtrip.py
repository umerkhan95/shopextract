"""Bounded historical audit pipeline diagnostic, not CI fixture or live evidence."""
from pathlib import Path
import json
import tempfile
from click.testing import CliRunner
from shopextract._cli_data import read_json_file,products_from_value
from shopextract._cli_core import CliFailure
from dataclasses import fields,asdict
from shopextract._models import Product
from shopextract._evidence import encode_value,decode_value
def contract_data(owner):
    contract=getattr(owner,"evidence_contract",None)
    return encode_value(asdict(contract)) if contract is not None else None
from shopextract.cli import main
from shopextract.export._bundle import load_evidence_sidecar

base=Path(__file__).parent
source=json.loads((base/'actual-audit-shape.json').read_text())
report={'provenance':'supplied historical extraction; current bounded pipeline diagnostic',
        'source':source['source'],'sha256':source['sha256'],'known_nodes':source['nodes'],'checks':{},'status':'running','stage':'reader'}
def save():
    (base/'actual-audit-roundtrip.json').write_text(json.dumps(report,indent=2)+'\n')
save()
try:
    value=read_json_file(source['source']);products=products_from_value(value)
    report['stage']='record-equality';save()
    original=value.get('data',value)['products']
    assert len(products)==25
    for before,product in zip(original,products):
        expected=decode_value(before['product'])
        for field in fields(Product):
            actual=getattr(product,field.name)
            if field.name=='variants':actual=[asdict(v) for v in actual]
            assert actual==expected[field.name],field.name
        assert contract_data(product)==before['evidence_contract']
        assert [contract_data(v) for v in product.variants]==before['variant_contracts']
    variant_count=sum(len(p.variants) for p in products);assert variant_count>0
    report['checks']['reader_variants_evidence']=True;report['stage']='analyzer';save()
    analyzer=CliRunner().invoke(main,['--output-format','json','analyze-file',source['source']])
    assert analyzer.exit_code==0,analyzer.output[:200]
    assert json.loads(analyzer.stdout)['data']['statistics']['total_products']==25
    report['checks']['analyzer']=True;report['stage']='export';save()
    with tempfile.TemporaryDirectory(prefix='audit-roundtrip-') as temp:
        artifact=Path(temp)/'products.csv';sidecar=Path(temp)/'evidence.json'
        export=CliRunner().invoke(main,['--output-format','json','export',source['source'],
            '--format','csv','-o',str(artifact),'--evidence-output',str(sidecar)])
        assert export.exit_code==0,export.output[:200]
        report['stage']='sidecar-reload';save()
        restored=load_evidence_sidecar(json.loads(sidecar.read_text()),artifact.read_bytes())
        report['stage']='restored-record-equality';save()
        assert restored==products
        for left,right in zip(restored,products):
            assert contract_data(left)==contract_data(right)
            assert [contract_data(v) for v in left.variants]==[contract_data(v) for v in right.variants]
    report.update(status='passed',product_count=25,variant_count=variant_count)
    report['checks']['export_sidecar_variants_evidence']=True
except (CliFailure,OSError,ValueError,AssertionError) as error:
    report.update(status='blocked' if isinstance(error,(CliFailure,OSError)) else 'failed',
                  error=type(error).__name__,error_code=getattr(error,'code',None),reason=str(error)[:200])
(base/'actual-audit-roundtrip.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
