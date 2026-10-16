"""One real parser/normalizer/evidence smoke for every promised native platform."""
import json
from pathlib import Path
import httpx
import pytest
from shopextract.tools import ToolConfig, ToolRuntime
from tests.tool_api_fixtures import ORIGIN, resolver
from tests.test_agent_tool_api import completed
from tests.test_storefront_apis import magento_item, bigcommerce_item


@pytest.mark.parametrize('platform', ['shopify', 'woocommerce', 'magento', 'shopware', 'bigcommerce'])
@pytest.mark.asyncio
async def test_native_mode_guarded_parser_and_retained_evidence(platform):
    sent = []
    fixtures = Path(__file__).parent / 'fixtures'
    def respond(request):
        sent.append((request.method, request.url.path))
        if request.url.path == '/':
            pages = {
                'shopify': '<meta name="generator" content="shopify">',
                'woocommerce': '<meta name="generator" content="wordpress">',
                'magento': '<html>Magento</html>',
                'shopware': '<meta name="generator" content="Shopware"><script>window.__NUXT__.config={public:{shopware:{accessToken:"public-key",endpoint:"'+ORIGIN+'/store-api/"}}}</script>',
                'bigcommerce': '<meta name="platform" content="bigcommerce"><script>var jsContext={"storefrontAPIToken":"public-token"}</script>',
            }
            return httpx.Response(200, text=pages[platform])
        if platform == 'shopify' and request.url.path == '/products.json':
            body = json.loads((fixtures/'shopify_products.json').read_text())
            body['products'] = body['products'][:1]
            return httpx.Response(200, json=body)
        if platform == 'woocommerce' and request.url.path.endswith('/products'):
            return httpx.Response(200, json=json.loads((fixtures/'woocommerce_products.json').read_text())[:1],
                                  headers={'X-WP-TotalPages': '1'})
        if platform == 'magento' and request.url.path == '/graphql':
            if 'storeConfig' in request.url.params.get('query', ''):
                return httpx.Response(200, json={'data': {'storeConfig': {'store_code': 'default'}}})
            return httpx.Response(200, json={'data': {'products': {'items': [magento_item()],
                'total_count': 1, 'page_info': {'current_page': 1, 'total_pages': 1}}}})
        if platform == 'bigcommerce' and request.url.path == '/graphql':
            return httpx.Response(200, json={'data': {'site': {'products': {
                'edges': [{'node': bigcommerce_item()}], 'pageInfo': {'hasNextPage': False, 'endCursor': 'done'}}}}})
        if platform == 'shopware' and request.url.path.endswith('/context'):
            return httpx.Response(200, json={'currency': {'isoCode': 'EUR'}})
        if platform == 'shopware' and request.url.path == '/store-api/product':
            return httpx.Response(200, json={'total': 1, 'elements': [{'id': 'p', 'name': 'Product',
                'productNumber': 'SW1', 'available': False, 'stock': 9,
                'calculatedPrice': {'unitPrice': 0}, 'seoUrls': [{'seoPathInfo': 'product'}],
                'children': [{'id': 'v', 'name': 'Variant', 'available': False,
                              'stock': 0, 'calculatedPrice': {'unitPrice': 0}}]}]})
        return httpx.Response(404, text='Synthetic missing route')
    engine = ToolRuntime(ToolConfig(allowed_origins=(ORIGIN,)), resolver=resolver,
                         wire_transport=httpx.MockTransport(respond))
    try:
        jid = await completed(engine.call, 'extract', {'url': ORIGIN, 'max_items': 2})
        result = await engine.call('job_result', {'schema_version': '1.0', 'job_id': jid, 'collection': 'products'})
        assert result['ok'], result
        product = result['data']['items'][0]
        price_ids = product['field_evidence']['/price']
        assert price_ids
        evidence = await engine.call('evidence', {'schema_version': '1.0',
            'owner': product['owner_handle'], 'evidence_id': price_ids[0]})
        assert evidence['ok'] and evidence['data']['status'] == 'available', evidence
        assert evidence['data']['evidence']['pointer'] == '/value'
        if platform in {'shopware', 'bigcommerce', 'magento'}:
            assert product['price'] == '0'
            assert product['in_stock'] is False
        assert len(sent) <= 20
    finally:
        await engine.aclose()
