"""008 intended red smoke; source/capture/mapper/codec remain real after implementation."""
import importlib
from pathlib import Path

import pytest

from shopextract._capture import capture
from shopextract._models import Platform
from shopextract.categories import categorized_product_from_record, categorized_product_to_record


def test_full_catalog_normalization_and_context_schema_smoke():
    try:
        api = importlib.import_module('shopextract.taxonomies.shopify')
    except ModuleNotFoundError as error:
        if error.name not in ('shopextract.taxonomies', 'shopextract.taxonomies.shopify'):
            raise
        pytest.fail('008 full Shopify taxonomy public API is not implemented', pytrace=False)
    catalog_root=Path(__file__).resolve().parents[1]/'build/shopify-taxonomy/catalogs'
    if not catalog_root.exists():pytest.skip('Full-catalog acceptance requires explicit prepared source resource; installed default loader verified separately')
    catalog = api.load_shopify_taxonomy(catalog_root=catalog_root)
    assert catalog.manifest.counts.categories == 14606
    assert catalog.manifest.counts.base_attributes == 8240
    assert catalog.manifest.counts.extensions == 316
    assert catalog.manifest.counts.values == 74820
    gid = 'gid://shopify/TaxonomyCategory/el-6-6'
    node = catalog.category(gid)
    assert node == catalog.category('el-6-6')
    assert node.id == gid and node.short_id == 'el-6-6' and node.name == 'Laptops'
    raw = capture({'id':101,'title':'Laptop','handle':'laptop','variants':[],
                   'category':{'id':gid,'name':'Laptops'}},
                  'https://merchant.test/products/laptop','synthetic_fixture')
    value = api.normalize_with_shopify_taxonomy(raw,platform=Platform.SHOPIFY,
        shop_url='https://merchant.test',taxonomy=catalog,allow_unknown_source_version=True)
    assert value is not None
    mapped = [decision for decision in value.mappings if decision.status == 'mapped']
    assert len(mapped) == 1 and mapped[0].target_ids == ('el-6-6',)
    assert mapped[0].target_version == catalog.registry_version
    restored = categorized_product_from_record(categorized_product_to_record(value))
    view = catalog.schema_for(restored)
    assert len(view.resolved) == 1 and view.resolved[0].category.id == gid
    assert len(view.resolved[0].attributes) == 19
    assert any(binding.handle == 'memory-technology' for binding in view.resolved[0].attributes)
    assert all(binding.base_attribute_id.startswith('gid://shopify/TaxonomyAttribute/')
               for binding in view.resolved[0].attributes)
