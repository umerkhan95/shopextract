"""Where an unexpected exception was raised, without its message.

Error boundaries turn unexpected exceptions into a generic internal failure and
must not echo the exception text, which can hold credentials or provider bodies.
The class name and the innermost shopextract frame are safe to report and are
enough to start debugging.
"""
from __future__ import annotations

from pathlib import Path

_PACKAGE = Path(__file__).resolve().parent


def failure_origin(exc: BaseException) -> str:
    """Return ``"TypeError at extractors/feed.py:42"`` for an exception."""
    location = None
    tb = exc.__traceback__
    while tb is not None:
        path = Path(tb.tb_frame.f_code.co_filename)
        try:
            location = f"{path.resolve().relative_to(_PACKAGE).as_posix()}:{tb.tb_lineno}"
        except ValueError:
            pass
        tb = tb.tb_next
    name = type(exc).__name__
    return f"{name} at {location}" if location else name
