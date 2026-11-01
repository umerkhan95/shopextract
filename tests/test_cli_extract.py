"""P1 acceptance through the real Click entry point; synthetic transport only."""
import json
from decimal import Decimal

import pytest
from click.testing import CliRunner

from shopextract.cli import main


def invoke(*args, input=None, env=None):
    return CliRunner().invoke(main, ['--output-format', 'json', *args], input=input, env=env)


def value(result):
    assert result.stdout.startswith('{'), result.output[:800]
    return json.loads(result.stdout)


def test_new_commands_declared():
    assert {'extract-one', 'feed', 'normalize', 'quality'} <= set(main.commands)


def test_actual_quality_stdin():
    result = invoke('quality', '-', input='[{"title":"A","image_url":"x"},{}]')
    assert result.exit_code == 0, result.output[:800]
    assert value(result)['data'] == {'scores': [0.55, 0.0], 'batch_score': 0.275, 'product_count': 2}


def test_actual_normalize_and_portable_roundtrip():
    from shopextract._portable import product_from_record
    result = invoke('normalize', '-', '--platform', 'shopify', '--shop-url', 'https://fixture.invalid', input=json.dumps([{'id':'001','title':'A','handle':'a','images':[{'src':'https://fixture.invalid/a.png'}], 'variants':[{'id':'002','price':'0.10','sku':'0012','available':False}]}, {}]))
    assert result.exit_code == 0, result.output[:800]
    data = value(result)['data']
    assert data['product_count'] == 1 and data['dropped_indices'] == [1]
    product = product_from_record(data['products'][0])
    assert product.price == Decimal('0.10') and product.sku == '0012' and product.in_stock is False


@pytest.mark.parametrize('args', [('extract','https://fixture.invalid','--max','0'), ('discover','https://fixture.invalid','--max','1001'), ('extract','https://fixture.invalid','--llm-model','ollama/test')])
def test_invalid_options_before_fetch(args):
    result = invoke(*args)
    assert result.exit_code == 2, result.output[:800]
    assert value(result)['error']['code'] == 'E_USAGE'


def test_empty_extract_one_is_unavailable(monkeypatch):
    import shopextract
    async def empty(url, **kwargs):
        return {}
    monkeypatch.setattr(shopextract, 'extract_one', empty)
    result = invoke('extract-one', 'https://fixture.invalid/a')
    assert result.exit_code == 1
    response = value(result)
    assert response['data'] is None and response['completeness'] == 'unavailable'
    assert response['error']['code'] == 'E_OPERATION'


@pytest.fixture
def transport(monkeypatch):
    import httpx
    original = httpx.AsyncClient
    calls=[]
    routes={}
    from tests._discovery_boundary import borrow_worker_network
    borrow_worker_network(monkeypatch)
    def handle(request):
        calls.append(request)
        route = routes.get(request.url.path)
        assert route is not None, f'Undeclared synthetic transport {request.url.path}'
        if callable(route):
            return route(request)
        return httpx.Response(200, json=route)
    def client(*args, **kwargs):
        kwargs['transport'] = httpx.MockTransport(handle)
        return original(*args, **kwargs)
    monkeypatch.setattr(httpx, 'AsyncClient', client)
    return routes,calls


def shopify_products(count=11):
    return [{'id':f'{i:04}', 'title':f'Synthetic product {i}', 'handle':f'item-{i}',
             'images':[{'src':f'https://fixture.invalid/{i}.png'}], 'body_html':'<p>Source description</p>',
             'variants':[{'id':f'{i:04}01', 'price':'0.10','sku':f'{i:06}',
                          'barcode':'036000291452','available':False,'compare_at_price':None}]}
            for i in range(count)]


