"""Predesigned actual HTML/native paths; synthetic external boundaries only."""
import asyncio
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys

import httpx
import pytest
from shopextract.extractors.unified import UnifiedCrawlExtractor
from shopextract._normalize import normalize
from shopextract._models import Platform

URL='https://fixture.invalid/products/widget'
P={'@type':'Product','name':'Widget','description':'Source description','image':'https://fixture.invalid/widget.jpg',
   'offers':{'price':'10','priceCurrency':'PKR'},'gtin13':'4006381333931','brand':{'name':'Acme'}}
def ld(value):return '<script type="application/ld+json">'+json.dumps(value)+'</script>'
def parse(html):return UnifiedCrawlExtractor._extract_structured_from_html(html,URL)
def shared(html,**kw):return importlib.import_module('shopextract._structured_html').extract_structured_products(html,URL,**kw)
def diagnostic(result,code):return any(d['code']==code for d in result.diagnostics)


@pytest.mark.parametrize('form',['root','list','graph','itempage'])
def test_jsonld_context_equivalence(form):
    node={**P,'sku':'SKU1'}
    data={'root':node,'list':[node],'graph':{'@graph':[node]},'itempage':{'@type':'ItemPage','mainEntity':node}}[form]
    values=parse(ld(data));assert len(values)==1
    p=normalize(values[0],Platform.GENERIC,URL)
    assert (p.title,p.sku,p.vendor,p.gtin)==('Widget','SKU1','Acme','4006381333931')


def test_linked_offer_brand_and_cycle_resolve_once():
    node={**P,'@id':'#p','brand':{'@id':'#b'},'offers':{'@id':'#o'}}
    values=parse(ld({'@graph':[{'@type':'ItemPage','mainEntity':{'@id':'#p'}},node,
        {'@id':'#b','@type':'Brand','name':'Linked Acme','subjectOf':{'@id':'#p'}},
        {'@id':'#o','@type':'Offer','price':'11','priceCurrency':'PKR'}]}))
    assert len(values)==1
    product=normalize(values[0],Platform.GENERIC,URL)
    assert product.vendor=='Linked Acme' and product.price==11


@pytest.mark.parametrize('nodes',[255,256,257])
def test_container_budget_boundary(nodes):
    # root dict +graph list +product dicts.
    data={'@graph':[{'@type':'Product','name':f'P{i}'} for i in range(nodes-2)]}
    result=shared(ld(data))
    if nodes<=256:assert len(result.products)==nodes-2
    else:assert result.products==[] and diagnostic(result,'jsonld_budget_exceeded')


@pytest.mark.parametrize('depth',[7,8,9])
def test_depth_budget_boundary(depth):
    # Wrapping arrays each add one depth; Product dict at specified depth.
    data={'@type':'Product','name':'Depth product'}
    for _ in range(depth):data=[data]
    result=shared(ld(data))
    if depth<=8:assert len(result.products)==1
    else:assert result.products==[] and diagnostic(result,'jsonld_budget_exceeded')


def test_external_reference_not_fetched_or_invented():
    result=shared(ld({**P,'brand':{'@id':'https://external.invalid/brand'}}))
    assert result.products and diagnostic(result,'external_reference_ignored')
    assert normalize(result.products[0],Platform.GENERIC,URL).vendor is None


@pytest.mark.parametrize('mode',['lazy','only','genuine'])
def test_placeholder_image_selection(mode):
    raw={**P,'image':'https://fixture.invalid/static/Magento_Catalog/images/product/placeholder/image.jpg'}
    tail=''
    if mode=='lazy':tail='<main class="product"><img data-src="/real.jpg"></main>'
    if mode=='genuine':raw['image']='https://fixture.invalid/products/placeholder-board.jpg'
    result=shared(ld(raw)+tail);p=normalize(result.products[0],Platform.GENERIC,URL)
    if mode=='lazy':assert p.image_url=='https://fixture.invalid/real.jpg'
    elif mode=='only':assert p.image_url=='' and diagnostic(result,'placeholder_image')
    else:assert p.image_url==raw['image']


