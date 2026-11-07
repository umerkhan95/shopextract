"""Client-rendered storefronts read from the browser-rendered DOM.

Some stores ship an empty application shell: the server HTML has no product
links, no schema.org data and no Open Graph product tags, and the catalog API is
request-signed and response-encrypted (haiermall.pk: crypto-js signs every call
to api.haiermall.pk and the JSON body arrives as ciphertext). The only stable
public contract left is what the store renders for a shopper.

A profile names that contract for one storefront application:

* listing cards carry no ``href``; the app opens a product with
  ``window.open``/``history.pushState`` from a click handler, so the listing
  script patches both, clicks each card, and records the URL the app asked for;
* pagination is a row of numbered buttons;
* product fields are read from the rendered product page by CSS selector.

The listing script writes what it found into the DOM as JSON so that the HTML
crawl4ai returns carries it. Signed APIs are never called directly.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from .._capture import capture

RESULT_ID = 'shopextract-rendered-listing'
# Wall-clock budget for the in-page listing script, in milliseconds.
LISTING_SCRIPT_BUDGET_MS = 45000


@dataclass(frozen=True)
class RenderedProfile:
    name: str
    hosts: frozenset[str]
    currency: str
    card: str
    page_buttons: str
    active_page: str
    product_ready: str
    title: str
    price: str
    compare_at_price: str
    availability: str
    option_rows: str
    option_key: str
    option_selected: str
    images: str
    breadcrumb: str
    product_path: str

    def matches(self, url: str) -> bool:
        host = urlsplit(url).netloc.lower()
        return (host[4:] if host.startswith('www.') else host) in self.hosts

    def is_product_url(self, url: str) -> bool:
        return urlsplit(url).path.startswith(self.product_path)


# Observed on 2026-11-07 (Vue 3 + Element Plus storefront).
HAIER_MALL = RenderedProfile(
    name='haier_mall',
    hosts=frozenset({'haiermall.pk'}),
    currency='PKR',
    card='.commodity-item',
    page_buttons='.page-box .main .rowSC > button',
    active_page='xuan',
    product_ready='.pro-main-center .pro-name',
    title='.pro-main-center .pro-name',
    price='.pro-main-center .amount-num',
    compare_at_price='.pro-main-center .mrp-num',
    availability='.pro-main-center .availability',
    option_rows='.pro-main-center .pro_shux',
    option_key='.key',
    option_selected='.value .xuan',
    images='.pro-main-left img',
    breadcrumb='.breadcrumb .item',
    product_path='/en/products/',
)

PROFILES = (HAIER_MALL,)


def profile_for(url: str) -> RenderedProfile | None:
    return next((profile for profile in PROFILES if profile.matches(url)), None)


def listing_script(profile: RenderedProfile, max_urls: int, max_pages: int) -> str:
    """In-page script: click each card with navigation trapped, then turn pages."""
    settings = json.dumps({'card': profile.card, 'buttons': profile.page_buttons,
                           'active': profile.active_page, 'maxUrls': max_urls,
                           'maxPages': max_pages, 'budget': LISTING_SCRIPT_BUDGET_MS, 'id': RESULT_ID})
    return f"""
const s = {settings};
const started = Date.now();
const sleep = ms => new Promise(r => setTimeout(r, ms));
const urls = [], seen = new Set();
let pages = 0, exhausted = false, error = null;
const record = u => {{ if (u == null) return; const v = new URL(String(u), location.href).href;
  if (!seen.has(v)) {{ seen.add(v); urls.push(v); }} }};
