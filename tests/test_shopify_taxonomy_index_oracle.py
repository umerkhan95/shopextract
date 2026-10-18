"""Experimental storage comparison oracle; not a production backend contract."""
import importlib,json,sqlite3
import pytest
from tests.test_shopify_taxonomy_data import build
from shopextract.taxonomies.shopify.resource import read_gzip
from shopextract.taxonomies.shopify.catalog import catalog_from_data


def test_sqlite_prototype_returns_equal_materialized_schema_and_exact_misses(tmp_path):
    try:module=importlib.import_module('tests.shopify_taxonomy_index_comparison')
    except ModuleNotFoundError:pytest.fail('Storage comparison oracle/prototype not implemented',pytrace=False)
    _,staged=build(tmp_path);data=json.loads(read_gzip(staged.path/'catalog.json.gz'))
    data['categories'][1]['name']='Laptops Δ > / "'
    catalog=catalog_from_data(data,staged.manifest)
    db=tmp_path/'prototype.sqlite';facts=module.prepare_records(data,db)
    backend=module.SQLitePrototype(db)
    try:
        actual=backend.schema('el-6-6')
        assert actual==module.catalog_schema(catalog,'el-6-6')
        value=json.loads(actual)
        assert value['category']['name']=='Laptops Δ > / "'
        assert value['attributes'][0]['handle']=='panel-color'
        assert value['attributes'][0]['value_ids']==['gid://shopify/TaxonomyValue/1']
        assert backend.schema('gid://shopify/TaxonomyCategory/el-6-6')==actual
        assert backend.schema('el-6-6-unknown')==b'null'
        with pytest.raises(sqlite3.OperationalError):backend.connection.execute('DELETE FROM record')
        assert backend.cache_info().maxsize==128
        assert facts['record_rows']==6
    finally:backend.close()