@pytest.mark.parametrize('count',[19,20,21])
def test_gallery_budget_dedup(count):
    raw={**P,'image':''}
    gallery='<main class="product"><div class="gallery">'+''.join(f'<img data-src="/g{i}.jpg">' for i in range(count))+'<img data-src="/g0.jpg"></div></main>'
    result=shared(ld(raw)+gallery);p=normalize(result.products[0],Platform.GENERIC,URL)
    assert len([p.image_url,*p.additional_images])==min(count,20)
    assert bool(diagnostic(result,'image_budget_reached')) is (count>20)


DOM='<main class="product-info-main"><span class="sku">DOM-SKU</span><form id="product_addtocart_form"><input name="product" value="123" type="hidden"></form></main><footer><span class="sku">WRONG</span></footer>'

def test_scoped_sku_retains_actual_capture_support():
    values=parse(ld(P)+DOM);p=normalize(values[0],Platform.GENERIC,URL)
    assert p.sku=='DOM-SKU'
    source=values[0]['_field_sources']['/sku']
    assert source['_capture']['values'][source['capture_path']]=='DOM-SKU'
    obs=[o for o in p.evidence_contract.observations if o.field_path=='/sku']
    assert obs and obs[0].state.value=='observed' and obs[0].evidence_ids


def test_magento_product_form_id_not_footer():
    values=parse(ld(P)+DOM.replace('<span class="sku">DOM-SKU</span>',''))
    assert values[0]['productID']=='123'
    assert normalize(values[0],Platform.GENERIC,URL).external_id=='123'


def test_structured_sku_kept_conflict_retained():
    result=shared(ld({**P,'sku':'SOURCE-SKU'})+DOM)
    assert result.products[0]['sku']=='SOURCE-SKU' and diagnostic(result,'conflicting_sku')
    assert set(result.products[0]['_html_field_conflicts']['sku'])=={'SOURCE-SKU','DOM-SKU'}


@pytest.mark.parametrize('valid',[True,False])
def test_breadcrumb_positions_and_projection(valid):
    crumbs=[{'@type':'ListItem','position':3,'name':'Widget','item':URL},
        {'@type':'ListItem','position':1,'name':'Home','item':'https://fixture.invalid/'},
        {'@type':'ListItem','position':2,'name':'Electronics','item':'https://fixture.invalid/electronics'}]
    if not valid:crumbs[0].pop('position')
    result=shared(ld(P)+ld({'@type':'BreadcrumbList','itemListElement':crumbs}))
    p=normalize(result.products[0],Platform.GENERIC,URL)
    if valid:assert p.category_path==['Electronics']
    else:assert p.category_path==[] and diagnostic(result,'breadcrumb_invalid')


@pytest.mark.parametrize('kind',['policy','free_group','native'])
def test_existing_admission_native_compatibility(kind):
    if kind=='policy':assert parse('<meta property="og:title" content="Returns"><meta property="og:type" content="website">'+DOM)==[]
    elif kind=='free_group':assert parse(ld({'@type':'ProductGroup','name':'Free group','hasVariant':[{'@type':'Product','name':'Free','offers':{'price':'0'}}]}))
    else:assert normalize({'id':1,'title':'API','variants':[{'id':2,'price':'0'}]},Platform.SHOPIFY,'https://fixture.invalid').title=='API'


def test_fresh_native_generic_parse_no_browser_dependency():
    payload={'operation':'parse','mode':'html','html':ld(P),'raw':None,'platform':'generic',
        'url':URL,'origin':'https://fixture.invalid','maximum':2,'observed_at':'2026-11-01T00:00:00+00:00'}
    code="from shopextract.tools.domain import synchronous;import json,sys;v=synchronous("+repr(payload)+");print(json.dumps({'count':len(v),'heavy':[m for m in sys.modules if m.split('.')[0] in ('crawl4ai','playwright')]}))"
    result=subprocess.run([sys.executable,'-c',code],env={**os.environ,'PYTHONPATH':str(Path(__file__).resolve().parents[1]/'src')},capture_output=True,text=True,timeout=15)
    assert result.returncode==0,result.stderr[-300:]
    assert json.loads(result.stdout)=={'count':1,'heavy':[]}


