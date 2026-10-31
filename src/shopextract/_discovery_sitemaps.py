"""Bounded native advertised-sitemap discovery, before optional browser seeding."""
from collections import deque
from dataclasses import dataclass
import asyncio
import re
import time
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit
from urllib.robotparser import RobotFileParser

import httpx
from defusedxml import ElementTree as ET
from defusedxml.common import DefusedXmlException

from ._execution import current_state
from ._filters import is_non_product_url

MAX_REQUESTS = 12
MAX_RESPONSE_BYTES = 10 * 1024 * 1024
MAX_TOTAL_BYTES = 20 * 1024 * 1024
MAX_SECONDS = 30.0
USER_AGENT = 'ShopExtract/0.1'
_CATEGORY_MAP = re.compile(r'(?:^|[_-])(?:categor(?:y|ies)|collections?|product_cat)(?:[_\-.]|$)', re.I)


@dataclass(frozen=True)
class SitemapDiscovery:
    urls: tuple[str, ...]
    stop_fallback: bool = False


class _BudgetStop(Exception):
    pass


def _canonical(url):
    try:
        if any(ord(c) < 32 for c in url) or '\\' in url:
            return None
        p = urlsplit(url)
        if p.scheme not in ('http', 'https') or not p.hostname or p.username or p.password:
            return None
        port = p.port or (443 if p.scheme == 'https' else 80)
        path = p.path or '/'
        decoded = path
        for _ in range(3):
            value = unquote(decoded)
            if value == decoded:
                break
            decoded = value
        if unquote(decoded) != decoded or '\\' in decoded or any(x in ('.', '..') for x in decoded.split('/')):
            return None
        host = p.hostname.lower()
        netloc = ('[' + host + ']') if ':' in host else host
        if port != (443 if p.scheme == 'https' else 80):
            netloc += ':' + str(port)
        return urlunsplit((p.scheme, netloc, path, p.query, ''))
    except (ValueError, TypeError):
        return None


def _same_origin(url, base):
    a, b = urlsplit(url), urlsplit(base)
    return (a.scheme, a.netloc) == (b.scheme, b.netloc)


def _in_store(url, base):
    if not _same_origin(url, base):
        return False
    path = unquote(urlsplit(url).path)
    prefix = unquote(urlsplit(base).path).rstrip('/')
    return not prefix or path == prefix or path.startswith(prefix + '/')


def _category_map(url):
    return bool(_CATEGORY_MAP.search(urlsplit(url).path.rsplit('/', 1)[-1]))


def _locations(body):
    root = ET.fromstring(body)
    kind = root.tag.split('}')[-1]
    if kind not in ('sitemapindex', 'urlset'):
        return None, ()
    # Direct child <loc> only: image/video extension locations are not products.
    rows = (node for node in root if node.tag.split('}')[-1] == ('sitemap' if kind == 'sitemapindex' else 'url'))
    locations = tuple(node.text.strip() for row in rows for node in row
                      if node.tag.split('}')[-1] == 'loc' and node.text)
    return kind, locations


