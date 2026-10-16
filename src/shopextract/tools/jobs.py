"""Single active bounded jobs, enqueue deadlines and one terminal winner."""
import asyncio
import time
from collections import OrderedDict
from datetime import datetime, timezone
from .context import OperationContext, OperationBudget
from .contracts import ToolError

TERMINAL = {'succeeded', 'failed', 'cancelled', 'timed_out'}


class JobManager:
    def __init__(self, store, limits, *, auxiliary=None, clock=time.monotonic, utc_now=None):
        self.store, self.limits, self.auxiliary, self.clock = store, limits, auxiliary, clock
        self.utc_now = utc_now or (lambda: datetime.now(timezone.utc))
        self.jobs = OrderedDict()
        self.slot = asyncio.Semaphore(1)
        self.closed = False

    def trim(self):
        self.store.sweep()
        terminal = [k for k, j in self.jobs.items() if j['state'] in TERMINAL and not j.get('private')]
        for key in terminal:
            j = self.jobs[key]
            if self.clock() >= j['expires']:
                self.jobs.pop(key)
                self.store.release(key)
        terminal = [k for k, j in self.jobs.items() if j['state'] in TERMINAL and not j.get('private')]
        while len(terminal) > self.limits.terminal_jobs:
            key = terminal.pop(0)
            self.jobs.pop(key)
            self.store.release(key)

    def submit(self, operation, timeout, *, private=False):
        if self.closed:
            raise ToolError('resource_limit', 'Session is closed')
        self.trim()
        active = sum(j['state'] not in TERMINAL for j in self.jobs.values())
        if active >= self.limits.queued_jobs + 1:
            raise ToolError('resource_limit', 'Job queue is full')
        key = self.store.mint()
        ctx = OperationContext(key, self.clock() + timeout, asyncio.Event(),
            OperationBudget(self.limits), self.auxiliary, self.utc_now())
        j = {'state': 'queued', 'context': ctx, 'queued_at': self.utc_now().isoformat(),
             'started_at': None, 'terminal_at': None, 'expires': float('inf'), 'error': None, 'private': private}
        self.jobs[key] = j
        j['task'] = asyncio.create_task(self.run(key, operation))
        return {'job_id': key, 'state': 'queued'}

    async def run(self, key, operation):
        j = self.jobs[key]
        ctx = j['context']
        async def work():
            async with self.slot:
                if ctx.cancelled.is_set():
                    raise asyncio.CancelledError()
                j['state'], j['started_at'] = 'running', self.utc_now().isoformat()
                self.store.reserve(self.limits.graph_bytes)
                ctx.budget.graph_bytes_reserved = self.limits.graph_bytes
                graph = await operation(ctx)
                if ctx.cancelled.is_set():
                    raise asyncio.CancelledError()
                for dependency in graph.dependencies:
                    self.store.get(dependency)
                self.store.unreserve(ctx.budget.graph_bytes_reserved)
                ctx.budget.graph_bytes_reserved = 0
                if j['private']:
                    size = graph.size
                    if size > self.limits.graph_bytes:
                        raise ToolError('resource_limit')
                    self.store.reserve(size)
                    j['staged_size'], j['graph'] = size, graph
                else:
                    self.store.publish(key, graph)
                j['state'] = 'succeeded'
        # Keep the actual work task owned here. A timeout of its shield must
        # not detach nested worker cleanup or permit private discard to finish.
        work_task = asyncio.create_task(work())
        failure = None
        try:
            await asyncio.wait_for(asyncio.shield(work_task), max(0, ctx.deadline - self.clock()))
        except asyncio.TimeoutError:
            ctx.cancelled.set()
            failure = ('timed_out', ToolError('timeout'))
        except asyncio.CancelledError:
            ctx.cancelled.set()
            failure = ('cancelled', ToolError('cancelled'))
        except ToolError as error:
            failure = ('timed_out' if error.code == 'timeout' else 'failed', error)
        except Exception:
            failure = ('failed', ToolError('internal_error', 'Operation failed'))
        finally:
            if not work_task.done():
                ctx.cancelled.set()
                work_task.cancel()
            while not work_task.done():
                try:
                    await asyncio.shield(work_task)
                except asyncio.CancelledError:
                    # Repeated outer cancellation cannot detach owned cleanup.
                    continue
                except Exception:
                    break
            if work_task.done() and not work_task.cancelled():
                work_task.exception()  # Retrieve an error even after an outer timeout.
            if failure is not None and j['state'] != 'succeeded':
                j['state'], j['error'] = failure
            if ctx.budget.graph_bytes_reserved:
                self.store.unreserve(ctx.budget.graph_bytes_reserved)
                ctx.budget.graph_bytes_reserved = 0
            j['terminal_at'] = self.utc_now().isoformat()
            j['expires'] = self.clock() + self.limits.retention_seconds
            self.trim()

    def find(self, key):
        self.trim()
        j = self.jobs.get(key)
        if j is None:
            self.store.get(key)
            raise ToolError('not_found')
        return j

    def status(self, key):
        j = self.find(key)
        result = {k: j[k] for k in ('state', 'queued_at', 'started_at', 'terminal_at')}
        if j['error']:
            result['error'] = {'code': j['error'].code, 'message': j['error'].message}
        return result

    def result(self, key, collection, size, cursor):
        j = self.find(key)
        if j['state'] not in TERMINAL:
            return {'state': j['state']}
        if j['error']:
            raise j['error']
        return self.store.page(key, collection, size, cursor)

    async def cancel(self, key):
        j = self.find(key)
        if j['state'] not in TERMINAL:
            j['context'].cancelled.set()
            if not j.get('cancelling'):
                j['cancelling'] = True
                j['task'].cancel()
            try:
                await asyncio.shield(j['task'])
            except asyncio.CancelledError:
                # A task cancelled before its first instruction has no finally block.
                j.update(state='cancelled', error=ToolError('cancelled'),
                    terminal_at=self.utc_now().isoformat(), expires=self.clock() + self.limits.retention_seconds)
        return self.status(key)

    async def discard_private(self, key):
        j = self.jobs.get(key)
        if j is None or not j.get('private'):
            return
        if j['state'] not in TERMINAL:
            await self.cancel(key)
        self.store.unreserve(j.pop('staged_size', 0))
        self.jobs.pop(key, None)

    async def close(self):
        self.closed = True
        for key in list(self.jobs):
            if key in self.jobs:
                await self.cancel(key)
        self.store.close()
        self.jobs.clear()
