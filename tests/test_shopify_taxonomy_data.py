"""008 data importer/lookup mechanisms; tiny source-shaped fixtures, no HTTP."""
import gzip
import hashlib
import importlib
import json
from pathlib import Path

import pytest


def api():
    try:
        return importlib.import_module('shopextract.taxonomies.shopify')
    except ModuleNotFoundError as error:
        if error.name not in ('shopextract.taxonomies','shopextract.taxonomies.shopify'):
            raise
        pytest.fail('008 full catalog importer/loader is not implemented',pytrace=False)


def sources(tmp_path, *, broken=False):
    prefix='gid://shopify/'
    value={'id':prefix+'TaxonomyValue/1','name':'Blue','handle':'color__blue'}
    attribute={'id':prefix+'TaxonomyAttribute/1','name':'Color','handle':'color','description':'Canonical color',
        'extended_attributes':[{'name':'Panel color','handle':'panel-color'}],'values':[value]}
    root={'id':prefix+'TaxonomyCategory/el','level':0,'name':'Electronics','full_name':'Electronics','parent_id':None,
        'attributes':[],'return_reasons':[],'children':[{'id':prefix+'TaxonomyCategory/el-6-6','name':'Laptops'}],'ancestors':[]}
    root['return_reasons']=[{'id':prefix+'ReturnReasonDefinition/10','name':'Color','handle':'color','description':'Color mismatch'}]
    leaf={'id':prefix+'TaxonomyCategory/el-6-6','level':1,'name':'Laptops','full_name':'Electronics > Laptops','parent_id':root['id'],
        'attributes':[{'id':attribute['id'],'name':'Panel color','handle':'panel-color','description':'Contextual color','extended':True}],
        'return_reasons':[],'children':[],'ancestors':[{'id':root['id'],'name':root['name']}]}
    if broken:
        leaf['parent_id']=prefix+'TaxonomyCategory/missing'
    data={'version':'fixture','verticals':[{'name':'Electronics','prefix':'el','categories':[root,leaf]}],'attributes':[attribute]}
    yaml_data={'base_attributes':[{'id':1,'name':'Color','friendly_id':'color','handle':'color','description':'Canonical color','values':['color__blue']}],
        'extended_attributes':[{'name':'Panel color','friendly_id':'panel_color','handle':'panel-color','description':'Contextual color','values_from':'color'}]}
    paths=[]
    for name,blob in [('taxonomy.en.json.gz',gzip.compress(json.dumps(data).encode(),mtime=0)),('attributes.yml',json.dumps(yaml_data).encode()),('LICENSE',b'MIT synthetic fixture')]:
        path=tmp_path/name;path.write_bytes(blob);paths.append(path)
    return paths


def build(tmp_path, *, broken=False):
    api_module=api()
    contracts=importlib.import_module('shopextract.taxonomies.shopify.contracts')
    builder=importlib.import_module('shopextract.taxonomies.shopify.build')
    paths=sources(tmp_path,broken=broken)
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    source=contracts.ShopifyReleaseSource('fixture','0'*40,*(sha(p) for p in paths))
    downloaded=contracts.DownloadedRelease(source,*paths)
    staged=builder.build_shopify_taxonomy(downloaded,staging_root=tmp_path/'staging')
    return api_module,staged


def test_data_smoke_build_publish_lookup_context(tmp_path):
    module,staged=build(tmp_path)
    publisher=importlib.import_module('shopextract.taxonomies.shopify.publish')
    manifest=publisher.publish_shopify_taxonomy(staged,catalog_root=tmp_path/'catalogs')
    catalog=module.load_shopify_taxonomy('fixture',catalog_root=tmp_path/'catalogs',fingerprint=manifest.fingerprint)
    leaf=catalog.category('el-6-6')
    assert leaf.id=='gid://shopify/TaxonomyCategory/el-6-6'
    assert [c.short_id for c in catalog.ancestors(leaf.id)]==['el']
    assert catalog.manifest.counts.categories==2 and catalog.manifest.counts.extensions==1
    assert catalog.category('el').return_reason_ids==('gid://shopify/ReturnReasonDefinition/10',)
    binding,=catalog.attributes_for(leaf.id)
    assert binding.name=='Panel color' and binding.extended and binding.extension_handle=='panel-color'
    assert catalog.attribute('1').name=='Color'
    assert catalog.attribute('panel_color').values_from=='color'
    assert catalog.values_for('panel-color')==catalog.values_for('color')
    assert catalog.value('color__blue').name=='Blue'
    with pytest.raises(AttributeError):
        leaf.name='changed'
    assert catalog.category('unknown') is None
    with pytest.raises(TypeError): catalog.category(None)


def test_invalid_source_is_rejected_before_publication(tmp_path):
    module=api()
    with pytest.raises(module.TaxonomyIntegrityError):
        build(tmp_path,broken=True)
    assert not (tmp_path/'catalogs').exists()