@pytest.mark.asyncio
async def test_actual_tool_pipeline_scoped_sku():
    from shopextract.tools import ToolConfig,ToolRuntime
    from tests.tool_api_fixtures import ORIGIN,resolver
    def response(req):
        if req.url.path=='/graphql':return httpx.Response(404)
        return httpx.Response(200,text=ld(P)+DOM,headers={'content-type':'text/html'})
    engine=ToolRuntime(ToolConfig(allowed_origins=(ORIGIN,)),resolver=resolver,wire_transport=httpx.MockTransport(response))
    try:
        start=await engine.call('extract',{'schema_version':'1.0','url':ORIGIN,'max_items':2});jid=start['data']['job_id']
        for _ in range(500):
            status=await engine.call('job_status',{'schema_version':'1.0','job_id':jid})
            if status['data']['state'] not in ('queued','running'):break
            await asyncio.sleep(.02)
        assert status['data']['state']=='succeeded',status
        result=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'products'})
        assert result['data']['items'][0]['sku']=='DOM-SKU'
    finally:await engine.aclose()


def diagnostic_html(kind):
    if kind=='breadcrumb':return ld(P)+ld({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','name':'Category'}]})
    over=ld({'@graph':[{'@type':'Product','name':f'Untrusted{i}'} for i in range(255)]})
    return over if kind=='fatal' else ld(P)+over


@pytest.mark.parametrize('optin',[False,True])
def test_real_domain_diagnostics_serialization(optin):
    from shopextract.tools.domain import synchronous
    value=synchronous({'operation':'parse','mode':'html','html':diagnostic_html('breadcrumb'),
        'raw':None,'platform':'generic','url':URL,'origin':'https://fixture.invalid',
        'maximum':2,'observed_at':'2026-11-01T00:00:00+00:00','include_diagnostics':optin})
    if not optin:assert isinstance(value,list) and len(value)==1
    else:
        assert set(value)=={'products','diagnostics'} and len(value['products'])==1
        assert any(d['code']=='breadcrumb_invalid' for d in value['diagnostics'])


@pytest.mark.asyncio
@pytest.mark.parametrize('kind',['mixed','breadcrumb','fatal'])
async def test_unified_http_diagnostics_retained(kind):
    from shopextract._execution import execution_policy,ExecutionPolicy
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r:httpx.Response(200,text=diagnostic_html(kind)))) as client:
        with execution_policy(ExecutionPolicy(browser=False),10):result=await UnifiedCrawlExtractor(http_client=client).extract(URL)
    assert len(result.products)==(0 if kind=='fatal' else 1)
    code='breadcrumb_invalid' if kind=='breadcrumb' else 'jsonld_budget_exceeded'
    assert result.complete is False and code in result.error


@pytest.mark.asyncio
@pytest.mark.parametrize('kind',['mixed','breadcrumb','fatal'])
async def test_actual_native_diagnostic_collection_partial_or_failed(kind):
    from shopextract.tools import ToolConfig,ToolRuntime
    from tests.tool_api_fixtures import ORIGIN,resolver
    def response(req):
        if req.url.path=='/graphql':return httpx.Response(404)
        return httpx.Response(200,text=diagnostic_html(kind),headers={'content-type':'text/html'})
    engine=ToolRuntime(ToolConfig(allowed_origins=(ORIGIN,)),resolver=resolver,wire_transport=httpx.MockTransport(response))
    try:
        start=await engine.call('extract',{'schema_version':'1.0','url':ORIGIN,'max_items':2});jid=start['data']['job_id']
        for _ in range(500):
            status=await engine.call('job_status',{'schema_version':'1.0','job_id':jid})
            if status['data']['state'] not in ('queued','running'):break
            await asyncio.sleep(.02)
        code='breadcrumb_invalid' if kind=='breadcrumb' else 'jsonld_budget_exceeded'
        if kind=='fatal':
            assert status['data']['state']=='failed',status
            assert status['data']['error']['code']=='source_error' and code in status['data']['error']['message']
        else:
            assert status['data']['state']=='succeeded',status
            products=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'products'})
            assert len(products['data']['items'])==1 and products['data']['completeness']=='partial'
            issues=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'diagnostics'})
            assert any(d['code']==code for d in issues['data']['items'])
    finally:await engine.aclose()


