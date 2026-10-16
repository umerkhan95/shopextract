"""One killable, byte-bounded child shared by DNS and synchronous domain calls."""
import asyncio
import json
import multiprocessing
import socket
import time
from .contracts import ToolError, encoded


def _execute(kind, payload):
    if kind == 'resolve':
        addresses = {row[4][0] for row in socket.getaddrinfo(payload['host'], None, type=socket.SOCK_STREAM)}
        return sorted(addresses)
    from .domain import synchronous
    return synchronous(payload)


def _child(connection, kind, payload, maximum):
    try:
        result = encoded({'ok': True, 'value': _execute(kind, json.loads(payload))})
        if len(result) > maximum:
            result = encoded({'ok': False, 'code': 'resource_limit'})
        connection.send_bytes(result)
    except ToolError as error:
        connection.send_bytes(encoded({'ok': False, 'code': error.code}))
    except (ValueError, KeyError, OSError):
        connection.send_bytes(encoded({'ok': False, 'code': 'source_error'}))
    except BaseException:
        connection.send_bytes(encoded({'ok': False, 'code': 'internal_error'}))
    finally:
        connection.close()


class OwnedProcess:
    def __init__(self, limits, *, child_target=None):
        self.limits = limits
        self.child_target = child_target or _child
        self.lock = asyncio.Lock()
        self.process = None
        self.broken = False
        self._cleanup_task = None

    async def run(self, kind, payload, context):
        if self.broken:
            raise ToolError('resource_limit', 'Worker cleanup failed; restart server')
        maximum = self.limits.graph_bytes * 2
        if len(payload) > maximum:
            raise ToolError('resource_limit', 'Worker input is too large')
        async with self.lock:
            if context.cancelled.is_set():
                raise asyncio.CancelledError()
            remaining = context.deadline - time.monotonic()
            end = time.monotonic() + min(remaining, self.limits.resolver_seconds if kind == 'resolve' else remaining)
            if remaining <= 0:
                raise ToolError('timeout')
            mp = multiprocessing.get_context('spawn')
            receive, send = mp.Pipe(duplex=False)
            proc = mp.Process(target=self.child_target, args=(send, kind, payload, maximum), daemon=True)
            self.process = proc
            proc.start()
            send.close()
            try:
                while not receive.poll():
                    if context.cancelled.is_set():
                        raise asyncio.CancelledError()
                    if time.monotonic() >= end:
                        raise ToolError('timeout')
                    if not proc.is_alive():
                        raise ToolError('source_error', 'Worker exited without result')
                    await asyncio.sleep(.005)
                reply = receive.recv_bytes(maxlength=maximum)
                if context.cancelled.is_set() or time.monotonic() >= end:
                    raise ToolError('timeout')
                result = json.loads(reply)
                if not result['ok']:
                    raise ToolError(result['code'])
                return encoded(result['value'])
            except (OSError, EOFError, ValueError):
                raise ToolError('source_error', 'Invalid bounded worker reply') from None
            finally:
                receive.close()
                await self.cancel_and_reap(context)

    async def cancel_and_reap(self, context=None):
        # Deadline and explicit cancellation may overlap. All callers await one
        # cleanup task, and repeated cancellation cannot interrupt child reaping.
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._reap())
        task = self._cleanup_task
        cancelled = False
        try:
            while True:
                try:
                    await asyncio.shield(task)
                    break
                except asyncio.CancelledError:
                    if task.cancelled():
                        raise
                    cancelled = True
            if cancelled:
                raise asyncio.CancelledError()
        finally:
            if task.done() and self._cleanup_task is task:
                self._cleanup_task = None

    async def _reap(self):
        proc = self.process
        if proc is None:
            return
        # No further awaits are needed for terminate/kill; bounded nonblocking polls
        # avoid joining an unreaped child on the event loop.
        if proc.is_alive():
            proc.terminate()
        end = time.monotonic() + self.limits.cleanup_seconds
        while proc.is_alive() and time.monotonic() < end:
            if time.monotonic() >= end - self.limits.cleanup_seconds / 2:
                proc.kill()
            await asyncio.sleep(.005)
        if proc.is_alive():
            self.broken = True
            raise ToolError('internal_error', 'Worker cleanup failed; server must stop')
        proc.join(timeout=0)
        proc.close()
        self.process = None
