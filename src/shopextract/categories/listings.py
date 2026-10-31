"""Opt-in bounded Magento listing membership acquisition, with retained evidence."""
from __future__ import annotations

import asyncio
import json
import time
from collections import deque
from datetime import datetime
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit

import httpx
from bs4 import BeautifulSoup
from defusedxml import ElementTree

from .._capture import capture
from .contracts import CategoryError, CategoryFactBinding, CategoryObservation, CategoryTerm, CategoryTermRef
from .evidence import source_fact
from .helpers import merchant_scope, nonblank_text, observation_id

NAMESPACE = 'merchant:listing_category'
MAX_BYTES = 1048576
_TOTAL_TIMEOUT = 300
_EXCLUDED = ('nav', 'aside', 'footer')


def _url(value, store_url=None):
    if not isinstance(value, str) or not value or len(value) > 4096 or any(c.isspace() for c in value) or '\\' in value:
        raise CategoryError('Invalid listing URL')
    try:
        parts = urlsplit(value)
        if parts.scheme not in ('http', 'https') or not parts.hostname or parts.username or parts.password:
            raise ValueError()
        parts.port
        path = parts.path
        for _ in range(4):
            decoded = unquote(path, errors='strict')
            if decoded == path:
                break
            path = decoded
        else:
            raise ValueError()
        if '\\' in path or any(s in ('.', '..') for s in path.split('/')):
            raise ValueError()
        if store_url is not None:
            scope = urlsplit(_url(store_url))
            prefix = unquote(scope.path).rstrip('/')
            if (parts.scheme, parts.netloc.lower()) != (scope.scheme, scope.netloc.lower()) or not (path == prefix or path.startswith(prefix + '/')):
                raise ValueError()
        return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ''))
    except (ValueError, UnicodeError) as error:
        raise CategoryError('Listing URL differs from safe store origin/base path') from error


def listing_urls(content: bytes) -> list[str]:
    """Read a bounded saved URL list or sitemap urlset; never treat it as membership."""
    if not isinstance(content, bytes) or len(content) > MAX_BYTES:
        raise CategoryError('Listing URL input exceeds 1MiB')
    try:
        if content.lstrip().startswith(b'<'):
            root = ElementTree.fromstring(content)
            if root.tag.rsplit('}', 1)[-1] != 'urlset':
                raise ValueError()
            values = [child.text for entry in root if entry.tag.rsplit('}', 1)[-1] == 'url'
                      for child in entry if child.tag.rsplit('}', 1)[-1] == 'loc']
        else:
            values = json.loads(content)
        if not isinstance(values, list) or not values or len(values) > 1000:
            raise ValueError()
        return list(dict.fromkeys(_url(value) for value in values))
    except (ValueError, TypeError, ElementTree.ParseError) as error:
        raise CategoryError('Expected bounded URL JSON list or sitemap urlset') from error


def _excluded(node):
    for parent in node.parents:
        classes = set(parent.get('class', ())) if hasattr(parent, 'get') else set()
        if parent.name in _EXCLUDED or classes & {'related', 'upsell', 'crosssell'}:
            return True
    return False


def _parse(html, page_url, category_url, store_url):
    soup = BeautifulSoup(html, 'html.parser')
    main = soup.find('main') or soup.body or soup
    grids = [g for g in main.select('.products-grid, .products-list') if not _excluded(g)]
    if not grids:
        return [], [], ['listing_structure_missing']
    heading = main.select_one('h1.page-title')
    label = heading.get_text(' ', strip=True) if heading else None
    if not label or len(label.encode('utf-8')) > 4096:
        label = None
    rows, next_urls, reasons = [], [], []
    for grid in grids:
        for node in grid.select('.product-item a.product-item-link[href]'):
            if _excluded(node):
                continue
            href = node.get('href', '')
            if not href or href.startswith('#'):
                continue
            try:
                product_url = _url(urljoin(page_url, href), store_url)
            except CategoryError:
                reasons.append('product_link_out_of_scope')
                continue
            row = dict(product_url=product_url, category_url=category_url, label=label)
            capture(row, page_url, 'html_category_listing', excerpt=(str(heading) if heading else '') + str(node))
            rows.append(row)
    for node in main.select('.pages a.next[href], a[rel~=next][href]'):
        if _excluded(node):
            continue
        href = node.get('href', '')
        if not href or href.startswith('#'):
            continue
        try:
            next_urls.append(_url(urljoin(page_url, href), store_url))
        except CategoryError:
            reasons.append('pagination_out_of_scope')
    return rows, list(dict.fromkeys(next_urls)), reasons


