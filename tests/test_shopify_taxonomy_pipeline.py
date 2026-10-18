"""008 bounded real capture/mapper/codec bridge checks."""
from dataclasses import replace
import pytest
from tests.test_shopify_taxonomy_data import build
from shopextract._capture import capture
from shopextract._models import Platform
from shopextract.categories import categorized_product_from_record, categorized_product_to_record
from shopextract.categories.contracts import CategoryScope
from shopextract.taxonomies import shopify as api

@pytest.fixture
def catalog(tmp_path):
    _, staged = build(tmp_path)
    from shopextract.taxonomies.shopify.publish import publish_shopify_taxonomy
    publish_shopify_taxonomy(staged,catalog_root=tmp_path/'catalog')
    return api.load_shopify_taxonomy('fixture',catalog_root=tmp_path/'catalog')

def raw(gid='gid://shopify/TaxonomyCategory/el-6-6'):
    return capture({'id':101,'title':'Laptop','handle':'laptop','variants':[],
        'category':{'id':gid,'name':'Laptops'}},'https://merchant.test/products/laptop','synthetic_fixture')

def test_bridge_maps_bound_schema_and_strict_roundtrip(catalog):
    value=api.normalize_with_shopify_taxonomy(raw(),platform=Platform.SHOPIFY,shop_url='https://merchant.test',
        taxonomy=catalog,allow_unknown_source_version=True)
    restored=categorized_product_from_record(categorized_product_to_record(value))
    schema=catalog.schema_for(restored)
    assert schema.catalog_identity==catalog.registry_version
    assert [s.category.short_id for s in schema.resolved]==['el-6-6']
    assert schema.resolved[0].attributes[0].handle=='panel-color'
    assert len(schema.unresolved)==2
    with pytest.raises(ValueError):catalog.schema_for(replace(value,original_binding='broken'))

def test_bridge_unknown_version_and_unknown_gid_are_not_guessed(catalog):
    value=api.normalize_with_shopify_taxonomy(raw(),platform=Platform.SHOPIFY,shop_url='https://merchant.test',taxonomy=catalog)
    assert not catalog.schema_for(value).resolved
    value=api.normalize_with_shopify_taxonomy(raw('gid://shopify/TaxonomyCategory/missing'),platform=Platform.SHOPIFY,
        shop_url='https://merchant.test',taxonomy=catalog,allow_unknown_source_version=True)
    assert not catalog.schema_for(value).resolved
    options=api.shopify_taxonomy_options(CategoryScope(Platform.SHOPIFY,'https://merchant.test'),
        category_ids=['el-6-6','gid://shopify/TaxonomyCategory/el-6-6'],taxonomy=catalog,allow_unknown_source_version=True)
    assert options.registry.target_ids==('el-6-6',) and len(options.rules)==1
    with pytest.raises(api.TaxonomyLookupError):
        api.shopify_taxonomy_options(options.scope,category_ids=['missing'],taxonomy=catalog)
