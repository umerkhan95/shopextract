"""Immutable, byte-accounted session results and opaque owner references."""
import base64
import copy
import hashlib
import hmac
import json
import secrets
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from .contracts import ToolError, encoded


@dataclass
class RetainedGraph:
    collections: dict
    metadata: dict
    completeness: str
    products: list = field(default_factory=list)
    owners: dict = field(default_factory=dict)
    dependencies: tuple = ()

    @property
    def size(self):
        # Charge every reachable serialized representation conservatively. Python
        # objects are not physically interned, so logical capture dedup is unsafe.
        return len(encoded({'collections': self.collections, 'metadata': self.metadata,
            'completeness': self.completeness, 'products': self.products,
            'owners': self.owners, 'dependencies': list(self.dependencies)}))



class SessionStore:
    def __init__(self, limits, *, clock=time.monotonic):
        self.limits, self.clock = limits, clock
        self.graphs, self.handles = OrderedDict(), {}
        self.expired = OrderedDict()
        self.expired_handles = OrderedDict()
        self.used_bytes = 0
        self.secret = secrets.token_bytes(32)

    def reserve(self, size):
        self.sweep()
        if self.used_bytes + size > self.limits.session_graph_bytes:
            raise ToolError('resource_limit', 'Session retained byte limit reached')
        self.used_bytes += size

    def unreserve(self, size):
        self.used_bytes -= size

    def mint(self):
        return secrets.token_urlsafe(24)

    def sweep(self):
        for job_id, (_, expires, _) in list(self.graphs.items()):
            if self.clock() >= expires:
                self.release(job_id)

    def release(self, job_id):
        record = self.graphs.pop(job_id, None)
        if record:
            self.used_bytes -= record[2]
            for handle,value in list(self.handles.items()):
                if value[0] == job_id:
                    self.expired_handles[handle] = None
                    del self.handles[handle]
            while len(self.expired_handles) > self.limits.terminal_jobs * self.limits.item_count * 2:
                self.expired_handles.popitem(last=False)
            self.expired[job_id] = None
            while len(self.expired) > self.limits.terminal_jobs * 2:
                self.expired.popitem(last=False)

    def publish(self, job_id, graph):
        self.sweep()
        size = graph.size
        if size > self.limits.graph_bytes:
            raise ToolError('resource_limit', 'Retained job graph is too large')
        if len(self.graphs) >= self.limits.terminal_jobs:
            self.release(next(iter(self.graphs)))
        if self.used_bytes + size > self.limits.session_graph_bytes:
            raise ToolError('resource_limit', 'Session retained byte limit reached')
        self.graphs[job_id] = (graph, self.clock() + self.limits.retention_seconds, size)
        self.used_bytes += size
        catalog = graph.metadata.get('catalog_handle')
        if catalog:
            self.handles[catalog] = (job_id, 'catalog', None)
        for owner, data in graph.owners.items():
            self.handles[owner] = (job_id, 'owner', data)
        capture = graph.metadata.get('capture_handle')
        if capture:
            self.handles[capture] = (job_id, 'capture', graph.metadata.get('grant'))

    def publish_batch(self, staged):
        """Transfer already charged private graphs atomically; never evict others."""
        self.sweep()
        if len(self.graphs) + len(staged) > self.limits.terminal_jobs:
            raise ToolError('resource_limit', 'Capture capacity unavailable')
        pending = {}
        for job_id, graph in staged:
            if graph.size > self.limits.graph_bytes or job_id in self.graphs:
                raise ToolError('resource_limit')
            values = {graph.metadata['catalog_handle']: ('catalog', None),
                      graph.metadata['capture_handle']: ('capture', graph.metadata['grant'])}
            values.update({owner: ('owner', value) for owner, value in graph.owners.items()})
            for handle, (kind, value) in values.items():
                if handle in self.handles or handle in pending:
                    raise ToolError('internal_error', 'Capture handle collision')
                pending[handle] = (job_id, kind, value)
        # All validation precedes this non-awaiting commit; reservations stay charged.
        for job_id, graph in staged:
            self.graphs[job_id] = (graph, self.clock() + self.limits.retention_seconds, graph.size)
        self.handles.update(pending)

    def get(self, job_id):
        self.sweep()
        if job_id not in self.graphs:
            raise ToolError('expired' if job_id in self.expired else 'not_found')
        return self.graphs[job_id][0]

    def lookup(self, handle, kind):
        self.sweep()
        value = self.handles.get(handle)
        if value is None:
            raise ToolError('expired' if handle in self.expired_handles else 'not_found')
        if value[1] != kind:
            raise ToolError('not_found')
        self.get(value[0])
        return value[0], value[2]

    def page(self, job_id, collection, size, cursor):
        graph = self.get(job_id)
        if collection not in graph.collections:
            raise ToolError('invalid_argument', 'Unknown result collection')
        offset = 0
        if cursor:
            try:
                payload, sig = cursor.split('.')
                expected = hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()
                if not hmac.compare_digest(expected, sig):
                    raise ValueError()
                data = json.loads(base64.urlsafe_b64decode(payload))
                if data[:4] != [job_id, collection, size, '1.0'] or type(data[4]) is not int or data[4] < 0:
                    raise ValueError()
                offset = data[4]
            except (ValueError, TypeError, KeyError, IndexError):
                raise ToolError('invalid_argument', 'Invalid cursor') from None
        items = graph.collections[collection]
        end = offset + size
        nxt = None
        if end < len(items):
            payload = base64.urlsafe_b64encode(encoded([job_id, collection, size, '1.0', end])).decode()
            nxt = payload + '.' + hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()
        return copy.deepcopy({'state': 'succeeded', 'collection': collection, 'items': items[offset:end],
            'next_cursor': nxt, 'total': len(items), 'completeness': graph.completeness, 'metadata': {k: v for k, v in graph.metadata.items() if k != 'grant'}})

    def close(self):
        self.graphs.clear()
        self.handles.clear()
        self.expired.clear()
        self.expired_handles.clear()
        self.used_bytes = 0
