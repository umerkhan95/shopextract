"""Rendered-storefront profiles: listing script, listing result and product view.

Markup follows haiermall.pk as rendered on 2026-11-07 (Vue 3, Element Plus).
"""
import json
from decimal import Decimal

import pytest

from shopextract import Platform, normalize
from shopextract.extractors.rendered_profiles import (HAIER_MALL, RESULT_ID, listing_script, profile_for,
                                                      read_listing, read_product)

SHOP = 'https://haiermall.pk'

PRODUCT_HTML = """<html><body>
<div class="breadcrumb"><div class="item"><div>Home Appliances</div></div>
<div class="item"><div>Refrigerators</div></div><div class="item"><div>Inverter Refrigerator</div></div></div>
<div class="pro-main-right"><div class="pro-main-left"><div class="el-image"><img src="https://obs.haiermall.pk/1.png"></div>
<div class="el-image"><img src="https://obs.haiermall.pk/2.png"></div></div>
<div class="pro-main-center">
 <div class="pro-name-box"><div class="pro-name text_hide2">Haier - 13CFT HCS Digital Inverter Refrigerator - HRF-368
 </div><div class="availability"><span class="availability-title">Availability:&nbsp;</span><span>In Stock</span></div></div>
 <div class="pro_shux"><div class="key">Color</div><div class="value">
  <div class="type_main_img" title="Green"><span>Green</span></div>
  <div class="type_main_img xuan" title="Red*HRF-368 - 14 Cu Ft/368 Liter"><span>Red</span></div></div></div>
 <div class="pro_shux"><div class="key">Quantity</div><div class="quantity-box rowSC"></div></div>
 <div class="pro-amount-box rowSC"><div class="rowSC price-box"><div><div class="amount-num">Rs. 106,899</div></div></div></div>
 <div><div class="mrp-num">Rs. 115,000</div></div>
</div></div></body></html>"""


def test_image_only_swatch_is_named_by_its_title():
    html = PRODUCT_HTML.replace('<div class="type_main_img xuan" title="Red*HRF-368 - 14 Cu Ft/368 Liter"><span>Red</span></div>',
                                '<div class="type_main_img xuan" title="Red"><img src="https://obs.haiermall.pk/r.png"></div>')
    assert read_product(html, SHOP + '/en/products/x', HAIER_MALL)['attributes'] == {'Color': 'Red'}


def test_profile_matches_the_store_host_only():
    assert profile_for('https://haiermall.pk/en/refrigerators') is HAIER_MALL
    assert profile_for('https://www.haiermall.pk/en/air-fryers') is HAIER_MALL
    assert profile_for('https://haier.com.pk/') is None


def test_product_view_is_read_with_compare_price_stock_and_selected_option():
    url = SHOP + '/en/products/haier-13cft-hcs'
    raw = read_product(PRODUCT_HTML, url, HAIER_MALL)
    product = normalize(raw, Platform.GENERIC, SHOP)
    assert product.title.startswith('Haier - 13CFT') and product.price == Decimal('106899')
    assert product.compare_at_price == Decimal('115000') and product.currency == 'PKR'
    assert product.in_stock is True and product.mpn is None
    # The swatch shows "Red"; its title is the store's internal variant key.
    assert product.attributes == {'Color': 'Red'}
    assert product.category_path == ['Home Appliances', 'Refrigerators', 'Inverter Refrigerator']
    assert product.image_url == 'https://obs.haiermall.pk/1.png' and product.product_url == url
    observed = {o.field_path: o.state.value for o in product.evidence_contract.observations}
    assert observed['/price'] == 'observed' and observed['/in_stock'] == 'observed'


def test_out_of_stock_label_and_missing_view():
    html = PRODUCT_HTML.replace('In Stock', 'Out of Stock')
    product = normalize(read_product(html, SHOP + '/en/products/x', HAIER_MALL), Platform.GENERIC, SHOP)
    assert product.in_stock is False
    assert read_product('<html><div id="app"></div></html>', SHOP + '/en/products/x', HAIER_MALL) is None


def test_listing_result_keeps_only_same_store_product_urls():
    payload = {'urls': [SHOP + '/en/products/a', SHOP + '/en/products/a', SHOP + '/en/help',
                        'https://evil.test/en/products/b'], 'pages': 2, 'exhausted': True, 'error': None}
    html = f'<html><body><script type="application/json" id="{RESULT_ID}">{json.dumps(payload)}</script></body></html>'
    listing = read_listing(html, SHOP + '/en/refrigerators', HAIER_MALL)
    assert listing.product_urls == (SHOP + '/en/products/a',) and listing.pages == 2 and listing.exhausted
    assert read_listing('<html></html>', SHOP, HAIER_MALL) is None


