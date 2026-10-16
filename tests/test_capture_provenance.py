"""Offline field capture acceptance fixtures for issue #35."""
import json
from dataclasses import asdict
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from shopextract import Platform, normalize
from shopextract._capture import capture, FRAGMENT_BYTES, PRODUCT_BYTES, _size
from shopextract._evidence import TrustContract, factual_paths
from shopextract._extract import _normalize_batch
from shopextract.extractors.css import CSSExtractor
from shopextract.extractors.feed import GoogleFeedExtractor
from shopextract.extractors.shopify import ShopifyExtractor
from shopextract.extractors.woocommerce import WooCommerceExtractor
from shopextract.extractors.magento import MagentoExtractor
from shopextract.extractors.unified import UnifiedCrawlExtractor

SHOP = 'https://shop.test'


def audit(product):
    contract = product.evidence_contract
    contract.validate()
    assert {o.field_path for o in contract.observations} == set(factual_paths(product))
    for o in contract.observations:
        assert o.evidence_ids if o.state == 'observed' else o.reason
        assert o.validated_confidence is None
    for e in contract.evidence:
        e.resolve_pointer()
        assert e.observed_at.utcoffset().total_seconds() == 0
        assert _size(e.retained_data) <= FRAGMENT_BYTES
    assert sum(_size(e.retained_data) for e in contract.evidence) <= PRODUCT_BYTES
    assert TrustContract.from_dict(contract.to_dict()) == contract
    assert 'evidence_contract' not in asdict(product)
    return product.trust_view()


def observation(product, path):
    return next(o for o in product.evidence_contract.observations if o.field_path == path)


@pytest.mark.asyncio
@pytest.mark.parametrize('family', ['shopify', 'woocommerce', 'magento'])
async def test_api_response_redirect_and_zero_false(family):
    data = {
        'shopify': {'products': [{'id': 1, 'title': 'A', 'available': False,
                     'variants': [{'id': 2, 'price': '0', 'available': False}]}]},
        'woocommerce': [{'id': 1, 'name': 'A', 'is_in_stock': False,
                         'prices': {'price': '0', 'currency_code': 'EUR', 'currency_minor_unit': 2}}],
        'magento': {'items': [{'id': 1, 'sku': 'A', 'name': 'A', 'price': 0}], 'total_count': 1},
    }[family]
    def respond(req):
        if req.url.host == 'shop.test':
            return httpx.Response(302, headers={'location': 'https://api.test/catalog'})
        return httpx.Response(200, json=data)
    client = httpx.AsyncClient(transport=httpx.MockTransport(respond), follow_redirects=True)
    extractor = {'shopify': ShopifyExtractor, 'woocommerce': WooCommerceExtractor,
                 'magento': MagentoExtractor}[family](max_pages=1)
    with patch(f'shopextract.extractors.{family}.httpx.AsyncClient', return_value=client):
        result = await extractor.extract(SHOP)
    product = _normalize_batch(result.products, Platform(family), SHOP)[0]
    view = audit(product)
    assert view['/price']['value'] == Decimal(0)
    assert all(e.source_url == 'https://api.test/catalog' for e in product.evidence_contract.evidence)
    if family != 'magento':
        assert view['/in_stock']['value'] is False
    else:
        assert view['/in_stock']['state'] == 'unsupported'


@pytest.mark.asyncio
async def test_variant_enrichment_and_gtin_history():
    def respond(req):
        if req.url.path.endswith('.json'):
            return httpx.Response(200, json={'products': [{'id': 1, 'title': 'A', 'handle': 'a', 'variants': [
                {'id': 9, 'title': 'Bad', 'price': 'bad'},
                {'id': 10, 'title': 'B', 'price': '10'},
                {'id': 11, 'title': 'C', 'price': '11', 'barcode': '4006381333931'}]}]})
        return httpx.Response(200, json={'id': 1, 'variants': [
            {'id': 10, 'barcode': '29877030712'}, {'id': 99, 'barcode': 'wrong'}]})
    client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    with patch('shopextract.extractors.shopify.httpx.AsyncClient', return_value=client):
        result = await ShopifyExtractor().extract(SHOP, enrich_identifiers=True)
    raw = result.products[0]
    assert '/variants/1/barcode' not in raw['_capture']['values']
    product = normalize(raw, Platform.SHOPIFY, SHOP, restore_short_gtin=True)
    view = audit(product)
    assert product.variants[0].variant_id == '10'
    assert view['/variants/0/price']['value'] == Decimal(10)
    # Restoration maps by ID even when an invalid earlier variant was omitted.
    gtin = observation(product, '/variants/0/gtin')
    assert gtin.raw_value == '29877030712'
    assert 'restore_upc_leading_zero' in gtin.transformations
    evidence = next(e for e in product.evidence_contract.evidence if e.evidence_id in gtin.evidence_ids)
    assert evidence.source_url == SHOP + '/products/a.js'
    assert view['/variants/1/gtin']['value'] == '4006381333931'


