"""Guarded native extraction using the existing parsers and capture normalizer."""
import json
from urllib.parse import urlsplit, urljoin, unquote
import httpx
from .contracts import ToolError, encoded
from .security import GuardedTransport, NativeReadPolicy, normalized
from .._models import Platform


class _TransportLease(httpx.AsyncBaseTransport):
    """Borrow the exact guarded authority/accounting without owning its pools."""
    def __init__(self,transport):self.transport=transport
    async def handle_async_request(self,request):return await self.transport.handle_async_request(request)
    async def aclose(self):pass


class GuardedSources:
    def __init__(self, config, guard, wire=None, *, category_config=None,shopify_storefront=None,include_refrigerator_attributes=False):
        self.config, self.guard, self.wire = config, guard, wire
        if type(include_refrigerator_attributes) is not bool:
            raise ValueError("Refrigerator attribute opt-in must be boolean")
        self.include_refrigerator_attributes = include_refrigerator_attributes
        self.category_config = category_config
        self.shopify_storefront = shopify_storefront
        if shopify_storefront is not None:
            from ..extractors.shopify_taxonomy import ShopifyStorefrontConfig
            if not isinstance(shopify_storefront,ShopifyStorefrontConfig) or category_config is None:
                raise ValueError('Storefront supplement requires category configuration')
        if category_config is not None:
            from ..categories.config import runtime_record
            runtime_record(category_config)

    async def execute(self, name, url, maximum, context):
        transport = GuardedTransport(self.config, context, self.guard, self.wire,
            policy=NativeReadPolicy(category_mode=self.category_config is not None and self.category_config.options.limits.terms > 0,
                shopify_endpoint=self.shopify_storefront.endpoint if self.shopify_storefront else None))
        try:
            async with httpx.AsyncClient(transport=transport, trust_env=False,
                    follow_redirects=False, timeout=10, headers={'User-Agent': 'ShopExtract/0.1.2'}) as client:
                norm, _ = await self.guard.authorize(url, context)
                if name == 'discover':
                    return await self.discover(client, norm, maximum, context)
                return await self.extract(client, transport, norm, maximum, context)
        except httpx.HTTPError:
            raise ToolError('source_error', 'Source request failed', retryable=True) from None

    async def discover(self, client, url, maximum, context):
        from .._discover import _parse_sitemap_xml
        # Native sitemap parser, no crawl4ai fallback or discovered authority.
        origin = normalized(url)[1]
        response = await client.get(origin + '/sitemap.xml')
        if response.status_code != 200:
            raise ToolError('source_error', 'Public sitemap unavailable')
        urls, diagnostics = [], []
        pending = [(str(response.url), response.text)]
        seen_maps = {str(response.url)}
        from defusedxml import ElementTree
        while pending:
            visit, text = pending.pop(0)
            if text is None:
                try:
                    nested = await client.get(visit)
                except ToolError as error:
                    if error.code != 'permission_denied':
                        raise
                    diagnostics.append({'code': 'rejected_source', 'message': 'Discovered source denied'})
                    continue
                if nested.status_code != 200:
                    raise ToolError('source_error', 'Nested sitemap unavailable')
                text = nested.text
            try:
                root = ElementTree.fromstring(text)
            except Exception:
                raise ToolError('source_error', 'Invalid sitemap') from None
            is_index = root.tag.rsplit('}', 1)[-1] == 'sitemapindex'
            candidates = _parse_sitemap_xml(text)
            # Existing helper returns nested-map locations as well as product locations.
            if not candidates:
                candidates = [e.text.strip() for e in root.iter() if e.tag.rsplit('}', 1)[-1] == 'loc' and e.text]
            for candidate in candidates:
                try:
                    target = urljoin(origin, candidate)
                    if is_index:
                        # Queue identity only: no DNS for unvisited siblings.
                        allowed = normalized(target)[0]
                        if allowed not in seen_maps:
                            seen_maps.add(allowed)
                            pending.append((allowed, None))
                        continue
                    if unquote(urlsplit(target).path).lower().endswith(('.md', '.markdown', '.txt', '.pdf')):
                        diagnostics.append({'code': 'unsupported_source', 'message': 'Discovered format is unsupported'})
                        continue
                    allowed, _ = await self.guard.authorize(target, context)
                except ToolError as error:
                    if error.code != 'permission_denied':
                        raise
                    diagnostics.append({'code': 'rejected_source', 'message': 'Discovered source denied'})
                    continue
                if allowed not in urls:
                    urls.append(allowed)
                    if len(urls) >= maximum:
                        return {'urls': urls, 'complete': False, 'diagnostics': diagnostics}
        return {'urls': urls, 'complete': not diagnostics, 'diagnostics': diagnostics}

    async def extract(self, client, transport, url, maximum, context):
        from .._detect import _analyze_meta_tags, _analyze_cdn_sources, _determine_platform
        response = await client.get(url)
        if response.status_code != 200:
            raise ToolError('source_error', 'Source returned unsuccessful status')
        html = response.text
        path = urlsplit(url).path.lower()
        mode = 'html'
        if path.endswith(('.csv', '.tsv')):
            mode = 'csv'
        elif path.endswith('.xml') and 'sitemap' not in path:
            mode = 'xml'
        signals = {platform: [] for platform in Platform}
        if mode == 'html':
            _analyze_meta_tags(html, signals)
            _analyze_cdn_sources(html, signals)
            if any(key.startswith('x-shopify') for key in response.headers):
                signals[Platform.SHOPIFY].append('Shopify response header')
        platform, _ = _determine_platform(signals)
        if platform == Platform.GENERIC and mode == 'html':
            from .._detect import _probe_magento_graphql
            await _probe_magento_graphql(client, normalized(url)[1], signals)
            if transport.last_error:
                raise transport.last_error
            platform, _ = _determine_platform(signals)
        raw, complete, diagnostics = None, True, []
        origin = normalized(url)[1]
        if platform != Platform.GENERIC:
            from ..extractors.shopify import ShopifyExtractor
            from ..extractors.woocommerce import WooCommerceExtractor
            from ..extractors.magento_graphql import MagentoGraphQLExtractor
            from ..extractors.shopware import ShopwareExtractor
            from ..extractors.bigcommerce import BigCommerceExtractor
            classes = {Platform.SHOPIFY: ShopifyExtractor, Platform.WOOCOMMERCE: WooCommerceExtractor,
                Platform.MAGENTO: MagentoGraphQLExtractor, Platform.SHOPWARE: ShopwareExtractor,
                Platform.BIGCOMMERCE: BigCommerceExtractor}
            cls = classes.get(platform)
            if cls:
                extractor = cls(http_client=client, max_pages=20)
                options = {} if platform == Platform.WOOCOMMERCE else {'max_products': maximum}
                if self.category_config is not None and platform in (Platform.BIGCOMMERCE,Platform.MAGENTO):
                    options['include_categories'] = self.category_config.options.limits.terms > 0
                if platform == Platform.SHOPWARE:
                    from ..extractors._storefront import resolve_config
                    base, token = await resolve_config(client, origin, 'shopware')
                    if base and token:
                        target = base.rstrip('/') + '/product'
                        eligible, _ = await self.guard.authorize(target, context)
                        if urlsplit(eligible).path != '/store-api/product' or urlsplit(eligible).query:
                            raise ToolError('source_error', 'Unsupported native Shopware search route')
                        transport.policy = NativeReadPolicy(eligible,category_mode=self.category_config is not None and self.category_config.options.limits.terms > 0)
                        options.update(endpoint=base, access_token=token)
                result = await extractor.extract(origin, **options)
                if platform==Platform.SHOPIFY and self.shopify_storefront is not None:
                    from ..extractors.shopify_taxonomy import supplement_categories
                    from ..extractors._storefront import stateless_cookies
                    async with httpx.AsyncClient(transport=_TransportLease(transport),trust_env=False,
                            follow_redirects=False,timeout=10,cookies=stateless_cookies(),
                            headers={'User-Agent':'ShopExtract/0.1.2'}) as category_client:
                        await supplement_categories(result.products,self.shopify_storefront,client=category_client)
                if transport.last_error:
                    raise transport.last_error
                raw, complete = result.products, result.complete
                if result.error:
                    diagnostics.append({'code': 'source_error', 'message': 'Native source incomplete'})
                if not raw:
                    if complete:
                        return {'products': [], 'complete': True, 'diagnostics': diagnostics}
                    if self.category_config is not None:
                        return {'products': [], 'complete': False, 'diagnostics': diagnostics}
                    # A static supported product can still supply truthful partial results.
                    raw = None
        payload = {'operation': 'parse', 'mode': mode, 'html': html if raw is None else None,
            'raw': raw, 'platform': platform.value, 'url': url, 'origin': origin,
            'maximum': maximum, 'observed_at': context.observed_at.isoformat()}
        if self.include_refrigerator_attributes:
            payload['include_refrigerator_attributes'] = True
        if self.category_config is not None:
            from ..categories.config import runtime_record
            payload['category_config'] = runtime_record(self.category_config)
        value = json.loads(await context.auxiliary.run('domain', encoded(payload), context))
        if self.category_config is not None:
            from ..categories.portable import validate_categorized_products
            validate_categorized_products(value, options=self.category_config.options, maximum=maximum)
        if not value:
            raise ToolError('source_error', 'No supported native or static product data; browser/model modes unavailable')
        if raw is not None and len(raw) >= maximum:
            complete = False
        return {'products': value, 'complete': complete and len(value) < maximum,
                'diagnostics': diagnostics}