def test_eleven_products_native_transport_and_exact_codec(transport):
    from shopextract._portable import product_from_record
    routes,calls=transport
    routes['/products.json']={'products':shopify_products()}
    result=invoke('extract','https://fixture.invalid','--platform','shopify','--max','11')
    assert result.exit_code == 3, result.output[:800]
    response=value(result); data=response['data']
    assert response['error']['retryable'] is False and response['completeness']=='partial'
    assert data['product_count']==11 and len(data['products'])==11
    assert len(calls)==1
    assert {r['product']['external_id'] for r in data['products']}=={f'{i:04}' for i in range(11)}
    assert [r['product']['canonical_product_id'] for r in data['products']]==sorted(r['product']['canonical_product_id'] for r in data['products'])
    for record in data['products']:
        i=int(record['product']['external_id'])
        assert record['product']['variants'][0]['price']=={'$type':'decimal','value':'0.10'}
        product=product_from_record(record)
        assert product.variants[0].price==Decimal('0.10')
        assert product.external_id==f'{i:04}' and product.sku==f'{i:06}'
        assert product.in_stock is False and product.compare_at_price is None
        assert product.evidence_contract.evidence and product.variants[0].evidence_contract.evidence
    assert data['raw_products'][0]['variants'][0]['available'] is False
    assert data['catalog_complete'] is False and 'product_budget_reached' in data['incompleteness_reasons']


def test_native_shopify_exhaustion_complete(transport):
    routes,_=transport; routes['/products.json']={'products':shopify_products(1)}
    result=invoke('extract','https://fixture.invalid','--platform','shopify','--max','2')
    assert result.exit_code==0, result.output[:800]
    assert value(result)['data']['catalog_complete'] is True


def test_actual_jsonld_extract_one_without_browser(transport,monkeypatch):
    import httpx
    from shopextract.extractors.unified import UnifiedCrawlExtractor
    routes,_=transport
    raw={'@context':'https://schema.org','@type':'Product','name':'Synthetic one','sku':'0001','offers':{'price':'0.10','priceCurrency':'EUR','availability':'https://schema.org/OutOfStock'}}
    routes['/one']=lambda r:httpx.Response(200,text='<script type="application/ld+json">'+json.dumps(raw)+'</script>')
    async def forbidden(*a,**kw):
        raise AssertionError('browser must stay disabled')
    monkeypatch.setattr(UnifiedCrawlExtractor,'_extract_with_browser',forbidden)
    result=invoke('extract-one','https://fixture.invalid/one')
    assert result.exit_code==0, result.output[:800]
    product=value(result)['data']['product']
    assert product['name']=='Synthetic one' and product['sku']=='0001' and product['_capture']['method'].startswith('json_ld')


@pytest.mark.parametrize('kind',['csv','xml'])
def test_native_feed_cap_reports_partial(transport,kind):
    import httpx
    routes,_=transport
    if kind=='csv':
        body='id,title,price,link,image_link,availability\n001,A,0.10 EUR,https://fixture.invalid/a,https://fixture.invalid/a.png,out_of_stock\n002,B,1.00 EUR,https://fixture.invalid/b,https://fixture.invalid/b.png,in_stock\n'
        content_type='text/csv'
    else:
        body='<rss xmlns:g="http://base.google.com/ns/1.0"><channel>'+''.join(f'<item><g:id>00{i}</g:id><title>{t}</title><g:price>0.10 EUR</g:price><link>https://fixture.invalid/{i}</link><g:image_link>https://fixture.invalid/{i}.png</g:image_link><g:availability>out_of_stock</g:availability></item>' for i,t in [(1,'A'),(2,'B')])+'</channel></rss>'
        content_type='application/xml'
    routes['/feed']=lambda r:httpx.Response(200,text=body,headers={'content-type':content_type})
    result=invoke('feed','https://fixture.invalid/feed','--max','1')
    assert result.exit_code==3, result.output[:800]
    data=value(result)['data']; assert data['product_count']==1 and len(data['raw_products'])==1
    assert data['catalog_complete'] is False


