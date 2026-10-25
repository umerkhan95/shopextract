"""P2 acceptance contracts; synthetic data, no public network."""
import json
from click.testing import CliRunner
from shopextract.cli import main


def invoke(args, value=None):
    return CliRunner().invoke(main, args, input=None if value is None else json.dumps(value))


def test_analyze_file_smoke():
    result = invoke(['analyze-file','-'], [{'title':'A','price':'0.10','currency':'USD','vendor':'V'}]*11)
    assert result.exit_code == 0, result.output
    data = json.loads(result.output)['data']
    assert data['statistics']['total_products'] == 11
    assert data['statistics']['brands'] == {'V':11}
    assert data['aggregate_precision'] == 'native_float_approximate'


def test_nested_help_skips_config():
    result = invoke(['--config','missing','stats','distribution','--help'])
    assert result.exit_code == 0, result.output
    assert '--buckets' in result.output


def test_nested_unknown_child_machine():
    result = invoke(['--output-format','json','stats','missing','--help'])
    assert result.exit_code == 2
    assert json.loads(result.output)['error']['code'] == 'E_USAGE'


def test_nested_operand_help_is_value():
    result = invoke(['--output-format','json','stats','distribution','--buckets','--help','-'], [])
    assert result.exit_code == 2
    assert json.loads(result.output)['error']['code'] == 'E_USAGE'


def test_nested_root_flags_rejected():
    result = invoke(['--output-format','json','stats','brands','--output-format','json','-'], [])
    assert result.exit_code == 2
    assert json.loads(result.output)['error']['code'] == 'E_USAGE'


def test_double_dash_operand():
    result = invoke(['--output-format','json','stats','brands','--','--help'])
    assert result.exit_code == 2
    assert json.loads(result.output)['error']['code'] == 'E_USAGE'

import pytest
from decimal import Decimal
from shopextract._models import Product
from shopextract._portable import product_to_record

@pytest.mark.parametrize('args,value', [
    (['match','-','right.json'], []),
    (['match-gtin','00012345600012','-'], []),
    (['match-pair','-','pair.json'], [{'title':'A'}]),
    (['match-evaluate','-'], []),
    (['identity','assign','-'], []),
    (['identity','inspect','-'], []),
    (['stats','distribution','-'], []),
    (['stats','outliers','-'], []),
    (['stats','brands','-'], []),
    (['competitive','brands','-'], {}),
    (['duplicates','-'], []),
    (['images','check','-'], []),
    (['export','-','--format','json','--output','-'], []),
])
def test_workflow_red_families(args,value,tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path/'right.json').write_text('[]')
    (tmp_path/'pair.json').write_text('[{"title":"A"}]')
    result = invoke(args,value)
    assert result.exit_code == 0, result.output


def test_exact_portable_identity():
    product = Product(title='A',product_url='https://synthetic.example/a',price=Decimal('0.10'),gtin='00012345600012',in_stock=False)
    result = invoke(['identity','assign','-'], [product_to_record(product)])
    assert result.exit_code == 0, result.output
    record = json.loads(result.output)['data']['products'][0]
    assert record['product']['price'] == {'$type':'decimal','value':'0.10'}
    assert record['product']['gtin'] == '00012345600012'
    assert record['product']['in_stock'] is False


def test_safe_compare_native_signature():
    import inspect
    from shopextract.compare.price import compare
    assert 'currency_safe' in inspect.signature(compare).parameters


def test_safe_position_native_signature():
    import inspect
    from shopextract.analyze.competitive import price_position
    assert 'currency' in inspect.signature(price_position).parameters


def test_machine_validate_stdin():
    result = invoke(['--output-format','json','validate','-'], [{'title':'A'}])
    assert result.exit_code == 4, result.output
    assert json.loads(result.output)['data']['invalid'] == 1


def test_export_replace_rollback(tmp_path,monkeypatch):
    import os
    source = tmp_path/'source.json'
    source.write_text(json.dumps([product_to_record(Product(title='A',price=Decimal('0.10')))]))
    output = tmp_path/'out.csv'; side = tmp_path/'side.json'
    side.write_text('old side')
    original = os.replace
    attempts = []
    def fail_second(src,dst):
        attempts.append(str(dst))
        if str(dst) == str(side):
            raise OSError('injected second replacement')
        original(src,dst)
    monkeypatch.setattr(os,'replace',fail_second)
    result = invoke(['export',str(source),'--format','csv','--output',str(output),'--evidence-output',str(side)])
    assert result.exit_code == 1
    assert attempts[:2] == [str(output),str(side)]
    assert not output.exists()
    assert side.read_text() == 'old side'
    assert not list(tmp_path.glob('.out.csv.*'))


@pytest.mark.parametrize('path',[['--','stats','distribution','--help'],['stats','--','distribution','--help']])
def test_nested_parser_resets_terminator_for_help(path):
    result=invoke(['--config','missing',*path])
    assert result.exit_code==0,result.output
    assert '--buckets' in result.output