def test_resource_corruption_rejected_and_publication_idempotent(tmp_path):
    module,staged=build(tmp_path)
    publisher=importlib.import_module('shopextract.taxonomies.shopify.publish')
    first=publisher.publish_shopify_taxonomy(staged,catalog_root=tmp_path/'catalogs')
    second=publisher.publish_shopify_taxonomy(staged,catalog_root=tmp_path/'catalogs')
    assert first==second
    resource=tmp_path/'catalogs'/'fixture'/first.fingerprint/'catalog.json.gz'
    resource.write_bytes(resource.read_bytes()+b'corrupt')
    with pytest.raises(module.TaxonomyIntegrityError):
        module.load_shopify_taxonomy('fixture',catalog_root=tmp_path/'catalogs',fingerprint=first.fingerprint)


@pytest.mark.parametrize('change',['traversal','release','fingerprint','counts','source_hash'])
def test_publication_rejects_staged_identity_before_filesystem(tmp_path,change):
    from dataclasses import replace
    module,staged=build(tmp_path)
    publisher=importlib.import_module('shopextract.taxonomies.shopify.publish')
    manifest=staged.manifest
    if change=='traversal':manifest=replace(manifest,release='../../outside')
    elif change=='release':manifest=replace(manifest,release='other')
    elif change=='fingerprint':manifest=replace(manifest,fingerprint='bad')
    elif change=='counts':manifest=replace(manifest,counts=replace(manifest.counts,categories=999))
    else:manifest=replace(manifest,source_hashes=(('taxonomy.en.json.gz','f'*64),)+manifest.source_hashes[1:])
    with pytest.raises((module.TaxonomyPublicationError,module.TaxonomyIntegrityError)):
        publisher.publish_shopify_taxonomy(replace(staged,manifest=manifest),catalog_root=tmp_path/'catalogs')
    assert not (tmp_path/'catalogs').exists()
    assert not (tmp_path/'outside').exists()


def test_publication_rejects_changed_copied_stage(tmp_path,monkeypatch):
    module,staged=build(tmp_path)
    publisher=importlib.import_module('shopextract.taxonomies.shopify.publish')
    original=Path.read_bytes
    def substituted(path):
        data=original(path)
        if path==staged.path/'manifest.json':
            manifest=json.loads(data);manifest['release']='other'
            return json.dumps(manifest).encode()
        return data
    monkeypatch.setattr(Path,'read_bytes',substituted)
    root=tmp_path/'catalogs';root.mkdir();marker=root/'prior';marker.write_text('unchanged')
    with pytest.raises((module.TaxonomyPublicationError,module.TaxonomyIntegrityError)):
        publisher.publish_shopify_taxonomy(staged,catalog_root=root)
    assert marker.read_text()=='unchanged'
    assert not (root/'fixture'/staged.manifest.fingerprint).exists()
    assert not list(root.rglob('.publishing-*')) and not list(root.rglob('*.lock'))


@pytest.mark.parametrize('bad',['value_name','attribute_name','short_id','bool_level','bool_schema','id_suffix','extra_field'])
def test_metadata_schema_rejects_mutable_or_mistyped_records(tmp_path,bad):
    from shopextract.taxonomies.shopify.resource import read_gzip
    from shopextract.taxonomies.shopify.validation import validate_catalog
    module,staged=build(tmp_path)
    data=json.loads(read_gzip(staged.path/'catalog.json.gz'))
    if bad=='value_name':data['values'][0]['name']=[]
    elif bad=='attribute_name':data['attributes'][0]['name']={'bad':'mutable'}
    elif bad=='short_id':data['categories'][1]['short_id']='wrong'
    elif bad=='bool_level':data['categories'][1]['level']=True
    elif bad=='bool_schema':data['schema_version']=True
    elif bad=='extra_field':data['values'][0]['unexpected']='data'
    else:
        data['values'][0]['id']='gid://shopify/TaxonomyValue/'
        data['attributes'][0]['value_ids']=[data['values'][0]['id']]
    with pytest.raises(module.TaxonomyIntegrityError):validate_catalog(data)


def test_publication_rejects_changed_logical_payload_with_valid_byte_hash(tmp_path):
    from shopextract.taxonomies.shopify.resource import read_gzip
    module,staged=build(tmp_path)
    publisher=importlib.import_module('shopextract.taxonomies.shopify.publish')
    resource=staged.path/'catalog.json.gz'
    data=json.loads(read_gzip(resource));data['values'][0]['name']='Coherent but different data'
    resource.write_bytes(gzip.compress(json.dumps(data).encode(),mtime=0))
    manifest_path=staged.path/'manifest.json'
    manifest=json.loads(manifest_path.read_text())
    manifest['resource_sha256']=hashlib.sha256(resource.read_bytes()).hexdigest()
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(module.TaxonomyPublicationError,match='fingerprint'):
        publisher.publish_shopify_taxonomy(staged,catalog_root=tmp_path/'catalogs')
    assert not (tmp_path/'catalogs').exists()
