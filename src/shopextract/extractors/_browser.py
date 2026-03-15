"""Shared browser configuration for crawl4ai-based extractors.

Provides three anti-bot tiers:
  - STANDARD: Basic headless browser, fast, for sites with no bot protection.
  - STEALTH:  Stealth patches (webdriver flag removal, fingerprint spoofing).
  - UNDETECTED: crawl4ai UndetectedAdapter with deep-level browser patches.
"""

from __future__ import annotations

import logging
from enum import Enum

from crawl4ai import BrowserConfig, CacheMode, CrawlerRunConfig, UndetectedAdapter
from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy

try:
    from crawl4ai import DefaultMarkdownGenerator
    from crawl4ai.content_filter_strategy import PruningContentFilter
except ImportError:
    DefaultMarkdownGenerator = None  # type: ignore[assignment,misc]
    PruningContentFilter = None  # type: ignore[assignment,misc]

try:
    from crawl4ai import GeolocationConfig
except ImportError:
    GeolocationConfig = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)


# JS condition that returns true when product content is likely rendered.
PRODUCT_WAIT_CONDITION = (
    'js:() => {'
    '  const hasProduct = !!(document.querySelector("[itemtype*=Product]") || '
    '    document.querySelector("[itemtype*=product]") || '
    '    document.querySelector(".product") || '
    '    document.querySelector("[data-product]") || '
    '    document.querySelector("[data-product-id]") || '
    '    document.querySelectorAll("[class*=product]").length > 0 || '
    '    document.querySelector("[data-testid*=product]") || '
    '    document.querySelector("script[type=\\"application/ld+json\\"]"));'
    '  if (!hasProduct) return false;'
    '  const priceEl = document.querySelector("[data-price], .price, .product-price, '
    '    [class*=price], [itemprop=price], [data-product-price]");'
    '  if (priceEl) return !!(priceEl.textContent && priceEl.textContent.trim().match(/\\d/));'
    '  const jsonLd = document.querySelector("script[type=\\"application/ld+json\\"]");'
    '  if (jsonLd) { try { const d = JSON.parse(jsonLd.textContent);'
    '    const hasPrice = JSON.stringify(d).match(/"price"\\s*:\\s*"?[\\d.]+/);'
    '    if (hasPrice) return true; } catch(e) {} }'
    '  return false;'
    '}'
)

DEFAULT_PAGE_TIMEOUT = 30000
DEFAULT_DELAY_BEFORE_RETURN = 3.0

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

# Cookie consent dismiss script
DISMISS_COOKIE_JS = """
(function() {
  const selectors = [
    '#onetrust-accept-btn-handler',
    '.onetrust-close-btn-handler',
    '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll',
    '#CybotCookiebotDialogBodyButtonAccept',
    '[data-cookieconsent="accept"]',
    'button[aria-label="Accept cookies"]',
    'button[aria-label="Accept all cookies"]',
    'button[aria-label="Alle akzeptieren"]',
    'button[aria-label="Alle Cookies akzeptieren"]',
    '.cc-accept', '.cc-allow', '.cc-dismiss',
    '[data-testid="cookie-accept"]',
    'button.agree-btn',
    '#accept-cookies',
    '.cookie-accept-all',
  ];
  const textPatterns = [
    /^accept all$/i,
    /^accept cookies$/i,
    /^alle akzeptieren$/i,
    /^alle cookies akzeptieren$/i,
    /^i agree$/i,
    /^got it$/i,
  ];
  for (const sel of selectors) {
    const el = document.querySelector(sel);
    if (el) { el.click(); return; }
  }
  const buttons = document.querySelectorAll('button, a.btn, a.button');
  for (const btn of buttons) {
    const text = (btn.textContent || '').trim();
    for (const pat of textPatterns) {
      if (pat.test(text)) { btn.click(); return; }
    }
  }
})();
"""


def get_default_user_agent() -> str:
    """Return a modern Chrome User-Agent for httpx (non-browser) requests."""
    return HTTPX_USER_AGENT


class StealthLevel(str, Enum):
    """Anti-bot protection tier for browser-based crawling."""

    STANDARD = "standard"
    STEALTH = "stealth"
    UNDETECTED = "undetected"


