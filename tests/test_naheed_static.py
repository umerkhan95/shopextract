"""Synthetic Naheed-shaped regression fixtures; no live website claims."""
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from shopextract._detect import detect
from shopextract._execution import ExecutionPolicy, execution_policy
from shopextract._models import Platform
from shopextract._normalize import normalize
from shopextract.extractors.unified import UnifiedCrawlExtractor

STORE = 'https://www.naheed.pk'
URL = STORE + '/max-factor-powder'
PLACEHOLDER = STORE + '/static/Magento_Catalog/images/product/placeholder/.jpg'
IMAGE = 'https://media.naheed.pk/catalog/product/m/f.jpg'


def page(**changes):
    product = {'@type': 'Product', 'name': 'Max Factor Powder', 'image': PLACEHOLDER,
               'offers': {'price': '2500', 'priceCurrency': 'PKR'}, 'url': URL}
    product.update(changes)
    return ('<script type="application/ld+json">' + json.dumps(product) + '</script>'
            '<meta property="og:image" content="' + PLACEHOLDER + '">'
            '<script src="/static/Magento_Catalog/js/product.js"></script>'
            '<main><a class="MagicZoom" href="' + IMAGE + '"><img src="thumb.jpg"></a>'
            '<a data-zoom-id="zoom" href="/media/catalog/product/second.jpg">second</a>'
            '<a data-zoom-id="zoom" href="' + IMAGE + '">duplicate</a>'
            '<div class="brand-name"><a href="/brands/max-factor">Max Factor</a></div>'
            '<span class="sku">IC-1160205</span></main><footer>+9221111624333</footer>')


def observation(product, path):
    return next(o for o in product.evidence_contract.observations if o.field_path == path)


@pytest.mark.asyncio
async def test_static_dom_enriches_before_early_return_with_honest_provenance():
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req: httpx.Response(200, text=page()))) as client:
        extractor = UnifiedCrawlExtractor(http_client=client)
        with execution_policy(ExecutionPolicy()), patch.object(extractor, '_extract_with_browser', AsyncMock()) as browser:
            result = await extractor.extract(URL)
        browser.assert_not_called()
    raw = result.products[0]
    assert raw['_capture']['values']['/image'] == PLACEHOLDER
    product = normalize(raw, Platform.MAGENTO, STORE)
    assert product.image_url == IMAGE
    assert product.additional_images == [STORE + '/media/catalog/product/second.jpg']
    assert product.vendor == 'Max Factor' and product.sku == 'IC-1160205'
    assert product.gtin is None and product.variants == []
    for path in ['/image_url', '/vendor', '/sku', '/additional_images/0']:
        fact = observation(product, path)
        assert fact.state.value == 'observed', (path, fact)
        evidence = [e for e in product.evidence_contract.evidence if e.evidence_id in fact.evidence_ids]
        assert evidence and all(e.method == 'html_product_dom' and e.source_url == URL for e in evidence)


@pytest.mark.parametrize('image', [PLACEHOLDER, [PLACEHOLDER], {'@type': 'ImageObject', 'url': PLACEHOLDER}, [], None])
def test_placeholder_is_not_complete_or_normalized_as_image(image):
    html = '<script type="application/ld+json">' + json.dumps({'@type':'Product','name':'Powder','image':image,'offers':{'price':10}}) + '</script>'
    raw = UnifiedCrawlExtractor._extract_structured_from_html(html, URL)[0]
    assert not UnifiedCrawlExtractor._has_price_and_image(raw)
    assert normalize(raw, shop_url=STORE).image_url == ''


def test_mixed_image_reindex_keeps_real_source_support_and_structured_fields():
    raw = UnifiedCrawlExtractor._extract_structured_from_html(page(image=[PLACEHOLDER, {'url': IMAGE}], brand='Original', sku='Original-SKU'), URL)[0]
    product = normalize(raw, Platform.MAGENTO, STORE)
    assert product.image_url == IMAGE and product.vendor == 'Original' and product.sku == 'Original-SKU'
    fact = observation(product, '/image_url')
    assert fact.state.value == 'observed'
    assert next(e for e in product.evidence_contract.evidence if e.evidence_id in fact.evidence_ids).method == 'json_ld'