async def _read_page(client, page_url, store_url, page_bytes, timeout):
    # Body consumption is included in the caller's whole-request deadline.
    async with client.stream('GET', page_url, timeout=min(15, timeout), follow_redirects=False) as response:
        if response.status_code != 200:
            return None, None, 'listing_http_' + str(response.status_code)
        final_url = _url(str(response.url), store_url)
        chunks, used = [], 0
        async for chunk in response.aiter_bytes():
            used += len(chunk)
            if used > page_bytes:
                return None, None, 'page_byte_budget_reached'
            chunks.append(chunk)
        return final_url, b''.join(chunks).decode(response.encoding or 'utf-8', errors='replace'), None


async def build_listing_index(urls, store_url, *, client=None, max_pages=20,
                              max_memberships=1000, page_bytes=MAX_BYTES) -> dict:
    """Acquire positive memberships sequentially. Complete means supplied pages only."""
    store_url = _url(store_url)
    for name, value, maximum in [('max_pages', max_pages, 1000), ('max_memberships', max_memberships, 10000), ('page_bytes', page_bytes, MAX_BYTES)]:
        if type(value) is not int or not 1 <= value <= maximum:
            raise CategoryError('Invalid listing limit: ' + name)
    if not isinstance(urls, (list, tuple)) or not urls or len(urls) > 1000:
        raise CategoryError('Supply 1..1000 category listing URLs')
    roots = list(dict.fromkeys(_url(url, store_url) for url in urls))
    queue = deque((url, url) for url in roots)
    seen, pairs = set(), set()
    index = dict(schema_version=1, store_url=store_url, pages_visited=0, complete=True, reasons=[], memberships=[])
    size = 1024
    own = client is None
    if own:
        client = httpx.AsyncClient(follow_redirects=False, timeout=15)
    deadline = time.monotonic() + _TOTAL_TIMEOUT
    try:
        while queue:
            page_url, category_url = queue.popleft()
            if (page_url, category_url) in seen:
                continue
            if index['pages_visited'] >= max_pages:
                index['reasons'].append('page_budget_reached')
                break
            if time.monotonic() >= deadline:
                index['reasons'].append('time_budget_reached')
                break
            seen.add((page_url, category_url))
            index['pages_visited'] += 1
            try:
                remaining = max(.001, deadline-time.monotonic())
                final_url, html, error = await asyncio.wait_for(
                    _read_page(client, page_url, store_url, page_bytes, remaining), remaining)
                if error:
                    index['reasons'].append(error)
                    continue
                rows, next_urls, reasons = _parse(html, final_url, category_url, store_url)
                index['reasons'].extend(reasons)
                for row in rows:
                    pair = (row['product_url'], row['category_url'])
                    if pair in pairs:
                        continue
                    row_size = len(json.dumps(row, ensure_ascii=False).encode('utf-8'))
                    if len(pairs) >= max_memberships or size + row_size > MAX_BYTES:
                        index['reasons'].append('membership_budget_reached' if len(pairs) >= max_memberships else 'index_byte_budget_reached')
                        queue.clear()
                        break
                    index['memberships'].append(row)
                    pairs.add(pair)
                    size += row_size
                else:
                    queue.extend((next_url, category_url) for next_url in next_urls)
            except asyncio.TimeoutError:
                index['reasons'].append('time_budget_reached')
                break
            except (httpx.HTTPError, CategoryError, UnicodeError):
                index['reasons'].append('listing_source_error')
    finally:
        if own:
            await client.aclose()
    index['reasons'] = list(dict.fromkeys(index['reasons']))
    index['complete'] = not index['reasons']
    return index


