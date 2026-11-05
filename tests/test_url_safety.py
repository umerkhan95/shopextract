"""T3 URL policy and direct-transport acceptance checks."""
from __future__ import annotations

import asyncio
import socket

import httpx
import pytest


@pytest.mark.parametrize("url", [
    "http://127.0.0.1/",
    "http://10.1.2.3/",
    "http://169.254.169.254/latest/meta-data/",
    "http://[::1]/",
    "http://[fe80::1]/",
    "http://224.0.0.1/",
    "http://[ff02::1]/",
    "http://240.0.0.1/",
    "http://[2001:db8::1]/",
    "http://[::ffff:127.0.0.1]/",
])
@pytest.mark.asyncio
async def test_validate_url_target_rejects_non_public_literal_addresses(url):
    from shopextract._url_safety import UnsafeURLTarget, validate_url_target

    with pytest.raises(UnsafeURLTarget):
        await validate_url_target(url)


@pytest.mark.asyncio
async def test_validate_url_target_rejects_mixed_dns_answers(monkeypatch):
    from shopextract._url_safety import UnsafeURLTarget, validate_url_target

    loop = asyncio.get_running_loop()

    async def mixed(host, port, *args, **kwargs):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", port)),
        ]

    monkeypatch.setattr(loop, "getaddrinfo", mixed)
    with pytest.raises(UnsafeURLTarget):
        await validate_url_target("https://mixed.invalid/product")


@pytest.mark.asyncio
async def test_validate_url_target_allows_private_only_with_operator_flag():
    from shopextract._url_safety import validate_url_target

    await validate_url_target("http://127.0.0.1:8888/health", allow_private=True)


