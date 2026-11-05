"""URL destination validation and pinned transports for user supplied URLs.

The policy rejects non-global addresses on every DNS lookup. Direct HTTP
connections repeat that validation at socket creation and dial a numeric IP so
the TLS connection still uses the original request host for SNI and Host.
"""
from __future__ import annotations

import asyncio
import ipaddress
import os
import socket
import ssl
from contextlib import suppress
from urllib.parse import urlsplit

import httpcore
import httpx


class UnsafeURLTarget(ValueError):
    """A URL is invalid or resolves to an address outside the public internet."""


class UnguardedHTTPClient(UnsafeURLTarget):
    """An injected HTTPX client has no ShopExtract URL guard."""


def _unwrap_discovery_client(candidate):
    # Import lazily because discovery imports this module for its own clients.
    from ._discovery_runtime import DiscoveryClient

    if type(candidate) is DiscoveryClient:
        return candidate.client
    return candidate


def require_guarded_client(client):
    """Reject injected clients that can perform unpinned network I/O.

    Only a client whose actual transport is exactly GuardedHTTPXTransport, or
    the exact HTTPX MockTransport, is accepted. MockTransport is an explicitly
    trusted, no-wire seam for programmatic callers writing deterministic tests;
    it does not guard real networking and isn't exposed through CLI/MCP input.
    """
    candidate = _unwrap_discovery_client(client)
    if isinstance(candidate, httpx.AsyncClient):
        if type(candidate._transport) is GuardedHTTPXTransport:
            return client
        if type(candidate._transport) is httpx.MockTransport:
            return client
    raise UnguardedHTTPClient(
        "Injected clients must use shopextract._url_safety.async_client; "
        "only its guarded transport or exact HTTPX MockTransport test seam is accepted"
    )


async def validate_client_url(url: str, client):
    """Validate a request URL, using lexical-only checks for no-wire mocks."""
    require_guarded_client(client)
    candidate = _unwrap_discovery_client(client)
    if (isinstance(candidate, httpx.AsyncClient)
            and type(candidate._transport) is httpx.MockTransport):
        _parse_url(url)
        return
    await validate_url_target(url, allow_private=operator_allows_private_urls())


def operator_allows_private_urls() -> bool:
    """Return whether the operator explicitly enabled local development URLs."""
    return os.environ.get("SHOPEXTRACT_ALLOW_PRIVATE_URLS") == "1"


def _parse_url(url: str) -> tuple[str, int]:
    try:
        parts = urlsplit(url)
        if parts.scheme.lower() not in {"http", "https"}:
            raise ValueError("only HTTP and HTTPS URLs are supported")
        if not parts.hostname or parts.username is not None or parts.password is not None:
            raise ValueError("URL must include a host and must not include credentials")
        host = parts.hostname.rstrip(".").encode("idna").decode("ascii").lower()
        if not host or "%" in host or "\\" in url or any(ord(c) < 32 for c in url):
            raise ValueError("invalid URL host")
        port = parts.port or (443 if parts.scheme.lower() == "https" else 80)
        if not 1 <= port <= 65535:
            raise ValueError("invalid URL port")
        return host, port
    except (ValueError, UnicodeError) as exc:
        if isinstance(exc, UnsafeURLTarget):
            raise
        raise UnsafeURLTarget(str(exc)) from None


