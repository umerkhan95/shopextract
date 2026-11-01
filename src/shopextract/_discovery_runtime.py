"""Operation-owned, bounded public sitemap discovery. No browser network."""
from __future__ import annotations
import asyncio
from contextlib import asynccontextmanager
import json
import os
import signal
import sys
from urllib.parse import urljoin, urlsplit, urldefrag
from urllib.robotparser import RobotFileParser
import httpx


class DiscoveryURLs(list):
    def __init__(self, values=(), *, reasons=(), request_count=0):
        super().__init__(values)
        self.reasons = list(dict.fromkeys(['discovery_coverage_unverified', *reasons]))
        self.request_count = request_count


class DiscoveryClient:
    """Borrowed client; all requests use manual same-origin redirects and robots."""
    def __init__(self, client, *, max_requests=16, response_bytes=10*1024*1024):
        self.client = client
        self.max_requests = max_requests
        self.response_bytes = response_bytes
        self.request_count = 0
        self.reasons = []
        self.origin = None
        self.robots = {}
        self.robot_responses = {}

    def __getattr__(self, name):
        return getattr(self.client, name)

    def note(self, code):
        if code not in self.reasons:
            self.reasons.append(code)

    def check_origin(self, url):
        parts = urlsplit(str(url))
        origin = (parts.scheme.lower(), parts.hostname, parts.port or (443 if parts.scheme=='https' else 80))
        if parts.scheme not in ('http','https') or not parts.hostname or parts.username or parts.password or len(str(url))>2048:
            self.note('discovery_origin_denied')
            return False
        if self.origin is None:
            self.origin = origin
        if origin != self.origin:
            self.note('discovery_origin_denied')
            return False
        return True

    async def _read(self, url, *, limit, headers=None):
        if self.request_count >= self.max_requests:
            self.note('discovery_request_budget')
            raise httpx.RequestError('Discovery request budget exhausted')
        self.request_count += 1
        async with self.client.stream('GET', url, follow_redirects=False,
                headers={**(headers or {}), 'User-Agent':'ShopExtract/0.1.2'}) as response:
            body = bytearray()
            async for chunk in response.aiter_bytes():
                if len(body)+len(chunk)>limit:
                    self.note('discovery_response_budget')
                    raise httpx.RequestError('Discovery response byte budget exhausted')
                body.extend(chunk)
            # aiter_bytes already decoded transport content. Preserve the remaining
            # header multiplicity without asking HTTPX to decode these bytes again.
            headers=response.headers.copy()
            headers.pop('content-encoding',None)
            headers.pop('content-length',None)
            return httpx.Response(response.status_code, headers=headers,
                                  content=bytes(body), request=response.request)

    async def allowed(self, url):
        if not self.check_origin(url):
            return False
        parts = urlsplit(str(url))
        origin = f'{parts.scheme}://{parts.netloc}'
        if origin not in self.robots:
            # Set fail-closed before request; no recursion and no repeated retries.
            self.robots[origin] = False
            try:
                response = await self._read(origin+'/robots.txt', limit=min(self.response_bytes,256*1024))
                self.robot_responses[origin]=response
                if response.status_code == 404:
                    self.robots[origin] = True
                elif 200 <= response.status_code < 300:
                    parser = RobotFileParser()
                    parser.parse(response.text.splitlines())
                    for entry in [*parser.entries,*([parser.default_entry] if parser.default_entry else [])]:
                        entry.rulelines.sort(key=lambda rule:(len(rule.path.encode('utf-8')),rule.allowance),reverse=True)
                    self.robots[origin] = parser
                elif response.status_code not in (401,403):
                    self.note('robots_unavailable')
            except (httpx.HTTPError, ValueError):
                self.note('robots_unavailable')
        policy = self.robots[origin]
        allowed = policy if isinstance(policy,bool) else policy.can_fetch('ShopExtract',str(url))
        if not allowed:
            # A fail-closed default is not a robots rule; report it as unavailable.
            self.note('robots_disallowed' if isinstance(policy,RobotFileParser) else 'robots_unavailable')
        return allowed

    async def request(self, method, url, **kwargs):
        if method.upper() != 'GET':
            raise httpx.RequestError('Discovery only supports public GET')
        if kwargs.get('params'):
            url = str(httpx.URL(url, params=kwargs['params']))
        for _ in range(6):
            if not await self.allowed(url):
                raise httpx.RequestError('Discovery policy denied URL')
            response = await self._read(url, limit=self.response_bytes, headers=kwargs.get('headers'))
            if response.status_code not in (301,302,303,307,308):
                return response
            location=response.headers.get('location')
            if not location:
                return response
            url=urljoin(str(response.url),location)
        self.note('discovery_redirect_budget')
        raise httpx.RequestError('Discovery redirect budget exhausted')

    @asynccontextmanager
    async def stream(self, method, url, **kwargs):
        # Native main sitemap traversal borrows this same accounting/policy.
        parts=urlsplit(str(url));origin=f'{parts.scheme}://{parts.netloc}'
        if parts.path=='/robots.txt':
            await self.allowed(origin+'/')
            response=self.robot_responses.get(origin)
            if response is None:raise httpx.RequestError('Robots source unavailable')
        else:
            if method.upper()!='GET' or not await self.allowed(url):
                raise httpx.RequestError('Discovery policy denied URL')
            # Caller owns per-hop redirect accounting; one stream is one send.
            response=await self._read(url,limit=self.response_bytes,headers=kwargs.get('headers'))
        yield response

    async def get(self, url, **kwargs):
        return await self.request('GET',url,**kwargs)


