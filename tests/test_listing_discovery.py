"""Category scope on SEO paths, platform listing markup and detection causes.

Fixtures copy the structure observed on live stores on 2026-11-07: Magento
category pages (li.product-item, ?p=N pagination, "Items 1 - 32 of 288"),
Salesforce B2C Commerce SFRA tiles (.product[data-pid], Search-UpdateGrid in
data-sort-options) and a generic store that lists products only in a
schema.org ItemList. Product pages carry JSON-LD Product, as observed.
"""

import json

import httpx
import pytest
from click.testing import CliRunner

from shopextract._listing import parse_listing
from shopextract._models import Platform

STORE = "https://fixture.invalid"


def magento_card(slug, product_id, price):
    return (f'<li class="item product product-item"><div class="product-item-info">'
            f'<a class="product photo product-item-photo" href="{STORE}/{slug}" tabindex="-1"><img/></a>'
            f'<strong class="product name product-item-name"><a class="product-item-link" href="{STORE}/{slug}">{slug}</a></strong>'
            f'<div class="price-box" data-product-id="{product_id}"><span data-price-amount="{price}">Rs. {price}</span></div>'
            f'<form action="{STORE}/checkout/cart/add/product/{product_id}/"></form></div></li>')


def magento_page(slugs, *, next_url=None, total=None):
    cards = "".join(magento_card(slug, index, 100 + index) for index, slug in enumerate(slugs))
    nav = (f'<nav><a href="{STORE}/groceries-pets/bakery">Bakery</a>'
           f'<a href="{STORE}/customer/account">Account</a></nav>')
    pager = f'<li class="item pages-item-next"><a class="action next" href="{next_url}">Next</a></li>' if next_url else ""
    amount = f'<p class="toolbar-amount">Items 1 - {len(slugs)} of {total}</p>' if total else ""
    return (f'<html><body class="page-products catalog-category-view">{nav}<main>{amount}'
            f'<ol class="products list items product-items">{cards}</ol><ul class="pages">{pager}</ul>'
            f'</main></body></html>')


def product_page(name, price):
    data = {"@context": "https://schema.org", "@type": "Product", "name": name, "sku": name.upper(),
            "image": f"{STORE}/media/{name}.jpg",
            "offers": {"@type": "Offer", "price": str(price), "priceCurrency": "PKR",
                       "availability": "https://schema.org/InStock"}}
    return (f'<html><head><script type="application/ld+json">{json.dumps(data)}</script>'
            f'<meta property="og:image" content="{STORE}/media/{name}.jpg"></head>'
            f'<body><h1>{name}</h1></body></html>')


def test_magento_listing_reads_cards_pagination_and_total_not_navigation():
    page = parse_listing(magento_page(["cheese-a", "cheese-b"], next_url=f"{STORE}/groceries-pets/dairy?p=2",
                                      total=288), f"{STORE}/groceries-pets/dairy")
    assert page.product_urls == (f"{STORE}/cheese-a", f"{STORE}/cheese-b")
    assert page.next_url == f"{STORE}/groceries-pets/dairy?p=2"
    assert page.total == 288
    assert page.strategy == "li.product-item"


def test_sfcc_tiles_drop_tracking_query_and_continue_through_update_grid():
    grid = (f"{STORE}/on/demandware.store/Sites-Store-Site/en_PK/Search-UpdateGrid"
            "?cgid=003-Ready-To-Wear&srule=predictive-sorting&start=0&sz=2")
    options = json.dumps({"options": [{"id": "Recommended", "url": grid}]})
    html = ('<div class="product-grid">'
            '<div class="product" data-pid="1-A"><div class="product-tile">'
            '<a class="wishlistTile" data-url="/on/demandware.store/Sites-Store-Site/en_PK/Wishlist-AddProduct">w</a>'
            '<a class="link plpRedirectPdp" href="/kurta-a/1-A.html?source=recommendation">Kurta A</a></div></div>'
            '<div class="product" data-pid="1-B"><div class="product-tile">'
            '<a class="link plpRedirectPdp" href="/kurta-b/1-B.html?source=recommendation">Kurta B</a></div></div>'
            f"<div class=\"grid-footer\" data-sort-options='{options}'></div></div>")
    first = parse_listing(html, f"{STORE}/ready-to-wear/")
    assert first.product_urls == (f"{STORE}/kurta-a/1-A.html", f"{STORE}/kurta-b/1-B.html")
    assert "start=2" in first.next_url and "sz=2" in first.next_url and "cgid=003-Ready-To-Wear" in first.next_url

    # A grid fragment advances from its own start, so pages never repeat.
    second = parse_listing(html, first.next_url)
    assert "start=4" in second.next_url