@pytest.mark.parametrize('kind', ['csv', 'xml'])
def test_feed_retains_source_and_transformations(kind):
    if kind == 'csv':
        body = 'id,title,price,availability,gtin\na,Item,0 EUR,out_of_stock,4006381333931\n'
        raw = GoogleFeedExtractor._parse_csv(body, SHOP+'/feed.csv')[0]
    else:
        body = '<rss xmlns:g="http://base.google.com/ns/1.0"><channel><item><g:id>a</g:id><g:title>Item</g:title><g:price>0 EUR</g:price><g:availability>out_of_stock</g:availability><g:gtin>4006381333931</g:gtin></item></channel></rss>'
        raw = GoogleFeedExtractor._parse_xml(body, SHOP+'/feed.xml')[0]
    product = normalize(raw)
    view = audit(product)
    assert view['/price']['value'] == 0
    assert view['/in_stock']['value'] is False
    assert view['/currency']['value'] == 'EUR'
    assert any('0 EUR' in e.retained_data.get('source_excerpt', '') for e in product.evidence_contract.evidence)


@pytest.mark.asyncio
async def test_structured_http_redirect_distinct_items_and_defaults():
    html = '<script type="application/ld+json">'+json.dumps([
        {'@type':'Product', 'name':'A', 'sku':'a', 'image':'a.jpg', 'offers':{'price':'10', 'priceCurrency':'EUR'}},
        {'@type':'Product', 'name':'B', 'sku':'b', 'image':'b.jpg', 'offers':{'price':'20'}}])+'</script>'
    def respond(req):
        return httpx.Response(302, headers={'location':'https://page.test/p'}) if req.url.host == 'shop.test' else httpx.Response(200, text=html)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond), follow_redirects=True) as client:
        result = await UnifiedCrawlExtractor(http_client=client).extract(SHOP)
    products = _normalize_batch(result.products, Platform.GENERIC, SHOP)
    assert [audit(p)['/price']['value'] for p in products] == [Decimal(10), Decimal(20)]
    assert audit(products[1])['/currency']['state'] == 'unsupported'
    assert all(e.source_url == 'https://page.test/p' for p in products for e in p.evidence_contract.evidence)


def test_css_matching_nodes_and_ambiguous_items():
    schema = {'baseSelector': '.product', 'fields': [
        {'name':'title','selector':'h1','type':'text'},
        {'name':'price','selector':'.price','type':'text'},
        {'name':'sku','selector':'.sku','type':'text'}]}
    html = '<div class="product"><h1>A</h1><b class="price">0</b><b class="sku">a</b></div>'
    result = SimpleNamespace(success=True, url=SHOP+'/actual', html=html,
                             extracted_content=json.dumps({'title':'A','price':'0','sku':'a'}))
    extractor = CSSExtractor(schema)
    raw = extractor._parse_extracted_content(SHOP, result)[0]
    product = normalize(raw)
    assert audit(product)['/price']['value'] == 0
    assert product.evidence_contract.evidence[0].source_url.endswith('/actual')
    result.html = html + html
    raw = extractor._parse_extracted_content(SHOP, result)[0]
    assert audit(normalize(raw))['/price']['state'] == 'unsupported'


