"""Predesigned resource edges; synthetic data, no source/model activity."""
import json

import pytest

from shopextract._cli_core import CliFailure
from shopextract._cli_data import bounded_tree, raw_records, read_json_file


@pytest.mark.parametrize('size',[1048575,1048576,1048577])
def test_input_byte_edges(tmp_path,size):
    path=tmp_path/'input.json';path.write_bytes(b'[]'+b' '*(size-2))
    if size>1048576:
        with pytest.raises(CliFailure): read_json_file(str(path))
    else:
        assert read_json_file(str(path))==[]


@pytest.mark.parametrize('size',[999,1000,1001])
def test_record_count_edges(size):
    records=[{} for _ in range(size)]
    if size>1000:
        with pytest.raises(CliFailure): raw_records(records)
    else:
        assert len(raw_records(records))==size


@pytest.mark.parametrize('depth',[63,64,65])
def test_depth_edges(depth):
    value=0
    for _ in range(depth): value=[value]
    if depth>64:
        with pytest.raises(ValueError): bounded_tree(value)
    else: bounded_tree(value)


@pytest.mark.parametrize('nodes',[99999,100000,100001])
def test_node_edges(nodes):
    value=[None]*(nodes-1)
    if nodes>100000:
        with pytest.raises(ValueError): bounded_tree(value)
    else: bounded_tree(value)


def test_mixed_and_variant_misalignment_rejected():
    from shopextract._cli_data import products_from_value
    from shopextract._portable import product_to_record
    from shopextract._models import Product
    record=product_to_record(Product(title='A'))
    record['variant_contracts']=[None]
    with pytest.raises(CliFailure): products_from_value([record])
    valid=product_to_record(Product(title='B'))
    with pytest.raises(CliFailure): products_from_value([valid,{'title':'raw'}])


def test_empty_batch_quality():
    from click.testing import CliRunner
    from shopextract.cli import main
    result=CliRunner().invoke(main,['--output-format','json','quality','-'],input='[]')
    assert result.exit_code==0
    assert json.loads(result.stdout)['data']=={'scores':[],'batch_score':0.0,'product_count':0}
