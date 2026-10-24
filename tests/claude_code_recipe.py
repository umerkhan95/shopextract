"""Bounded test oracle for the written recipe; never a production report export."""
import time
from dataclasses import dataclass, field


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
        extracted = await submitted('extract', urls['items'][0])
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
