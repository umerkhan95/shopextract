"""P4 synthetic CLI binding acceptance; native mechanisms remain real."""
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
import pytest
from click.testing import CliRunner

from shopextract.cli import main
from shopextract._capture import capture
from shopextract._models import Platform
from shopextract.categories import (CategoryScope,CategoryOptions,CategoryLimits,TargetRegistry,
    CategorySelector,MappingRule,normalize_with_categories,categorized_product_to_record)
from shopextract.categories._codec import wire

STORE='https://supplier.test/shop'
AT=datetime(2026,10,25,tzinfo=timezone.utc)

def dump(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False));return str(path)

def options(platform=Platform.WOOCOMMERCE):
    scope=CategoryScope(platform,STORE)
    namespace={'woocommerce':'woocommerce:product_cat','shopify':'shopify:product_type',
        'magento':'magento:category','shopware':'shopware:category','bigcommerce':'bigcommerce:category',
        'generic':'schema:category'}[platform.value]
    selector=CategorySelector(namespace,None,scope=scope,native_id='7',allow_unknown_version=True)
    return CategoryOptions(scope,TargetRegistry('operator','v1',('boots',)),
        (MappingRule('r1','1',selector,('boots',)),))

def raw(platform=Platform.WOOCOMMERCE):
    if platform==Platform.WOOCOMMERCE:
        value={'id':501,'name':'Boot','prices':{'price':'9900','currency_code':'EUR','currency_minor_unit':2},'categories':[{'id':7,'name':'Boots'}]}
    elif platform==Platform.SHOPIFY:value={'id':501,'title':'Boot','variants':[],'product_type':'Boots'}
    elif platform==Platform.MAGENTO:value={'sku':'boot','name':'Boot','uid':'U501','categories':[{'uid':'Nw==','name':'Boots'}]}
    elif platform==Platform.SHOPWARE:value={'id':'501','name':'Boot','categoryIds':['7']}
    elif platform==Platform.BIGCOMMERCE:value={'entityId':501,'name':'Boot','path':'/boot','categories':{'edges':[{'node':{'entityId':7,'name':'Boots'}}],'pageInfo':{'hasNextPage':False}}}
    else:value={'@type':'Product','name':'Boot','url':STORE+'/boot','category':'Boots','offers':{'price':'99','priceCurrency':'EUR'}}
    return capture(value,STORE+'/source','synthetic_fixture',observed_at=AT)

def fixture_files(tmp_path):
    opt=options(); value=normalize_with_categories(raw(),Platform.WOOCOMMERCE,STORE,category_options=opt)
    assert value is not None
    from shopextract.categories.contracts import CategoryRuntimeConfig
    return dict(options=dump(tmp_path/'options.json',wire(opt)),raw=dump(tmp_path/'raw.json',raw()),
        categorized=dump(tmp_path/'categorized.json',[categorized_product_to_record(value)]),
        config=dump(tmp_path/'config.json',wire(CategoryRuntimeConfig(opt,(('boots','footwear'),)))))

def invoke(args,input=None):return CliRunner().invoke(main,['--output-format','json',*args],input=input)

def body(result):
    try:return json.loads(result.output)
    except Exception:raise AssertionError((result.exit_code,result.output,result.exception))

@pytest.mark.parametrize('family',['extract','normalize','map','validate','record-create','record-load',
    'tree-fetch','tree-link','tree-load','tree-export','policy-inspect','policy-review','export-companion'])
