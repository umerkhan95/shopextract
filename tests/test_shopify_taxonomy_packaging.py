"""Explicit preparation and shared offline build resource discovery."""
import importlib.util,json
from pathlib import Path
import pytest
from tests.test_shopify_taxonomy_data import sources
from shopextract.taxonomies.shopify.contracts import ShopifyReleaseSource,TaxonomyPublicationError


def test_prepare_local_override_and_cold_checkout_fail_closed(tmp_path):
    from shopextract.taxonomies.shopify.prepare import prepare_shopify_taxonomy_build
    import hashlib
    paths=sources(tmp_path);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    source=ShopifyReleaseSource('fixture','0'*40,*(sha(p) for p in paths))
    with pytest.raises(TaxonomyPublicationError):prepare_shopify_taxonomy_build(source=source,source_cache=tmp_path/'missing',build_root=tmp_path/'bad')
    staged=prepare_shopify_taxonomy_build(source=source,source_cache=tmp_path,build_root=tmp_path/'build')
    assert staged.path.joinpath('catalog.json.gz').is_file()


def test_hook_is_standalone_and_checks_pin_before_force_include(tmp_path,monkeypatch):
    spec=importlib.util.spec_from_file_location('taxonomy_build_hook',Path('hatch_build.py'))
    hook=importlib.util.module_from_spec(spec);spec.loader.exec_module(hook)
    assert callable(hook.prepared_resource)
    with pytest.raises(ValueError,match='prepare'):
        hook.prepared_resource(tmp_path)