async def discover_sitemap_urls(base_url, *, max_urls=100, timeout=30, client=None):
    """Resolve ordered candidates; a caller-provided HTTP client remains open."""
    base = _canonical(base_url)
    if not base:
        return SitemapDiscovery(())
    if max_urls <= 0:
        return SitemapDiscovery((), True)
    state = current_state()
    remaining = min(float(timeout), MAX_SECONDS)
    if state is not None:
        remaining = min(remaining, state.deadline - time.monotonic())
    if remaining <= 0:
        raise asyncio.TimeoutError()
    deadline = time.monotonic() + remaining

    async def resolve(c):
        requests = total = 0
        urls, emitted, visited, excluded = [], set(), set(), set()
        robots = None
        denied_candidate = False
        origin = urlunsplit((*urlsplit(base)[:2], '', '', ''))

        async def fetch(url, *, policy=True):
            nonlocal requests, total
            for redirect in range(3):
                url = _canonical(url)
                if not url or not _same_origin(url, base):
                    return None
                if policy and robots is not None and not robots.can_fetch(USER_AGENT, url):
                    return None
                if requests >= MAX_REQUESTS:
                    raise _BudgetStop()
                left = deadline - time.monotonic()
                if left <= 0:
                    raise asyncio.TimeoutError()
                requests += 1
                async with c.stream('GET', url, follow_redirects=False,
                                    timeout=min(15, left), headers={'User-Agent': USER_AGENT}) as response:
                    if response.status_code in (301, 302, 303, 307, 308):
                        location = response.headers.get('location')
                        if redirect == 2 or not location:
                            return None
                        url = urljoin(url, location)
                        continue
                    if response.status_code != 200:
                        return None
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        total += len(chunk)
                        if len(body) + len(chunk) > MAX_RESPONSE_BYTES or total > MAX_TOTAL_BYTES:
                            raise _BudgetStop()
                        if time.monotonic() >= deadline:
                            raise asyncio.TimeoutError()
                        body.extend(chunk)
                    return bytes(body), url
            return None

        try:
            robot_source = await fetch(origin + '/robots.txt', policy=False)
            roots = []
            if robot_source is not None:
                robots = RobotFileParser()
                robots.parse(robot_source[0].decode('utf-8', errors='replace').splitlines())
                # stdlib uses the first matching rule. Order literal rules by
                # specificity, with Allow winning ties (RFC 9309 section 2.2.2).
                entries = [*robots.entries, *([robots.default_entry] if robots.default_entry else [])]
                for entry in entries:
                    entry.rulelines.sort(key=lambda rule: (len(rule.path.encode('utf-8')), rule.allowance), reverse=True)
                if not robots.can_fetch(USER_AGENT, base):
                    return SitemapDiscovery((), True)
                roots = robots.site_maps() or []
            if not roots:
                roots = [base.rstrip('/') + '/sitemap.xml']
            roots = [u for value in roots if (u := _canonical(urljoin(origin + '/', value))) and _same_origin(u, base)]
            queue = deque(sorted(roots, key=lambda u: not _category_map(u)))
            allowed_source = False
            while queue and len(urls) < max_urls:
                url = queue.popleft()
                if url in visited:
                    continue
                visited.add(url)
                if robots is not None and not robots.can_fetch(USER_AGENT, url):
                    continue
                allowed_source = True
                try:
                    source = await fetch(url)
                    if source is None:
                        continue
                    body, final_url = source
                    kind, locations = _locations(body)
                except (httpx.HTTPError, ET.ParseError, DefusedXmlException, UnicodeError):
                    continue
                if kind == 'sitemapindex':
                    children = [u for value in locations if (u := _canonical(urljoin(final_url, value))) and _same_origin(u, base)]
                    for child in reversed(sorted(children, key=lambda u: not _category_map(u))):
                        queue.appendleft(child)
                    continue
                if kind != 'urlset':
                    continue
                candidates = [u for value in locations if (u := _canonical(urljoin(final_url, value))) and _in_store(u, base)]
                if _category_map(url) or _category_map(final_url):
                    excluded.update(candidates)
                    # A later category map can revoke an earlier ambiguous candidate.
                    urls[:] = [u for u in urls if u not in excluded]
                    emitted.difference_update(excluded)
                    continue
                for candidate in candidates:
                    if candidate in emitted or candidate in excluded or is_non_product_url(candidate):
                        continue
                    if robots is not None and not robots.can_fetch(USER_AGENT, candidate):
                        denied_candidate = True
                        continue
                    urls.append(candidate)
                    emitted.add(candidate)
                    if len(urls) == max_urls:
                        break
            return SitemapDiscovery(tuple(urls), bool(robots is not None and ((roots and not allowed_source) or (denied_candidate and not urls))))
        except _BudgetStop:
            if state is not None:
                state.warnings.append('Native sitemap discovery resource limit reached')
            return SitemapDiscovery(tuple(urls), True)
        except httpx.HTTPError:
            return SitemapDiscovery(())

    async def operation():
        if client is not None:
            return await resolve(client)
        async with httpx.AsyncClient(follow_redirects=False) as owned:
            return await resolve(owned)

    # Covers response-body consumption as well as transport header/read timeouts.
    return await asyncio.wait_for(operation(), remaining)
