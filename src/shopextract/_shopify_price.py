"""Small source-qualified Shopify price markers shared by normalization and scoring."""
from __future__ import annotations

import re
from html import unescape


_REQUEST_PRICE = re.compile(r"\bprice\s+on\s+request\b", re.IGNORECASE)


def request_price_source(raw: dict) -> str | None:
    """Return the source path only when Shopify source text says this exact marker."""
    sources = [("/title", raw.get("title")), ("/body_html", raw.get("body_html")),
               ("/description", raw.get("description")), ("/price_note", raw.get("price_note"))]
    for index, variant in enumerate(raw.get("variants") or []):
        if isinstance(variant, dict):
            sources.append((f"/variants/{index}/price_note", variant.get("price_note")))
    for path, value in sources:
        if isinstance(value, str):
            visible = re.sub(r"<(script|style)\b[^>]*>.*?</\1\s*>", " ", value,
                             flags=re.IGNORECASE | re.DOTALL)
            visible = unescape(re.sub(r"<[^>]+>", " ", visible))
            if _REQUEST_PRICE.search(visible):
                return path
    return None


def has_explicit_request_price_marker(raw: dict) -> bool:
    return request_price_source(raw) is not None
