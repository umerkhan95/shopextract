"""Lightweight shared HTTP defaults; browser configuration reexports these objects."""

# Modern Chrome UA for httpx (non-browser) requests
HTTPX_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

# Default HTTP headers
DEFAULT_HEADERS: dict[str, str] = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def get_default_user_agent() -> str:
    """Return a modern Chrome User-Agent for httpx (non-browser) requests."""
    return HTTPX_USER_AGENT
