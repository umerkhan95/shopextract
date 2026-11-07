"""Read product links and pagination from a storefront listing page.

A category, search or brand page lists products as repeated cards. The card
markup follows the platform's storefront theme: Magento renders
``li.product-item`` with ``a.product-item-link``, Salesforce B2C Commerce (SFRA)
renders ``.product[data-pid]`` tiles and pages through ``Search-UpdateGrid``,
WooCommerce renders ``ul.products li.product``. Pages that publish a schema.org
``ItemList`` are read from it when no card markup is present.

Parsing is pure: the caller fetches pages, owns the request budget and decides
what an empty listing means.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup

# (card selector, link selectors in preference order). The first card selector
# that matches anything on the page wins; mixing them would add nav and
# recommendation links that share a generic class.
_CARD_SELECTORS = (
    ("li.product-item", ("a.product-item-link", "a.product-item-photo")),
    (".product[data-pid]", (".pdp-link a[href]", "a.link[href]", "a[href]")),
    ("ul.products li.product", ("a.woocommerce-LoopProduct-link", "a.woocommerce-loop-product__link", "a[href]")),
    (".productGrid .product, article.card", (".card-title a", ".card-figure a", "a[href]")),
    (".product-box", ("a.product-name", "a.product-image-link", "a[href]")),
    ("[itemtype*='schema.org/Product']", ("a[itemprop='url']", "a[href]")),
)

_NEXT_SELECTORS = (
    "link[rel~='next'][href]",
    "a[rel~='next'][href]",
    ".pages-item-next a[href]",
    "a.next.page-numbers[href]",
    ".pagination__next[href]",
)

_SFCC_GRID = re.compile(r"/Search-UpdateGrid\b")
_TOTAL_PATTERNS = (
    re.compile(r"\bof\s+([\d,]+)\b", re.IGNORECASE),
    re.compile(r"([\d,]+)\s+(?:products?|items?|results?)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class ListingPage:
    """Product links found on one listing page and where the listing continues."""

    product_urls: tuple[str, ...]
    next_url: str | None
    total: int | None
    is_product_page: bool
    strategy: str | None


def parse_listing(html: str, page_url: str) -> ListingPage:
    soup = BeautifulSoup(html, "html.parser")
    host = _host(page_url)
    urls, strategy = _card_links(soup, page_url, host)
    if not urls:
        urls = _item_list_links(soup, page_url, host)
        strategy = "schema_org_item_list" if urls else None
    if not urls:
        urls = _product_path_links(soup, page_url, host)
        strategy = "product_path_links" if urls else None
    # A product page also lists related products as cards, so its own
    # declaration decides, not the absence of cards.
    product_page = _declares_product_page(soup, page_url) or (not urls and _has_json_ld_type(soup, "Product"))
    return ListingPage(
        product_urls=tuple(urls),
        next_url=_next_page(soup, page_url, host, len(urls)),
        total=_total(soup),
        is_product_page=product_page,
        strategy=strategy,
    )


def _host(url: str) -> str:
    netloc = urlsplit(url).netloc.lower()
    return netloc[4:] if netloc.startswith("www.") else netloc


def _same_store(url: str, host: str) -> bool:
    parts = urlsplit(url)
    return parts.scheme in ("http", "https") and _host(url) == host


def _canonical(href: str, page_url: str, *, drop_query: bool) -> str:
    parts = urlsplit(urljoin(page_url, href.strip()))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "" if drop_query else parts.query, ""))


def _card_links(soup, page_url: str, host: str) -> tuple[list[str], str | None]:
    for card_selector, link_selectors in _CARD_SELECTORS:
        cards = soup.select(card_selector)
        if not cards:
            continue
        # SFRA tile links carry tracking queries (?source=recommendation); the
        # product identity is the path, so the query is dropped for them only.
        drop_query = "data-pid" in card_selector
        found: list[str] = []
        for card in cards:
            link = next((node for selector in link_selectors for node in card.select(selector)
                         if _usable_href(node.get("href"))), None)
            if link is None:
                continue
            url = _canonical(link["href"], page_url, drop_query=drop_query)
            if _same_store(url, host) and url not in found:
                found.append(url)
        if found:
            return found, card_selector
    return [], None


_PRODUCT_SEGMENTS = {"product", "products", "p"}


def _product_path_links(soup, page_url: str, host: str) -> list[str]:
    """Last resort for themes without card markup: /product/ paths in the main content."""
    main = soup.find("main") or soup.body or soup
    found: list[str] = []
    for anchor in main.select("a[href]"):
        if not _usable_href(anchor.get("href")):
            continue
        url = _canonical(anchor["href"], page_url, drop_query=False)
        segments = {part.lower() for part in urlsplit(url).path.split("/") if part}
        if segments & _PRODUCT_SEGMENTS and _same_store(url, host) and url not in found:
            found.append(url)
    return found


def _usable_href(href) -> bool:
    if not isinstance(href, str):
        return False
    value = href.strip()
    return bool(value) and not value.startswith(("#", "javascript:", "mailto:", "tel:"))


def _json_ld_nodes(soup):
    for script in soup.select("script[type='application/ld+json']"):
        try:
            value = json.loads(script.string or script.get_text() or "")
        except (ValueError, TypeError):
            continue
        stack = [value]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, dict):
                yield node
                if isinstance(node.get("@graph"), list):
                    stack.extend(node["@graph"])
                if isinstance(node.get("mainEntity"), (dict, list)):
                    stack.append(node["mainEntity"])


def _types(node) -> set[str]:
    value = node.get("@type")
    values = value if isinstance(value, list) else [value]
    return {item for item in values if isinstance(item, str)}


def _has_json_ld_type(soup, name: str) -> bool:
    return any(name in _types(node) for node in _json_ld_nodes(soup))


# Layout handles the platform puts on the product view's <body>.
_PRODUCT_BODY_CLASSES = {"catalog-product-view", "single-product"}


def _declares_product_page(soup, page_url: str) -> bool:
    """True when the page says it shows one product: JSON-LD, Open Graph or layout.

    A listing that publishes an ItemList is never a product page. A JSON-LD
    Product counts only when it is the page's single Product; category pages
    that mark up every card carry several. SFRA wraps its product view in
    ``.product-detail[data-pid]`` and names the product id in the URL.
    """
    nodes = list(_json_ld_nodes(soup))
    if any("ItemList" in _types(node) for node in nodes):
        return False
    if sum("Product" in _types(node) for node in nodes) == 1:
        return True
    og_type = soup.select_one("meta[property='og:type'][content]")
    if og_type is not None and og_type["content"].strip().lower() in ("product", "product.item", "og:product"):
        return True
    body = soup.body
    if body is not None and _PRODUCT_BODY_CLASSES.intersection(body.get("class") or ()):
        return True
    details = soup.select(".product-detail[data-pid]")
    pid = details[0].get("data-pid", "").strip() if len(details) == 1 else ""
    return bool(pid) and pid in urlsplit(page_url).path


def _item_list_links(soup, page_url: str, host: str) -> list[str]:
    found: list[str] = []
    for node in _json_ld_nodes(soup):
        # BreadcrumbList is also a list of ListItem, but it lists categories.
        if "ItemList" not in _types(node):
            continue
        elements = node.get("itemListElement")
        for element in elements if isinstance(elements, list) else []:
            if not isinstance(element, dict):
                continue
            item = element.get("item")
            href = element.get("url")
            if isinstance(item, dict):
                href = href or item.get("url") or item.get("@id")
            elif isinstance(item, str):
                href = href or item
            if not isinstance(href, str):
                continue
            url = _canonical(href, page_url, drop_query=False)
            if _same_store(url, host) and url not in found:
                found.append(url)
    return found


def _next_page(soup, page_url: str, host: str, product_count: int) -> str | None:
    for selector in _NEXT_SELECTORS:
        node = soup.select_one(selector)
        if node is not None and _usable_href(node.get("href")):
            url = _canonical(node["href"], page_url, drop_query=False)
            if _same_store(url, host) and url != page_url:
                return url
    return _sfcc_next_grid(soup, page_url, host, product_count)


def _sfcc_next_grid(soup, page_url: str, host: str, product_count: int) -> str | None:
    """Continue an SFRA grid through Search-UpdateGrid with start advanced by sz."""
    if not product_count:
        return None
    template = None
    for node in soup.select("[data-url]"):
        if _SFCC_GRID.search(node.get("data-url") or ""):
            template = node["data-url"]
            break
    if template is None:
        footer = soup.select_one("[data-sort-options]")
        try:
            options = json.loads(footer["data-sort-options"]) if footer else {}
        except (ValueError, TypeError):
            options = {}
        for option in options.get("options", []) if isinstance(options, dict) else []:
            if isinstance(option, dict) and _SFCC_GRID.search(str(option.get("url", ""))):
                template = option["url"]
                break
    if template is None:
        return None
    url = urljoin(page_url, template)
    if not _same_store(url, host):
        return None
    parts = urlsplit(url)
    params = dict(parse_qsl(parts.query, keep_blank_values=True))
    current = dict(parse_qsl(urlsplit(page_url).query))
    try:
        size = int(params.get("sz") or product_count)
        start = int(current.get("start", 0)) if _SFCC_GRID.search(page_url) else 0
    except ValueError:
        return None
    if size <= 0:
        return None
    params["start"] = str(start + size)
    params["sz"] = str(size)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(params), ""))


def _total(soup) -> int | None:
    for node in _json_ld_nodes(soup):
        count = node.get("numberOfItems") if "ItemList" in _types(node) else None
        if isinstance(count, int) and not isinstance(count, bool) and count >= 0:
            return count
    for selector in (".toolbar-amount", ".woocommerce-result-count", ".result-count", ".search-result-count"):
        node = soup.select_one(selector)
        if node is None:
            continue
        text = node.get_text(" ", strip=True)
        for pattern in _TOTAL_PATTERNS:
            match = pattern.search(text)
            if match:
                return int(match.group(1).replace(",", ""))
    return None