def test_p4_family_binding(tmp_path,family,monkeypatch):
    files=fixture_files(tmp_path)
    if family.startswith('tree'):
        tree=dump(tmp_path/'tree.json',tree_record())
    if family=='extract':
        install_transport(monkeypatch)
        args=['categories','extract',STORE,'--options',files['options'],'--max-products','1']
    elif family=='normalize':args=['categories','normalize',files['raw'],'--options',files['options']]
    elif family in ('map','validate'):args=['categories',family,files['categorized'],'--options',files['options']]
    elif family.startswith('record-'):
        args=['categories','record',family.split('-')[1],files['categorized']]
        if family=='record-create':args+=['--options',files['options']]
    elif family=='tree-fetch':
        install_transport(monkeypatch)
        args=['categories','tree','fetch','--options',files['options']]
    elif family=='tree-link':args=['categories','tree','link',tree,files['categorized']]
    elif family in ('tree-load','tree-export'):
        args=['categories','tree',family.split('-')[1],tree]
        if family=='tree-export':args+=['--output',str(tmp_path/'tree-out.json')]
    elif family=='policy-inspect':args=['categories','policy','inspect','--config',files['config']]
    elif family=='policy-review':args=['categories','policy','review',files['categorized'],'--config',files['config'],'--profile','footwear']
    else:args=['export',files['categorized'],'--format','json','--output',str(tmp_path/'out.json'),'--categories-output',str(tmp_path/'cats.json')]
    result=invoke(args)
    assert result.exit_code==0, (family,result.output,result.exception)
    response=body(result)
    data=response['data']
    assert response['ok'] is True and response['error'] is None and data is not None
    if family in ('extract','normalize','map','record-create','record-load','policy-review'):
        assert data['product_count']==1 and data['categorized_products'][0]['scope']['platform']=='woocommerce'
        assert data['products'][0]==data['categorized_products'][0]['product']
    if family=='validate':assert data=={'valid':True,'product_count':1}
    if family.startswith('tree-'):
        assert data.get('outcome',data.get('tree_outcome'))=='complete'
        if family=='tree-link':assert data['links'][0]['status']=='linked' and len(data['links'])==1
    if family=='policy-review':assert data['review_reasons']==[[]] and len(data['policy_digest'])==64
    if family=='policy-inspect':assert data['config']==json.loads(Path(files['config']).read_text()) and len(data['policy_digest'])==64
    if family=='export-companion':
        assert json.loads((tmp_path/'cats.json').read_text())==json.loads(Path(files['categorized']).read_text())

async def resolver(host,context):return ['93.184.216.34']

def tree_record(rows=None,headers=None):
    from shopextract.categories.woo_tree import fetch_woocommerce_category_tree,woo_tree_to_record,WooTreeLimits
    rows=rows if rows is not None else [{'id':7,'name':'Boots','slug':'boots','parent':0}]
    transport=httpx.MockTransport(lambda request:httpx.Response(200,json=rows,headers=headers or {'X-WP-Total':str(len(rows)),'X-WP-TotalPages':'1'}))
    tree=asyncio.run(fetch_woocommerce_category_tree(CategoryScope(Platform.WOOCOMMERCE,STORE),
        limits=WooTreeLimits(requests=1),resolver=resolver,wire_transport=transport,utc_now=lambda:AT))
    return woo_tree_to_record(tree)

def install_transport(monkeypatch,rows=None,status=200):
    from shopextract.categories import woo_tree
    original=woo_tree.fetch_woocommerce_category_tree
    rows=rows if rows is not None else [{'id':7,'name':'Boots','slug':'boots','parent':0}]
    async def delegated(scope,**kwargs):
        return await original(scope,**kwargs,resolver=resolver,
            wire_transport=httpx.MockTransport(lambda request:httpx.Response(status,json=rows,headers={'X-WP-Total':str(len(rows)),'X-WP-TotalPages':'1'})),utc_now=lambda:AT)
    monkeypatch.setattr(woo_tree,'fetch_woocommerce_category_tree',delegated)
    original_client=httpx.AsyncClient
    def client(*args,**kwargs):
        kwargs.setdefault('transport',httpx.MockTransport(lambda request:httpx.Response(status,json=[{'id':501,'name':'Boot','permalink':STORE+'/boot','prices':{'price':'9900','currency_code':'EUR','currency_minor_unit':2},'categories':[{'id':7,'name':'Boots'}]}],headers={'X-WP-Total':'1','X-WP-TotalPages':'1'})))
        return original_client(*args,**kwargs)
    monkeypatch.setattr(httpx,'AsyncClient',client)

@pytest.mark.parametrize('flag,args',[('--storefront-config',True),('--enrich-identifiers',False),('--restore-short-gtin',False)])
def test_extract_controls_binding(tmp_path,monkeypatch,flag,args):
    files=fixture_files(tmp_path);install_transport(monkeypatch)
    command=['categories','extract',STORE,'--options',files['options'],flag]
    if args:command+=[dump(tmp_path/'storefront.json',{})]
    result=invoke(command)
    assert result.exit_code==0,(result.output,result.exception)
    assert body(result)['data']['product_count']==1