@pytest.mark.parametrize('ownership',['url','form','ambiguous'])
def test_dom_owner_selected_without_sibling_leakage(ownership):
    main={**P,'name':'Main','image':''};other={**P,'name':'Recommended','image':'','sku':'REC-SKU'}
    if ownership=='url':main['url']=URL;other['url']='https://fixture.invalid/products/other'
    elif ownership=='form':main['productID']='123';other['productID']='456'
    else:other.pop('sku')
    html=ld([main,other])+DOM.replace('</main>','<img data-src="/owner.jpg"></main>')
    result=shared(html);values={p['name']:p for p in result.products}
    first=normalize(values['Main'],Platform.GENERIC,URL);sibling=normalize(values['Recommended'],Platform.GENERIC,URL)
    if ownership=='ambiguous':
        assert diagnostic(result,'ambiguous_dom_owner')
        assert first.sku is None and sibling.sku is None and first.image_url==sibling.image_url==''
        assert all('/sku'!=o.field_path or o.state.value!='observed' for p in (first,sibling) for o in p.evidence_contract.observations)
    else:
        assert first.sku=='DOM-SKU' and first.image_url=='https://fixture.invalid/owner.jpg'
        assert values['Main']['productID']=='123'
        assert sibling.sku=='REC-SKU' and sibling.image_url==''
        assert not values['Recommended'].get('_field_sources',{}).get('/sku')
        obs=[o for o in first.evidence_contract.observations if o.field_path=='/sku']
        assert obs[0].state.value=='observed' and obs[0].evidence_ids


@pytest.mark.parametrize('unique',[True,False])
def test_page_og_only_unique_product_owner(unique):
    first={**P,'name':'Main','image':'','description':''};second={**P,'name':'Recommended','image':'','description':''}
    if unique:first['url']=URL
    meta='<meta property="og:url" content="'+URL+'"><meta property="og:image" content="https://fixture.invalid/main.jpg"><meta property="og:description" content="Main-only description">'
    result=shared(ld([first,second])+meta+DOM)
    rows={p['name']:p for p in result.products}
    if unique:
        assert rows['Main']['image']=='https://fixture.invalid/main.jpg'
        p=normalize(rows['Main'],Platform.GENERIC,URL)
        assert any(o.field_path=='/description' and o.state.value=='observed' for o in p.evidence_contract.observations)
    else:assert not rows['Main'].get('url') and not rows['Main'].get('image')
    assert not rows['Recommended'].get('url') and not rows['Recommended'].get('image') and not rows['Recommended'].get('description')


def test_og_placeholder_actual_normalizer_dom_source():
    html='<meta property="og:type" content="product"><meta property="og:title" content="Widget"><meta property="product:price:amount" content="10"><meta property="product:price:currency" content="PKR"><meta property="og:image" content="https://fixture.invalid/placeholder/image.jpg">'+DOM.replace('</main>','<img data-src="/real.jpg"></main>')
    result=shared(html);p=normalize(result.products[0],Platform.GENERIC,URL)
    assert p.image_url=='https://fixture.invalid/real.jpg'
    assert any(o.field_path=='/image_url' and o.state.value=='observed' for o in p.evidence_contract.observations)


@pytest.mark.parametrize('nested',[False,True])
def test_breadcrumb_object_items_bounded_nested(nested):
    crumb={'@type':'BreadcrumbList','itemListElement':[{'position':3,'item':{'@id':URL,'name':'Widget'}},{'position':1,'item':{'@id':'https://fixture.invalid/','name':'Home'}},{'position':2,'item':{'@id':'https://fixture.invalid/electronics','name':'Electronics'}}]}
    html=ld({'@graph':[P,crumb]}) if nested else ld(P)+ld(crumb)
    p=normalize(shared(html).products[0],Platform.GENERIC,URL)
    assert p.category_path==['Electronics']
    assert any(o.field_path=='/category_path/0' and o.state.value=='observed' for o in p.evidence_contract.observations)


def test_overbudget_breadcrumb_block_does_not_reparse_unbounded():
    crumb={'@graph':[{'@type':'BreadcrumbList','itemListElement':[]} for _ in range(256)]}
    result=shared(ld(P)+ld(crumb))
    assert diagnostic(result,'jsonld_budget_exceeded') and normalize(result.products[0],Platform.GENERIC,URL).category_path==[]


