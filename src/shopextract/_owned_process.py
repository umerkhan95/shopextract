"""Sequential POSIX worker groups with bounded pipes, deadlines and cleanup.

Linux subreaper state and signal handlers are process-wide: callers must use the
main thread, and overlapping invocations fail before starting another worker.
Only descendants remaining in the owned process group are supervised.
"""
import ctypes
import os
import selectors
import signal
import subprocess
import sys
import threading
import time

_LOCK = threading.Lock()
_BROKEN = False


def _subreaper(value=None):
    if sys.platform != 'linux':
        raise RuntimeError('Owned browser supervision requires Linux')
    libc = ctypes.CDLL(None, use_errno=True)
    previous = ctypes.c_int()
    if libc.prctl(37, ctypes.byref(previous), 0, 0, 0):
        raise OSError('Cannot inspect worker supervision')
    if value is not None and libc.prctl(36, int(value), 0, 0, 0):
        raise OSError('Cannot configure worker supervision')
    return previous.value


def _alive(group):
    try:
        os.killpg(group, 0)
        return True
    except ProcessLookupError:
        return False


def _cleanup(process, deadline):
    def reap():
        if process.poll() is not None:
            while True:
                try:
                    if os.waitpid(-process.pid, os.WNOHANG)[0] == 0:
                        break
                except ChildProcessError:
                    break
    for sig in (signal.SIGTERM, signal.SIGKILL):
        reap()
        if not _alive(process.pid):
            break
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            pass
        stop = deadline if sig == signal.SIGKILL else min(deadline, time.monotonic() + .15)
        while time.monotonic() < stop:
            reap()
            if not _alive(process.pid):
                break
            time.sleep(.002)
    reap()
    return not _alive(process.pid)


def run_owned(command, *, input_bytes=b'', timeout, maximum_bytes=1048576):
    """Return actual bounded bytes/exit/cleanup evidence, including on overflow.

    Reserve cleanup inside timeout. Inputs are small worker/config envelopes;
    no inherited proxy or credential variables are removed or printed.
    """
    global _BROKEN
    if (threading.current_thread() is not threading.main_thread() or
            type(timeout) not in (int, float) or not 0 < timeout <= 120 or
            type(maximum_bytes) is not int or not 1 <= maximum_bytes <= 1048576 or
            not isinstance(input_bytes, bytes) or len(input_bytes) > 1048576):
        raise ValueError('Invalid owned-worker bounds or calling thread')
    if not _LOCK.acquire(blocking=False):
        raise RuntimeError('Another owned worker is active')
    previous = None
    process = None
    handlers = {}
    started = time.monotonic()
    deadline = started + timeout
    work_end = deadline - min(.75, timeout / 3)
    result = dict(stdout=b'', stderr=b'', returncode=None, timed_out=False,
                  output_exceeded=False, cleanup_complete=False)
    def interrupted(signum, frame):
        if signum == signal.SIGINT:
            raise KeyboardInterrupt()
        raise SystemExit(128 + signum)
    try:
        if _BROKEN:
            raise RuntimeError('Owned worker cleanup previously failed; restart the process')
        previous = _subreaper(True)
        for sig in (signal.SIGINT, signal.SIGTERM):
            handlers[sig] = signal.signal(sig, interrupted)
        env = dict(os.environ, OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                   MKL_NUM_THREADS='1', TOKENIZERS_PARALLELISM='false')
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True, env=env)
        buffers = {'stdout': bytearray(), 'stderr': bytearray()}
        sent = 0
        with selectors.DefaultSelector() as selector:
            for pipe, name in ((process.stdout, 'stdout'), (process.stderr, 'stderr')):
                os.set_blocking(pipe.fileno(), False)
                selector.register(pipe, selectors.EVENT_READ, name)
            os.set_blocking(process.stdin.fileno(), False)
            if input_bytes:
                selector.register(process.stdin, selectors.EVENT_WRITE, 'stdin')
            else:
                process.stdin.close()
            while selector.get_map():
                remaining = work_end - time.monotonic()
                if remaining <= 0:
                    result['timed_out'] = True
                    break
                events = selector.select(min(.02, remaining))
                if not events and process.poll() is not None:
                    break
                for key, _ in events:
                    if key.data == 'stdin':
                        try:
                            sent += os.write(key.fd, input_bytes[sent:sent + 65536])
                        except BrokenPipeError:
                            sent = len(input_bytes)
                        if sent == len(input_bytes):
                            selector.unregister(key.fileobj)
                            key.fileobj.close()
                        continue
                    data = os.read(key.fd, 65536)
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    target = buffers[key.data]
                    remaining_bytes = maximum_bytes - len(target)
                    target.extend(data[:remaining_bytes])
                    if len(data) > remaining_bytes:
                        result['output_exceeded'] = True
                        break
                if result['output_exceeded']:
                    break
            # A process can close both pipes before it finishes its work.
            while (not result['output_exceeded'] and not result['timed_out']
                   and process.poll() is None):
                if time.monotonic() >= work_end:
                    result['timed_out'] = True
                    break
                time.sleep(.002)
        result.update({key: bytes(value) for key, value in buffers.items()})
    finally:
        try:
            if process is not None:
                # A repeated cancellation cannot interrupt the bounded teardown.
                for sig in handlers:
                    signal.signal(sig, signal.SIG_IGN)
                result['cleanup_complete'] = _cleanup(process, deadline)
                if not result['cleanup_complete']:
                    _BROKEN = True
                result['returncode'] = process.poll()
                for pipe in (process.stdin, process.stdout, process.stderr):
                    if pipe is not None and not pipe.closed:
                        pipe.close()
        finally:
            try:
                for sig, handler in handlers.items():
                    signal.signal(sig, handler)
                if previous is not None:
                    _subreaper(previous)
            finally:
                _LOCK.release()
    result['elapsed_seconds'] = time.monotonic() - started
    return result
