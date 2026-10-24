"""Seed24 source-boundary fixtures. Production jobs/parsers/evidence stay real."""
import asyncio
import sys
from datetime import datetime, timezone

import httpx

from shopextract.tools import Limits, ToolConfig, ToolRuntime
from tests.tool_api_fixtures import HTML, ORIGIN, SITEMAP, resolver

SEED = 24
CAPTURE_TIME = datetime(2026, 10, 16, 10, tzinfo=timezone.utc)
CASES = {'success', 'duplicates', 'feed-cap', 'failed-discover', 'failed-extract',
         'pending-discover', 'pending-extract', 'timeout-extract'}


def fixture_runtime(case='success', *, allowed_tools=None):
    assert case in CASES
    requests = []
    feed = '<rss xmlns:g="http://base.google.com/ns/1.0"><channel>' + ''.join(
        f'<item><g:id>p{i}</g:id><g:title>Widget {i}</g:title><g:price>10.25 EUR</g:price>'
        f'<g:link>{ORIGIN}/products/widget{i}</g:link></item>' for i in range(3)) + '</channel></rss>'

    async def response(request):
        requests.append((request.method, str(request.url)))
        if request.url.path == '/sitemap.xml':
            if case == 'pending-discover':
                await asyncio.Event().wait()
            if case == 'failed-discover':
                return httpx.Response(404)
            sitemap = SITEMAP
            if case == 'duplicates':
                sitemap = SITEMAP.replace('</urlset>', '<url><loc>' + ORIGIN +
                    '/products/widget</loc></url></urlset>')
            if case == 'feed-cap':
                sitemap = SITEMAP.replace('/products/widget', '/products/catalog.xml')
            return httpx.Response(200, text=sitemap, headers={'content-type': 'application/xml'})
        if request.url.path.startswith('/products/'):
            if case in {'pending-extract', 'timeout-extract'}:
                await asyncio.Event().wait()
            if case == 'failed-extract':
                return httpx.Response(404)
            return httpx.Response(200, text=feed if case == 'feed-cap' else HTML,
                headers={'content-type': 'application/xml' if case == 'feed-cap' else 'text/html'})
        return httpx.Response(404)

    options = {'allowed_origins': (ORIGIN,),
               'limits': Limits(item_count=2, timeout_seconds=1 if case == 'timeout-extract' else 5)}
    if allowed_tools is not None:
        options['allowed_tools'] = allowed_tools
    engine = ToolRuntime(ToolConfig(**options), resolver=resolver,
        wire_transport=httpx.MockTransport(response), utc_now=lambda: CAPTURE_TIME)
    return engine, requests


if __name__ == '__main__':
    from shopextract.tools.mcp_server import serve
    engine, _ = fixture_runtime(sys.argv[1] if len(sys.argv) == 2 else 'success')
    asyncio.run(serve(engine))