from tests.test_truthful_outcomes import crawl_boundary,crawl_result
@pytest.mark.asyncio
@pytest.mark.parametrize('kind',['dom','breadcrumb','batch'])
async def test_browser_real_shared_enrichment_and_diagnostics(crawl_boundary,kind):
    from shopextract._execution import execution_policy,ExecutionPolicy
    html=ld({**P,'image':'https://fixture.invalid/placeholder/image.jpg'})+DOM.replace('</main>','<img data-src="/browser.jpg"></main>')
    if kind=='breadcrumb':html=diagnostic_html('breadcrumb')
    if kind=='batch':crawl_boundary.extend([crawl_result(html=ld(P)),crawl_result(html=diagnostic_html('mixed'))])
    else:crawl_boundary.append(crawl_result(html=html))
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r:httpx.Response(404))) as client:
        extractor=UnifiedCrawlExtractor(http_client=client)
        with execution_policy(ExecutionPolicy(browser=True),10):result=await extractor.extract_batch([URL,URL+'/second']) if kind=='batch' else await extractor.extract(URL)
    if kind=='dom':
        p=normalize(result.products[0],Platform.GENERIC,URL)
        assert p.sku=='DOM-SKU' and p.image_url=='https://fixture.invalid/browser.jpg'
        assert any(o.field_path=='/sku' and o.state.value=='observed' for o in p.evidence_contract.observations)
    else:
        assert len(result.products)==(2 if kind=='batch' else 1)
        assert result.complete is False and ('jsonld_budget_exceeded' if kind=='batch' else 'breadcrumb_invalid') in result.error


@pytest.mark.asyncio
@pytest.mark.parametrize('mode',['metadata','media','zero','ambiguous'])
async def test_browser_only_gap_fields_owner_support(crawl_boundary,mode):
    from shopextract._execution import execution_policy,ExecutionPolicy
    bare={'@type':'Product','name':'Browser widget','sku':'BROWSER-SKU'}
    if mode=='zero':bare['offers']={'price':'0','priceCurrency':'EUR'}
    data=[bare,{'@type':'Product','name':'Recommendation','sku':'REC-SKU'}] if mode=='ambiguous' else bare
    result=crawl_result(html=ld(data));result.markdown='# Browser widget\nPrice: 12.50 EUR'
    result.metadata={'og:description':'Rendered description','og:url':URL}
    result.media={'images':[{'src':'https://fixture.invalid/browser-only.jpg','score':4}]}
    if mode=='metadata':result.metadata['og:image']='https://fixture.invalid/browser-only.jpg'
    crawl_boundary.append(result)
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req:httpx.Response(404))) as client:
        with execution_policy(ExecutionPolicy(browser=True),10):extracted=await UnifiedCrawlExtractor(http_client=client).extract(URL)
    products=[normalize(raw,Platform.GENERIC,URL) for raw in extracted.products]
    if mode=='ambiguous':
        assert len(products)==2
        assert all(p.image_url=='' and p.description=='' and p.price==0 for p in products)
    else:
        p=products[0]
        assert p.price==(0 if mode=='zero' else 12.50) and p.currency=='EUR'
        assert p.description=='Rendered description' and p.image_url=='https://fixture.invalid/browser-only.jpg'
        assert all(any(o.field_path==field and o.state.value=='observed' for o in p.evidence_contract.observations) for field in ('/price','/currency','/description','/image_url'))


# Live Naheed shape 2026-11-01: info column held payment-widget SVGs and share icons;
# the product photos sat in a sibling zoom gallery as full-size links over cached thumbnails.
INFO='<div class="product-info-main"><span class="sku">DOM-SKU</span><img src="https://widget.invalid/assets/logo.svg"><img src="/static/version1/frontend/Theme/en_US/images/fb_icon.png"></div>'
ZOOM='<div class="product media"><div class="MagicToolboxContainer"><a href="/media/catalog/product/1-1.jpg"><img src="/cache/thumb/1-1.jpg"></a><a href="/media/catalog/product/1-2.jpg"></a><a href="/brand-page">Brand</a></div></div>'

