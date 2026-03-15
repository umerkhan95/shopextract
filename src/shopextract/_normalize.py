"""Product normalizer -- map raw data from any extractor to unified Product model."""

from __future__ import annotations

import logging
import re
from decimal import Decimal, InvalidOperation

from ._models import Platform, Product, Variant

logger = logging.getLogger(__name__)


def _strip_html(html: str) -> str:
    """Simple HTML tag stripper (no bleach dependency)."""
    if not html:
        return ""
    # Remove script and style elements with content
    html = re.sub(r"<script[\s>].*?</script>", "", html, flags=re.IGNORECASE | re.DOTALL)
    html = re.sub(r"<style[\s>].*?</style>", "", html, flags=re.IGNORECASE | re.DOTALL)
    # Strip remaining tags
    html = re.sub(r"<[^>]+>", "", html)
    return html.strip()


def _validate_gtin(value: str | None) -> str | None:
    """Validate and normalize a GTIN/EAN/UPC value."""
    if not value:
        return None
    value = value.strip().replace("-", "").replace(" ", "")
    if not value:
        return None
    if not value.isdigit():
        return None
    if set(value) == {"0"}:
        return None
    if len(value) == 12:
        value = "0" + value
    if len(value) not in (8, 13, 14):
        return None
    return value


def _parse_additional_properties(props: list) -> dict:
    """Extract GTIN/MPN identifiers from Schema.org additionalProperty array."""
    known_ids = {"gtin", "gtin13", "gtin12", "gtin14", "gtin8", "ean", "mpn", "isbn"}
    result = {}
    for prop in props:
        if not isinstance(prop, dict):
            continue
        prop_id = str(prop.get("propertyID", "") or prop.get("name", "")).lower()
        if prop_id in known_ids:
            result[prop_id] = prop.get("value", "")
    return result


def normalize(
    raw: dict,
    platform: Platform = Platform.GENERIC,
    shop_url: str = "",
) -> Product | None:
    """Normalize raw product dict from ANY extractor to unified Product model.

    Args:
        raw: Raw product data dictionary from platform/extractor.
        platform: Source platform enum.
        shop_url: Base shop URL (e.g., "https://example.com").

    Returns:
        Product instance or None if data insufficient.
    """
    normalizers = {
        Platform.SHOPIFY: _normalize_shopify,
        Platform.WOOCOMMERCE: _normalize_woocommerce,
        Platform.MAGENTO: _normalize_magento,
        Platform.SHOPWARE: _normalize_shopware,
    }

    normalized_data = None
    if platform in normalizers:
        normalized_data = normalizers[platform](raw, shop_url)

    if not normalized_data:
        normalized_data = _normalize_generic(raw, shop_url)

    if not normalized_data:
        return None

    # Default condition
    if not normalized_data.get("condition"):
        normalized_data["condition"] = "NEW"

    try:
        product = Product(
            external_id=normalized_data.get("external_id", ""),
            title=normalized_data.get("title", ""),
            description=normalized_data.get("description", ""),
            price=normalized_data.get("price", Decimal("0")),
            compare_at_price=normalized_data.get("compare_at_price"),
            currency=normalized_data.get("currency", "USD"),
            image_url=normalized_data.get("image_url", ""),
            product_url=normalized_data.get("product_url", ""),
            sku=normalized_data.get("sku"),
            gtin=normalized_data.get("gtin"),
            mpn=normalized_data.get("mpn"),
            vendor=normalized_data.get("vendor"),
            product_type=normalized_data.get("product_type"),
            in_stock=normalized_data.get("in_stock", True),
            condition=normalized_data.get("condition"),
            variants=normalized_data.get("variants", []),
            tags=normalized_data.get("tags", []),
            additional_images=normalized_data.get("additional_images", []),
            category_path=normalized_data.get("category_path", []),
            platform=platform,
            raw_data=raw,
        )
    except Exception as e:
        logger.warning("Failed to create Product from normalized data: %s", e)
        return None

    if not _is_valid_product(product):
        return None
    return product


def _is_valid_product(product: Product) -> bool:
    has_price = product.price > 0
    has_image = bool(product.image_url and product.image_url.strip())
    has_identifier = bool(product.sku) or bool(product.external_id and product.external_id.strip())
    if not has_price and not has_image and not has_identifier:
        logger.info("Rejected non-product: title=%r price=%s", product.title, product.price)
        return False
    return True


def _shopify_stock_status(variants_raw: list[dict]) -> bool:
    if not variants_raw:
        return True
    for variant in variants_raw:
        inventory_qty = variant.get("inventory_quantity")
        if inventory_qty is None or inventory_qty > 0:
            return True
    return False