@pytest.mark.asyncio
async def test_mocked_llm_cannot_assert_support_or_confidence():
    from crawl4ai import LLMConfig
    from shopextract.extractors.llm import LLMExtractor
    result = SimpleNamespace(success=True, url=SHOP+'/actual', extracted_content=json.dumps(
        {'title':'A', 'sku':'a', 'price':'5', 'score':0.99, 'validated_confidence':1}))
    crawler = MagicMock()
    crawler.__aenter__ = AsyncMock(return_value=crawler)
    crawler.__aexit__ = AsyncMock(return_value=None)
    crawler.arun = AsyncMock(return_value=result)
    with patch('shopextract.extractors.llm.AsyncWebCrawler', return_value=crawler), \
         patch('shopextract.extractors.llm.get_crawler_strategy', return_value=None):
        extracted = await LLMExtractor(LLMConfig(provider='openai/test', api_token='test')).extract(SHOP)
    product = normalize(extracted.products[0])
    view = audit(product)
    assert all(v['state'] == 'unsupported' and 'LLM' in v['reason'] for v in view.values())
    assert not product.evidence_contract.evidence


def test_truncation_defaults_original_values_and_nested_escaping():
    raw = capture({'title':'A','sku':'a','description':'é'*5000,'price':0,
                   'attributes':{'size/color~':'L'},'bundle_components':[]}, SHOP+'/api', 'api')
    product = normalize(raw)
    view = audit(product)
    assert view['/description']['state'] == 'unsupported' and 'truncat' in view['/description']['reason']
    assert view['/attributes/size~1color~0']['value'] == 'L'
    assert view['/bundle_components']['value'] == []
    assert view['/price']['value'] == 0
    assert view['/currency']['state'] == 'unsupported'
    raw = capture({'title':'A','sku':'a','price':None}, SHOP+'/api', 'api')
    assert audit(normalize(raw))['/price']['state'] == 'unknown'
    raw = capture({'title':'A','sku':'a','price':'invalid'}, SHOP+'/api', 'api')
    assert audit(normalize(raw))['/price']['state'] == 'unsupported'
    raw = capture({'title':'A','sku':'a','gtin':'029877030712'}, SHOP+'/api', 'api')
    product = normalize(raw)
    gtin = observation(product, '/gtin')
    assert gtin.raw_value == '029877030712' and gtin.normalized_value == '0029877030712'
    assert gtin.transformations


@pytest.mark.asyncio
async def test_feed_redirect_and_extraction_error():
    def respond(req):
        if req.url.host == 'shop.test':
            return httpx.Response(302, headers={'location':'https://feeds.test/data.csv'})
        return httpx.Response(200, text='id,title,price\na,A,1 EUR\n', headers={'content-type':'text/csv'})
    client = httpx.AsyncClient(transport=httpx.MockTransport(respond), follow_redirects=True)
    with patch('shopextract.extractors.feed.httpx.AsyncClient', return_value=client):
        result = await GoogleFeedExtractor().extract(SHOP+'/feed')
    product = normalize(result.products[0])
    audit(product)
    assert all(e.source_url == 'https://feeds.test/data.csv' for e in product.evidence_contract.evidence)
    with patch.object(GoogleFeedExtractor, '_fetch_feed', AsyncMock(return_value=('<rss>', 'text/xml'))):
        result = await GoogleFeedExtractor().extract(SHOP+'/feed')
    assert not result.complete and result.error and not result.products


def test_product_budget_and_standalone_variant_view():
    raw = capture({'title':'A', 'sku':'a', 'attributes':{str(i):'x'*512 for i in range(200)}}, SHOP+'/api', 'api')
    assert raw['_capture']['truncated']
    assert sum(_size(v) for v in raw['_capture']['values'].values()) <= PRODUCT_BYTES
    view = audit(normalize(raw))
    assert any(v['state'] == 'unsupported' for p,v in view.items() if p.startswith('/attributes/'))
    raw = capture({'title':'A', 'id':1, 'variants':[{'id':2, 'price':'10', 'available':False}]}, SHOP+'/api', 'api')
    product = normalize(raw, Platform.SHOPIFY, SHOP)
    audit(product)
    assert product.variants[0].trust_view()['/price']['value'] == Decimal(10)
    assert product.variants[0].trust_view()['/in_stock']['value'] is False


def test_layered_fallback_cannot_borrow_jsonld_or_parent_support():
    html = '<script type="application/ld+json">'+json.dumps({'@type':'Product','name':'A','sku':'a'})+'</script>'
    result = SimpleNamespace(html=html, metadata={}, markdown='Price: € 12.00', media={})
    raw = UnifiedCrawlExtractor._extract_from_crawl_result(result, SHOP+'/p')[0]
    product = normalize(raw)
    view = audit(product)
    assert view['/title']['state'] == 'observed'
    assert view['/price']['state'] == 'unsupported'


