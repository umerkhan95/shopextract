"""Product pages that list related products, SFRA product views, Magento regular price.

Fixtures copy the structure observed on live stores on 2026-11-07:
- a Magento product view (body ``catalog-product-view``, ``og:type`` product,
  no JSON-LD) whose related-products block repeats ``li.product-item`` cards;
- a generic store product page with one JSON-LD Product and many ``/product/``
  spec links in its body;
- a Salesforce B2C Commerce (SFRA) product view without JSON-LD or product
  Open Graph, read from ``.product-detail[data-pid]`` and the data layer;
- a Magento price box with ``finalPrice`` and ``oldPrice`` keyed by product id.
"""

import json

import httpx
import pytest

from shopextract._listing import parse_listing
from shopextract._models import Platform
from shopextract._normalize import normalize
from shopextract._structured_html import extract_structured_products

STORE = "https://fixture.invalid"


def related_cards(*slugs):
    return "".join(f'<li class="item product product-item"><a class="product-item-link" href="{STORE}/{slug}">{slug}</a></li>'
                   for slug in slugs)


def magento_product_view(product_id=63291, final=124999, old=None, related_old=None):
    price_box = (f'<span id="product-price-{product_id}" data-price-amount="{final}" data-price-type="finalPrice">'
                 f'Rs. {final}</span>')
    if old is not None:
        price_box += f'<span id="old-price-{product_id}" data-price-amount="{old}" data-price-type="oldPrice">Rs. {old}</span>'
    related_box = ''
    if related_old is not None:
        related_box = (f'<div class="price-box"><span id="old-price-999" data-price-amount="{related_old}" '
                       f'data-price-type="oldPrice"></span></div>')
    return ('<html><head><meta property="og:type" content="product">'
            f'<meta property="og:title" content="Inverter Refrigerator">'
            f'<meta property="og:url" content="{STORE}/inverter-refrigerator/">'
            f'<meta property="og:image" content="{STORE}/media/catalog/product/fridge.jpg">'
            f'<meta property="product:price:amount" content="{final}">'
            '<meta property="product:price:currency" content="PKR"></head>'
            '<body class="page-product-configurable catalog-product-view">'
            '<main><div class="product-info-main">'
            f'<form id="product_addtocart_form"><input name="product" value="{product_id}"></form>{price_box}</div>'
            f'<div class="block related"><ol>{related_cards("other-fridge", "contact")}</ol>{related_box}</div>'
            '</main></body></html>')


def sfra_product_view(pid="WTOPV1026007_999", *, price: str | None = "10990.00", currencies=("PKR",),
                      name: str | None = "Knit Dress"):
    layer = "".join(f'<script>var ga4DataLayerEvent = {{"ecommerce":{{"currencyCode":"{c}"}}}};</script>'
                    for c in currencies)
    price_html = (f'<div class="prices"><span class="sales"><span class="value" content="{price}">Rs.{price}</span>'
                  '</span></div>') if price else ''
    name_html = f'<h2 class="product-name">{name}</h2>' if name else ''
    return ('<html><head><meta property="og:type" content="website"></head><body>'
            '<ol class="breadcrumb"><li><a href="https://fixture.invalid/">Home</a></li>'
            f'<li><a href="{STORE}/woman">Woman</a></li><li>{name}</li></ol>'
            f'<div class="product-detail product-wrapper" data-pid="{pid}">{name_html}'
            '<div class="primary-images">'
            f'<img src="data:image/png;base64,AAAA" data-src="{STORE}/dw/image/{pid}_1.jpg">'
            f'<img data-high-src="{STORE}/dw/image/{pid}_2.jpg" src="data:image/png;base64,AAAA"></div>'
            f'{price_html}<div class="description-and-detail"><div id="nav-description">'
            '<div class="value content"><p>Sweater Dress In Clean Yarn.</p></div></div></div></div>'
            f'<div class="recommendations"><div class="product" data-pid="OTHER_1">'
            f'<a class="link" href="{STORE}/products/OTHER_1.html">Other</a></div></div>'
            f'{layer}</body></html>')


SFRA_URL = f"{STORE}/collections/western-wear/products/WTOPV1026007_999.html"


# -- A page declares itself a product page --------------------------------

def test_magento_product_view_with_related_cards_is_a_product_page():
    # Before: the related cards made it a listing and discovery kept /contact.
    page = parse_listing(magento_product_view(), f"{STORE}/inverter-refrigerator/")
    assert page.is_product_page


def test_single_json_ld_product_with_spec_links_is_a_product_page():
    data = {"@type": "Product", "name": "Haier HRF 438", "offers": {"price": "122999", "priceCurrency": "PKR"}}
    links = "".join(f'<a href="{STORE}/product/laptop-specs-ram-{n}gb/">spec</a>' for n in (4, 8))
    html = (f'<html><head><script type="application/ld+json">{json.dumps(data)}</script></head>'
            f'<body><main>{links}</main></body></html>')
    page = parse_listing(html, f"{STORE}/fridge_products/25130/haier.html")
    assert len(page.product_urls) == 2 and page.is_product_page


def test_sfra_product_view_is_a_product_page_only_when_its_pid_is_in_the_url():
    assert parse_listing(sfra_product_view(), SFRA_URL).is_product_page
    # A quick-view fragment on another page names a product the URL does not.
    assert not parse_listing(sfra_product_view(), f"{STORE}/collections/dresses").is_product_page