def _shopify_variants(variants_raw: list[dict]) -> list[Variant]:
    variants = []
    for v in variants_raw:
        try:
            variant_price = Decimal(v.get("price", "0"))
            variant_in_stock = True
            inventory_qty = v.get("inventory_quantity")
            if inventory_qty is not None:
                variant_in_stock = inventory_qty > 0
            variants.append(Variant(
                variant_id=str(v.get("id", "")),
                title=v.get("title", ""),
                price=variant_price,
                sku=v.get("sku"),
                in_stock=variant_in_stock,
            ))
        except Exception:
            continue
    return variants


def _shopify_tags(raw: dict) -> list[str]:
    tags_raw = raw.get("tags", "")
    if isinstance(tags_raw, str):
        return [tag.strip() for tag in tags_raw.split(",") if tag.strip()]
    return list(tags_raw) if tags_raw else []


def _normalize_shopify(raw: dict, shop_url: str) -> dict | None:
    title = raw.get("title", "").strip()
    if not title:
        return None

    variants_raw = raw.get("variants", [])
    first_variant = variants_raw[0] if variants_raw else {}

    try:
        price = Decimal(first_variant.get("price", "0"))
    except (InvalidOperation, ValueError):
        price = Decimal("0")

    compare_at_price = None
    if compare_at_raw := first_variant.get("compare_at_price"):
        try:
            compare_at_price = Decimal(compare_at_raw)
        except (InvalidOperation, ValueError):
            pass

    images = raw.get("images", [])
    image_url = images[0]["src"] if images else ""
    additional_images = [img["src"] for img in images[1:] if img.get("src")]

    handle = raw.get("handle", "")
    product_url = f"{shop_url.rstrip('/')}/products/{handle}" if handle else shop_url

    return {
        "external_id": str(raw.get("id", "")),
        "title": title,
        "description": _strip_html(raw.get("body_html", "")),
        "price": price,
        "compare_at_price": compare_at_price,
        "currency": raw.get("_shop_currency", "USD"),
        "image_url": image_url,
        "product_url": product_url,
        "sku": first_variant.get("sku"),
        "gtin": _validate_gtin(first_variant.get("barcode")),
        "mpn": None,
        "vendor": raw.get("vendor"),
        "product_type": raw.get("product_type"),
        "in_stock": _shopify_stock_status(variants_raw),
        "condition": None,
        "variants": _shopify_variants(variants_raw),
        "tags": _shopify_tags(raw),
        "additional_images": additional_images,
        "category_path": [raw["product_type"]] if raw.get("product_type") else [],
    }


def _normalize_woocommerce(raw: dict, shop_url: str) -> dict | None:
    title = (raw.get("title") or raw.get("name") or "").strip()
    if not title:
        return None

    is_admin_api = raw.get("_source") == "woocommerce_admin_api" or (
        isinstance(raw.get("price"), str) and "prices" not in raw
    )

    if is_admin_api:
        try:
            price = Decimal(raw.get("price") or "0")
        except (InvalidOperation, ValueError):
            price = Decimal("0")
        compare_at_price = None
        if raw.get("compare_at_price"):
            try:
                cap = Decimal(raw["compare_at_price"])
                if cap != price:
                    compare_at_price = cap
            except (InvalidOperation, ValueError):
                pass
        currency = raw.get("currency", "USD")
    else:
        prices = raw.get("prices", {})
        currency_minor_unit = prices.get("currency_minor_unit", 2)
        divisor = 10**currency_minor_unit
        try:
            price = Decimal(prices.get("price", "0")) / divisor
        except (InvalidOperation, ValueError):
            price = Decimal("0")
        compare_at_price = None
        regular_price_raw = prices.get("regular_price")
        if regular_price_raw:
            try:
                regular_price = Decimal(regular_price_raw) / divisor
                if regular_price != price:
                    compare_at_price = regular_price
            except (InvalidOperation, ValueError):
                pass
        currency = prices.get("currency_code", "USD")

    images = raw.get("images", [])
    if images and isinstance(images[0], dict):
        image_url = images[0].get("src", "")
        additional_images = [img["src"] for img in images[1:] if img.get("src")]
    else:
        image_url = raw.get("image_url", "")
        additional_images = raw.get("additional_images", [])

    product_url = raw.get("permalink") or raw.get("product_url") or ""

    tags_raw = raw.get("tags", [])
    tags = [t.get("name", "") for t in tags_raw if isinstance(t, dict)] if tags_raw and isinstance(tags_raw[0], dict) else tags_raw

    categories = raw.get("categories", [])
    category_path = [
        c.get("name", "") for c in categories
        if isinstance(c, dict) and c.get("name")
    ] if categories and isinstance(categories[0], dict) else categories

    gtin = _validate_gtin(raw.get("gtin") or raw.get("ean") or raw.get("barcode"))

    return {
        "external_id": str(raw.get("id", "")),
        "title": title,
        "description": _strip_html(raw.get("description", "")),
        "price": price,
        "compare_at_price": compare_at_price,
        "currency": currency,
        "image_url": image_url,
        "product_url": product_url,
        "sku": raw.get("sku"),
        "gtin": gtin,
        "mpn": raw.get("mpn") or None,
        "vendor": None,
        "product_type": None,
        "in_stock": True,
        "condition": None,
        "variants": [],
        "tags": tags,
        "additional_images": additional_images,
        "category_path": category_path,
    }


