"""Extract price, title, and currency from rendered markdown text.

Stateless utility -- no LLM, no browser, no network.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

from .._normalization import Normalizer
from .._currencies import is_pricing_currency

# Bare dollar/yen/kr have multiple currency authorities and need captured context.
_SYMBOL_TO_CODE = {'€':'EUR','₹':'INR','₽':'RUB',
                  'R$':'BRL','A$':'AUD','C$':'CAD','NZ$':'NZD','HK$':'HKD','S$':'SGD','zł':'PLN'}
_PRICE_RE = re.compile(r'(?<![\w.,-])(?:(?P<pre>[A-Z]{3}|NZ\$|HK\$|R\$|A\$|C\$|S\$|[$€£¥₹₩₽]|kr|zł)\s*)?(?P<amount>-?\d[\d,.]*(?:[ \u00a0]\d[\d,.]*)*)(?:\s*(?P<post>[A-Z]{3}|[$€£¥₹₩₽]|kr|zł))?(?![\w.,])')

_NOISE_PATTERNS = re.compile(
    r"(?i)\b(?:shipping|subtotal|total|tax|discount|coupon|cart|"
    r"was\s+\$|original|compare|regular|list\s+price|you\s+save|"
    r"msrp|rrp|from\s+\$|starting\s+at|add\s+to|"
    r"rug\s+pad|protection\s+plan|warranty|accessory|"
    r"free\s+shipping|estimated|per\s+month|\/month|installment)\b"
)


def _normalize_amount(raw: str, *, currency=None, locale=None) -> str | None:
    n=Normalizer({'amount':raw})
    value=n.money('price','/amount',css=True,currency=currency,locale=locale)
    return str(value) if n.outcomes['/price'].accepted else None


def extract_price(text: str, *, currency=None, locale=None) -> tuple[str,str | None] | None:
    """Discover complete tokens; conversion and currency authority are shared."""
    for m in _PRICE_RE.finditer(text):
        line=text[text.rfind('\n',0,m.start())+1:text.find('\n',m.end()) if '\n' in text[m.end():] else len(text)]
        if _NOISE_PATTERNS.search(line):continue
        authorities=[]
        for token in (m.group('pre'),m.group('post')):
            if token:
                code=token if is_pricing_currency(token) else _SYMBOL_TO_CODE.get(token)
                if code:authorities.append(code)
        if currency:authorities.append(currency)
        n=Normalizer({str(i):v for i,v in enumerate(authorities)})
        code=n.currency('currency',*['/'+str(i) for i in range(len(authorities))]) if authorities else ''
        # Context still disambiguates numeric grouping when authorities conflict.
        amount=_normalize_amount(m.group('amount'),currency=code or currency,locale=locale)
        if amount is not None:return amount,code or None
    return None


def extract_title(markdown: str) -> str | None:
    """Extract product title from markdown headings."""
    m = re.search(r"^#\s+(.+)$", markdown, re.MULTILINE)
    if m:
        title = m.group(1).strip()
        if 3 <= len(title) <= 300:
            return title

    m = re.search(r"^##\s+(.+)$", markdown, re.MULTILINE)
    if m:
        title = m.group(1).strip()
        if 3 <= len(title) <= 300:
            return title

    m = re.search(r"^\*\*(.+?)\*\*", markdown, re.MULTILINE)
    if m:
        title = m.group(1).strip()
        if 3 <= len(title) <= 300:
            return title

    return None


def extract(markdown: str, url: str = "", *, currency=None, locale=None) -> dict:
    """Extract price, title, and currency from markdown text.

    Returns:
        Dict with available keys: {name, price, currency}. May be partial or empty.
    """
    result: dict = {}

    title = extract_title(markdown)
    if title:
        result["name"] = title

    price_data = extract_price(markdown,currency=currency,locale=locale)
    if price_data:
        amount, currency = price_data
        result["price"] = amount
        if currency:
            result["currency"] = currency

    return result