@pytest.mark.asyncio
async def test_guarded_async_client_never_sends_private_target_to_wire():
    from shopextract._url_safety import UnsafeURLTarget, async_client

    seen = []

    async def resolver(host, port, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", port))]

    wire = httpx.MockTransport(lambda request: (seen.append(request) or httpx.Response(200)))
    async with async_client(resolver=resolver, wire_transport=wire) as client:
        with pytest.raises(UnsafeURLTarget):
            await client.get("https://private.invalid/secret")
    assert seen == []


def test_guarded_client_factory_rejects_real_or_custom_wire_transport():
    from shopextract._url_safety import UnguardedHTTPClient, async_client

    with pytest.raises(UnguardedHTTPClient):
        async_client(wire_transport=httpx.AsyncHTTPTransport())

    class CustomTransport(httpx.AsyncBaseTransport):
        async def handle_async_request(self, request):
            raise AssertionError("custom transport must be rejected before request")

    with pytest.raises(UnguardedHTTPClient):
        async_client(wire_transport=CustomTransport())


@pytest.mark.asyncio
async def test_exact_mock_wire_transport_validates_then_dispatches_without_network():
    from shopextract._url_safety import async_client

    seen = []

    async def resolver(host, port, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]

    wire = httpx.MockTransport(lambda request: (seen.append(request) or httpx.Response(200)))
    async with async_client(resolver=resolver, wire_transport=wire) as client:
        response = await client.get("https://public.invalid/resource")
    assert response.status_code == 200
    assert len(seen) == 1 and seen[0].url.host == "public.invalid"


@pytest.mark.asyncio
async def test_guarded_async_client_rechecks_each_redirect_before_wire():
    from shopextract._url_safety import UnsafeURLTarget, async_client

    seen = []

    async def resolver(host, port, *args, **kwargs):
        if host == "public.invalid":
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", port))]

    def handle(request):
        seen.append(str(request.url))
        return httpx.Response(302, headers={"Location": "http://private.invalid/secret"})

    async with async_client(
        resolver=resolver,
        wire_transport=httpx.MockTransport(handle),
        follow_redirects=True,
    ) as client:
        with pytest.raises(UnsafeURLTarget):
            await client.get("https://public.invalid/start")
    assert seen == ["https://public.invalid/start"]


@pytest.mark.asyncio
async def test_guarded_async_client_connects_to_validated_numeric_address(monkeypatch):
    from shopextract._url_safety import async_client

    connections = []

    async def resolver(host, port, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]

    # Inject the lowest network backend seam; the request host remains public.invalid
    # for HTTP Host and TLS SNI while the socket destination is numeric.
    from shopextract import _url_safety
    backend_type = getattr(_url_safety, "PinnedNetworkBackend", None)
    assert backend_type is not None, "direct HTTP backend must expose testable pinning seam"
    sentinel = object()

    async def connect(host, port, **kwargs):
        connections.append((host, port))
        return sentinel

    backend = backend_type(resolver=resolver, connect=connect)
    stream = await backend.connect_tcp("public.invalid", 443)
    assert stream is sentinel
    assert connections == [("93.184.216.34", 443)]


@pytest.mark.asyncio
async def test_guarded_http_client_uses_pinned_backend_for_local_opt_in(monkeypatch):
    import os
    from shopextract._url_safety import async_client

    monkeypatch.setenv("SHOPEXTRACT_ALLOW_PRIVATE_URLS", "1")
    requests = []

    async def serve(reader, writer):
        request = await reader.readuntil(b"\r\n\r\n")
        requests.append(request.split(b"\r\n", 1)[0])
        writer.write(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nok")
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(serve, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    try:
        async with async_client(timeout=2) as client:
            response = await client.get(f"http://127.0.0.1:{port}/controlled")
        assert response.status_code == 200 and response.text == "ok"
        assert requests == [b"GET /controlled HTTP/1.1"]
    finally:
        server.close()
        await server.wait_closed()


@pytest.mark.asyncio
async def test_local_validating_proxy_rejects_private_connect_before_dial():
    from shopextract._url_safety import ValidatingProxy

    dials = []

    async def connect(host, port, **kwargs):
        dials.append((host, port))
        raise AssertionError("blocked target reached connector")

    async with ValidatingProxy(connect=connect) as proxy:
        reader, writer = await asyncio.open_connection(proxy.host, proxy.port)
        writer.write(b"CONNECT 127.0.0.1:443 HTTP/1.1\r\nHost: 127.0.0.1:443\r\n\r\n")
        await writer.drain()
        response = await reader.readuntil(b"\r\n\r\n")
        writer.close()
        await writer.wait_closed()
    assert response.startswith(b"HTTP/1.1 403")
    assert dials == []


@pytest.mark.asyncio
async def test_local_validating_proxy_routes_crawl4ai_config_through_proxy():
    from shopextract._url_safety import ValidatingProxy
    from shopextract.extractors._browser import get_browser_config, get_crawl_config

    async with ValidatingProxy() as proxy:
        browser = get_browser_config()
        run = get_crawl_config(proxy_config=proxy.crawl4ai_config)
        assert run.proxy_config.server == proxy.url
        assert "--proxy-bypass-list=<-loopback>" in browser.extra_args


@pytest.mark.asyncio
async def test_local_validating_proxy_rejects_private_http_without_dial():
    from shopextract._url_safety import ValidatingProxy

    dials = []

    async def connect(host, port):
        dials.append((host, port))
        raise AssertionError("blocked target reached connector")

    async with ValidatingProxy(connect=connect) as proxy:
        reader, writer = await asyncio.open_connection(proxy.host, proxy.port)
        writer.write(b"GET http://127.0.0.1:80/private HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")
        await writer.drain()
        response = await reader.read()
        writer.close()
        await writer.wait_closed()
    assert response.startswith(b"HTTP/1.1 403")
    assert dials == []


@pytest.mark.asyncio
async def test_local_validating_proxy_pins_public_dns_and_preserves_connect_tunnel():
    import ssl
    from shopextract._url_safety import ValidatingProxy

    upstream_bytes = bytearray()

    async def upstream(reader, writer):
        data = await reader.read(4096)
        upstream_bytes.extend(data)
        writer.write(data)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    upstream_server = await asyncio.start_server(upstream, "127.0.0.1", 0)
    upstream_port = upstream_server.sockets[0].getsockname()[1]
    dials = []

    async def resolve(host, port):
        assert host == "shop.invalid"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]

    async def connect(host, port):
        dials.append((host, port))
        return await asyncio.open_connection("127.0.0.1", upstream_port)

    proxy = ValidatingProxy(resolver=resolve, connect=connect)
    try:
        async with proxy:
            reader, writer = await asyncio.open_connection(proxy.host, proxy.port)
            writer.write(b"CONNECT shop.invalid:443 HTTP/1.1\r\nHost: shop.invalid:443\r\n\r\n")
            await writer.drain()
            assert await reader.readuntil(b"\r\n\r\n") == b"HTTP/1.1 200 Connection Established\r\n\r\n"

            client_context = ssl.create_default_context()
            incoming = ssl.MemoryBIO()
            outgoing = ssl.MemoryBIO()
            tls = client_context.wrap_bio(incoming, outgoing, server_side=False,
                                          server_hostname="shop.invalid")
            with pytest.raises(ssl.SSLWantReadError):
                tls.do_handshake()
            client_hello = outgoing.read()
            writer.write(client_hello)
            await writer.drain()
            echoed = await reader.readexactly(len(client_hello))
            assert echoed == client_hello
            writer.close()
            await writer.wait_closed()
        assert dials == [("93.184.216.34", 443)]
        assert bytes(upstream_bytes) == client_hello
        assert proxy.events[0]["connected_address"] == "93.184.216.34"
    finally:
        upstream_server.close()
        await upstream_server.wait_closed()


@pytest.mark.asyncio
async def test_validating_proxy_forwards_websocket_upgrade_through_pinned_upstream():
    from shopextract._url_safety import ValidatingProxy

    received = []

    async def upstream(reader, writer):
        headers = await reader.readuntil(b"\r\n\r\n")
        received.append(headers)
        writer.write(b"HTTP/1.1 101 Switching Protocols\r\nConnection: Upgrade\r\nUpgrade: websocket\r\n\r\n")
        await writer.drain()
        payload = await reader.read(64)
        received.append(payload)
        writer.write(payload)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    upstream_server = await asyncio.start_server(upstream, "127.0.0.1", 0)
    upstream_port = upstream_server.sockets[0].getsockname()[1]
    dials = []

    async def resolve(host, port):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]

    async def connect(host, port):
        dials.append((host, port))
        return await asyncio.open_connection("127.0.0.1", upstream_port)

    try:
        async with ValidatingProxy(resolver=resolve, connect=connect) as proxy:
            reader, writer = await asyncio.open_connection(proxy.host, proxy.port)
            writer.write(b"GET ws://shop.invalid/socket HTTP/1.1\r\nHost: shop.invalid\r\n"
                         b"Connection: Upgrade\r\nUpgrade: websocket\r\n\r\n")
            await writer.drain()
            response = await reader.readuntil(b"\r\n\r\n")
            assert response.startswith(b"HTTP/1.1 101")
            writer.write(b"\x81\x02ok")
            await writer.drain()
            assert await reader.readexactly(4) == b"\x81\x02ok"
            writer.close()
            await writer.wait_closed()
        assert dials == [("93.184.216.34", 80)]
        assert received[0].startswith(b"GET /socket HTTP/1.1\r\n")
        assert b"Connection: Upgrade\r\n" in received[0]
        assert received[1] == b"\x81\x02ok"
    finally:
        upstream_server.close()
        await upstream_server.wait_closed()

@pytest.mark.asyncio
@pytest.mark.parametrize("surface", ["detect", "discover", "unified", "images", "storefront", "listings"])
async def test_production_injected_httpx_client_is_rejected_before_wire(surface):
    from shopextract._url_safety import UnguardedHTTPClient
    async with httpx.AsyncClient() as unguarded:
        with pytest.raises(UnguardedHTTPClient):
            if surface == "detect":
                from shopextract._detect import detect
                await detect("http://127.0.0.1/", client=unguarded)
            elif surface == "discover":
                from shopextract._discover import discover
                await discover("http://127.0.0.1/", client=unguarded)
            elif surface == "unified":
                from shopextract.extractors.unified import UnifiedCrawlExtractor
                UnifiedCrawlExtractor(http_client=unguarded)
            elif surface == "images":
                from shopextract.validate.images import check_images
                await check_images([{"image_url": "http://127.0.0.1/image.jpg"}], client=unguarded)
            elif surface == "storefront":
                from shopextract.extractors._storefront import storefront_client
                async with storefront_client(unguarded, 1):
                    pass
            else:
                from shopextract.categories.listings import build_listing_index
                await build_listing_index(
                    ["https://shop.example.test/category"],
                    "https://shop.example.test/",
                    client=unguarded,
                )


@pytest.mark.asyncio
async def test_deterministic_mock_transport_injection_remains_supported():
    from shopextract._url_safety import require_guarded_client, validate_client_url

    client = httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, request=request)
    ))
    try:
        assert require_guarded_client(client) is client
        await validate_client_url("http://127.0.0.1/private-test-only", client)
        response = await client.get("https://shop.example.test/")
        assert response.status_code == 200
    finally:
        await client.aclose()