def _normalize_magento(raw: dict, shop_url: str) -> dict | None:
    title = raw.get("name", "").strip()
    if not title:
        return None

    currency = raw.get("currency", "USD")

    try:
        price = Decimal(str(raw.get("price", "0")))
    except (InvalidOperation, ValueError):
        price = Decimal("0")

    custom_attrs = raw.get("custom_attributes", [])
    description = ""
    image_path = ""
    url_key = ""
    gtin = None
    mpn = None
    manufacturer = None

    for attr in custom_attrs:
        if not isinstance(attr, dict):
            continue
        code = attr.get("attribute_code", "")
        value = attr.get("value", "")
        if code == "description":
            description = value
        elif code == "image":
            image_path = value
        elif code == "url_key":
            url_key = value
        elif code in ("ean", "gtin", "barcode"):
            gtin = value if value else None
        elif code == "mpn":
            mpn = value if value else None
        elif code == "manufacturer":
            manufacturer = value if value else None

    image_url = ""
    if image_path:
        image_url = f"{shop_url.rstrip('/')}/media/catalog/product{image_path}"

    gallery = raw.get("media_gallery_entries", [])
    additional_images = []
    for entry in gallery:
        if not isinstance(entry, dict):
            continue
        file_path = entry.get("file", "")
        if file_path and not entry.get("disabled") and file_path != image_path:
            additional_images.append(f"{shop_url.rstrip('/')}/media/catalog/product{file_path}")

    product_url = shop_url
    if url_key:
        product_url = f"{shop_url.rstrip('/')}/{url_key}.html"

    return {
        "external_id": raw.get("sku", str(raw.get("id", ""))),
        "title": title,
        "description": _strip_html(description),
        "price": price,
        "compare_at_price": None,
        "currency": currency,
        "image_url": image_url,
        "product_url": product_url,
        "sku": raw.get("sku"),
        "gtin": gtin,
        "mpn": mpn,
        "vendor": manufacturer,
        "product_type": None,
        "in_stock": True,
        "condition": None,
        "variants": [],
        "tags": [],
        "additional_images": additional_images,
        "category_path": [],
    }


def _normalize_shopware(raw: dict, shop_url: str) -> dict | None:
    title = (raw.get("title") or raw.get("name") or "").strip()
    if not title:
        return None

    try:
        price = Decimal(str(raw.get("price") or "0"))
    except (InvalidOperation, ValueError):
        price = Decimal("0")

    compare_at_price = None
    if raw.get("compare_at_price"):
        try:
            cap = Decimal(str(raw["compare_at_price"]))
            if cap != price:
                compare_at_price = cap
        except (InvalidOperation, ValueError):
            pass

    gtin = _validate_gtin(raw.get("gtin") or raw.get("barcode") or raw.get("ean"))

    variants: list[Variant] = []
    for v in raw.get("variants") or []:
        if not isinstance(v, dict):
            continue
        try:
            variant_price = Decimal(str(v.get("price") or "0"))
            variants.append(Variant(
                variant_id=str(v.get("variant_id") or v.get("id") or ""),
                title=v.get("title") or v.get("name") or "",
                price=variant_price,
                sku=v.get("sku"),
                in_stock=bool(v.get("in_stock", True)),
            ))
        except Exception:
            continue

    return {
        "external_id": str(raw.get("id") or raw.get("sku") or ""),
        "title": title,
        "description": _strip_html(raw.get("description") or ""),
        "price": price,
        "compare_at_price": compare_at_price,
        "currency": raw.get("currency") or "EUR",
        "image_url": raw.get("image_url") or "",
        "product_url": raw.get("product_url") or shop_url,
        "sku": raw.get("sku"),
        "gtin": gtin,
        "mpn": None,
        "vendor": raw.get("vendor") or None,
        "product_type": None,
        "in_stock": bool(raw.get("in_stock", True)),
        "condition": raw.get("condition") or None,
        "variants": variants,
        "tags": list(raw.get("tags") or []),
        "additional_images": list(raw.get("additional_images") or []),
        "category_path": list(raw.get("categories") or []),
    }