def test_item_list_is_read_but_breadcrumbs_are_not_products():
    breadcrumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "item": {"@id": f"{STORE}/airconditioners/", "name": "AC"}}]}
    items = {"@context": "https://schema.org", "@type": "ItemList", "numberOfItems": 35, "itemListElement": [
        {"@type": "ListItem", "position": 1, "url": f"{STORE}/airconditioners_products/1/ac-one.html"},
        {"@type": "ListItem", "position": 2, "url": "https://outside.invalid/ac-two.html"}]}
    html = "".join(f'<script type="application/ld+json">{json.dumps(value)}</script>'
                   for value in (breadcrumbs, items))
    page = parse_listing(f"<html>{html}</html>", f"{STORE}/airconditioners/")
    assert page.product_urls == (f"{STORE}/airconditioners_products/1/ac-one.html",)
    assert page.total == 35
    assert page.strategy == "schema_org_item_list"


def test_product_page_is_recognised_and_not_mistaken_for_an_empty_listing():
    page = parse_listing(product_page("kraft-cheese", 2250), f"{STORE}/kraft-cheese")
    assert page.product_urls == () and page.is_product_page


def test_cards_beat_item_list_and_reject_other_hosts():
    html = magento_page(["only-card"]) + (
        '<script type="application/ld+json">'
        + json.dumps({"@type": "ItemList", "itemListElement": [{"url": f"{STORE}/promo"}]}) + "</script>"
        + magento_card("x", 9, 1).replace(f"{STORE}/x", "https://outside.invalid/x"))
    page = parse_listing(html, f"{STORE}/c")
    assert page.product_urls == (f"{STORE}/only-card",)


def _transport(routes, calls):
    def handler(request):
        url = str(request.url)
        calls.append(url)
        body = routes.get(url)
        if body is None:
            return httpx.Response(404, request=request)
        return httpx.Response(200, text=body, request=request)
    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_seo_category_path_without_marker_is_read_as_a_listing_with_pages():
    from shopextract._discover import discover

    category = f"{STORE}/groceries-pets/dairy"
    routes = {
        category: magento_page(["cheese-a", "cheese-b"], next_url=f"{category}?p=2", total=3),
        f"{category}?p=2": magento_page(["cheese-c"], total=3),
        f"{STORE}/sitemap.xml": ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                 f'<url><loc>{STORE}/whole-store-item</loc></url></urlset>'),
    }
    calls = []
    async with httpx.AsyncClient(transport=_transport(routes, calls)) as client:
        urls = await discover(category, platform=Platform.MAGENTO, max_urls=10, client=client)
    assert list(urls) == [f"{STORE}/cheese-a", f"{STORE}/cheese-b", f"{STORE}/cheese-c"]
    assert not any("sitemap" in call or "/rest/" in call for call in calls)
    assert "category_listing_truncated" not in urls.reasons


@pytest.mark.asyncio
async def test_unreadable_category_never_falls_back_to_whole_store_products():
    from shopextract._discover import discover

    category = f"{STORE}/groceries-pets/dairy"
    routes = {
        category: "<html><main><p>Please enable JavaScript.</p></main></html>",
        f"{STORE}/robots.txt": f"Sitemap: {STORE}/sitemap.xml\n",
        f"{STORE}/sitemap.xml": ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                 f'<url><loc>{STORE}/whole-store-item</loc></url></urlset>'),
    }
    async with httpx.AsyncClient(transport=_transport(routes, [])) as client:
        urls = await discover(category, platform=Platform.MAGENTO, max_urls=10, client=client)
    assert list(urls) == []
    assert "category_scope_unavailable" in urls.reasons


@pytest.mark.asyncio
async def test_product_url_discovers_itself():
    from shopextract._discover import discover

    url = f"{STORE}/kraft-cheese"
    async with httpx.AsyncClient(transport=_transport({url: product_page("kraft-cheese", 2250)}, [])) as client:
        urls = await discover(url, platform=Platform.MAGENTO, max_urls=10, client=client)
    assert list(urls) == [url]


@pytest.mark.asyncio
async def test_magento_category_extract_returns_listing_products_without_whole_catalog_api(monkeypatch):
    from shopextract import _extract, _url_safety
    from shopextract.extractors import unified, _storefront

    category = f"{STORE}/groceries-pets/dairy"
    routes = {category: magento_page(["cheese-a", "cheese-b"], total=2),
              f"{STORE}/cheese-a": product_page("cheese-a", 2250),
              f"{STORE}/cheese-b": product_page("cheese-b", 980)}
    calls = []
    transport = _transport(routes, calls)
    original = httpx.AsyncClient

    def factory(*args, **kwargs):
        kwargs["transport"] = transport
        return original(*args, **kwargs)

    for module in (_url_safety, unified, _storefront, _extract):
        if hasattr(module, "async_client"):
            monkeypatch.setattr(module, "async_client", factory)
    monkeypatch.setattr(unified, "browser_allowed", lambda: False, raising=False)
    result = await _extract.extract(category, platform=Platform.MAGENTO, max_urls=10)

    assert sorted(p.title for p in result.products) == ["cheese-a", "cheese-b"]
    assert sorted(str(p.price) for p in result.products) == ["2250", "980"]
    assert not any("/graphql" in call or "/rest/V1" in call for call in calls)