const open = window.open, push = history.pushState, replace = history.replaceState;
window.open = u => {{ record(u); return null; }};
history.pushState = function(state, title, u) {{ record(u); }};
history.replaceState = function(state, title, u) {{ if (u != null && new URL(String(u), location.href).pathname !== location.pathname) record(u); else return replace.apply(this, arguments); }};
const firstTitle = () => {{ const c = document.querySelector(s.card); return c ? c.innerText.slice(0, 200) : null; }};
try {{
  while (true) {{
    pages += 1;
    let cut = false;
    for (const card of document.querySelectorAll(s.card)) {{
      if (urls.length >= s.maxUrls || Date.now() - started > s.budget) {{ cut = true; break; }}
      card.click();
      await sleep(50);
    }}
    const buttons = [...document.querySelectorAll(s.buttons)].filter(b => /^\\d+$/.test(b.textContent.trim()));
    const current = buttons.findIndex(b => b.classList.contains(s.active));
    const next = current >= 0 ? buttons[current + 1] : null;
    // The last page read in full is the end of the listing; a page budget is not.
    if (!next) {{ exhausted = !cut; break; }}
    if (urls.length >= s.maxUrls || pages >= s.maxPages || Date.now() - started > s.budget) break;
    const before = firstTitle();
    next.click();
    let changed = false;
    for (let i = 0; i < 60 && !changed; i++) {{ await sleep(250); changed = firstTitle() !== before; }}
    if (!changed) {{ error = 'page_did_not_change'; break; }}
  }}
}} catch (e) {{ error = String(e); }}
finally {{ window.open = open; history.pushState = push; history.replaceState = replace; }}
const node = document.createElement('script');
node.type = 'application/json'; node.id = s.id;
node.textContent = JSON.stringify({{urls, pages, exhausted, error}});
document.body.appendChild(node);
return {{count: urls.length, pages, exhausted, error}};
"""


@dataclass(frozen=True)
class RenderedListing:
    product_urls: tuple[str, ...]
    pages: int
    exhausted: bool
    error: str | None


def read_listing(html: str, page_url: str, profile: RenderedProfile) -> RenderedListing | None:
    soup = BeautifulSoup(html or '', 'html.parser')
    node = soup.find('script', id=RESULT_ID)
    if node is None:
        return None
    try:
        value = json.loads(node.get_text() or '')
    except ValueError:
        return None
    host = urlsplit(page_url).netloc.lower()
    urls = tuple(dict.fromkeys(
        url for url in value.get('urls') or [] if isinstance(url, str)
        and urlsplit(url).netloc.lower() == host and profile.is_product_url(url)))
    return RenderedListing(urls, int(value.get('pages') or 0), bool(value.get('exhausted')),
                           value.get('error') if isinstance(value.get('error'), str) else None)


def _text(soup, selector):
    node = soup.select_one(selector)
    return ' '.join(node.get_text(' ', strip=True).split()) if node else None


def availability_in_stock(text):
    if not text:
        return None
    value = text.split(':', 1)[-1].strip().casefold()
    if value in ('in stock', 'available'):
        return True
    if value in ('out of stock', 'sold out', 'unavailable'):
        return False
    return None


def read_product(html: str, page_url: str, profile: RenderedProfile) -> dict | None:
    """Raw product from the rendered page; None when the product view is absent."""
    soup = BeautifulSoup(html or '', 'html.parser')
    title = _text(soup, profile.title)
    price = _text(soup, profile.price)
    if not title or not price:
        return None
    # Selected variant options ("Color: Red"); the label is the store's own. The
    # swatch title can be an internal key ("Red*HRF-368 - 14 Cu Ft/368 Liter"),
    # so the shown text wins and the title only names an image-only swatch.
    options = {}
    for row in soup.select(profile.option_rows):
        key, chosen = row.select_one(profile.option_key), row.select_one(profile.option_selected)
        if key is not None and chosen is not None:
            value = chosen.get_text(strip=True) or str(chosen.get('title') or '').strip()
            if value:
                options[key.get_text(strip=True)] = value
    images = [urljoin(page_url, str(img.get('src'))) for img in soup.select(profile.images) if img.get('src')]
    raw = {
        'title': title,
        'price': price,
        'compare_at_price': _text(soup, profile.compare_at_price),
        'availability': _text(soup, profile.availability),
        'attributes': options,
        'image_url': images[0] if images else None,
        'additional_images': images[1:],
        'category_path': [crumb.get_text(strip=True) for crumb in soup.select(profile.breadcrumb)
                          if crumb.get_text(strip=True)],
        'product_url': page_url,
    }
    capture(raw, page_url, 'rendered_dom', observed_at=datetime.now(timezone.utc))
    # The store's currency is the profile's declaration, not a page value.
    raw['currency'] = profile.currency
    raw['_field_sources'] = {'/currency': {'capture_path': '/currency', '_capture': capture(
        {'currency': profile.currency}, page_url, 'rendered_profile')['_capture']}}
    raw['_profile'] = profile.name
    return raw


# Product pages rendered at once; one browser, bounded tabs.
PRODUCT_CONCURRENCY = 4


@dataclass
class RenderedRun:
    products: list[dict]
    listing: RenderedListing | None
    errors: list[str]


async def render_catalog(url: str, profile: RenderedProfile, *, max_urls: int) -> RenderedRun:
    """Render the listing (or the one product page) and each product view."""
    import asyncio

    from crawl4ai import AsyncWebCrawler

    from .._url_safety import ValidatingProxy, operator_allows_private_urls, validate_url_target
    from ._browser import StealthLevel, get_browser_config, get_crawl_config
    from .._product_admission import crawl_document_allowed

    await validate_url_target(url, allow_private=operator_allows_private_urls())
    errors: list[str] = []
    listing = None
    async with ValidatingProxy() as proxy:
        def config(wait_for, script=None):
            base = get_crawl_config(stealth_level=StealthLevel.STANDARD, wait_for=wait_for,
                                    page_timeout=45000, delay_before_return_html=1.0,
                                    scan_full_page=False, proxy_config=proxy.crawl4ai_config)
            return base.clone(js_code=script) if script else base

        async with AsyncWebCrawler(config=get_browser_config(StealthLevel.STANDARD)) as crawler:
            if profile.is_product_url(url):
                product_urls = [url]
            else:
                pages = max(1, min(10, -(-max_urls // 20)))
                result = await crawler.arun(url=url, config=config(
                    f'css:{profile.card}', listing_script(profile, max_urls, pages)))
                if not crawl_document_allowed(result):
                    errors.append(f'rendered listing unavailable: {getattr(result, "error_message", "") or getattr(result, "status_code", "")}')
                    return RenderedRun([], None, errors)
                listing = read_listing(result.html, url, profile)
                if listing is None:
                    errors.append('rendered listing script returned no result')
                    return RenderedRun([], None, errors)
                if listing.error:
                    errors.append(f'rendered listing stopped: {listing.error}')
                product_urls = list(listing.product_urls[:max_urls])

            gate = asyncio.Semaphore(PRODUCT_CONCURRENCY)

            async def one(product_url):
                async with gate:
                    try:
                        result = await crawler.arun(url=product_url, config=config(f'css:{profile.product_ready}'))
                    except Exception as exc:
                        errors.append(f'{product_url}: {type(exc).__name__}')
                        return None
                    if not crawl_document_allowed(result):
                        errors.append(f'{product_url}: rendered product page unavailable')
                        return None
                    raw = read_product(result.html, product_url, profile)
                    if raw is None:
                        errors.append(f'{product_url}: product view not rendered')
                    return raw

            products = [raw for raw in await asyncio.gather(*(one(u) for u in product_urls)) if raw]
    return RenderedRun(products, listing, errors)