@pytest.mark.parametrize('raw',['NaN','{"x":1,"x":2}','[{"title":"A"},0]','{"$type":"decimal","value":"bad"}','\ufeff[]','[{"schema_version":1,"product":{}}]'])
def test_malformed_input_rejected(raw):
    result=invoke('quality','-',input=raw)
    assert result.exit_code==2, result.output[:800]
    assert value(result)['error']['code']=='E_USAGE'


@pytest.mark.parametrize('flag,arg',[('--timeout','nan'),('--timeout','inf'),('--timeout','0'),('--timeout','301'),('--llm-temperature','nan'),('--llm-max-calls','0'),('--llm-max-output-tokens','4097'),('--llm-max-input-bytes','32769')])
def test_invalid_resource_controls_no_transport(transport,flag,arg):
    _,calls=transport
    result=invoke('extract','https://fixture.invalid','--platform','shopify',flag,arg)
    assert result.exit_code==2 and not calls, result.output[:800]


def test_storefront_protocol_invalid_before_transport(transport,tmp_path):
    _,calls=transport; path=tmp_path/'options.json';path.write_text('{"protocol":"rest","access_token":"SECRET"}')
    result=invoke('extract','https://fixture.invalid','--platform','shopify','--storefront',str(path))
    assert result.exit_code==2 and not calls and 'SECRET' not in result.output[:800]


def test_option_fidelity_and_empty_extraction_failure(monkeypatch,tmp_path):
    import shopextract
    from shopextract._models import ExtractionResult,Platform
    calls=[]
    async def boundary(url,**kwargs):
        calls.append(kwargs)
        return ExtractionResult(platform=Platform.MAGENTO)
    monkeypatch.setattr(shopextract,'extract',boundary)
    path=tmp_path/'options.json';path.write_text('{"protocol":"rest","endpoint":"https://fixture.invalid/api","access_token":"secret"}')
    result=invoke('extract','https://fixture.invalid','--platform','magento','--shop-url','https://fixture.invalid/shop','--enrich-identifiers','--restore-short-gtin','--storefront',str(path),'--max','17')
    assert result.exit_code==1, result.output[:800]
    assert calls==[dict(max_urls=17,platform=Platform.MAGENTO,shop_url='https://fixture.invalid/shop',enrich_identifiers=True,restore_short_gtin=True,api_options={'protocol':'rest','endpoint':'https://fixture.invalid/api','access_token':'secret'})]
    assert value(result)['data'] is None
    assert value(result)['error']['code']=='E_OPERATION'


def test_timeout_cleanup_and_policy_reset(monkeypatch):
    import asyncio,shopextract
    from shopextract._execution import current_policy
    cleanup=[]
    async def sleeping(url,**kw):
        try:
            assert current_policy() is not None
            await asyncio.sleep(10)
        finally:
            cleanup.append(True)
    monkeypatch.setattr(shopextract,'extract_one',sleeping)
    result=invoke('extract-one','https://fixture.invalid','--timeout','.01')
    assert result.exit_code==1 and value(result)['error']['code']=='E_TIMEOUT'
    assert cleanup==[True] and current_policy() is None


def test_interrupt_cleanup(monkeypatch):
    import shopextract
    from shopextract._execution import current_policy
    cleanup=[]
    async def interrupted(url,**kw):
        try:
            raise KeyboardInterrupt()
        finally:
            cleanup.append(True)
    monkeypatch.setattr(shopextract,'extract_one',interrupted)
    result=invoke('extract-one','https://fixture.invalid')
    assert result.exit_code==130 and value(result)['error']['code']=='E_CANCELLED'
    assert cleanup==[True] and current_policy() is None


def test_atomic_output_failure_preserves_old_result(transport,tmp_path,monkeypatch):
    import os
    routes,_=transport;routes['/products.json']={'products':shopify_products(1)}
    target=tmp_path/'result.json';target.write_text('old')
    def fail(*a): raise OSError('SECRET')
    monkeypatch.setattr(os,'replace',fail)
    result=invoke('extract','https://fixture.invalid','--platform','shopify','--max','2','-o',str(target))
    assert result.exit_code==1 and value(result)['error']['code']=='E_OPERATION'
    assert target.read_text()=='old' and 'SECRET' not in result.output[:800]
    assert list(tmp_path.iterdir())==[target]


