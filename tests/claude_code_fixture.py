"""Seed24 source-boundary fixtures. Production jobs/parsers/evidence stay real."""
import asyncio
import sys
import json
import os
from pathlib import Path
from datetime import datetime, timezone

import httpx

from shopextract.tools import Limits, ToolConfig, ToolRuntime
from tests.tool_api_fixtures import HTML, ORIGIN, SITEMAP, resolver

SEED = 24
CAPTURE_TIME = datetime(2026, 10, 16, 10, tzinfo=timezone.utc)
CASES = {'success', 'duplicates', 'feed-cap', 'failed-discover', 'failed-extract',
         'pending-discover', 'pending-extract', 'timeout-extract', 'index-blog-first',
         'index-no-product', 'product-redirect', 'denied-redirect', 'delayed-discover', 'delayed-extract'}


class RequestLog(list):
    def __init__(self, path=None):
        super().__init__()
        self.path = Path(path) if path else None
        self.active_delays = set()
        self.persist()

    def append(self, value):
        super().append(value)
        self.persist()

    def persist(self):
        if self.path:
            self.path.write_text(json.dumps([{'method': method, 'url': url} for method, url in self]))


def fixture_runtime(case='success', *, allowed_tools=None, request_log_path=None, deny=False):
    assert case in CASES
    requests = RequestLog(request_log_path)
    feed = '<rss xmlns:g="http://base.google.com/ns/1.0"><channel>' + ''.join(
        f'<item><g:id>p{i}</g:id><g:title>Widget {i}</g:title><g:price>10.25 EUR</g:price>'
        f'<g:link>{ORIGIN}/products/widget{i}</g:link></item>' for i in range(3)) + '</channel></rss>'

    def make_map(urls):
        return '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(
            '<url><loc>' + url + '</loc></url>' for url in urls) + '</urlset>'

    async def finite_delay(path):
        requests.active_delays.add(path)
        try:
            await asyncio.sleep(.35)
        finally:
            requests.active_delays.discard(path)

    async def response(request):
        requests.append((request.method, str(request.url)))
        if request.url.path == '/sitemap.xml':
            if case == 'delayed-discover':
                await finite_delay('/sitemap.xml')
            if case in {'index-blog-first', 'index-no-product'}:
                index = '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(
                    '<sitemap><loc>' + ORIGIN + path + '</loc></sitemap>'
                    for path in ('/blogs-map.xml', '/products-map.xml')) + '</sitemapindex>'
                return httpx.Response(200, text=index, headers={'content-type': 'application/xml'})
            if case == 'pending-discover':
                await asyncio.Event().wait()
            if case == 'failed-discover':
                return httpx.Response(404)
            sitemap = SITEMAP
            if case == 'duplicates':
                sitemap = SITEMAP.replace('</urlset>', '<url><loc>' + ORIGIN +
                    '/products/widget</loc></url></urlset>')
            if case in {'product-redirect', 'denied-redirect'}:
                sitemap = SITEMAP.replace('/products/widget', '/products/redirect')
            if case == 'feed-cap':
                sitemap = SITEMAP.replace('/products/widget', '/products/catalog.xml')
            return httpx.Response(200, text=sitemap, headers={'content-type': 'application/xml'})
        if request.url.path in {'/blogs-map.xml', '/products-map.xml'}:
            if request.url.path == '/blogs-map.xml':
                urls = [ORIGIN + '/articles/first']
                if case == 'index-no-product':
                    urls.append(ORIGIN + '/blogs/second')
            else:
                urls = [ORIGIN + '/products/widget']
            return httpx.Response(200, text=make_map(urls), headers={'content-type': 'application/xml'})
        if request.url.path.startswith('/products/'):
            if request.url.path == '/products/redirect':
                destination = ORIGIN if case == 'product-redirect' else 'https://other.example'
                return httpx.Response(302, headers={'location': destination + '/products/widget'})
            if case == 'delayed-extract':
                await finite_delay('/products/widget')
            if case in {'pending-extract', 'timeout-extract'}:
                await asyncio.Event().wait()
            if case == 'failed-extract':
                return httpx.Response(404)
            return httpx.Response(200, text=feed if case == 'feed-cap' else HTML,
                headers={'content-type': 'application/xml' if case == 'feed-cap' else 'text/html'})
        return httpx.Response(404)

    options = {'allowed_origins': () if deny else (ORIGIN,),
               'limits': Limits(item_count=2, timeout_seconds=1 if case == 'timeout-extract' else 5)}
    if allowed_tools is not None:
        options['allowed_tools'] = allowed_tools
    engine = ToolRuntime(ToolConfig(**options), resolver=resolver,
        wire_transport=httpx.MockTransport(response), utc_now=lambda: CAPTURE_TIME)
    return engine, requests


if __name__ == '__main__':
    from shopextract.tools.mcp_server import serve
    host = os.environ.get('SHOPEXTRACT_FIXTURE_HOST') == '1'
    engine, _ = fixture_runtime(sys.argv[1] if len(sys.argv) == 2 else 'success',
        allowed_tools=('discover', 'extract', 'job_status', 'job_result', 'evidence') if host else None,
        request_log_path=os.environ.get('SHOPEXTRACT_FIXTURE_LOG'),
        deny=os.environ.get('SHOPEXTRACT_FIXTURE_DENY') == '1')
    asyncio.run(serve(engine))
