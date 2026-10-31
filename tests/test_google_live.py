"""Controlled boundary tests; these never claim actual merchant verification."""
from dataclasses import asdict
from hashlib import sha256
import importlib
import json

import httpx
import pytest


def api():
    try:
        return importlib.import_module('shopextract.taxonomies.google.live')
    except ModuleNotFoundError as error:
        if error.name != 'shopextract.taxonomies.google.live':
            raise
        pytest.fail('Configured Google live verification API is not implemented', pytrace=False)


@pytest.fixture
def profile(tmp_path):
    from shopextract import prepare_google_taxonomy, load_google_taxonomy
    source = tmp_path / 'source.txt'
    source.write_text('# Google_Product_Taxonomy_Version: 2021-09-21\n1 - Media\n784 - Media > Books\n')
    prepare_google_taxonomy(source, tmp_path / 'catalogs')
    taxonomy = load_google_taxonomy(catalog_root=tmp_path / 'catalogs')
    (tmp_path / 'cli.json').write_text('{"schema_version":1,"output_format":"json","diagnostics":"quiet"}')
    rule = {'rule_id':'books-reviewed','version':'1','selector':{'namespace':'schema.org:category',
        'taxonomy_version':None,'scope':None,'native_id':None,'raw_label':'Books',
        'raw_path':None,'allow_unknown_version':True},'target_ids':['784']}
    data = {'schema_version':1,'catalog_root':'catalogs','catalog_fingerprint':taxonomy.manifest.fingerprint,
        'cli_config':'cli.json','sites':[{'id':'books','url':'https://shop.test/item',
        'platform':'generic','source_kind':'html','shop_url':'https://shop.test','mapping_rules':[rule]}],
        'limits':{'requests':8,'products':4,'seconds':120,'response_bytes':1048576}}
    path = tmp_path / 'profile.json';path.write_text(json.dumps(data))
    return tmp_path, path, data


def test_live_dry_run_is_not_a_scan(profile):
    root, path, _ = profile
    result = api().verify_google_live(path, root / 'out', project_root=root)
    assert result['status'] == 'needs_review' and not result['live_verified']
    assert result['usage']['requests'] == 0 and result['sites'][0]['fetch']['status'] == 'not_run'


def test_live_current_policy_skip_never_requests(profile, monkeypatch):
    root, path, _ = profile
    module = api()
    monkeypatch.setattr(module, 'policy_denial', lambda url: {'reason':'host_not_allowed','sha256':'a'*64})
    result = module.verify_google_live(path, root / 'out', project_root=root, live=True)
    assert result['status'] == 'blocked' and not result['live_verified']
    assert result['usage']['requests'] == 0
    assert result['sites'][0]['fetch']['status'] == 'skipped_network_policy'


def test_live_controlled_actual_parse_cli_export_roundtrip(profile):
    root, path, _ = profile
    body = '<script type="application/ld+json">'+json.dumps({'@type':'Product','name':'Book',
        'category':'Books','offers':{'price':'1.00','priceCurrency':'PKR'}})+'</script>'
    transport = httpx.MockTransport(lambda request: httpx.Response(200, text=body))
    result = api().verify_google_live(path, root / 'out', project_root=root, live=True, transport=transport)
    assert result['status'] == 'pass', result
    assert result['mode'] == 'controlled' and not result['live_verified']
    site = result['sites'][0]
    assert site['mapping']['classifications'][0]['target_id'] == '784'
    assert site['export']['verified'] and site['cli']['exit_code'] == 0
    assert site['cli']['sha256']==sha256((root/'out'/site['cli']['output']).read_bytes()).hexdigest()
    assert (root / 'out' / site['artifacts']['raw']).is_file()


def test_live_empty_rules_cannot_guess_from_title(profile):
    root, path, data = profile;data['sites'][0]['mapping_rules']=[];path.write_text(json.dumps(data))
    body='<script type="application/ld+json">'+json.dumps({'@type':'Product','name':'Book','category':'Books'})+'</script>'
    result=api().verify_google_live(path,root/'out',project_root=root,live=True,
        transport=httpx.MockTransport(lambda request:httpx.Response(200,text=body)))
    assert result['status']=='needs_review' and not result['live_verified']
    assert not any(c['status']=='mapped' for c in result['sites'][0]['mapping']['classifications'])


def test_live_redirect_cannot_expand_source_origin(profile):
    root,path,_=profile;calls=[]
    def respond(request):
        calls.append(str(request.url));return httpx.Response(302,headers={'location':'https://other.test/item'})
    result=api().verify_google_live(path,root/'out',project_root=root,live=True,transport=httpx.MockTransport(respond))
    assert result['status']=='blocked' and calls==['https://shop.test/item']
    assert result['usage']['requests']==1


def test_live_rejects_existing_output_before_network(profile):
    root,path,_=profile;(root/'out').mkdir()
    with pytest.raises(ValueError):api().verify_google_live(path,root/'out',project_root=root,live=True)


@pytest.mark.parametrize('change',[lambda p:p.update(extra=True),
    lambda p:p['sites'][0].update(shop_url='https://other.test'),
    lambda p:p['limits'].update(requests=9)])
