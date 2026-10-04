"""Shared read-only storefront transport and public runtime configuration discovery."""
from contextlib import asynccontextmanager
from html import unescape
import re
from urllib.parse import urljoin, urlsplit

import httpx

MAX_RESPONSE_BYTES = 10 * 1024 * 1024


def positive_limits(*values):
    if any(not isinstance(v, int) or isinstance(v, bool) or v <= 0 for v in values):
        raise ValueError('Storefront product and page limits must be positive integers')


@asynccontextmanager
async def storefront_client(client, timeout):
    if client is not None:
        yield client
    else:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as owned:
            yield owned


async def request(client, method, url, **kwargs):
    """Limit body size and never replay a storefront key to a redirect's new origin."""
    for _ in range(4):
        async with client.stream(method, url, follow_redirects=False, **kwargs) as response:
            if response.is_redirect:
                target = urljoin(str(response.url), response.headers['location'])
                old, new = urlsplit(str(response.url)), urlsplit(target)
                keyed = any(k.lower() in ('authorization', 'sw-access-key', 'sw-context-token',
                                         'x-bc-customer-access-token', 'x-bc-customer-id')
                            for k in list(client.headers) + list((kwargs.get('headers') or {})))
                if (old.scheme, old.netloc) != (new.scheme, new.netloc) and (keyed or method != 'GET'):
                    raise ValueError('API redirect changes origin; endpoint must be configured explicitly')
                if response.status_code in (301, 302, 303) and method != 'GET':
                    raise ValueError('API redirect changes request method')
                url = target
                continue
            response.raise_for_status()
            chunks, size = [], 0
            async for chunk in response.aiter_bytes():
                size += len(chunk)
                if size > MAX_RESPONSE_BYTES:
                    raise ValueError('Storefront response exceeds 10 MiB limit')
                chunks.append(chunk)
            return httpx.Response(response.status_code, content=b''.join(chunks),
                                  headers={k:v for k,v in response.headers.items()
                                           if k.lower() not in ('content-encoding','content-length')},
                                  request=response.request)
    raise ValueError('Too many API redirects')


def endpoint_url(value):
    parts = urlsplit(value)
    if parts.scheme not in ('http', 'https') or not parts.netloc or parts.username or parts.password:
        raise ValueError('Storefront endpoint must be an HTTP(S) URL without embedded credentials')
    return value.rstrip('/')


def _string(text, key):
    match = re.search(r'["\']?' + re.escape(key) + r'["\']?\s*:\s*(["\'])([^"\']+)\1', text, re.I)
    return match.group(2) if match else None


def public_config(html, platform, page_url):
    """Read explicit storefront keys from public HTML; never execute merchant scripts."""
    text = unescape(html).replace('\\"', '"')
    if platform == 'shopware':
        block = re.search(r'["\']?shopware["\']?\s*:\s*\{([^{}]{1,8192})\}', text, re.I)
        if block:
            endpoint, token = _string(block[1], 'endpoint'), _string(block[1], 'accessToken')
            if endpoint and token:
                return endpoint_url(urljoin(page_url, endpoint)), token
        return None, None
    for key in ('storefrontApiToken', 'storefrontAPIToken', 'storefront_api_token'):
        token = _string(text, key)
        if token:
            return urljoin(page_url, '/graphql'), token
    return None, None


async def resolve_config(client, url, platform, endpoint=None, access_token=None):
    if endpoint and access_token:
        return endpoint_url(endpoint), access_token
    response = await request(client, 'GET', url)
    discovered_endpoint, discovered_token = public_config(response.text, platform, str(response.url))
    # A discovered token is bound to its published endpoint, not an arbitrary override.
    if endpoint and discovered_endpoint and endpoint_url(endpoint) != endpoint_url(discovered_endpoint):
        return endpoint_url(endpoint), access_token
    return endpoint_url(endpoint) if endpoint else discovered_endpoint, access_token or discovered_token


def json_body(response):
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError('Expected storefront JSON object')
    if data.get('errors'):
        raise ValueError('GraphQL response reported errors; partial data is not accepted')
    return data
