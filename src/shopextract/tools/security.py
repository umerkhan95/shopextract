"""Origin policy, cancellable DNS and raw-byte guards before HTTP decompression."""
from dataclasses import dataclass
import asyncio
import ipaddress
import json
import socket
import ssl
from urllib.parse import urlsplit, urlunsplit, urljoin
import httpcore
import httpx
from .runtime import ToolConfig
from .context import OperationContext, Resolver
from .contracts import ToolError, encoded


def normalized(url):
    try:
        parts = urlsplit(url)
        if parts.scheme not in {'http', 'https'} or parts.username is not None or parts.password is not None or parts.fragment:
            raise ValueError()
        host = (parts.hostname or '').rstrip('.').encode('idna').decode('ascii').lower()
        if not host or '%' in host or '\\' in url or any(ord(c) < 33 for c in url):
            raise ValueError()
        try:
            numeric = ipaddress.ip_address(host)
            host = numeric.compressed
        except ValueError:
            # Reject historical numeric/octal/hex host parsing differences.
            if host.replace('.', '').isdigit() or host.startswith('0x') or ':' in host:
                raise ValueError()
        port = parts.port or (443 if parts.scheme == 'https' else 80)
        bracketed = '[' + host + ']' if ':' in host else host
        authority = bracketed + (':' + str(port) if port != (443 if parts.scheme == 'https' else 80) else '')
        origin = parts.scheme + '://' + authority
        return urlunsplit((parts.scheme, authority, parts.path or '/', parts.query, '')), origin, host, port
    except (ValueError, UnicodeError):
        raise ToolError('permission_denied', 'Unsupported source URL') from None


def public(address):
    try:
        value = ipaddress.ip_address(address)
        if value.version == 6 and value.ipv4_mapped:
            value = value.ipv4_mapped
        return value.is_global and not (value.is_multicast or value.is_reserved or value.is_unspecified)
    except ValueError:
        return False


class SourceGuard:
    def __init__(self, config: ToolConfig, *, resolver: Resolver | None = None):
        self.config, self.resolver = config, resolver
        self.origins = {normalized(origin)[1] for origin in config.allowed_origins}

    async def authorize(self, url: str, context: OperationContext):
        if context.cancelled.is_set():
            raise asyncio.CancelledError()
        norm, origin, host, _ = normalized(url)
        if origin not in self.origins:
            raise ToolError('permission_denied', 'Source origin is not permitted')
        try:
            ipaddress.ip_address(host)
            addresses = [host]
        except ValueError:
            try:
                remaining = min(context.budget.limits.resolver_seconds,
                                context.deadline - asyncio.get_running_loop().time())
                if remaining <= 0:
                    raise ToolError('timeout')
                if self.resolver:
                    addresses = await asyncio.wait_for(self.resolver(host, context), remaining)
                else:
                    reply = await context.auxiliary.run('resolve', encoded({'host': host}), context)
                    addresses = json.loads(reply)
            except asyncio.TimeoutError:
                raise ToolError('timeout') from None
        if not addresses or len(addresses) > 64 or not all(public(address) for address in addresses):
            raise ToolError('permission_denied', 'Source resolved to a prohibited address')
        if context.cancelled.is_set():
            raise asyncio.CancelledError()
        return norm, tuple(addresses)


class PinnedBackend(httpcore.AsyncNetworkBackend):
    def __init__(self, context, guard, scheme):
        self.context, self.guard, self.scheme = context, guard, scheme
        self.backend = httpcore.AnyIOBackend()

    async def connect_tcp(self, host, port, timeout=None, local_address=None, socket_options=None):
        authority = '[' + host + ']' if ':' in host else host
        url = f'{self.scheme}://{authority}:{port}/'
        _, addresses = await self.guard.authorize(url, self.context)
        # Numeric address prevents another uncontrolled hostname lookup. HTTPCore
        # retains the original request origin for TLS start_tls and HTTP Host.
        return await self.backend.connect_tcp(addresses[0], port, timeout=timeout,
                    local_address=local_address, socket_options=socket_options)

    async def connect_unix_socket(self, *args, **kwargs):
        raise ToolError('permission_denied', 'Unix sockets are unavailable')

    async def sleep(self, seconds):
        await asyncio.sleep(seconds)


class CoreStream(httpx.AsyncByteStream):
    def __init__(self, stream):
        self.stream = stream
    async def __aiter__(self):
        async for chunk in self.stream:
            yield chunk
    async def aclose(self):
        await self.stream.aclose()


@dataclass(frozen=True)
class NativeReadPolicy:
    shopware_search_url: str | None = None
    category_mode: bool = False