def test_machine_ambient_keys_never_resolve_or_submit(transport,monkeypatch):
    import importlib
    native=importlib.import_module('shopextract._extract')
    routes,_=transport;routes['/products.json']={'products':shopify_products(1)}
    def forbidden(*a,**k): raise AssertionError('ambient activation')
    monkeypatch.setattr(native,'_resolve_llm_api_key',forbidden)
    result=invoke('extract','https://fixture.invalid','--platform','shopify',env={'SHOPEXTRACT_LLM_API_KEY':'SECRET','SHOPEXTRACT_LLM_MODEL':'ollama/wrong'})
    assert result.exit_code==0, result.output[:800]


def test_native_nested_llm_helper_stays_disabled(monkeypatch):
    import asyncio,importlib,sys
    from types import SimpleNamespace
    from shopextract._execution import ExecutionPolicy,execution_policy
    native=importlib.import_module('shopextract._extract')
    def forbidden(*a,**k): raise AssertionError('provider')
    monkeypatch.setitem(sys.modules,'litellm',SimpleNamespace(acompletion=forbidden))
    async def run():
        with execution_policy(ExecutionPolicy()):
            return await native._try_llm_extraction(['https://fixture.invalid'],'ambient','ollama/wrong',.2)
    assert asyncio.run(run())==[]


def provider_stub(monkeypatch, mode='valid'):
    import sys
    from types import SimpleNamespace
    calls=[]
    async def complete(**kwargs):
        calls.append(kwargs)
        if mode=='secret': raise RuntimeError('SECRET_PROVIDER_KEY response payload')
        text='not JSON' if mode=='malformed' else '{"title":"LLM synthetic","price":"0.10"}'
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])
    monkeypatch.setitem(sys.modules,'litellm',SimpleNamespace(acompletion=complete))
    return calls


def test_bounded_native_llm_shared_calls_input_output_deadline(transport,monkeypatch):
    import asyncio,httpx,time,importlib
    from shopextract._execution import ExecutionPolicy,LLMBudget,execution_policy
    native=importlib.import_module('shopextract._extract')
    routes,_=transport;routes['/page']=lambda r:httpx.Response(200,text='x'*100)
    calls=provider_stub(monkeypatch)
    async def run():
        budget=LLMBudget('ollama/already-running','',.3,2,8,16)
        with execution_policy(ExecutionPolicy(llm=budget),1) as state:
            first=await native._try_llm_extraction(['https://fixture.invalid/page']*3,'ignored','wrong/model',0)
            second=await native._try_llm_extraction(['https://fixture.invalid/page'],'ignored','wrong/model',0)
            assert state.llm_calls==2 and state.warnings
            return first,second
    first,second=asyncio.run(run())
    assert len(first)==2 and second==[] and len(calls)==2
    for call in calls:
        assert len(call['messages'][1]['content'].encode())==16
        assert call['max_tokens']==8 and call['num_retries']==0
        assert 0<call['timeout']<=1 and call['model']=='ollama/already-running' and call['temperature']==.3


@pytest.mark.parametrize('mode',['malformed','secret'])
def test_provider_error_sanitized_real_native_fallback(transport,monkeypatch,mode):
    import httpx
    routes,captured=transport;routes['/page']=lambda r:httpx.Response(200,text='<html>no facts</html>')
    calls=provider_stub(monkeypatch,mode)
    result=invoke('extract-one','https://fixture.invalid/page','--allow-llm','--llm-model','openai/explicit',env={'SHOPEXTRACT_LLM_API_KEY':'SECRET_PROVIDER_KEY','SHOPEXTRACT_LLM_MODEL':'ollama/wrong'})
    assert result.exit_code==1 and value(result)['error']['code']=='E_OPERATION'
    assert len(calls)==1 and calls[0]['model']=='openai/explicit'
    assert 'SECRET_PROVIDER_KEY' not in result.output and 'response payload' not in result.output


