"""Bounded test oracle for the written recipe; never a production report export."""
import time
import re
from urllib.parse import unquote, urlsplit
from dataclasses import dataclass, field


def select_product_url(urls, origin):
    """Conservative returned-route heuristic; never invent a candidate URL."""
    def identity(value):
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {'http', 'https'} or parsed.username or parsed.password:
            raise ValueError('unsupported origin')
        return parsed.scheme.lower(), parsed.hostname, parsed.port or (443 if parsed.scheme.lower() == 'https' else 80)
    if not isinstance(origin, str):
        return None
    try:
        granted = identity(origin)
    except (ValueError, TypeError):
        return None
    excluded = {'blog', 'blogs', 'article', 'articles', 'news', 'journal'}
    markers = ('products', 'product', 'p', 'item', 'dp')
    ranked = []
    for url in urls:
        if not isinstance(url, str):
            continue
        try:
            if identity(url) != granted:
                continue
            raw_path = urlsplit(url).path
            if re.search(r'%(?:2f|5c)', raw_path, re.I):
                continue
            path = unquote(raw_path).lower()
            if '\\' in path or re.search(r'%(?:2f|5c)', path):
                continue
            segments = [part for part in path.split('/') if part]
            if excluded.intersection(segments) or {'.', '..'}.intersection(segments):
                continue
            ranks = [rank for rank, marker in enumerate(markers)
                     if any(part == marker and i + 1 < len(segments) for i, part in enumerate(segments))]
            if ranks:
                ranked.append((min(ranks), url))
        except (ValueError, TypeError):
            continue
    return min(ranked)[1] if ranked else None


def preflight_tools(definitions, *, server_prefix):
    required = ('discover', 'extract', 'job_status', 'job_result', 'evidence')
    result = {'ok': False, 'tools': {}, 'reason': ''}
    for operation in required:
        full = server_prefix + operation
        matches = [value for value in definitions if isinstance(value, dict) and value.get('name') == full]
        if len(matches) != 1:
            result['reason'] = 'missing_or_ambiguous_tool:' + operation
            return result
        schema = matches[0].get('inputSchema')
        properties = schema.get('properties') if isinstance(schema, dict) else None
        field = properties.get('schema_version', {}) if isinstance(properties, dict) else {}
        if not isinstance(field, dict) or not (field.get('const') == '1.0' or '1.0' in field.get('enum', [])):
            result['reason'] = 'unsupported_schema:' + operation
            return result
        result['tools'][operation] = full
    result['ok'] = True
    return result


@dataclass
class RecipeTrace:
    calls: list = field(default_factory=list)
    records: list = field(default_factory=list)
    evidence: dict | None = None
    stop: str = ''


class StopRecipe(Exception):
    pass


async def run_recipe(call, url, *, max_calls=6, timeout_seconds=120,
                     after_submit=None, clock=time.monotonic):
    trace = RecipeTrace()
    deadline = clock() + timeout_seconds

    async def invoke(name, **arguments):
        if len(trace.calls) >= max_calls or clock() >= deadline:
            trace.stop = 'budget'
            raise StopRecipe()
        envelope = await call(name, {'schema_version': '1.0', **arguments})
        trace.calls.append((name, arguments, envelope))
        if not envelope['ok']:
            trace.stop = envelope['error']['code']
            raise StopRecipe()
        return envelope['data']

    async def submitted(name, target):
        data = await invoke(name, url=target, max_items=2)
        # Offline deterministic synchronization only; does not fabricate tool data.
        if after_submit is not None:
            await after_submit(data['job_id'], name)
        return data['job_id']

    try:
        discovered = await submitted('discover', url)
        urls = await invoke('job_result', job_id=discovered, collection='urls', page_size=2)
        if urls['state'] != 'succeeded':
            trace.stop = urls['state']
            return trace
        if not urls['items']:
            trace.stop = 'empty'
            return trace
        target = select_product_url(urls['items'], url)
        if target is None:
            trace.stop = 'no product URL discovered'
            return trace
        extracted = await submitted('extract', target)
        status = await invoke('job_status', job_id=extracted)
        if status['state'] != 'succeeded':
            trace.stop = status['state']
            return trace
        products = await invoke('job_result', job_id=extracted, collection='products', page_size=2)
        if products['state'] != 'succeeded':
            trace.stop = products['state']
            return trace
        trace.records = products['items'][:2]
        if not trace.records:
            trace.stop = 'empty'
            return trace
        selected = trace.records[0]
        ids = selected['field_evidence'].get('/price', [])
        if not ids:
            trace.stop = 'unavailable'
            return trace
        trace.evidence = await invoke('evidence', owner=selected['owner_handle'], evidence_id=ids[0])
        trace.stop = 'complete'
    except StopRecipe:
        pass
    return trace