@pytest.mark.parametrize('layout',['zoom','thumbs_only','no_gallery','two_galleries'])
def test_gallery_scope_excludes_widget_and_theme_images(layout):
    html=ld({**P,'image':''})+INFO
    if layout=='zoom':html+=ZOOM
    elif layout=='thumbs_only':html+='<div class="product media"><img data-src="/cache/thumb/1-1.jpg"></div>'
    elif layout=='two_galleries':html+=ZOOM+'<div class="woocommerce-product-gallery"><img src="/other.jpg"></div>'
    result=shared(html);p=normalize(result.products[0],Platform.GENERIC,URL)
    images=[p.image_url,*p.additional_images]
    if layout=='zoom':
        assert images==['https://fixture.invalid/media/catalog/product/1-1.jpg','https://fixture.invalid/media/catalog/product/1-2.jpg']
    elif layout=='thumbs_only':assert images==['https://fixture.invalid/cache/thumb/1-1.jpg']
    else:
        # Without one unambiguous gallery the info column is used, minus theme assets.
        assert p.image_url=='' and diagnostic(result,'theme_asset_image')
        assert bool(diagnostic(result,'ambiguous_gallery')) is (layout=='two_galleries')


@pytest.mark.parametrize('case',['dom_only','agrees','conflict','structured_differs'])
def test_dom_brand_scoped_and_conflicts_retained(case):
    raw={**P};raw.pop('brand')
    if case=='agrees':raw['brand']={'name':'Max Factor'}
    if case=='structured_differs':raw['brand']={'name':'Acme'}
    dom='<div class="product-info-main"><div class="brand-name"><a href="/max-factor">Max Factor</a> <a href="/max-factor">Visit</a></div></div>'
    if case=='conflict':dom+='<div class="product media"><span itemprop="brand" content="Other"></span></div>'
    footer='<footer><div class="brand-name"><a href="/x">Footer Brand</a></div></footer>'
    result=shared(ld(raw)+dom+footer);p=normalize(result.products[0],Platform.GENERIC,URL)
    if case=='conflict':assert p.vendor is None and diagnostic(result,'conflicting_brand')
    elif case=='structured_differs':
        assert p.vendor=='Acme' and diagnostic(result,'conflicting_brand')
        assert set(result.products[0]['_html_field_conflicts']['brand'])=={'Acme','Max Factor'}
    else:
        assert p.vendor=='Max Factor' and not diagnostic(result,'conflicting_brand')
        if case=='dom_only':
            assert any(o.field_path=='/vendor' and o.state.value=='observed' and o.evidence_ids for o in p.evidence_contract.observations)


@pytest.mark.parametrize('case',['dom','jsonld_wins','home_only'])
def test_dom_breadcrumb_fallback(case):
    items=[('Home','https://fixture.invalid/'),('Health &amp; Beauty','/health'),('Setting Powders','/health/powders'),('Widget',None)]
    if case=='home_only':items=[items[0],items[-1]]
    crumbs='<div class="breadcrumbs"><ul>'+''.join(f'<li><a href="{h}">{n}</a></li>' if h else f'<li><strong>{n}</strong></li>' for n,h in items)+'</ul></div>'
    html=ld(P)+crumbs
    if case=='jsonld_wins':html+=ld({'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'Electronics','item':'https://fixture.invalid/electronics'}]})
    p=normalize(shared(html).products[0],Platform.GENERIC,URL)
    expected={'dom':['Health & Beauty','Setting Powders'],'jsonld_wins':['Electronics'],'home_only':[]}[case]
    assert p.category_path==expected


@pytest.mark.asyncio
@pytest.mark.parametrize('kind',['placeholder','theme_asset','budget'])
async def test_cleanup_diagnostics_do_not_mark_page_incomplete(kind):
    raw={**P,'image':'https://fixture.invalid/placeholder/image.jpg'} if kind=='placeholder' else {**P}
    html=ld(raw)+INFO.replace('<span class="sku">DOM-SKU</span>','')+('<div class="gallery"></div>' if kind!='budget' else '')
    if kind=='budget':html=ld({**P,'image':''})+'<main class="product">'+''.join(f'<img src="/g{i}.jpg">' for i in range(21))+'</main>'
    from shopextract._execution import execution_policy,ExecutionPolicy
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r:httpx.Response(200,text=html))) as client:
        with execution_policy(ExecutionPolicy(browser=False),10):result=await UnifiedCrawlExtractor(http_client=client).extract(URL)
    if kind=='budget':assert result.complete is False and 'image_budget_reached' in result.error
    else:assert result.complete is not False and not result.error