def test_listings_stay_listings():
    item_list = {"@type": "ItemList", "itemListElement": [{"url": f"{STORE}/a"}]}
    product = {"@type": "Product", "name": "A"}
    both = "".join(f'<script type="application/ld+json">{json.dumps(v)}</script>' for v in (item_list, product))
    assert not parse_listing(f"<html>{both}</html>", f"{STORE}/c").is_product_page
    two = "".join(f'<script type="application/ld+json">{json.dumps({"@type": "Product", "name": n})}</script>'
                  for n in "AB")
    # A listing that marks up every card carries several Products.
    page = parse_listing(f"<html>{two}<ol>{related_cards('a', 'b')}</ol></html>", f"{STORE}/c")
    assert not page.is_product_page and len(page.product_urls) == 2
    cards = (f'<html><head><meta property="og:type" content="website"></head>'
             f'<body class="catalog-category-view"><ol>{related_cards("a", "b")}</ol></body></html>')
    page = parse_listing(cards, f"{STORE}/c")
    assert not page.is_product_page and len(page.product_urls) == 2


def _transport(routes):
    def handler(request):
        body = routes.get(str(request.url))
        return httpx.Response(200, text=body, request=request) if body else httpx.Response(404, request=request)
    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_magento_product_url_discovers_itself_not_its_related_links():
    from shopextract._discover import discover
    url = f"{STORE}/inverter-refrigerator/"
    async with httpx.AsyncClient(transport=_transport({url: magento_product_view()})) as client:
        urls = await discover(url, platform=Platform.MAGENTO, max_urls=1, client=client)
    assert list(urls) == [url]


# -- SFRA product view --------------------------------------------------------

def test_sfra_product_view_reads_name_price_currency_images_and_breadcrumb():
    result = extract_structured_products(sfra_product_view(), SFRA_URL)
    assert result.diagnostics == []
    product = normalize(result.products[0], Platform.DEMANDWARE, STORE)
    assert product is not None
    assert (product.title, str(product.price), product.currency, product.sku) == (
        "Knit Dress", "10990.00", "PKR", "WTOPV1026007_999")
    assert product.image_url == f"{STORE}/dw/image/WTOPV1026007_999_1.jpg"
    assert product.additional_images == [f"{STORE}/dw/image/WTOPV1026007_999_2.jpg"]
    assert product.category_path == ["Woman"]
    assert product.description == "Sweater Dress In Clean Yarn."
    # The view states no stock; availability is a default without support.
    stock = next(o for o in product.evidence_contract.observations if o.field_path == "/in_stock")
    assert stock.state.value == "unsupported"


def test_sfra_product_view_without_price_or_name_is_not_a_product():
    for html in (sfra_product_view(price=None), sfra_product_view(name=None)):
        result = extract_structured_products(html, SFRA_URL)
        assert result.products == []
        assert [d["code"] for d in result.diagnostics] == ["sfra_product_incomplete"]


def test_sfra_conflicting_data_layer_currencies_leave_currency_unsupported():
    result = extract_structured_products(sfra_product_view(currencies=("PKR", "USD")), SFRA_URL)
    assert "priceCurrency" not in result.products[0]["offers"]
    assert "conflicting_currency" in [d["code"] for d in result.diagnostics]


# -- Magento regular price ---------------------------------------------------------------

def _magento(html):
    result = extract_structured_products(html, f"{STORE}/inverter-refrigerator/")
    product = normalize(result.products[0], Platform.MAGENTO, STORE)
    assert product is not None
    return product


def test_magento_old_price_of_the_page_product_is_the_compare_at_price():
    product = _magento(magento_product_view(final=314999, old=328999))
    assert (str(product.price), str(product.compare_at_price)) == ("314999", "328999")
    regular = next(o for o in product.evidence_contract.observations if o.field_path == "/compare_at_price")
    assert regular.state.value == "observed" and regular.raw_value == "328999"


def test_related_product_old_price_is_never_borrowed():
    product = _magento(magento_product_view(final=314999, related_old=400000))
    assert product.compare_at_price is None


def test_old_price_not_above_final_price_is_rejected():
    product = _magento(magento_product_view(final=314999, old=314999))
    assert product.compare_at_price is None


# -- A store that refuses the requested page --------------------------------------

@pytest.mark.asyncio
async def test_store_refusing_every_request_is_reported_blocked_not_out_of_scope(monkeypatch):
    # czone.com.pk, 2026-11-07: HTTP 403 on the page, robots.txt and every probe.
    from shopextract import _detect, _extract, _url_safety
    from shopextract._cli_data import extraction_data
    from shopextract._cli_extract import _source_failure
    from shopextract.extractors import unified

    transport = httpx.MockTransport(lambda request: httpx.Response(403, request=request))
    original = httpx.AsyncClient

    def factory(*args, **kwargs):
        kwargs["transport"] = transport
        return original(*args, **kwargs)

    for module in (_url_safety, _detect, unified, _extract):
        if hasattr(module, "async_client"):
            monkeypatch.setattr(module, "async_client", factory)
    result = await _extract.extract(f"{STORE}/laptops-pakistan-ppt.74.aspx", max_urls=3)
    assert result.products == [] and "blocked" in result.incompleteness_reasons
    assert _source_failure(extraction_data(result)).cause == "blocked"