def test_ollama_explicit_route_no_key_no_launch(transport,monkeypatch):
    import httpx
    routes,_=transport;routes['/page']=lambda r:httpx.Response(200,text='source')
    calls=provider_stub(monkeypatch)
    result=invoke('extract-one','https://fixture.invalid/page','--allow-llm','--llm-model','ollama/already-running',env={'SHOPEXTRACT_LLM_API_KEY':''})
    assert result.exit_code==0, result.output[:800]
    assert len(calls)==1 and calls[0]['api_key'] is None
    assert value(result)['data']['product']['title']=='LLM synthetic'


def test_expired_budget_submits_no_provider(transport,monkeypatch):
    import asyncio,time
    from shopextract._execution import ExecutionPolicy,LLMBudget,execution_policy,bounded_llm
    calls=provider_stub(monkeypatch)
    async def run():
        with execution_policy(ExecutionPolicy(llm=LLMBudget('ollama/test','')),1) as state:
            state.deadline=time.monotonic()-1
            await bounded_llm(['https://fixture.invalid/page'])
    with pytest.raises(TimeoutError): asyncio.run(run())
    assert calls==[]


def test_browser_preflight_missing_before_fetch(transport,monkeypatch):
    from shopextract import _cli_extract
    from shopextract._cli_core import CliFailure
    _,calls=transport
    def absent(): raise CliFailure('E_DEPENDENCY','Browser unavailable; configure Playwright Chromium.')
    monkeypatch.setattr(_cli_extract,'_browser_preflight',absent)
    result=invoke('extract-one','https://fixture.invalid/page','--browser')
    assert result.exit_code==1 and value(result)['error']['code']=='E_DEPENDENCY' and calls==[]


def test_browser_shared_gate_is_enforced():
    from shopextract._execution import ExecutionPolicy,execution_policy
    from shopextract.extractors._browser import get_browser_config
    with execution_policy(ExecutionPolicy()):
        with pytest.raises(RuntimeError,match='disabled'): get_browser_config()


def test_quality_accepts_native_portable_envelope():
    normalized=invoke('normalize','-',input='{"title":"A","price":"0.10","image_url":"https://fixture.invalid/a.png"}')
    assert normalized.exit_code==0
    result=invoke('quality','-',input=normalized.stdout)
    assert result.exit_code==0 and value(result)['data']['product_count']==1


def test_invalid_utf8_stdin():
    result=invoke('quality','-',input=b'\xff')
    assert result.exit_code==2


def test_machine_csv_rejects_before_fetch(transport):
    _,calls=transport
    result=invoke('extract','https://fixture.invalid','--format','csv')
    assert result.exit_code==2 and not calls


def test_new_default_errors_are_envelopes():
    result=CliRunner().invoke(main,['quality','-'],input='bad')
    assert result.exit_code==2 and value(result)['error']['code']=='E_USAGE'


def test_actual_discover_shopify_transport(transport):
    import httpx
    routes,calls=transport
    routes['/robots.txt']=lambda r:httpx.Response(404)
    routes['/products.json']=lambda r:httpx.Response(404)
    # Native advertised-sitemap discovery precedes the known Shopify fallback.
    routes['/robots.txt']=lambda r:httpx.Response(404)
    routes['/sitemap.xml']=lambda r:httpx.Response(404)
    routes['/sitemap_products_1.xml']=lambda r:httpx.Response(200,text='<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://fixture.invalid/products/a</loc></url><url><loc>https://fixture.invalid/products/b</loc></url></urlset>')
    result=invoke('discover','https://fixture.invalid','--platform','shopify','--max','1')
    assert result.exit_code==3, result.output[:800]
    assert value(result)['data']=={'urls':['https://fixture.invalid/products/a'],'count':1,
        'catalog_complete':None,'incompleteness_reasons':['discovery_coverage_unverified','discovery_url_budget'],'request_count':4}
    assert [request.url.path for request in calls]==['/robots.txt','/products.json','/sitemap.xml','/sitemap_products_1.xml']

    assert value(result)['data']['catalog_complete'] is None
    assert value(result)['completeness']=='partial'


