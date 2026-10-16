"""Bounded read-only observations; run only after independent plan/offline approval."""
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

import httpx

from shopextract._models import Platform
from shopextract.categories import (
    CategoryOptions, CategoryScope, TargetRegistry, normalize_with_categories,
    categorized_product_to_record,
)
from shopextract.extractors._storefront import public_config, request

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/category-mapping/live'
CASES = {
    'shopify': 'https://www.boardgamebliss.com',
    'woocommerce': 'https://demo.athemes.com/botiga',
    'magento': 'https://magento2-demo.magebit.com',
    'shopware': 'https://frontends-demo.vercel.app',
    'bigcommerce': 'https://cornerstone-light-demo.mybigcommerce.com',
    'generic': 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html',
}
API_BASES = {
    'shopware': 'https://demo-frontends.shopware.store/store-api',
    'bigcommerce': 'https://cornerstone-light-demo.mybigcommerce.com/graphql',
}
PLAN = dict(schema_version=1, sources=CASES, requests_total=12,
            requests_per_platform=2, products_retained=2, request_seconds=10,
            aggregate_seconds=120, response_bytes=2097152, workers=1,
            retries=0, browser=False, models=False,
            expected='supported captured categories or explicit unavailable; never a complete taxonomy',
            prerequisites='Shopware/BigCommerce only previously published saved public configuration; no new credentials',
            provenance='actual live responses only; prior captures used solely for access configuration',
            state='planned_independent_review_required')

EXPECTATIONS = {
    'shopify': ('shopify:product_type', 'label'),
    'woocommerce': ('woocommerce:product_cat', 'memberships'),
    'magento': ('magento:category', 'memberships'),
    'shopware': ('shopware:category', 'memberships'),
    'bigcommerce': ('bigcommerce:category', 'memberships'),
    'generic': (None, None),  # Actual structured source may have no category at all.
}
PLAN['category_assertions'] = EXPECTATIONS
PLAN['saved_public_api_endpoints'] = API_BASES


def safe_reason(error):
    known = {'live_request_cap', 'live_aggregate_timeout', 'live_rate_limited_no_retry',
             'live_response_byte_cap', 'live_endpoint_not_allowed', 'live_encoded_response_rejected'}
    return str(error) if isinstance(error, RuntimeError) and str(error) in known else type(error).__name__


class BudgetTransport(httpx.AsyncBaseTransport):
    def __init__(self, status, case, deadline, save):
        self.inner = httpx.AsyncHTTPTransport(retries=0)
        self.status, self.case, self.deadline = status, case, deadline
        self.save = save

    async def handle_async_request(self, req):
        events = self.status['network']
        expected = httpx.URL(API_BASES.get(self.case, CASES[self.case]))
        if req.url.scheme != 'https' or req.url.host != expected.host or req.url.port != expected.port:
            raise RuntimeError('live_endpoint_not_allowed')
        if len(events) >= 12 or sum(e['platform'] == self.case for e in events) >= 2:
            raise RuntimeError('live_request_cap')
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError('live_aggregate_timeout')
        # Never persist query parameters or request headers/access keys.
        event = dict(platform=self.case, method=req.method,
                     url=str(req.url.copy_with(query=None)))
        events.append(event)
        self.save()  # Reserve attempt before any wire access, including on crash/resume.
        req.headers['accept-encoding'] = 'identity'

        async def fetch():
            response = await self.inner.handle_async_request(req)
            try:
                event['status'] = response.status_code
                if response.headers.get('content-encoding', 'identity').lower() != 'identity':
                    raise RuntimeError('live_encoded_response_rejected')
                if response.status_code == 429:
                    raise RuntimeError('live_rate_limited_no_retry')
                parts, count = [], 0
                async for chunk in response.aiter_raw():
                    count += len(chunk)
                    if count > 2097152:
                        raise RuntimeError('live_response_byte_cap')
                    parts.append(chunk)
                return httpx.Response(response.status_code,
                    headers={k: v for k, v in response.headers.items()
                             if k.lower() not in ('content-encoding', 'content-length')},
                    content=b''.join(parts), request=req)
            finally:
                await response.aclose()
        try:
            return await asyncio.wait_for(fetch(), timeout=min(10, remaining))
        except Exception as error:
            event['error'] = safe_reason(error)
            raise
        finally:
            self.save()

    async def aclose(self):
        await self.inner.aclose()


