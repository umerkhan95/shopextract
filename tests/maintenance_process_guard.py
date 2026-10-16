"""Sequential process-group deadline enforcement for bounded verification."""
import os
import signal
import subprocess
import time


def run_group(command, *, timeout, stdout, stderr):
    started = time.monotonic()
    process = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
    previous_handler = signal.getsignal(signal.SIGTERM)
    def forward(signum, frame):
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=.5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=.5)
        except ProcessLookupError:
            pass
        raise SystemExit(128 + signum)
    signal.signal(signal.SIGTERM, forward)
    timed_out = False
    cleanup = 0.0
    try:
        process.wait(timeout=max(0, timeout - (time.monotonic() - started)))
    except subprocess.TimeoutExpired:
        timed_out = True
        cleanup_started = time.monotonic()
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=.5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=max(.001, 1 - (time.monotonic() - cleanup_started)))
        cleanup = time.monotonic() - cleanup_started
    signal.signal(signal.SIGTERM, previous_handler)
    return {'returncode':process.returncode,'timed_out':timed_out,
            'seconds':time.monotonic()-started,'cleanup_seconds':cleanup,'pid':process.pid}