class GuardedTransport(httpx.AsyncBaseTransport):
    def __init__(self, config, context, guard, wire_transport=None, *, policy=None):
        self.config, self.context, self.guard, self.wire = config, context, guard, wire_transport
        self.policy = policy or NativeReadPolicy()
        self.pools = {}
        self.last_error = None

    async def raw(self, request):
        if self.wire is not None:
            return await self.wire.handle_async_request(request)
        scheme = request.url.scheme
        if scheme not in self.pools:
            self.pools[scheme] = httpcore.AsyncConnectionPool(
                ssl_context=httpcore.default_ssl_context(), max_connections=1,
                max_keepalive_connections=0, retries=0,
                network_backend=PinnedBackend(self.context, self.guard, scheme))
        response = await self.pools[scheme].handle_async_request(httpcore.Request(
            method=request.method, url=httpcore.URL(scheme=request.url.raw_scheme,
                host=request.url.raw_host, port=request.url.port, target=request.url.raw_path),
            headers=request.headers.raw, content=request.stream, extensions=request.extensions))
        return httpx.Response(response.status, headers=response.headers,
                              stream=CoreStream(response.stream), extensions=response.extensions)

    async def handle_async_request(self, request):
        try:
            return await self.guarded(request)
        except ToolError as error:
            self.last_error = error
            raise
        except (httpcore.NetworkError, httpcore.ProtocolError, httpcore.TimeoutException, ssl.SSLError, OSError):
            self.last_error = ToolError('source_error', 'Source transport failed', retryable=True)
            raise self.last_error from None

    async def guarded(self, request):
        for _ in range(self.context.budget.limits.redirects + 1):
            canonical, _ = await self.guard.authorize(str(request.url), self.context)
            request.url = httpx.URL(canonical)
            request.headers['Host'] = request.url.netloc.decode('ascii')
            if request.method not in {'GET', 'HEAD', 'POST'}:
                raise ToolError('permission_denied', 'Source write methods are unavailable')
            if request.method == 'POST':
                try:
                    body = json.loads(request.content)
                    if 'query' in body:
                        from ..extractors.bigcommerce import _QUERY, _QUERY_WITH_CATEGORIES
                        allowed_queries = (_QUERY, _QUERY_WITH_CATEGORIES) if self.policy.category_mode else (_QUERY,)
                        if body['query'] not in allowed_queries or set(body) - {'query', 'variables'}:
                            raise ValueError()
                    else:
                        expected = {'page': body.get('page'), 'limit': body.get('limit'),
                            'total-count-mode': 1, 'sort': [{'field': 'id', 'order': 'ASC'}],
                            'associations': {'children': {'limit': 50}, 'seoUrls': {},
                                'manufacturer': {}, 'cover': {'associations': {'media': {}}}}}
                        if not (self.policy.shopware_search_url == str(request.url)
                            and request.url.path == '/store-api/product' and not request.url.query
                            and type(body.get('page')) is int and 1 <= body['page'] <= 20
                            and type(body.get('limit')) is int and 1 <= body['limit'] <= 20
                            and type(body.get('total-count-mode')) is int and body == expected):
                            raise ValueError()
                except (ValueError, TypeError, AttributeError):
                    raise ToolError('permission_denied', 'Only fixed native read queries are available') from None
            budget = self.context.budget
            if budget.requests_used >= budget.limits.requests:
                raise ToolError('resource_limit', 'Source request budget reached')
            budget.requests_used += 1
            request.headers['accept-encoding'] = 'identity'
            accounting = self.context.request_accounting
            if accounting is not None:
                try:
                    accounting.before_request(request.method, str(request.url))
                except Exception as error:
                    # Retain callback failures as transport errors so native
                    # adapters cannot swallow parent budget/cancel denial.
                    raise ToolError(getattr(error, 'code', 'internal_error')) from None
            response = await self.raw(request)
            try:
                if accounting is not None:
                    accounting.after_request(request.method, str(request.url), response.status_code)
                encoding = response.headers.get('content-encoding', 'identity').lower().strip()
                if encoding != 'identity':
                    raise ToolError('source_error', 'unsupported_content_encoding')
                if response.status_code in {301, 302, 303, 307, 308}:
                    location = response.headers.get('location')
                    if not location:
                        raise ToolError('source_error', 'Redirect missing destination')
                    if budget.redirects_used >= budget.limits.redirects:
                        raise ToolError('resource_limit', 'Redirect budget reached')
                    budget.redirects_used += 1
                    destination = urljoin(str(request.url), location)
                    await self.guard.authorize(destination, self.context)
                    if request.method == 'POST':
                        raise ToolError('permission_denied', 'Native query redirects are unavailable')
                    headers = dict(request.headers)
                    if normalized(destination)[1] != normalized(str(request.url))[1]:
                        safe = {'accept', 'accept-language', 'user-agent', 'accept-encoding'}
                        headers = {key: value for key, value in headers.items() if key.lower() in safe}
                    for header in ('authorization', 'cookie', 'host'):
                        headers.pop(header, None)
                    request = httpx.Request(request.method, destination, headers=headers)
                    continue
                length = response.headers.get('content-length')
                if length and length.isdigit() and int(length) > budget.limits.response_bytes:
                    raise ToolError('resource_limit', 'Response byte cap reached')
                data = bytearray()
                if response.is_stream_consumed:
                    chunks = [response.content]
                    for chunk in chunks:
                        if len(data) + len(chunk) > budget.limits.response_bytes:
                            raise ToolError('resource_limit', 'Response byte cap reached')
                        data.extend(chunk)
                else:
                    async for chunk in response.aiter_raw(chunk_size=65536):
                        if len(data) + len(chunk) > budget.limits.response_bytes:
                            raise ToolError('resource_limit', 'Response byte cap reached')
                        data.extend(chunk)
                return httpx.Response(response.status_code, headers=response.headers,
                    content=bytes(data), request=request)
            finally:
                await response.aclose()
        raise ToolError('resource_limit', 'Redirect budget reached')

    async def aclose(self):
        for pool in self.pools.values():
            await pool.aclose()