def _normalize_google_feed(raw: dict, shop_url: str) -> dict | None:
    title = (raw.get("title") or "").strip()
    if not title:
        return None

    try:
        price = Decimal(raw["price"]) if raw.get("price") else Decimal("0")
    except (InvalidOperation, ValueError):
        price = Decimal("0")

    compare_at_price = None
    if raw.get("sale_price"):
        try:
            sale = Decimal(raw["sale_price"])
            if sale > 0 and price > 0 and sale < price:
                compare_at_price = price
                price = sale
        except (InvalidOperation, ValueError):
            pass

    avail = (raw.get("availability") or "").lower().replace(" ", "_")
    in_stock = "in_stock" in avail if avail else True

    condition_raw = (raw.get("condition") or "").lower()
    condition = None
    if "new" in condition_raw:
        condition = "NEW"
    elif "refurbished" in condition_raw:
        condition = "REFURBISHED"
    elif "used" in condition_raw:
        condition = "USED"

    product_type = raw.get("product_type", "")
    category_path = [
        c.strip() for c in re.split(r"\s*>\s*", product_type) if c.strip()
    ] if product_type else []

    return {
        "external_id": raw.get("id", ""),
        "title": title,
        "description": _strip_html(raw.get("description", "")),
        "price": price,
        "compare_at_price": compare_at_price,
        "currency": raw.get("currency") or "EUR",
        "image_url": raw.get("image_link", ""),
        "product_url": raw.get("link", "") or shop_url,
        "sku": raw.get("id", ""),
        "gtin": _validate_gtin(raw.get("gtin")),
        "mpn": raw.get("mpn") or None,
        "vendor": raw.get("brand") or None,
        "product_type": category_path[0] if category_path else None,
        "in_stock": in_stock,
        "condition": condition,
        "variants": [],
        "tags": [],
        "additional_images": raw.get("additional_image_link", []),
        "category_path": category_path,
    }


def _normalize_generic(raw: dict, shop_url: str) -> dict | None:
    # Google Shopping feed
    if raw.get("_source") == "google_feed":
        return _normalize_google_feed(raw, shop_url)

    # Schema.org JSON-LD
    is_schema_org = "name" in raw and (
        "offers" in raw
        or (isinstance(raw.get("@type"), str) and "Product" in raw.get("@type", ""))
        or (isinstance(raw.get("@type"), list) and any("Product" in str(t) for t in raw["@type"]))
    )
    if is_schema_org:
        return _normalize_schema_org(raw, shop_url)

    # OpenGraph
    if "og:title" in raw or "product:price:amount" in raw:
        return _normalize_opengraph(raw, shop_url)

    # Direct field mapping
    return _normalize_css_generic(raw, shop_url)


def _parse_condition(condition_str: str) -> str | None:
    if not condition_str:
        return None
    condition_str = str(condition_str)
    if "NewCondition" in condition_str:
        return "NEW"
    if "RefurbishedCondition" in condition_str:
        return "REFURBISHED"
    if "UsedCondition" in condition_str or "DamagedCondition" in condition_str:
        return "USED"
    return None


def _extract_image_url(img: str | dict) -> str:
    if isinstance(img, dict):
        return img.get("url") or img.get("contentUrl") or ""
    return str(img) if img else ""


