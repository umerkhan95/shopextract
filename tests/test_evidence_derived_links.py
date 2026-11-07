"""Links the parser derives deterministically keep their source support.

Observed 2026-11-07: Khaadi JSON-LD images are page-relative
(``/on/demandware.static/...jpg``) and Imtiaz (BlinkX) links are built from the
API id and slug. Both values were correct, but the evidence contract marked
them unsupported, so ``validate -m google_shopping`` rejected 20/20 products
with missing_image and missing_link.
"""

import json

from shopextract._capture import capture
from shopextract._models import Platform
from shopextract._normalize import normalize
from shopextract._structured_html import extract_structured_products

PAGE = "https://store.invalid/raw-silk-pants/2-26-406.html"


def observation(product, path):
    return next(o for o in product.evidence_contract.observations if o.field_path == path)


def json_ld_page(image):
    data = {"@type": "Product", "name": "Raw Silk Pants", "sku": "2-26-406", "image": image,
            "offers": {"price": "5990", "priceCurrency": "PKR", "availability": "https://schema.org/InStock"}}
    return f'<html><script type="application/ld+json">{json.dumps(data)}</script></html>'


def test_page_relative_image_resolved_against_its_page_is_observed():
    raw = extract_structured_products(json_ld_page("/on/demandware.static/images/a.jpg"), PAGE).products[0]
    product = normalize(raw, Platform.DEMANDWARE, "https://store.invalid")
    assert product.image_url == "https://store.invalid/on/demandware.static/images/a.jpg"
    image = observation(product, "/image_url")
    assert image.state.value == "observed"
    assert "Resolve relative URL against the captured page URL" in image.transformations


def test_a_value_that_is_not_the_resolved_link_stays_unsupported():
    raw = capture({"@type": "Product", "name": "A", "image": "/images/a.jpg",
                   "offers": {"price": "1", "priceCurrency": "PKR"}}, PAGE, "json_ld")
    raw["image"] = "https://elsewhere.invalid/images/a.jpg"
    product = normalize(raw, Platform.GENERIC, "https://store.invalid")
    assert observation(product, "/image_url").state.value == "unsupported"


def test_absolute_image_is_unchanged_and_observed_without_a_resolution_step():
    raw = extract_structured_products(json_ld_page("https://cdn.invalid/a.jpg"), PAGE).products[0]
    image = observation(normalize(raw, Platform.DEMANDWARE, "https://store.invalid"), "/image_url")
    assert image.state.value == "observed"
    assert "Resolve relative URL against the captured page URL" not in image.transformations


def blinkx_item():
    from shopextract.extractors.blinkx import BlinkXExtractor
    currency = capture({"currency": "PKR"}, "https://shop.invalid/", "blinkx_page_config")["_capture"]
    config = type("Config", (), {"origin": "https://shop.invalid", "currency": "PKR"})()
    item = {"id": 365195, "name": "Olper's Milk 1L", "slug": "olpers-milk-1l", "price": 360,
            "dish_branch_stock": {"stock": 4}}
    return BlinkXExtractor._record(item, {"config": config, "currency_capture": currency,
                                          "branch": 7, "area": "Askari 1"}, "https://api.invalid/items", None)


def test_blinkx_link_built_from_captured_id_and_slug_is_observed():
    product = normalize(blinkx_item(), Platform.BLINKX, "https://shop.invalid/catalog/milk")
    assert product.product_url == "https://shop.invalid/product/olpers-milk-1l-365195"
    link = observation(product, "/product_url")
    assert link.state.value == "observed" and link.raw_value == 365195
    assert link.transformations == ["Build storefront link /product/<slug>-<id> from the captured id and slug"]


def test_blinkx_record_from_a_file_without_origin_keeps_the_old_reading():
    item = blinkx_item()
    item.pop("_storefront_origin")
    product = normalize(item, Platform.BLINKX, "https://shop.invalid")
    assert product.product_url == "https://shop.invalid/product/olpers-milk-1l-365195"
    assert observation(product, "/product_url").state.value == "unsupported"
