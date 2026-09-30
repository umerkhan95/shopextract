"""Stable observation scopes, separate from individual product identity."""
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from ._models import Platform


def catalog_scope(url: str, platform: Platform | str) -> str:
    """Keep collection paths and query context; normalize host, slash and fragment."""
    parts = urlsplit(url if "://" in url else f"https://{url}")
    canonical = urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                           parts.path.rstrip("/"), urlencode(sorted(parse_qsl(parts.query, keep_blank_values=True))), ""))
    kind = getattr(platform, "value", platform)
    return f"{kind}:catalog:{canonical}"