# A local page shaped like the store: cards open products through window.open
# and numbered buttons replace the card list.
FAKE_LISTING = """<html><body><div class="page-box"><div id="cards"></div>
<div class="main"><div class="rowSC"><button>1</button><button>2</button><button>3</button></div></div></div>
<script>
const pages = {1: ['a', 'b'], 2: ['c', 'd'], 3: ['e']};
function show(n) {
  const box = document.getElementById('cards'); box.innerHTML = '';
  for (const slug of pages[n]) {
    const card = document.createElement('div'); card.className = 'commodity-item';
    card.innerHTML = '<div class="title">' + slug + '</div>';
    card.onclick = () => window.open('/en/products/' + slug, '_blank');
    box.appendChild(card);
  }
  document.querySelectorAll('.rowSC > button').forEach(b => b.classList.toggle('xuan', b.textContent == n));
}
document.querySelectorAll('.rowSC > button').forEach(b => b.onclick = () => setTimeout(() => show(+b.textContent), 100));
show(1);
</script></body></html>"""


async def _run_listing(max_urls, max_pages):
    playwright = pytest.importorskip('playwright.async_api')
    async with playwright.async_playwright() as p:
        try:
            browser = await p.chromium.launch()
        except Exception as exc:  # pragma: no cover - depends on the local browser install
            pytest.skip(f'Chromium unavailable: {exc}')
        page = await browser.new_page()
        await page.route('https://haiermall.pk/**', lambda route: route.fulfill(body=FAKE_LISTING, content_type='text/html'))
        await page.goto(SHOP + '/en/refrigerators')
        await page.evaluate(f'(async () => {{ {listing_script(HAIER_MALL, max_urls, max_pages)} }})()')
        html = await page.content()
        await browser.close()
    return read_listing(html, SHOP + '/en/refrigerators', HAIER_MALL)


@pytest.mark.asyncio
async def test_listing_script_follows_numbered_pages_to_the_end():
    listing = await _run_listing(max_urls=20, max_pages=5)
    assert [u.rsplit('/', 1)[-1] for u in listing.product_urls] == ['a', 'b', 'c', 'd', 'e']
    assert listing.pages == 3 and listing.exhausted and listing.error is None


@pytest.mark.asyncio
async def test_listing_script_stops_at_the_budget_and_says_it_is_not_exhausted():
    listing = await _run_listing(max_urls=3, max_pages=5)
    assert [u.rsplit('/', 1)[-1] for u in listing.product_urls] == ['a', 'b', 'c']
    assert not listing.exhausted
    listing = await _run_listing(max_urls=20, max_pages=1)
    assert len(listing.product_urls) == 2 and not listing.exhausted


@pytest.mark.asyncio
async def test_without_browser_the_store_is_reported_as_browser_required(monkeypatch):
    from shopextract import extract
    import shopextract._extract as extract_module
    monkeypatch.setattr(extract_module, 'browser_allowed', lambda: False)
    result = await extract(SHOP + '/en/refrigerators', platform=Platform.GENERIC)
    assert not result.products and result.incompleteness_reasons == ['browser_required']
    assert any('--browser' in error for error in result.errors)


def test_browser_required_is_a_usage_failure():
    from shopextract._cli_extract import _source_failure
    failure = _source_failure({'errors': ['x'], 'incompleteness_reasons': ['browser_required']})
    assert failure.code == 'E_USAGE' and failure.cause is None and '--browser' in failure.message


@pytest.mark.asyncio
async def test_a_browser_failure_is_a_source_error_not_a_crash(monkeypatch):
    from shopextract import extract
    import shopextract._extract as extract_module
    import shopextract.extractors.rendered_profiles as profiles
    monkeypatch.setattr(extract_module, 'browser_allowed', lambda: True)

    async def broken(*args, **kwargs):
        raise RuntimeError('secret provider body')
    monkeypatch.setattr(profiles, 'render_catalog', broken)
    result = await extract(SHOP + '/en/refrigerators', platform=Platform.GENERIC)
    assert not result.products and 'source_error' in result.incompleteness_reasons
    assert result.errors == ['rendered storefront unavailable: RuntimeError']