def validate_listing_index(index, store_url) -> None:
    try:
        if not isinstance(index, dict) or set(index) != {'schema_version','store_url','pages_visited','complete','reasons','memberships'}:
            raise ValueError()
        if type(index['schema_version']) is not int or index['schema_version'] != 1 or _url(index['store_url']) != _url(store_url):
            raise ValueError()
        if type(index['pages_visited']) is not int or not 0 <= index['pages_visited'] <= 1000 or type(index['complete']) is not bool:
            raise ValueError()
        reasons, rows = index['reasons'], index['memberships']
        if not isinstance(reasons, list) or len(reasons) > 100 or any(not isinstance(r,str) or not r or len(r)>64 for r in reasons):
            raise ValueError()
        if index['complete'] != (not reasons) or not isinstance(rows, list) or len(rows) > 10000:
            raise ValueError()
        if len(json.dumps(index, ensure_ascii=False, allow_nan=False).encode('utf-8')) > MAX_BYTES:
            raise ValueError()
        pairs = set()
        for row in rows:
            if not isinstance(row,dict) or set(row) != {'product_url','category_url','label','_capture'}:
                raise ValueError()
            for key in ('product_url','category_url'):
                if _url(row[key], store_url) != row[key]:
                    raise ValueError()
            if row['label'] is not None and (not isinstance(row['label'],str) or not row['label'].strip() or len(row['label'].encode('utf-8')) > 4096):
                raise ValueError()
            context = row['_capture']
            if not isinstance(context,dict) or context.get('method') != 'html_category_listing' or _url(context.get('url'),store_url) != context.get('url'):
                raise ValueError()
            if datetime.fromisoformat(context['at']).tzinfo is None:
                raise ValueError()
            if not isinstance(context.get('values'),dict) or any(context['values'].get('/'+key) != row[key] for key in ('product_url','category_url','label')):
                raise ValueError()
            if type(context.get('truncated')) is not bool or ('excerpt' in context and (not isinstance(context['excerpt'],str) or len(context['excerpt'].encode('utf-8')) > 4096)):
                raise ValueError()
            pair = (row['product_url'],row['category_url'])
            if pair in pairs:
                raise ValueError()
            pairs.add(pair)
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError,OverflowError) as error:
        raise CategoryError('Invalid listing index shape, scope or capture') from error


def with_listing_categories(raw, index):
    """Return an enriched copy; absence in an index is never negative membership."""
    if not isinstance(raw, dict):
        raise CategoryError('Raw product must be a dictionary')
    validate_listing_index(index, index.get('store_url') if isinstance(index,dict) else None)
    product_url = raw.get('url') or raw.get('og:url') or (raw.get('_capture') or {}).get('url')
    try:
        product_url = _url(product_url,index['store_url'])
    except CategoryError:
        raise CategoryError('Product URL differs from listing index store') from None
    rows = [dict(row) for row in index['memberships'] if row['product_url'] == product_url]
    result = dict(raw, listing_categories=rows, _listing_complete=index['complete'])
    result['_field_sources'] = dict(raw.get('_field_sources', {}))
    for i, row in enumerate(rows):
        for key in ('category_url','label','product_url'):
            result['_field_sources'][f'/listing_categories/{i}/{key}'] = {'_capture':row['_capture'],'capture_path':'/'+key}
    return result


def observe_listing_categories(raw, *, context):
    rows = raw.get('listing_categories', [])
    if not isinstance(rows,list):
        raise CategoryError('Invalid listing categories carrier')
    terms, clipped = [], False
    cap = min(context.limits.terms, context.limits.relation_refs)
    for i, row in enumerate(rows):
        if len(terms) >= cap:
            clipped = True
            break
        category = _url(row['category_url'], context.scope.store_url)
        ref = CategoryTermRef(NAMESPACE, None, category, merchant_scope(context.scope))
        pointer = f'/listing_categories/{i}'
        facts = [source_fact(raw,pointer+'/category_url',binding=CategoryFactBinding('native_id',term=ref),convert=nonblank_text)]
        label = row.get('label')
        if label is not None:
            facts.append(source_fact(raw,pointer+'/label',binding=CategoryFactBinding('label',term=ref),convert=nonblank_text))
        terms.append(CategoryTerm(ref,label,tuple(facts)))
    partial = clipped or not raw.get('_listing_complete',False)
    return (CategoryObservation(observation_id(context.scope,NAMESPACE,'memberships','/listing_categories'), context.scope,
        'memberships','merchant','present' if terms else 'empty','partial' if partial else 'unknown',tuple(terms),(),(),
        'category_budget_reached' if clipped else 'listing_acquisition_partial' if partial else 'listing_membership_coverage_unknown'),)