def test_live_profile_rejects_invalid_scope_limits(profile,change):
    root,path,data=profile;change(data);path.write_text(json.dumps(data))
    with pytest.raises(ValueError):api().verify_google_live(path,root/'out',project_root=root)


def test_live_duplicate_profile_key_rejected_before_output(profile):
    root,path,_=profile;path.write_text('{"schema_version":1,"schema_version":1}')
    with pytest.raises(ValueError):api().verify_google_live(path,root/'out',project_root=root)
    assert not (root/'out').exists()


def test_live_wrong_store_rule_rejected(profile):
    root,path,data=profile
    data['sites'][0]['mapping_rules'][0]['selector']['scope']={'platform':'generic','store_url':'https://other.test','catalog':None,'channel':None,'locale':None}
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):api().verify_google_live(path,root/'out',project_root=root)


def test_live_failed_report_write_cannot_publish_success(profile,monkeypatch):
    root,path,_=profile;module=api()
    def fail(*args,**kwargs):raise OSError('Injected report publication failure')
    monkeypatch.setattr(module,'atomic_json',fail)
    with pytest.raises(OSError):module.verify_google_live(path,root/'out',project_root=root)
    assert not (root/'out'/'report.json').exists()


def test_live_response_limit_has_no_fabricated_products(profile):
    root,path,data=profile;data['limits']['response_bytes']=10;path.write_text(json.dumps(data))
    result=api().verify_google_live(path,root/'out',project_root=root,live=True,
        transport=httpx.MockTransport(lambda request:httpx.Response(200,text='x'*11)))
    assert result['status']=='blocked' and result['usage']=={'requests':1,'products':0}
    assert not result['live_verified'] and not (root/'out'/'books.raw.json').exists()


def test_live_malformed_shopify_response_is_reported(profile):
    root,path,data=profile;data['sites'][0].update(platform='shopify',source_kind='shopify_products',mapping_rules=[])
    path.write_text(json.dumps(data))
    result=api().verify_google_live(path,root/'out',project_root=root,live=True,
        transport=httpx.MockTransport(lambda request:httpx.Response(200,json=[])))
    assert result['status']=='fail' and not result['live_verified']
    assert result['sites'][0]['parser']['status']=='not_run'


def test_policy_unknown_boolean_version_never_establishes_denial(tmp_path,monkeypatch):
    policy=importlib.import_module('shopextract.taxonomies.google.live_policy')
    source=tmp_path/'policy.json';source.write_text(json.dumps({'version':True,
        'http_network_policy':{'type':'restricted','egress_rules':[]}}))
    monkeypatch.setattr(policy,'Path',lambda _:source)
    assert policy.policy_denial('https://shop.test/item') is None


@pytest.mark.parametrize('change',[lambda r:r.update(target_ids=[]),
    lambda r:r['selector'].update(allow_unknown_version=False),lambda r:r.update(target_ids=['999'])])
def test_live_invalid_semantic_rules_reject_before_transport(profile,change):
    root,path,data=profile;change(data['sites'][0]['mapping_rules'][0]);path.write_text(json.dumps(data));calls=[]
    with pytest.raises(ValueError):
        api().verify_google_live(path,root/'out',project_root=root,live=True,
            transport=httpx.MockTransport(lambda request:calls.append(request) or httpx.Response(200,text='x')))
    assert not calls and not (root/'out').exists()


def test_live_duplicate_css_field_rejects_before_output(profile):
    root,path,data=profile;field={'name':'title','selector':'h1','type':'text'}
    data['sites'][0].update(source_kind='html_css',css_schema={'baseSelector':'body','fields':[field,field]})
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError):api().verify_google_live(path,root/'out',project_root=root)


def test_live_static_css_reuses_dom_capture_without_browser(profile):
    root,path,data=profile
    data['sites'][0].update(source_kind='html_css',css_schema={'baseSelector':'body','fields':[
        {'name':'title','selector':'h1','type':'text'}, {'name':'price','selector':'.price','type':'text'},
        {'name':'product_type','selector':'.category','type':'text'}]})
    data['sites'][0]['mapping_rules'][0]['selector']['namespace']='generic:product_type'
    path.write_text(json.dumps(data))
    result=api().verify_google_live(path,root/'out',project_root=root,live=True,
        transport=httpx.MockTransport(lambda request:httpx.Response(200,text='<html><body><h1>Book</h1><p class="price">1.00</p><p class="category">Books</p></body></html>')))
    assert result['status']=='pass',result
    assert result['sites'][0]['mapping']['classifications'][0]['target_id']=='784'
    assert not result['live_verified']


@pytest.mark.parametrize('url,shop',[('https://shop.test/shop/%2525252e%2525252e/private','https://shop.test/shop'),
    ('https://224.0.0.1/item','https://224.0.0.1')])
def test_live_public_scope_rejects_ambiguous_escape_and_multicast(url,shop):
    api()
    from shopextract.taxonomies.google.live_profile import in_scope
    assert not in_scope(url,shop)


def test_live_default_project_root_is_invocation_directory(profile,monkeypatch):
    root,path,_=profile;monkeypatch.chdir(root)
    result=api().verify_google_live(path,root/'out')
    assert result['status']=='needs_review' and result['usage']['requests']==0