def test_real_filename_with_placeholder_substring_is_retained():
    image = STORE + '/catalog/product/placeholder-artwork-print.jpg'
    raw = UnifiedCrawlExtractor._extract_structured_from_html(page(image=image), URL)[0]
    assert normalize(raw).image_url == image


def test_global_dom_does_not_leak_into_multiple_products_or_missing_sku():
    html = page() + '<script type="application/ld+json">' + json.dumps({'@type':'Product','name':'Other','offers':{'price':5}}) + '</script>'
    raws = UnifiedCrawlExtractor._extract_structured_from_html(html, URL)
    assert all(not raw.get('brand') and not raw.get('sku') for raw in raws)
    raw = UnifiedCrawlExtractor._extract_structured_from_html(page().replace('<span class="sku">IC-1160205</span>', ''), URL)[0]
    assert normalize(raw).sku is None


def test_browser_result_and_og_path_share_dom_enrichment():
    html = page().replace('<script type="application/ld+json">', '<script type="not-json-ld">')
    html += '<meta property="og:title" content="Max Factor Powder"><meta property="product:price:amount" content="2500">'
    result = SimpleNamespace(url=URL, html=html, metadata={}, markdown='', media={'images':[{'src':PLACEHOLDER,'score':10}]})
    raw = UnifiedCrawlExtractor._extract_from_crawl_result(result, URL)[0]
    product = normalize(raw, Platform.MAGENTO, STORE)
    assert product.image_url == IMAGE and product.vendor == 'Max Factor' and product.sku == 'IC-1160205'
    assert product.additional_images == [STORE + '/media/catalog/product/second.jpg']


@pytest.mark.asyncio
@pytest.mark.parametrize('html,expected', [('<script src="/static/Magento_Catalog/js/catalog.js"></script>',Platform.MAGENTO),
    ('<script>require(["mage/gallery/gallery"],function(){});</script>',Platform.MAGENTO),
    ('<p>We discuss Magento_Catalog and mage/ as plain prose.</p>',Platform.GENERIC)])
async def test_magento_html_detected_despite_403_apis_and_generic_zero_confidence(html, expected):
    def handler(req):
        return httpx.Response(200, text=html) if req.url.path == '/' else httpx.Response(403)
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await detect(STORE, client=client)
    assert result.platform == expected
    assert (result.confidence > 0) if expected == Platform.MAGENTO else result.confidence == 0


@pytest.mark.parametrize('href', ['', '#', '#zoom', 'javascript:void(0)'])
def test_non_image_gallery_references_never_become_product_page_images(href):
    product={'@type':'Product','name':'Powder','offers':{'price':10}}
    html='<script type="application/ld+json">'+json.dumps(product)+'</script><a class="MagicZoom" href="'+href+'">zoom</a>'
    raw=UnifiedCrawlExtractor._extract_structured_from_html(html,URL)[0]
    assert not UnifiedCrawlExtractor._has_price_and_image(raw)
    assert normalize(raw).image_url==''


@pytest.mark.asyncio
async def test_detected_magento_blocked_api_routes_static_raw_through_generic_normalizer():
    from shopextract import extract
    requests=[]
    def handler(req):
        requests.append((req.method,str(req.url)))
        if req.url.path in ('/', '/max-factor-powder'):
            return httpx.Response(200,text=page())
        return httpx.Response(403)
    client_type=httpx.AsyncClient
    def factory(**kwargs):
        return client_type(transport=httpx.MockTransport(handler),**kwargs)
    with patch('httpx.AsyncClient',side_effect=factory), patch('shopextract._discover.discover',AsyncMock(return_value=[URL])), execution_policy(ExecutionPolicy()):
        result=await extract(STORE,max_urls=1)
    assert result.platform==Platform.MAGENTO
    assert any('/graphql' in url for _,url in requests)
    assert len(result.products)==1
    product=result.products[0]
    assert product.image_url==IMAGE and product.sku=='IC-1160205' and product.vendor=='Max Factor'
    assert product.additional_images==[STORE+'/media/catalog/product/second.jpg']
