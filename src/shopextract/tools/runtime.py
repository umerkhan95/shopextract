"""Feature #24 skeleton. Deliberately no working domain implementation."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Mapping, TYPE_CHECKING

import httpx
import asyncio
import copy
import math
import time

if TYPE_CHECKING:
    from .context import Resolver

TOOL_NAMES = ('discover', 'extract', 'match', 'changes', 'evidence',
              'job_status', 'job_result', 'job_cancel')


@dataclass(frozen=True)
class Limits:
    active_jobs: int = 1
    queued_jobs: int = 8
    terminal_jobs: int = 32
    retention_seconds: float = 600
    timeout_seconds: float = 30
    max_timeout_seconds: float = 120
    item_count: int = 1000
    input_bytes: int = 256 * 1024
    graph_bytes: int = 4 * 1024 * 1024
    session_graph_bytes: int = 32 * 1024 * 1024
    evidence_bytes: int = 1024 * 1024
    response_bytes: int = 2 * 1024 * 1024
    requests: int = 20
    redirects: int = 5
    resolver_seconds: float = 2
    cleanup_seconds: float = 1


@dataclass(frozen=True)
class CaptureGrant:
    """Trusted operator declaration; never accepted in tool-call arguments."""
    alias: str
    db_path: str
    snapshot_id: int
    supplier: str


@dataclass(frozen=True)
class ToolConfig:
    allowed_origins: tuple[str, ...] = ()
    allowed_tools: tuple[str, ...] = TOOL_NAMES
    captures: tuple[CaptureGrant, ...] = ()
    limits: Limits = field(default_factory=Limits)


class ToolRuntime:
    def __init__(self, config: ToolConfig, *, resolver: Resolver | None = None,
                 wire_transport: httpx.AsyncBaseTransport | None = None, clock=None,
                 utc_now: Callable[[], datetime] | None = None, category_config=None,shopify_storefront=None):
        import time
        from dataclasses import fields
        from .contracts import ToolError
        from .state import SessionStore
        from .execution import OwnedProcess
        from .security import SourceGuard, normalized
        from .sources import GuardedSources
        from .domain import DomainAdapter
        from .jobs import JobManager
        defaults = Limits()
        for value in fields(Limits):
            actual, maximum = getattr(config.limits, value.name), getattr(defaults, value.name)
            if (type(actual) not in (int, float) or not 0 < actual <= maximum
                or (type(maximum) is int and type(actual) is not int)):
                raise ValueError('Limits must be positive and no higher than defaults')
        if config.limits.active_jobs != 1 or any(name not in TOOL_NAMES for name in config.allowed_tools):
            raise ValueError('Invalid tool/worker configuration')
        if any(normalized(origin)[0].rstrip('/') != normalized(origin)[1] for origin in config.allowed_origins):
            raise ValueError('Allowlist entries must be origins')
        if len(config.captures) > config.limits.terminal_jobs:
            raise ValueError('Too many configured capture grants')
        self.config = config
        self.store = SessionStore(config.limits, clock=clock or time.monotonic)
        self.auxiliary = OwnedProcess(config.limits)
        self.guard = SourceGuard(config, resolver=resolver)
        self.sources = GuardedSources(config, self.guard, wire_transport, category_config=category_config,shopify_storefront=shopify_storefront)
        self.domain = DomainAdapter(self.store, self.sources)
        self.jobs = JobManager(self.store, config.limits, auxiliary=self.auxiliary,
                               clock=clock or time.monotonic, utc_now=utc_now)
        self.grants = None
        self._bootstrap_lock = asyncio.Lock()
        self._bootstrap_tasks = set()
        self.closed = False

    async def call(self, name, arguments):
        from .contracts import validate, envelope, ToolError, encoded
        try:
            args = validate(name, arguments, self.config.limits)
            if self.closed or self.auxiliary.broken:
                raise ToolError('resource_limit', 'Session is closed; restart server')
            if name not in self.config.allowed_tools:
                raise ToolError('permission_denied', 'Tool is not enabled')
            if name in {'discover', 'extract'}:
                # No DNS/network needed to reject an explicit ungranted origin.
                from .security import normalized
                if normalized(args['url'])[1] not in self.guard.origins:
                    raise ToolError('permission_denied', 'Source origin is not permitted')
            if name in {'discover', 'extract', 'match', 'changes'}:
                return envelope(self.jobs.submit(lambda ctx: self.domain.execute(name, args, ctx),
                    args.get('timeout_seconds', self.config.limits.timeout_seconds)))
            if name == 'job_status':
                return envelope(self.jobs.status(args['job_id']))
            if name == 'job_cancel':
                return envelope(await self.jobs.cancel(args['job_id']))
            if name == 'job_result':
                return envelope(self.jobs.result(args['job_id'], args['collection'], args.get('page_size', 20), args.get('cursor')))
            _, owner = self.store.lookup(args['owner'], 'owner')
            evidence = owner['evidence'].get(args['evidence_id'])
            if evidence is None:
                availability = next((e for e in owner['availability'] if e['evidence_id'] == args['evidence_id']), None)
                if availability:
                    return envelope({'status': availability['status'], 'reason': availability['reason']})
                raise ToolError('not_found')
            if len(encoded(evidence)) > self.config.limits.evidence_bytes:
                metadata = {k: v for k, v in evidence.items() if k != 'retained_data'}
                raise ToolError('resource_limit', 'Evidence response exceeds cap', details={'metadata': metadata, 'payload_status': 'not_retained'})
            return envelope({'status': 'available', 'reason': 'retained_capture', 'evidence': evidence})
        except ToolError as error:
            return envelope(error=error)
        except Exception:
            return envelope(error=ToolError('internal_error', 'Tool operation failed'))

    def tool_schemas(self):
        from .contracts import schema
        return [schema(name) for name in self.config.allowed_tools]

    async def bootstrap(self, *, timeout_seconds=None):
        """Materialize trusted captures through the shared bounded job/worker slot."""
        from dataclasses import asdict
        from .contracts import ToolError, encoded
        from .state import RetainedGraph
        seconds = self.config.limits.timeout_seconds if timeout_seconds is None else timeout_seconds
        if type(seconds) not in (int, float) or not math.isfinite(seconds) or not 1 <= seconds <= self.config.limits.max_timeout_seconds:
            raise ToolError('invalid_argument', 'Invalid bootstrap timeout')
        if self.closed or self.auxiliary.broken:
            raise ToolError('resource_limit', 'Session is closed')
        deadline = time.monotonic() + seconds
        caller = asyncio.current_task()
        self._bootstrap_tasks.add(caller)
        async def initialize():
            async with self._bootstrap_lock:
                if self.closed:
                    raise ToolError('resource_limit', 'Session is closed')
                if self.grants is not None:
                    for grant in self.grants:
                        self.store.lookup(grant['capture_handle'], 'capture')
                    return copy.deepcopy({'schema_version': '1.0', 'captures': self.grants, 'limits': asdict(self.config.limits)})
                if len(self.store.graphs) + len(self.config.captures) > self.config.limits.terminal_jobs:
                    raise ToolError('resource_limit', 'Capture capacity unavailable')
                private, staged, grants = [], [], []
                committed = False
                try:
                    for grant in self.config.captures:
                        async def operation(ctx, grant=grant):
                            payload = {'operation': 'capture', 'grant': asdict(grant), 'limits': asdict(self.config.limits)}
                            result = await ctx.auxiliary.run('domain', encoded(payload), ctx)
                            return RetainedGraph(**__import__('json').loads(result))
                        accepted = self.jobs.submit(operation, max(0, deadline-time.monotonic()), private=True)
                        key = accepted['job_id']; private.append(key)
                        job = self.jobs.jobs[key]
                        await asyncio.shield(job['task'])
                        if job['error']:
                            raise job['error']
                        graph = job['graph']; staged.append((key, graph))
                        grants.append({'alias': grant.alias, 'capture_handle': graph.metadata['capture_handle'],
                            'catalog_handle': graph.metadata['catalog_handle'], 'owners': [
                                {'record_key': product.get('canonical_product_id'), 'owner_handle': product['owner_handle']}
                                for product in graph.collections['products']]})
                    if self.closed or time.monotonic() >= deadline:
                        raise ToolError('timeout')
                    self.store.publish_batch(staged)
                    committed = True
                    self.grants = grants
                    return copy.deepcopy({'schema_version': '1.0', 'captures': grants, 'limits': asdict(self.config.limits)})
                finally:
                    for key in private:
                        if committed:
                            self.jobs.jobs[key]['staged_size'] = 0
                        await self.jobs.discard_private(key)
        try:
            return await asyncio.wait_for(initialize(), seconds)
        except asyncio.TimeoutError:
            raise ToolError('timeout', 'Configured capture deadline reached') from None
        finally:
            self._bootstrap_tasks.discard(caller)

    async def aclose(self):
        if self.closed:
            return
        self.closed = True
        for task in list(self._bootstrap_tasks):
            if task is not asyncio.current_task():
                task.cancel()
                try:
                    await asyncio.shield(task)
                except (asyncio.CancelledError, Exception):
                    pass
        await self.jobs.close()
        await self.auxiliary.cancel_and_reap()