def _normalize_schema_org(raw: dict, shop_url: str) -> dict | None:
    title = raw.get("name", "").strip()
    if not title:
        return None

    offers = raw.get("offers", {})
    if isinstance(offers, list):
        offers = offers[0] if offers else {}

    try:
        price = Decimal(str(offers.get("price", "0")))
    except (InvalidOperation, ValueError):
        price = Decimal("0")

    image = raw.get("image", "")
    additional_images: list[str] = []
    if isinstance(image, dict):
        image_url = _extract_image_url(image)
    elif isinstance(image, list):
        image_url = _extract_image_url(image[0]) if image else ""
        additional_images = [url for img in image[1:] if (url := _extract_image_url(img))]
    else:
        image_url = str(image) if image else ""

    if not image_url:
        image_url = raw.get("thumbnailUrl", "")
    if not image_url:
        image_url = raw.get("og:image", "")

    availability = offers.get("availability", "")
    in_stock = "InStock" in str(availability) if availability else True

    additional = _parse_additional_properties(raw.get("additionalProperty", []))

    gtin_raw = (
        raw.get("gtin13") or raw.get("gtin") or raw.get("gtin14")
        or raw.get("gtin12") or raw.get("gtin8") or raw.get("isbn")
        or offers.get("gtin13") or offers.get("gtin") or offers.get("gtin14")
        or offers.get("gtin12") or offers.get("gtin8")
        or additional.get("gtin13") or additional.get("gtin12")
        or additional.get("gtin14") or additional.get("gtin8")
        or additional.get("gtin") or additional.get("ean")
        or additional.get("isbn")
    )
    gtin = _validate_gtin(gtin_raw)

    mpn = raw.get("mpn") or offers.get("mpn") or None
    sku = raw.get("sku") or additional.get("mpn")
    external_id = raw.get("sku") or raw.get("productID") or gtin or ""

    condition = _parse_condition(offers.get("itemCondition", ""))

    category = raw.get("category")
    category_path: list[str] = []
    if isinstance(category, str) and category.strip():
        category_path = [c.strip() for c in re.split(r"[>/]", category) if c.strip()]
    elif isinstance(category, list):
        category_path = [str(c) for c in category if c]

    return {
        "external_id": external_id,
        "title": title,
        "description": _strip_html(raw.get("description", "")),
        "price": price,
        "compare_at_price": None,
        "currency": offers.get("priceCurrency", "USD"),
        "image_url": image_url,
        "product_url": raw.get("url", shop_url),
        "sku": sku,
        "gtin": gtin,
        "mpn": mpn,
        "vendor": raw.get("brand", {}).get("name") if isinstance(raw.get("brand"), dict) else raw.get("brand"),
        "product_type": None,
        "in_stock": in_stock,
        "condition": condition,
        "variants": [],
        "tags": [],
        "additional_images": additional_images,
        "category_path": category_path,
    }


def _normalize_opengraph(raw: dict, shop_url: str) -> dict | None:
    title = raw.get("og:title", "").strip()
    if not title:
        return None

    price_amount = raw.get("og:price:amount") or raw.get("product:price:amount", "0")
    try:
        price = Decimal(str(price_amount))
    except (InvalidOperation, ValueError):
        price = Decimal("0")

    return {
        "external_id": raw.get("og:product_id", raw.get("product:retailer_item_id", "")),
        "title": title,
        "description": _strip_html(raw.get("og:description", "")),
        "price": price,
        "compare_at_price": None,
        "currency": raw.get("og:price:currency") or raw.get("product:price:currency", "USD"),
        "image_url": raw.get("og:image", ""),
        "product_url": raw.get("og:url", shop_url),
        "sku": None,
        "gtin": None,
        "mpn": None,
        "vendor": None,
        "product_type": None,
        "in_stock": True,
        "condition": raw.get("product:condition") or None,
        "variants": [],
        "tags": [],
        "additional_images": [],
        "category_path": [raw["product:category"]] if raw.get("product:category") else [],
    }


def _normalize_css_generic(raw: dict, shop_url: str) -> dict | None:
    title = (
        raw.get("title") or raw.get("name") or raw.get("product_name") or raw.get("heading") or ""
    ).strip()
    if not title:
        return None

    price_raw = raw.get("price", "0")
    try:
        if isinstance(price_raw, str):
            price_cleaned = price_raw.replace("$", "").replace("\u20ac", "").replace("\u00a3", "").strip()
            if "," in price_cleaned and "." in price_cleaned:
                price_cleaned = price_cleaned.replace(",", "")
            elif "," in price_cleaned:
                price_cleaned = price_cleaned.replace(",", ".")
            price = Decimal(price_cleaned)
        else:
            price = Decimal(str(price_raw))
    except (InvalidOperation, ValueError):
        price = Decimal("0")

    return {
        "external_id": raw.get("sku", raw.get("id", "")),
        "title": title,
        "description": _strip_html(raw.get("description", "")),
        "price": price,
        "compare_at_price": None,
        "currency": raw.get("currency") or raw.get("price_currency") or "USD",
        "image_url": raw.get("image") or raw.get("image_url") or raw.get("src") or "",
        "product_url": raw.get("product_url") or raw.get("url") or raw.get("canonical") or shop_url,
        "sku": raw.get("sku"),
        "gtin": _validate_gtin(raw.get("gtin") or raw.get("ean") or raw.get("barcode")),
        "mpn": raw.get("mpn") or None,
        "vendor": None,
        "product_type": None,
        "in_stock": True,
        "condition": None,
        "variants": [],
        "tags": [],
        "additional_images": [],
        "category_path": [],
    }