def test_detect_deadline_cleanup(monkeypatch):
    import asyncio,shopextract
    cleanup=[]
    async def slow(*a,**k):
        try: await asyncio.sleep(10)
        finally: cleanup.append(True)
    monkeypatch.setattr(shopextract,'detect',slow)
    result=invoke('detect','https://fixture.invalid','--timeout','.01')
    assert result.exit_code==1 and value(result)['error']['code']=='E_TIMEOUT'
    assert cleanup==[True]


@pytest.mark.parametrize('command',['feed','extract'])
def test_empty_failed_extraction_is_unavailable(transport,command,tmp_path):
    import httpx
    routes,_=transport
    if command=='feed':
        routes['/failed']=lambda r:httpx.Response(200,text='id,title,price\n',headers={'content-type':'text/csv'})
        args=['feed','https://fixture.invalid/failed']
    else:
        routes['/graphql']=lambda r:httpx.Response(401,json={'errors':[{'message':'unauthorized'}]})
        config=tmp_path/'storefront.json'
        config.write_text(json.dumps({'endpoint':'https://fixture.invalid/graphql','access_token':'TOKEN','token_type':'private','customer_access_token':'CUSTOMER'}))
        args=['extract','https://fixture.invalid','--platform','bigcommerce','--storefront',str(config)]
    result=invoke(*args)
    assert result.exit_code==1, result.output[:800]
    assert value(result)['data'] is None and value(result)['error']['code']=='E_OPERATION'


def test_concurrent_nested_helpers_serialize_and_share_cap(transport,monkeypatch):
    import asyncio,httpx,sys
    from types import SimpleNamespace
    from shopextract._execution import ExecutionPolicy,LLMBudget,execution_policy,bounded_llm
    routes,_=transport;routes['/page']=lambda r:httpx.Response(200,text='source')
    active=0;maximum=0;calls=0
    async def complete(**kwargs):
        nonlocal active,maximum,calls
        calls+=1;active+=1;maximum=max(maximum,active)
        try:
            await asyncio.sleep(.005)
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='{"title":"A"}'))])
        finally: active-=1
    monkeypatch.setitem(sys.modules,'litellm',SimpleNamespace(acompletion=complete))
    async def run():
        with execution_policy(ExecutionPolicy(llm=LLMBudget('ollama/test','',max_calls=2)),1) as state:
            await asyncio.gather(bounded_llm(['https://fixture.invalid/page']*2),bounded_llm(['https://fixture.invalid/page']*2))
            assert state.llm_calls==2
    asyncio.run(run())
    assert maximum==1 and active==0 and calls==2


def test_provider_cancellation_cleanup_consumes_call(transport,monkeypatch):
    import asyncio,httpx,sys
    from types import SimpleNamespace
    from shopextract._execution import ExecutionPolicy,LLMBudget,execution_policy,bounded_llm
    routes,_=transport;routes['/page']=lambda r:httpx.Response(200,text='source')
    cleanup=[]
    async def complete(**kwargs):
        try: await asyncio.sleep(10)
        finally: cleanup.append(True)
    monkeypatch.setitem(sys.modules,'litellm',SimpleNamespace(acompletion=complete))
    async def run():
        with execution_policy(ExecutionPolicy(llm=LLMBudget('ollama/test','')),1) as state:
            with pytest.raises(asyncio.TimeoutError): await asyncio.wait_for(bounded_llm(['https://fixture.invalid/page']),.01)
            assert state.llm_calls==1
            assert await bounded_llm(['https://fixture.invalid/page'])==[]
    asyncio.run(run());assert cleanup==[True]