@pytest.mark.asyncio
async def test_sfcc_detected_from_asset_path_and_session_cookie():
    from shopextract._detect import detect

    def handler(request):
        if request.url.path == "/":
            return httpx.Response(200, request=request, headers=[
                ("set-cookie", "dwac_d1719aaffb34566fc83665bd13=x; Path=/"),
                ("set-cookie", "dwsid=abc; path=/; HttpOnly")],
                text='<script src="/on/demandware.static/Sites-Store-Site/-/en_PK/v1/js/main.js"></script>')
        return httpx.Response(404, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await detect(f"{STORE}/", client=client)
    assert result.platform is Platform.DEMANDWARE
    assert set(result.signals) == {"html:demandware-assets", "cookie:demandware-session"}


def _cli_detect(monkeypatch, context):
    from shopextract import _detect
    from shopextract.cli import main

    async def fake(url, **kwargs):
        return context

    monkeypatch.setattr(_detect, "detect_context", fake)
    result = CliRunner().invoke(main, ["--output-format", "json", "detect", STORE])
    return result, json.loads(result.stdout)


def _context(**kwargs):
    from shopextract._models import DetectionContext, PlatformResult
    result = PlatformResult(platform=Platform.GENERIC, confidence=0.0, signals=["fallback:no-signals-detected"])
    return DetectionContext(result=result, **kwargs)


def test_detect_reports_an_unreadable_store_page_instead_of_generic(monkeypatch):
    result, value = _cli_detect(monkeypatch, _context(page_status=403, errors=[f"HTTP 403 {STORE}"]))
    assert result.exit_code == 1
    assert value["ok"] is False and value["error"]["cause"] == "blocked"


def test_detect_classifies_dns_failure_from_the_page_error_only(monkeypatch):
    errors = [f"HTTP 403 {STORE}/graphql", f"{STORE}: ConnectError: [Errno 8] nodename nor servname provided, "
              "or not known; dns lookup failed"]
    result, value = _cli_detect(monkeypatch, _context(errors=errors))
    assert value["error"]["cause"] == "dns_failure"


def test_detect_timeout_is_partial_not_complete(monkeypatch):
    result, value = _cli_detect(monkeypatch, _context(timed_out=True, errors=["detection_timeout: exceeded 30s"]))
    assert result.exit_code == 0
    assert value["ok"] is True and value["completeness"] == "partial"
    assert value["warnings"] == ["detection_timeout"]


def test_detect_generic_after_reading_the_page_stays_complete(monkeypatch):
    result, value = _cli_detect(monkeypatch, _context(page_status=200))
    assert value["ok"] is True and value["completeness"] == "complete"


@pytest.mark.asyncio
@pytest.mark.parametrize("status,reason", [(429, "rate_limited"), (403, "blocked"), (500, "category_listing_http_500")])
async def test_refused_listing_keeps_its_status_as_the_reason(status, reason):
    from shopextract._discover import discover

    def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(404, request=request)
        if request.url.path == "/airconditioners/":
            return httpx.Response(status, request=request)
        return httpx.Response(404, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        urls = await discover(f"{STORE}/airconditioners/", platform=Platform.GENERIC, max_urls=10, client=client)
    assert list(urls) == []
    assert reason in urls.reasons and "category_scope_unavailable" in urls.reasons


@pytest.mark.parametrize("reasons,cause", [
    (["category_listing_unavailable", "rate_limited", "category_scope_unavailable"], "rate_limited"),
    (["category_listing_unavailable", "blocked", "category_scope_unavailable"], "blocked"),
    (["robots_disallowed", "category_scope_unavailable"], "blocked"),
    (["category_scope_unavailable"], "category_scope_unavailable")])
def test_listing_cause_is_not_taken_from_expected_api_probe_errors(reasons, cause):
    from shopextract._cli_extract import _source_failure

    # Detection probes /graphql and /rest on every store; their 403/404 must not decide.
    errors = [f"HTTP 403 {STORE}/graphql", f"HTTP 404 {STORE}/products.json?limit=250&page=1"]
    failure = _source_failure({"errors": errors, "incompleteness_reasons": reasons})
    assert failure.cause == cause
    assert failure.retryable is (cause == "rate_limited")
