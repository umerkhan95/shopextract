"""Stable observation scopes, separate from individual product identity."""
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from ._models import Platform


def catalog_scope(url: str, platform: Platform | str) -> str:
    """Keep collection paths and query context; normalize host, slash and fragment."""
    parts = urlsplit(url if "://" in url else f"https://{url}")
    canonical = urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                           parts.path.rstrip("/"), urlencode(sorted(parse_qsl(parts.query, keep_blank_values=True))), ""))
    kind = getattr(platform, "value", platform)
    return f"{kind}:catalog:{canonical}"


_SHOPIFY_COLLECTION = re.compile(r"^(?P<base>(?:/[^/]+)*?/collections/[^/]+)/?$")
# Shopify routes that are pages, not a catalog base (a locale or merchant base path is).
_SHOPIFY_PAGE_SEGMENTS = {"products", "pages", "blogs", "search", "cart", "account", "policies", "collections"}


def is_store_root(url: str) -> bool:
    """True when the URL names the whole store rather than one of its pages."""
    return not urlsplit(url if "://" in url else f"https://{url}").path.strip("/")


def shopify_catalog_base(url: str) -> str | None:
    """Base for /products.json that honours the requested scope.

    The store root, a locale prefix (/en-pk) or a merchant base path reads the
    catalog under it; /collections/<handle> reads that collection. A product,
    search or content page has no catalog endpoint, so None is returned.
    """
    parts = urlsplit(url if "://" in url else f"https://{url}")
    origin = f"{parts.scheme}://{parts.netloc}"
    match = _SHOPIFY_COLLECTION.match(parts.path)
    if match:
        return origin + match.group("base")
    segments = [segment for segment in parts.path.split("/") if segment]
    if any(segment.lower() in _SHOPIFY_PAGE_SEGMENTS for segment in segments):
        return None
    return origin + "".join("/" + segment for segment in segments)