def test_provider_failure_consumes_shared_call(transport,monkeypatch):
    import asyncio,httpx
    from shopextract._execution import ExecutionPolicy,LLMBudget,execution_policy,bounded_llm
    routes,_=transport;routes['/page']=lambda r:httpx.Response(200,text='source')
    calls=provider_stub(monkeypatch,'secret')
    async def run():
        with execution_policy(ExecutionPolicy(llm=LLMBudget('ollama/test','')),1) as state:
            assert await bounded_llm(['https://fixture.invalid/page'])==[]
            assert state.llm_calls==1
            assert await bounded_llm(['https://fixture.invalid/page'])==[]
    asyncio.run(run()); assert len(calls)==1


@pytest.mark.parametrize('flag,number',[('--llm-max-calls',0),('--llm-max-calls',11),('--llm-max-output-tokens',0),('--llm-max-output-tokens',4097),('--llm-max-input-bytes',0),('--llm-max-input-bytes',32769),('--llm-temperature','nan'),('--llm-temperature','inf'),('--llm-temperature',-1),('--llm-temperature',3)])
def test_activated_invalid_llm_bounds_no_transport(transport,flag,number):
    _,calls=transport
    result=invoke('extract-one','https://fixture.invalid/page','--allow-llm','--llm-model','ollama/test',flag,str(number))
    assert result.exit_code==2 and calls==[]


@pytest.mark.parametrize('calls,tokens,size,temperature',[(1,1,1,0),(10,4096,32768,2)])
def test_activated_accepted_llm_boundaries(transport,monkeypatch,calls,tokens,size,temperature):
    import httpx
    routes,_=transport;routes['/page']=lambda r:httpx.Response(200,text='x'*(size+1))
    requests=provider_stub(monkeypatch)
    result=invoke('extract-one','https://fixture.invalid/page','--allow-llm','--llm-model','ollama/test','--llm-max-calls',str(calls),'--llm-max-output-tokens',str(tokens),'--llm-max-input-bytes',str(size),'--llm-temperature',str(temperature))
    assert result.exit_code==0, result.output[:800]
    assert len(requests)==1 and requests[0]['max_tokens']==tokens and requests[0]['temperature']==temperature
    assert len(requests[0]['messages'][1]['content'].encode())==size


@pytest.mark.parametrize("cap,exit_code",[(1,3),(2,0)])
def test_atomic_output_roundtrip_quality_file(transport,tmp_path,cap,exit_code):
    routes,_=transport;routes['/products.json']={'products':shopify_products(1)}
    path=tmp_path/'catalog.json'
    result=invoke('extract','https://fixture.invalid','--platform','shopify','--max',str(cap),'-o',str(path))
    assert result.exit_code==exit_code and json.loads(path.read_text())==value(result)
    quality=invoke('quality',str(path))
    assert quality.exit_code==0 and value(quality)['data']['product_count']==1
    assert value(quality)['data']['batch_score']>0


def test_operation_prints_never_reach_response_stdout(monkeypatch):
    # crawl4ai 0.8.5 printed [FETCH]/[SCRAPE] progress to stdout during --browser runs.
    import shopextract
    async def noisy(url):
        print('[FETCH]... progress line')
        return {'@type': 'Product', 'name': 'Widget'}
    monkeypatch.setattr(shopextract, 'extract_one', noisy)
    result = CliRunner().invoke(main, ['--output-format', 'json', 'extract-one', 'https://fixture.invalid/p', '--timeout', '5'])
    assert result.exit_code == 0, result.output[:800]
    assert value(result)['data']['product']['name'] == 'Widget'
    assert '[FETCH]' not in result.stdout and '[FETCH]' in result.stderr


def test_browser_run_config_disables_crawl4ai_progress_logging():
    from shopextract.extractors._browser import get_crawl_config, StealthLevel
    assert all(get_crawl_config(stealth_level=level).verbose is False for level in StealthLevel)