def test_filtered_nested_images_retain_correct_source_item():
    raw = capture({'id':1, 'title':'A', 'variants':[{'id':2,'price':'10'}],
                   'images':[{'src':'primary.jpg'}, {}, {'src':'second.jpg'}, {'src':'third.jpg'}]},
                  SHOP+'/api', 'shopify_api')
    product = normalize(raw, Platform.SHOPIFY, SHOP)
    audit(product)
    for i, original in enumerate(('second.jpg', 'third.jpg')):
        o = observation(product, f'/additional_images/{i}')
        assert o.raw_value == original
        e = next(e for e in product.evidence_contract.evidence if e.evidence_id in o.evidence_ids)
        assert e.retained_data['source_pointer'] == f'/images/{i+2}/src'


@pytest.mark.parametrize('platform,raw', [
    (Platform.SHOPIFY, {'title':'A','id':1,'variants':[{'id':2,'price':'1,234'}]}),
    (Platform.WOOCOMMERCE, {'name':'A','id':1,'prices':{'price':'€ 5'}}),
    (Platform.MAGENTO, {'name':'A','sku':'a','price':'$5'}),
    (Platform.GENERIC, {'@type':'Product','name':'A','sku':'a','offers':{'price':'1,25'}}),
    (Platform.GENERIC, {'_source':'google_feed','title':'A','id':'a','price':'$5'}),
])
def test_rejected_price_conversion_never_supports_default(platform, raw):
    product = normalize(capture(raw, SHOP+'/api', 'api'), platform, SHOP)
    assert product.price == 0
    assert audit(product)['/price']['state'] == 'unsupported'


def test_image_fallback_tracks_actual_successful_selection():
    raw = {'@type':'Product', 'name':'A', 'sku':'a', 'image':{'caption':'irrelevant'},
           'thumbnailUrl':'thumb.jpg'}
    product = normalize(capture(raw, SHOP+'/p', 'json_ld'))
    assert product.image_url == 'thumb.jpg'
    assert observation(product, '/image_url').raw_value == 'thumb.jpg'


@pytest.mark.parametrize('raw', [
    {'@type':'Product','name':'A','sku':'a','offers':{'itemCondition':'UnrecognizedCondition'}},
    {'_source':'google_feed','title':'A','id':'a','condition':'unspecified'},
])
def test_unrecognized_condition_never_supports_default(raw):
    product = normalize(capture(raw, SHOP+'/p', 'fixture'))
    assert product.condition == 'NEW'
    assert audit(product)['/condition']['state'] == 'unsupported'


def test_shopware_variant_uses_its_own_stock_id_and_title_inputs():
    raw = {'title':'A', 'id':1, 'variants':[
        {'variant_id':'sw-1', 'name':'B', 'price':'10', 'in_stock':False, 'inventory_quantity':9}]}
    product = normalize(capture(raw, SHOP+'/api', 'shopware_api'), Platform.SHOPWARE, SHOP)
    audit(product)
    for field, expected, pointer in [('in_stock',False,'in_stock'), ('variant_id','sw-1','variant_id'), ('title','B','name')]:
        o = observation(product, '/variants/0/'+field)
        assert o.normalized_value == expected and o.raw_value == expected
        e = next(e for e in product.evidence_contract.evidence if e.evidence_id in o.evidence_ids)
        assert e.retained_data['source_pointer'] == '/variants/0/'+pointer