def _is_public_address(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
        if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
            address = address.ipv4_mapped
        return address.is_global and not (
            address.is_multicast or address.is_reserved or address.is_unspecified
        )
    except ValueError:
        return False


async def _resolve_addresses(
    host: str,
    port: int,
    *,
    allow_private: bool,
    resolver=None,
) -> tuple[str, ...]:
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None:
        values = (address.compressed,)
    else:
        try:
            loop = asyncio.get_running_loop()
            if resolver is None:
                answer = await loop.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            else:
                answer = resolver(host, port)
                if hasattr(answer, "__await__"):
                    answer = await answer
            values = tuple(dict.fromkeys(str(item[4][0]) for item in answer))
        except (OSError, asyncio.TimeoutError) as exc:
            raise UnsafeURLTarget(f"DNS resolution failed for {host}") from exc
    if not values or len(values) > 64:
        raise UnsafeURLTarget("DNS response had no addresses or exceeded the address limit")
    if not allow_private and not all(_is_public_address(item) for item in values):
        raise UnsafeURLTarget("URL resolves to a prohibited address")
    return values


async def validate_url_target(
    url: str,
    *,
    allow_private: bool = False,
) -> None:
    """Reject invalid URLs and any DNS answer that is not a public address."""
    host, port = _parse_url(url)
    await _resolve_addresses(host, port, allow_private=allow_private)


class PinnedNetworkBackend(httpcore.AsyncNetworkBackend):
    """HTTPCore backend that validates all answers and dials a chosen IP."""

    def __init__(self, *, resolver=None, connect=None, allow_private: bool = False):
        self._resolver = resolver
        self._connect = connect
        self._allow_private = allow_private
        self._backend = httpcore.AnyIOBackend()

    async def connect_tcp(
        self,
        host,
        port,
        timeout=None,
        local_address=None,
        socket_options=None,
    ):
        addresses = await _resolve_addresses(
            host, port, allow_private=self._allow_private, resolver=self._resolver
        )
        connector = self._connect or self._backend.connect_tcp
        last_error = None
        for address in addresses:
            try:
                return await connector(
                    address,
                    port,
                    timeout=timeout,
                    local_address=local_address,
                    socket_options=socket_options,
                )
            except (OSError, httpcore.NetworkError) as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        raise httpcore.ConnectError("No validated address was available")

    async def connect_unix_socket(self, *args, **kwargs):
        raise UnsafeURLTarget("Unix sockets are not valid HTTP URL destinations")

    async def sleep(self, seconds):
        await asyncio.sleep(seconds)


class _CoreByteStream(httpx.AsyncByteStream):
    def __init__(self, stream):
        self._stream = stream

    async def __aiter__(self):
        async for chunk in self._stream:
            yield chunk

    async def aclose(self):
        await self._stream.aclose()


class GuardedHTTPXTransport(httpx.AsyncBaseTransport):
    """Validate each request and pin each real socket made by HTTPX."""

    def __init__(self, *, resolver=None, wire_transport=None, allow_private=False):
        if wire_transport is not None and type(wire_transport) is not httpx.MockTransport:
            raise UnguardedHTTPClient(
                "wire_transport is reserved for exact HTTPX MockTransport test seams"
            )
        self._resolver = resolver
        self._wire = wire_transport
        self._allow_private = allow_private
        self._pools = {}

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        host, port = _parse_url(str(request.url))
        await _resolve_addresses(
            host,
            port,
            allow_private=self._allow_private,
            resolver=self._resolver,
        )
        if self._wire is not None:
            return await self._wire.handle_async_request(request)

        scheme = request.url.scheme
        pool = self._pools.get(scheme)
        if pool is None:
            pool = httpcore.AsyncConnectionPool(
                ssl_context=ssl.create_default_context(),
                max_connections=20,
                max_keepalive_connections=10,
                retries=0,
                network_backend=PinnedNetworkBackend(
                    resolver=self._resolver,
                    allow_private=self._allow_private,
                ),
            )
            self._pools[scheme] = pool
        response = await pool.handle_async_request(
            httpcore.Request(
                method=request.method,
                url=httpcore.URL(
                    scheme=request.url.raw_scheme,
                    host=request.url.raw_host,
                    port=request.url.port,
                    target=request.url.raw_path,
                ),
                headers=request.headers.raw,
                content=request.stream,
                extensions=request.extensions,
            )
        )
        return httpx.Response(
            response.status,
            headers=response.headers,
            stream=_CoreByteStream(response.stream),
            extensions=response.extensions,
        )

    async def aclose(self):
        for pool in self._pools.values():
            await pool.aclose()
        if self._wire is not None:
            await self._wire.aclose()


class ValidatingProxy:
    """Operation-scoped HTTP proxy that validates and pins each upstream.

    HTTPS uses CONNECT tunneling: TLS terminates in the browser, so the original
    origin hostname remains its SNI and certificate-verification name. This
    proxy does not itself prevent the browser process from opening other sockets;
    callers must provide an OS/network egress sandbox for that stronger guarantee.
    """

    def __init__(self, *, resolver=None, connect=None, host="127.0.0.1"):
        self._resolver = resolver
        self._connect = connect
        self.host = host
        self.port = 0
        self._server: asyncio.AbstractServer | None = None
        self.events: list[dict[str, object]] = []
        self._allow_private = operator_allows_private_urls()

    @property
    def url(self) -> str:
        if not self.port:
            raise RuntimeError("proxy has not been started")
        return f"http://{self.host}:{self.port}"

    @property
    def crawl4ai_config(self):
        from crawl4ai import ProxyConfig

        return ProxyConfig(server=self.url)

    async def start(self):
        if self._server is None:
            self._server = await asyncio.start_server(
                self._handle, self.host, 0, limit=65536
            )
            self.port = int(self._server.sockets[0].getsockname()[1])
        return self

    async def close(self):
        if self._server is not None:
            self._server.close()
            await self._server.wait_closed()
            self._server = None
            self.port = 0

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def _connect_upstream(self, address: str, port: int):
        connector = self._connect or asyncio.open_connection
        return await connector(address, port)

    @staticmethod
    def _target_host_port(authority: str, default_port: int):
        parsed = urlsplit("//" + authority)
        if not parsed.hostname or parsed.username is not None or parsed.password is not None:
            raise UnsafeURLTarget("invalid proxy authority")
        try:
            host = parsed.hostname.rstrip(".").encode("idna").decode("ascii").lower()
            port = parsed.port or default_port
        except (ValueError, UnicodeError):
            raise UnsafeURLTarget("invalid proxy authority") from None
        if not host or not 1 <= port <= 65535:
            raise UnsafeURLTarget("invalid proxy authority")
        return host, port

    async def _handle(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        upstream_writer = None
        try:
            request_line = await asyncio.wait_for(reader.readline(), 10)
            if not request_line or len(request_line) > 8192:
                return
            parts = request_line.decode("latin-1").strip().split(" ", 2)
            if len(parts) != 3:
                await self._respond(writer, 400, "Bad request")
                return
            method, target, version = parts
            headers = []
            total = len(request_line)
            while True:
                line = await asyncio.wait_for(reader.readline(), 10)
                total += len(line)
                if total > 65536:
                    await self._respond(writer, 431, "Headers too large")
                    return
                if line in (b"\r\n", b"\n", b""):
                    break
                headers.append(line)

            if method.upper() == "CONNECT":
                host, port = self._target_host_port(target, 443)
                scheme = "https"
                path = "/"
            else:
                parts_url = urlsplit(target)
                if not parts_url.scheme or not parts_url.netloc:
                    await self._respond(writer, 400, "Absolute proxy URL required")
                    return
                scheme = parts_url.scheme.lower()
                if scheme in {"ws", "wss"}:
                    host, port = self._target_host_port(
                        parts_url.netloc, 443 if scheme == "wss" else 80
                    )
                    scheme = "https" if scheme == "wss" else "http"
                else:
                    host, port = _parse_url(target)
                path = parts_url.path or "/"
                if parts_url.query:
                    path += "?" + parts_url.query

            try:
                addresses = await _resolve_addresses(
                    host,
                    port,
                    allow_private=self._allow_private,
                    resolver=self._resolver,
                )
            except UnsafeURLTarget:
                self.events.append({"method": method.upper(), "host": host, "port": port,
                                    "blocked": True, "connected_address": None})
                await self._respond(writer, 403, "Destination blocked")
                return

            connected = None
            for address in addresses:
                try:
                    upstream_reader, upstream_writer = await self._connect_upstream(address, port)
                    connected = address
                    break
                except OSError:
                    continue
            if connected is None or upstream_writer is None:
                self.events.append({"method": method.upper(), "host": host, "port": port,
                                    "blocked": False, "connected_address": None})
                await self._respond(writer, 502, "Upstream connection failed")
                return
            self.events.append({"method": method.upper(), "host": host, "port": port,
                                "blocked": False, "connected_address": connected})

            if method.upper() == "CONNECT":
                writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
                await writer.drain()
                await self._tunnel(reader, writer, upstream_reader, upstream_writer)
                return

            upgrade = any(b"upgrade" in line.lower() for line in headers)
            outgoing = [f"{method} {path} {version}\r\n".encode("latin-1")]
            outgoing.extend(line for line in headers
                            if not line.lower().startswith((b"proxy-connection:", b"connection:")))
            outgoing.append(("Connection: Upgrade\r\n" if upgrade else
                             "Connection: close\r\n").encode("ascii"))
            outgoing.append(b"\r\n")
            upstream_writer.writelines(outgoing)
            await upstream_writer.drain()

            header_map = {line.partition(b":")[0].strip().lower():
                          line.partition(b":")[2].strip().lower() for line in headers}
            body_size = int(header_map.get(b"content-length", b"0") or b"0")
            while body_size:
                chunk = await reader.readexactly(min(body_size, 65536))
                upstream_writer.write(chunk)
                body_size -= len(chunk)
            if header_map.get(b"transfer-encoding") == b"chunked":
                while True:
                    line = await reader.readline()
                    upstream_writer.write(line)
                    await upstream_writer.drain()
                    size = int(line.split(b";", 1)[0].strip(), 16)
                    if size == 0:
                        trailer = await reader.readuntil(b"\r\n\r\n")
                        upstream_writer.write(trailer)
                        break
                    chunk = await reader.readexactly(size + 2)
                    upstream_writer.write(chunk)
            await upstream_writer.drain()

            response_head = await asyncio.wait_for(upstream_reader.readuntil(b"\r\n\r\n"), 30)
            writer.write(response_head)
            await writer.drain()
            status_line = response_head.split(b"\r\n", 1)[0]
            if b" 101 " in status_line:
                await self._tunnel(reader, writer, upstream_reader, upstream_writer)
                return
            while True:
                chunk = await upstream_reader.read(65536)
                if not chunk:
                    break
                writer.write(chunk)
                await writer.drain()
        except (asyncio.IncompleteReadError, asyncio.LimitOverrunError, asyncio.TimeoutError,
                ConnectionError, OSError, UnicodeError, ValueError):
            with suppress(ConnectionError, OSError):
                await self._respond(writer, 502, "Proxy request failed")
        finally:
            if upstream_writer is not None:
                upstream_writer.close()
                with suppress(Exception):
                    await upstream_writer.wait_closed()
            writer.close()
            with suppress(Exception):
                await writer.wait_closed()

    @staticmethod
    async def _respond(writer, status, message):
        body = message.encode("utf-8")
        writer.write(
            f"HTTP/1.1 {status} {message}\r\nContent-Length: {len(body)}\r\n"
            "Connection: close\r\n\r\n".encode("ascii") + body
        )
        await writer.drain()

    @staticmethod
    async def _tunnel(client_reader, client_writer, upstream_reader, upstream_writer):
        async def pump(reader, writer):
            while True:
                data = await reader.read(65536)
                if not data:
                    with suppress(Exception):
                        writer.write_eof()
                        await writer.drain()
                    return
                writer.write(data)
                await writer.drain()

        tasks = {
            asyncio.create_task(pump(client_reader, upstream_writer)),
            asyncio.create_task(pump(upstream_reader, client_writer)),
        }
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        await asyncio.gather(*done, *pending, return_exceptions=True)


def async_client(
    *,
    timeout=30.0,
    follow_redirects=False,
    headers=None,
    resolver=None,
    wire_transport=None,
    **kwargs,
) -> httpx.AsyncClient:
    """Build an HTTPX client that validates requests and pins socket DNS.

    ``wire_transport`` is solely a programmatic deterministic-test seam and
    accepts only exact ``httpx.MockTransport``. It is not exposed through CLI
    or MCP inputs and is not a production network protection mechanism.
    """
    transport = GuardedHTTPXTransport(
        resolver=resolver,
        wire_transport=wire_transport,
        allow_private=operator_allows_private_urls(),
    )
    client = httpx.AsyncClient(
        transport=transport,
        timeout=timeout,
        follow_redirects=follow_redirects,
        headers=headers,
        trust_env=False,
        **kwargs,
    )
    return client

