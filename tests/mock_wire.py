"""Swap the network under a guarded HTTPX client for a mock, keeping the guard."""
import httpx

from shopextract._url_safety import GuardedHTTPXTransport


def mock_wire(kwargs, mock: httpx.MockTransport) -> dict:
    """Client kwargs whose network is ``mock`` behind shopextract's URL guard.

    Production clients arrive with a ``GuardedHTTPXTransport`` whose wire is the
    real network; it is replaced by a guarded one on ``mock``. Clients without a
    transport get the same. Any other explicit transport, such as the MCP tool
    layer's own guard, is kept: it already carries the test's wire.
    """
    transport = kwargs.get("transport")
    if transport is None or type(transport) is GuardedHTTPXTransport:
        return {**kwargs, "transport": GuardedHTTPXTransport(wire_transport=mock)}
    return kwargs