@pytest.mark.asyncio
@pytest.mark.parametrize('structured', ['json_ld', 'opengraph'])
async def test_browser_redirect_capture_uses_final_url(structured):
    if structured == 'json_ld':
        html = '<script type="application/ld+json">'+json.dumps(
            {'@type':'Product','name':'A','sku':'a','image':'a.jpg','offers':{'price':'10'}})+'</script>'
    else:
        html = '<meta property="og:title" content="A"><meta property="product:price:amount" content="10"><meta property="og:image" content="a.jpg">'
    result = SimpleNamespace(success=True, url='https://final.test/p', html=html,
                             metadata={}, markdown='', media={})
    crawler = MagicMock()
    crawler.__aenter__ = AsyncMock(return_value=crawler)
    crawler.__aexit__ = AsyncMock(return_value=None)
    crawler.arun = AsyncMock(return_value=result)
    extractor = UnifiedCrawlExtractor()
    with patch.object(extractor, '_fetch_html_httpx', AsyncMock(return_value=None)), \
         patch('crawl4ai.AsyncWebCrawler', return_value=crawler), \
         patch('shopextract.extractors.unified.get_crawler_strategy', return_value=None):
        extracted = await extractor.extract(SHOP+'/requested')
    product = normalize(extracted.products[0])
    assert audit(product)['/price']['value'] == Decimal(10)
    assert all(e.source_url == 'https://final.test/p' for e in product.evidence_contract.evidence)


def test_capture_budget_cannot_change_normalizer_source_selection():
    raw = {'@type':'Product','name':'A','sku':'a', 'image':'x'*5000, 'thumbnailUrl':'thumb.jpg'}
    product = normalize(capture(raw, SHOP+'/p', 'json_ld'))
    assert product.image_url == 'x'*5000
    o = observation(product, '/image_url')
    assert o.state == 'unsupported' and not o.evidence_ids
    assert 'truncat' in o.reason


def test_platform_fallback_consumes_outcomes_from_actual_normalizer():
    raw = {'@type':'Product','name':'A','sku':'a','offers':{'price':'12','priceCurrency':'EUR'}}
    product = normalize(capture(raw, SHOP+'/p', 'json_ld'), Platform.SHOPIFY, SHOP)
    assert audit(product)['/price']['value'] == Decimal(12)
    assert observation(product,'/price').raw_value == '12'


@pytest.mark.parametrize('field,value', [('price','1,20'), ('condition','UnrecognizedCondition')])
def test_rejected_conversion_retains_original_input_and_reason(field,value):
    raw = {'@type':'Product','name':'A','sku':'a','offers':{('price' if field == 'price' else 'itemCondition'):value}}
    product = normalize(capture(raw, SHOP+'/p', 'json_ld'))
    o = observation(product,'/'+field)
    assert o.state == 'unsupported' and o.raw_value == value
    assert 'reject' in o.reason.lower() or 'failed' in o.reason.lower()


def test_changed_captured_input_cannot_support_later_enrichment():
    raw = capture({'@type':'Product','name':'A','sku':'a','offers':{'price':'0'}}, SHOP+'/p', 'json_ld')
    raw['offers']['price'] = '15'
    product = normalize(raw)
    assert product.price == Decimal(15)
    o = observation(product,'/price')
    assert o.state == 'unsupported' and o.raw_value == '0' and not o.evidence_ids
    assert 'differs' in o.reason


def test_barcode_enrichment_preserves_aggregate_stock_support():
    raw = capture({'title':'A','id':1,'variants':[
        {'id':2,'price':'10','available':False}, {'id':3,'price':'20','available':True}]}, SHOP+'/api', 'shopify_api')
    raw['variants'][0]['barcode'] = '4006381333931'
    product = normalize(raw,Platform.SHOPIFY,SHOP)
    assert audit(product)['/in_stock']['value'] is True
    o = observation(product,'/in_stock')
    assert o.raw_value == [False,True]
    pointers = {e.retained_data['source_pointer'] for e in product.evidence_contract.evidence if e.evidence_id in o.evidence_ids}
    assert pointers == {'/variants/0/available','/variants/1/available'}


@pytest.mark.asyncio
async def test_response_cookie_currency_retains_actual_response_evidence():
    def respond(req):
        return httpx.Response(200,json={'products':[{'title':'A','id':1,'variants':[{'id':2,'price':'10'}]}]},
                              headers={'set-cookie':'cart_currency=CAD; Path=/'})
    client=httpx.AsyncClient(transport=httpx.MockTransport(respond))
    with patch('shopextract.extractors.shopify.httpx.AsyncClient',return_value=client):
        result=await ShopifyExtractor().extract(SHOP,max_products=1)
    product=normalize(result.products[0],Platform.SHOPIFY,SHOP)
    assert audit(product)['/currency']['value'] == 'CAD'
    o=observation(product,'/currency')
    e=next(e for e in product.evidence_contract.evidence if e.evidence_id in o.evidence_ids)
    assert e.method == 'shopify_response_cookie' and '/products.json?' in e.source_url
    assert e.resolve_pointer() == 'CAD'