def get_browser_config(
    stealth_level: StealthLevel = StealthLevel.STANDARD,
    headless: bool = True,
    text_mode: bool = False,
) -> BrowserConfig:
    """Create a BrowserConfig for the requested anti-bot tier."""
    headers = {**DEFAULT_HEADERS}

    if stealth_level == StealthLevel.STANDARD:
        return BrowserConfig(
            headless=headless,
            verbose=False,
            text_mode=text_mode,
            headers=headers,
        )

    # STEALTH and UNDETECTED both use stealth + large viewport
    return BrowserConfig(
        headless=headless,
        verbose=False,
        text_mode=text_mode,
        enable_stealth=True,
        viewport_width=1920,
        viewport_height=1080,
        headers=headers,
    )


def get_crawler_strategy(
    stealth_level: StealthLevel,
    browser_config: BrowserConfig | None = None,
) -> AsyncPlaywrightCrawlerStrategy | None:
    """Create a crawler strategy with UndetectedAdapter if needed."""
    if stealth_level != StealthLevel.UNDETECTED:
        return None

    if browser_config is None:
        browser_config = get_browser_config(stealth_level)

    adapter = UndetectedAdapter()
    return AsyncPlaywrightCrawlerStrategy(
        browser_config=browser_config,
        browser_adapter=adapter,
    )


def get_crawl_config(
    stealth_level: StealthLevel = StealthLevel.STANDARD,
    extraction_strategy=None,
    markdown_generator=None,
    deep_crawl_strategy=None,
    wait_until: str = "domcontentloaded",
    wait_for: str | None = PRODUCT_WAIT_CONDITION,
    page_timeout: int = DEFAULT_PAGE_TIMEOUT,
    delay_before_return_html: float = DEFAULT_DELAY_BEFORE_RETURN,
    scan_full_page: bool = True,
    remove_overlay_elements: bool = True,
    scroll_delay: float = 0.5,
    check_robots_txt: bool = True,
    locale: str = "en-US",
    timezone: str = "America/New_York",
) -> CrawlerRunConfig:
    """Create a CrawlerRunConfig with anti-bot settings for the requested tier."""
    use_anti_bot = stealth_level in (StealthLevel.STEALTH, StealthLevel.UNDETECTED)

    if use_anti_bot and page_timeout == DEFAULT_PAGE_TIMEOUT:
        page_timeout = 60000

    if use_anti_bot and delay_before_return_html == DEFAULT_DELAY_BEFORE_RETURN:
        delay_before_return_html = 4.0

    if markdown_generator is None and DefaultMarkdownGenerator is not None and PruningContentFilter is not None:
        markdown_generator = DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.48),
        )

    geo_kwargs: dict = {}
    if GeolocationConfig is not None:
        geo_kwargs["geolocation"] = GeolocationConfig(
            latitude=40.7128,
            longitude=-74.0060,
            accuracy=100,
        )
        geo_kwargs["timezone_id"] = timezone

    return CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        markdown_generator=markdown_generator,
        deep_crawl_strategy=deep_crawl_strategy,
        cache_mode=CacheMode.BYPASS,
        wait_until=wait_until,
        wait_for=wait_for,
        wait_for_images=True,
        page_timeout=page_timeout,
        delay_before_return_html=delay_before_return_html,
        simulate_user=use_anti_bot,
        magic=use_anti_bot,
        override_navigator=use_anti_bot,
        scan_full_page=scan_full_page,
        remove_overlay_elements=remove_overlay_elements,
        scroll_delay=scroll_delay,
        check_robots_txt=check_robots_txt,
        js_code=DISMISS_COOKIE_JS,
        locale=locale,
        **geo_kwargs,
    )


async def fetch_html_with_browser(
    url: str,
    stealth_level: StealthLevel = StealthLevel.STEALTH,
) -> str | None:
    """Fetch page HTML using crawl4ai browser (for bot-protected sites).

    Returns HTML string on success, None on failure.
    """
    from crawl4ai import AsyncWebCrawler

    try:
        browser_config = get_browser_config(stealth_level)
        crawl_config = get_crawl_config(stealth_level=stealth_level)
        crawler_strategy = get_crawler_strategy(stealth_level, browser_config)

        async with AsyncWebCrawler(
            config=browser_config,
            crawler_strategy=crawler_strategy,
        ) as crawler:
            result = await crawler.arun(url=url, config=crawl_config)
            if result.success and result.html:
                return result.html
            return None
    except Exception as e:
        logger.error("Browser fetch error for %s: %s", url, e)
        return None
