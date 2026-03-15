"""Extract price, title, and currency from rendered markdown text.

Stateless utility -- no LLM, no browser, no network.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

# Symbol -> ISO code mapping
_SYMBOL_TO_CODE: dict[str, str] = {
    "$": "USD", "\u20ac": "EUR", "\u00a3": "GBP", "\u00a5": "JPY",
    "\u20b9": "INR", "\u20a9": "KRW", "\u20bd": "RUB", "R$": "BRL",
    "kr": "SEK", "z\u0142": "PLN", "CHF": "CHF", "A$": "AUD",
    "C$": "CAD", "NZ$": "NZD", "HK$": "HKD", "S$": "SGD",
}

_ISO_CODES = frozenset({
    "USD", "EUR", "GBP", "JPY", "CAD", "AUD", "NZD", "CHF", "SEK", "NOK",
    "DKK", "PLN", "CZK", "HUF", "INR", "KRW", "BRL", "RUB", "HKD", "SGD",
    "MXN", "ZAR", "TRY", "THB", "MYR", "PHP", "IDR", "TWD", "AED", "SAR",
    "CNY", "VND", "BGN", "RON", "HRK", "ILS", "CLP", "COP", "PEN", "ARS",
    "UAH", "KZT", "QAR", "KWD", "BHD", "OMR", "JOD", "EGP", "NGN", "KES",
})

_PRICE_RE = re.compile(
    r"""
    (?:
        (?P<sym_pre>[\u20ac\u00a3\u00a5\u20b9\u20a9\u20bd]|
           (?:R\$|A\$|C\$|NZ\$|HK\$|S\$|\$)|
           (?:kr|z\u0142|CHF)
        )
        \s*
    )?
    (?P<amount>
        \d{1,3}(?:[,.\s]\d{3})*
        (?:[.,]\d{1,2})?
        |
        \d+[.,]\d{1,2}
    )
    (?:
        \s*
        (?P<sym_post>[\u20ac\u00a3\u00a5\u20b9\u20a9\u20bd]|
           (?:kr|z\u0142)
        )
    )?
    (?:
        \s+
        (?P<code>[A-Z]{3})
    )?
    """,
    re.VERBOSE,
)

_CODE_PRICE_RE = re.compile(
    r"""
    (?P<code>[A-Z]{3})
    \s+
    (?P<amount>
        \d{1,3}(?:[,.\s]\d{3})*
        (?:[.,]\d{1,2})?
        |
        \d+[.,]\d{1,2}
    )
    """,
    re.VERBOSE,
)

_NOISE_PATTERNS = re.compile(
    r"(?i)\b(?:shipping|subtotal|total|tax|discount|coupon|cart|"
    r"was\s+\$|original|compare|regular|list\s+price|you\s+save|"
    r"msrp|rrp|from\s+\$|starting\s+at|add\s+to|"
    r"rug\s+pad|protection\s+plan|warranty|accessory|"
    r"free\s+shipping|estimated|per\s+month|\/month|installment)\b"
)


def _normalize_amount(raw: str) -> str | None:
    cleaned = raw.replace(" ", "")
    if not cleaned or not any(c.isdigit() for c in cleaned):
        return None

    if re.search(r",\d{2}$", cleaned) and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif re.search(r",\d{2}$", cleaned):
        cleaned = cleaned.replace(",", ".")
    else:
        cleaned = cleaned.replace(",", "")

    try:
        val = float(cleaned)
    except ValueError:
        return None

    if val <= 0 or val > 1_000_000:
        return None

    return f"{val:.2f}"


def _resolve_currency(sym_pre: str | None, sym_post: str | None, code: str | None) -> str | None:
    if code and code in _ISO_CODES:
        return code
    sym = (sym_pre or sym_post or "").strip()
    if sym:
        return _SYMBOL_TO_CODE.get(sym)
    return None


def extract_price(text: str) -> tuple[str, str | None] | None:
    """Extract the first credible price + currency from text."""
    for m in _CODE_PRICE_RE.finditer(text):
        code = m.group("code")
        if code not in _ISO_CODES:
            continue
        amount = _normalize_amount(m.group("amount"))
        if amount:
            return amount, code

    for m in _PRICE_RE.finditer(text):
        line_start = text.rfind("\n", 0, m.start()) + 1
        line_end = text.find("\n", m.end())
        if line_end == -1:
            line_end = len(text)
        line = text[line_start:line_end]

        if _NOISE_PATTERNS.search(line):
            continue

        amount = _normalize_amount(m.group("amount"))
        if not amount:
            continue

        currency = _resolve_currency(m.group("sym_pre"), m.group("sym_post"), m.group("code"))
        return amount, currency

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


def extract(markdown: str, url: str = "") -> dict:
    """Extract price, title, and currency from markdown text.

    Returns:
        Dict with available keys: {name, price, currency}. May be partial or empty.
    """
    result: dict = {}

    title = extract_title(markdown)
    if title:
        result["name"] = title

    price_data = extract_price(markdown)
    if price_data:
        amount, currency = price_data
        result["price"] = amount
        if currency:
            result["currency"] = currency

    return result