@pytest.mark.asyncio
async def test_duck_typed_injected_client_is_rejected_before_request():
    from shopextract._detect import detect
    from shopextract._url_safety import UnguardedHTTPClient

    class DuckClient:
        def __init__(self):
            self.calls = 0

        async def head(self, *args, **kwargs):
            self.calls += 1
            raise AssertionError("unguarded test client must not receive a request")

        async def get(self, *args, **kwargs):
            self.calls += 1
            raise AssertionError("unguarded test client must not receive a request")

    client = DuckClient()
    with pytest.raises(UnguardedHTTPClient):
        await detect("https://shop.example.test/", client=client)
    assert client.calls == 0


@pytest.mark.asyncio
async def test_spoofed_guard_marker_does_not_trust_default_httpx_transport():
    from shopextract._detect import detect
    from shopextract._url_safety import UnguardedHTTPClient

    async with httpx.AsyncClient() as client:
        client._shopextract_url_guarded = True
        with pytest.raises(UnguardedHTTPClient):
            await detect("https://shop.example.test/", client=client)


@pytest.mark.asyncio
async def test_spoofed_discovery_wrapper_cannot_delegate_to_unsafe_client():
    from shopextract._detect import detect
    from shopextract._url_safety import UnguardedHTTPClient

    class CountingTransport(httpx.AsyncBaseTransport):
        def __init__(self):
            self.calls = 0

        async def handle_async_request(self, request):
            self.calls += 1
            return httpx.Response(200, request=request)

    unsafe_transport = CountingTransport()
    unsafe_client = httpx.AsyncClient(transport=unsafe_transport)
    trusted_client = httpx.AsyncClient(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, request=request)
    ))
    # Spoof both DiscoveryClient identity attributes and expose a guarded-looking
    # .client while forwarding actual methods to an unguarded client.
    SpoofedDiscoveryClient = type(
        "DiscoveryClient",
        (),
        {
            "__module__": "shopextract._discovery_runtime",
            "client": trusted_client,
            "__getattr__": lambda self, name: getattr(unsafe_client, name),
        },
    )
    try:
        with pytest.raises(UnguardedHTTPClient):
            await detect("https://shop.example.test/", client=SpoofedDiscoveryClient())
        assert unsafe_transport.calls == 0
    finally:
        await unsafe_client.aclose()
        await trusted_client.aclose()