async def observe(name, status, deadline, save):
    url = CASES[name]
    platform = Platform(name)
    options = CategoryOptions(CategoryScope(platform, url), TargetRegistry('live-observation', '1', ()))
    row = dict(platform=name, url=url, state='running')
    status['cases'].append(row)
    save()
    config = None
    if name in ('shopware', 'bigcommerce'):
        source = ROOT / ('artifacts/live-provenance-35/06-shopware-html.source'
                         if name == 'shopware' else 'artifacts/api-integration/bigcommerce-home.source')
        config = public_config(source.read_text(), name, url) if source.exists() else (None, None)
        if not all(config):
            row.update(state='blocked', reason='saved_public_endpoint_access_configuration_unavailable')
            return
        if config[0].rstrip('/') != API_BASES[name]:
            row.update(state='blocked', reason='saved_public_endpoint_does_not_match_plan')
            return
        row['native_endpoint'] = config[0]
        save()
    async with httpx.AsyncClient(transport=BudgetTransport(status, name, deadline, save),
                                 timeout=10, follow_redirects=False) as client:
        if name == 'generic':
            from shopextract.extractors.unified import UnifiedCrawlExtractor
            response = await request(client, 'GET', url)
            raw = UnifiedCrawlExtractor._extract_structured_from_html(
                response.text, str(response.url), include_categories=True)[:2]
            source_error = None
            row['catalog_complete'] = False
            row['source_reason'] = 'single_structured_page_only'
        else:
            from importlib import import_module
            module, klass = {
                'shopify': ('shopify', 'ShopifyExtractor'),
                'woocommerce': ('woocommerce', 'WooCommerceExtractor'),
                'magento': ('magento_graphql', 'MagentoGraphQLExtractor'),
                'shopware': ('shopware', 'ShopwareExtractor'),
                'bigcommerce': ('bigcommerce', 'BigCommerceExtractor'),
            }[name]
            extractor = getattr(import_module('shopextract.extractors.' + module), klass)(
                timeout=10, max_pages=1, http_client=client)
            kwargs = {} if name == 'woocommerce' else {'max_products': 2}
            if name in ('magento', 'bigcommerce'):
                kwargs['include_categories'] = True
            if config:
                kwargs.update(endpoint=config[0], access_token=config[1])
            result = await extractor.extract(url, **kwargs)
            raw, source_error = result.products[:2], bool(result.error)
            row['catalog_complete'] = result.complete
            row['source_reason'] = result.completeness_reason
        companions = [normalize_with_categories(item, platform, url, category_options=options) for item in raw]
        companions = [value for value in companions if value is not None]
        records = [categorized_product_to_record(value) for value in companions]
        (OUT / (name + '-companions.json')).write_text(json.dumps(records, indent=2) + '\n')
        namespace, relation = EXPECTATIONS[name]
        supported = [o for value in companions for o in value.observations
                     if (relation is None or o.relation == relation)
                     and any((namespace is None or t.ref.namespace == namespace)
                             and any(f.support.value == 'observed' for f in t.facts) for t in o.terms)]
        row.update(state='category_observed' if supported else 'inconclusive', products=len(companions),
                   category_assertion='passed' if supported else 'category_support_unavailable',
                   source_error=source_error,
                   observations=[dict(relation=o.relation, source_state=o.source_state,
                                      completeness=o.completeness, terms=len(o.terms),
                                      observed_facets=sum(f.support.value == 'observed' for t in o.terms for f in t.facts))
                                 for value in companions for o in value.observations])


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'plan.json').write_text(json.dumps(PLAN, indent=2) + '\n')
    if '--plan-only' in sys.argv:
        return
    path = OUT / 'status.json'
    status = json.loads(path.read_text()) if path.exists() else dict(
        at=datetime.now(timezone.utc).isoformat(), state='running', network=[], cases=[], seconds=0)
    for row in list(status['cases']):
        if row['state'] == 'running':
            if any(event['platform'] == row['platform'] for event in status['network']):
                row.update(state='inconclusive', reason='interrupted_after_reserved_attempt')
            else:
                status['cases'].remove(row)  # No wire attempt was reserved; safe to start.
    # Conservatively charge a full request timeout for reserved attempts on resume.
    status['seconds'] = max(status['seconds'], len(status['network']) * 10)
    if status['seconds'] >= 120:
        raise RuntimeError('live_budget_already_consumed')
    start = time.monotonic()
    deadline = start + 120 - status['seconds']
    if '--smoke' not in sys.argv and not any(
            row['platform'] == 'shopify' and row.get('state') != 'running' for row in status['cases']):
        raise RuntimeError('save_shopify_smoke_before_expansion')
    def save():
        status['seconds'] = round(120 - (deadline-time.monotonic()), 3)
        path.write_text(json.dumps(status, indent=2) + '\n')
    names = ['shopify'] if '--smoke' in sys.argv else list(CASES)
    for name in names:
        if any(row['platform'] == name for row in status['cases']):
            continue
        try:
            await asyncio.wait_for(observe(name, status, deadline, save), timeout=max(.01, deadline-time.monotonic()))
        except Exception as error:
            status['cases'][-1].update(state='inconclusive', reason=safe_reason(error))
        finally:
            save()
        if time.monotonic() >= deadline:
            break
    status['state'] = 'smoke_saved' if '--smoke' in sys.argv else 'completed_with_recorded_limitations'
    path.write_text(json.dumps(status, indent=2) + '\n')
    print(json.dumps(dict(state=status['state'], requests=len(status['network']),
                         cases=[(r['platform'],r['state']) for r in status['cases']], seconds=status['seconds'])))


if __name__ == '__main__':
    asyncio.run(main())
