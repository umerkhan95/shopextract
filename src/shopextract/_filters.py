"""URL filtering constants and helpers for URL discovery.

Centralizes denylist logic, platform-specific sitemap URLs, and product
URL patterns.
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

# Platform-specific product sitemap paths
PLATFORM_PRODUCT_SITEMAPS: dict[str, list[str]] = {
    "shopify": ["/sitemap_products_1.xml"],
    "woocommerce": ["/product-sitemap.xml", "/product-sitemap1.xml"],
    "magento": ["/pub/media/sitemap/sitemap.xml", "/media/sitemap.xml"],
    "bigcommerce": ["/xmlsitemap.php"],
    "shopware": ["/sitemap.xml"],
    "generic": [],
}

# Exact paths that are never product pages
NON_PRODUCT_PATHS: set[str] = {
    "/", "/about", "/about-us", "/contact", "/contact-us",
    "/blog", "/cart", "/checkout", "/account", "/login", "/register",
    "/search", "/faq", "/privacy", "/privacy-policy",
    "/terms", "/terms-of-service", "/terms-and-conditions",
    "/shipping", "/shipping-policy", "/returns", "/return-policy",
    "/refund-policy", "/sitemap", "/brands", "/categories",
    "/pages", "/wishlist", "/compare", "/basket", "/help",
    "/support", "/careers", "/press", "/newsletter",
    "/my-account", "/order-tracking", "/rewards",
}

# Path segments that indicate non-product pages
NON_PRODUCT_SEGMENTS: set[str] = {
    "checkout", "basket", "cart", "login", "register", "account",
    "blog", "faq", "help", "support", "careers", "press",
    "my-account", "order-tracking", "wp-admin", "wp-includes",
    "feed", "author", "tag", "category", "wp-login.php",
    "newsletter", "unsubscribe",
    "journal", "news", "stories", "articles", "recipe", "recipes",
    "tea_collections", "product_collection",
    "our-story", "sustainability", "charity", "events",
    "product-category", "product-tag",
}

# File extensions that are never product pages
_NON_PRODUCT_EXTENSIONS: set[str] = {
    ".xml", ".json", ".txt", ".pdf", ".png", ".jpg", ".jpeg",
    ".gif", ".svg", ".css", ".js", ".ico", ".woff", ".woff2",
    ".ttf", ".eot", ".map", ".gz",
}

# Date-path blog pattern: /YYYY/MM/DD/slug
_DATE_PATH_RE = re.compile(r"/\d{4}/\d{2}/\d{2}/")


def is_non_product_url(url: str) -> bool:
    """Return True if the URL is almost certainly NOT a product page.

    Checks:
    1. File extension denylist
    2. Exact path match against NON_PRODUCT_PATHS
    3. Any path segment in NON_PRODUCT_SEGMENTS
    4. Date-path blog pattern (/YYYY/MM/DD/slug)
    """
    parsed = urlparse(url)
    path = parsed.path.rstrip("/").lower()

    # 1. File extension
    dot_idx = path.rfind(".")
    if dot_idx != -1:
        ext = path[dot_idx:]
        if ext in _NON_PRODUCT_EXTENSIONS:
            return True

    # 2. Exact path match
    if path in NON_PRODUCT_PATHS or path == "":
        return True

    # 3. Segment match
    segments = set(path.strip("/").split("/"))
    if segments & NON_PRODUCT_SEGMENTS:
        return True

    # 4. Date-path blog posts
    if _DATE_PATH_RE.search(path):
        return True

    return False