async def bounded_sitemaps(base_url, platform, client, max_urls=1000):
    from ._filters import PLATFORM_PRODUCT_SITEMAPS, is_non_product_url
    from defusedxml import ElementTree
    paths=PLATFORM_PRODUCT_SITEMAPS.get(platform.value,[])
    pending=[urljoin(base_url+'/',p) for p in paths]
    root_url=urljoin(base_url+'/', '/sitemap.xml')
    pending.append(root_url)
    seen=set(); found=set(); locations=0
    while pending and len(found)<max_urls:
        target=pending.pop(0)
        if target==root_url and paths and found:
            break
        if target in seen:
            continue
        seen.add(target)
        try:
            response=await client.get(target)
            if response.status_code!=200:
                continue
            root=ElementTree.fromstring(response.content)
        except Exception:
            if client.request_count>=client.max_requests:
                break
            continue
        is_index=root.tag.rsplit('}',1)[-1]=='sitemapindex'
        for element in root.iter():
            if element.tag.rsplit('}',1)[-1]!='loc' or not element.text:
                continue
            locations+=1
            if locations>5000:
                client.note('discovery_location_budget')
                return sorted(found)
            candidate=urldefrag(urljoin(str(response.url),element.text.strip()))[0]
            if not await client.allowed(candidate):
                continue
            if is_index:
                if candidate not in seen and candidate not in pending:
                    pending.append(candidate)
            elif not is_non_product_url(candidate):
                found.add(candidate)
                if len(found)>=max_urls:
                    client.note('discovery_url_budget')
                    break
    return sorted(found)


async def run_discovery_worker(payload, *, command=None):
    """One process group; incremental bounded drains, cleanup even on cancellation."""
    proc = await asyncio.create_subprocess_exec(*(command or [sys.executable,'-m','shopextract._discovery_worker']),
        stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE, start_new_session=True)
    async def stop():
        # Kill the group even if its leader has exited; no orphaned descendants.
        try:os.killpg(proc.pid,signal.SIGTERM)
        except ProcessLookupError:pass
        try:await asyncio.wait_for(proc.wait(),1.5)
        except asyncio.TimeoutError:
            try:os.killpg(proc.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            await asyncio.wait_for(proc.wait(),.5)
        # A reaped leader does not prove its descendants honored TERM.
        try:os.killpg(proc.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    async def read(stream,cap):
        body=bytearray()
        while True:
            chunk=await stream.read(16384)
            if not chunk:return bytes(body)
            if len(body)+len(chunk)>cap:raise ValueError('Worker stream budget')
            body.extend(chunk)
    readers=[asyncio.create_task(read(proc.stdout,4*1024*1024)),asyncio.create_task(read(proc.stderr,64*1024))]
    try:
        proc.stdin.write(json.dumps(payload,allow_nan=False).encode())
        await proc.stdin.drain();proc.stdin.close()
        async def finish():
            out,err=await asyncio.gather(*readers)
            await proc.wait()
            return out,err
        out,err=await asyncio.wait_for(finish(),min(float(payload.get('timeout',30)),30))
        if err:
            sys.stderr.write(err.decode('utf-8','replace'))
        value=json.loads(out)
        urls=value['urls'];reasons=value['reasons'];count=value['request_count']
        if proc.returncode or not isinstance(urls,list) or len(urls)>1000 or any(not isinstance(u,str) or len(u)>2048 for u in urls):
            raise ValueError('Invalid worker URLs')
        if not isinstance(reasons,list) or len(reasons)>64 or any(not isinstance(r,str) or len(r)>128 for r in reasons) or type(count) is not int or not 0<=count<=16:
            raise ValueError('Invalid worker metadata')
        return DiscoveryURLs(sorted(set(urls)),reasons=reasons,request_count=count)
    except asyncio.TimeoutError:
        return DiscoveryURLs(reasons=['discovery_timeout'])
    except (ValueError,KeyError,TypeError,UnicodeError,BrokenPipeError):
        return DiscoveryURLs(reasons=['discovery_worker_protocol'])
    finally:
        await stop()
        for reader in readers:
            if not reader.done():reader.cancel()
        await asyncio.gather(*readers,return_exceptions=True)