def test_native_shopware_sources_and_child_availability():
    raw = capture({'id': 'p', 'name': 'Pepper', 'productNumber': 'SW1',
                   'available': False, 'stock': 9,
                   'calculatedPrice': {'unitPrice': 6.5},
                   'children': [{'id': 'c', 'name': 'Jar', 'productNumber': 'SW1.1',
                                 'available': False, 'stock': 9,
                                 'calculatedPrice': {'unitPrice': 0}}]}, SHOP, 'shopware_store_api')
    p = normalize(raw, Platform.SHOPWARE, SHOP)
    view = audit(p)
    assert p.price == Decimal('6.5') and not p.in_stock
    assert p.variants[0].price == 0 and not p.variants[0].in_stock
    assert view['/variants/0/price']['state'] == 'observed'
    for path, pointer in [('/price', '/calculatedPrice/unitPrice'),
                          ('/in_stock', '/available'),
                          ('/variants/0/in_stock', '/children/0/available')]:
        obs = observation(p, path)
        evidence = next(e for e in p.evidence_contract.evidence if e.evidence_id == obs.evidence_ids[0])
        assert evidence.retained_data['source_pointer'] == pointer


@pytest.mark.parametrize('price,stock,state', [(45, 'OUT_OF_STOCK', 'observed'), ('bad', 'UNKNOWN', 'unsupported')])
def test_native_magento_graphql_conversion_outcomes(price, stock, state):
    raw = capture({'sku': 'WSH12', 'name': 'Short', 'stock_status': stock,
                   'price_range': {'minimum_price': {'final_price': {'value': price, 'currency': 'EUR'}}}},
                  SHOP + '/graphql', 'magento_graphql')
    p = normalize(raw, Platform.MAGENTO, SHOP)
    view = audit(p)
    assert view['/price']['state'] == state
    assert view['/in_stock']['state'] == state
    assert view['/currency']['value'] == 'EUR'
    if state == 'observed':
        assert not p.in_stock and p.price == 45


def test_css_currency_and_relative_image_keep_exact_source():
    raw = capture({'title': 'Book', 'price': '£51.77', 'image': '../../media/book.jpg'},
                  SHOP + '/catalogue/book/index.html', 'css')
    p = normalize(raw, shop_url=SHOP + '/catalogue/book/index.html')
    view = audit(p)
    assert p.currency == 'GBP' and p.image_url == SHOP + '/media/book.jpg'
    assert view['/currency']['state'] == view['/image_url']['state'] == 'observed'
    assert observation(p, '/currency').raw_value == '£51.77'


@pytest.mark.parametrize('format', ['xml', 'csv'])
def test_currency_prefixed_feed_price_is_not_a_default_zero(format):
    body = ('<rss xmlns:g="http://base.google.com/ns/1.0"><channel><item>'
            '<g:id>a</g:id><g:title>Wallet</g:title><g:price>USD 110.00</g:price>'
            '</item></channel></rss>') if format == 'xml' else 'id,title,price\na,Wallet,USD 110.00\n'
    parse = GoogleFeedExtractor._parse_xml if format == 'xml' else GoogleFeedExtractor._parse_csv
    p = normalize(parse(body, SHOP + '/feed')[0])
    view = audit(p)
    assert p.price == 110 and p.currency == 'USD'
    assert view['/price']['state'] == view['/currency']['state'] == 'observed'
    assert any('USD 110.00' in e.retained_data.get('source_excerpt', '') for e in p.evidence_contract.evidence)


def test_capture_prioritizes_leaves_over_duplicate_parent_objects():
    raw = {'name': 'Pepper', 'id': 'p', 'children': [
        {'id': str(i), 'name': 'Child', 'details': {'label': 'x' * 1800}}
        for i in range(14)], 'calculatedPrice': {'unitPrice': 6.5}, 'available': False}
    p = normalize(capture(raw, SHOP, 'shopware_store_api'), Platform.SHOPWARE, SHOP)
    view = audit(p)
    assert view['/price']['state'] == 'observed' and view['/in_stock']['state'] == 'observed'
    assert sum(_size(v) for v in raw['_capture']['values'].values()) <= PRODUCT_BYTES
