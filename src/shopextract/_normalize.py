"""Product normalizer -- map raw data from any extractor to unified Product model."""

from __future__ import annotations

import logging
import re
from decimal import Decimal, InvalidOperation
from urllib.parse import urljoin

from ._models import Platform, Product, Variant
from .identity import assign_identity
from ._normalization import Normalizer

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
    value = str(value).strip().replace("-", "").replace(" ", "")
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
    *,
    restore_short_gtin: bool = False,
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
        Platform.BIGCOMMERCE: _normalize_bigcommerce,
    }

    normalized_data = None
    method = (raw.get('_capture') or {}).get('method', '')
    generic_source = (method.startswith(('json_ld', 'opengraph', 'css', 'llm', 'feed_'))
                      or raw.get('_source') == 'google_feed'
                      or 'offers' in raw or 'og:title' in raw
                      or 'Product' in str(raw.get('@type', '')))
    if generic_source:
        normalized_data = _normalize_generic(raw, shop_url)
    elif platform in normalizers:
        normalized_data = normalizers[platform](raw, shop_url)

    if not normalized_data:
        normalized_data = _normalize_generic(raw, shop_url)

    if not normalized_data:
        return None

    trace = Normalizer(raw)
    trace.outcomes = normalized_data.outcomes
    identifier_notes = []
    if platform == Platform.SHOPIFY and restore_short_gtin:
        from .compare.identity_match import _gtin
        for index, variant in enumerate(raw.get("variants") or []):
            barcode = str(variant.get("barcode") or "").strip()
            if len(barcode) == 11 and _gtin("0" + barcode):
                restored = _validate_gtin("0" + barcode)
                identifier_notes.append({"variant_id": str(variant.get("id", "")), "source_barcode": barcode, "normalized_gtin": restored, "policy": "restore_upc_leading_zero"})
                if index == 0:
                    normalized_data["gtin"] = trace.record("gtin", f"/variants/{index}/barcode", restored, operation="restore_upc_leading_zero")
                for output_index, normalized_variant in enumerate(normalized_data.get("variants", [])):
                    if normalized_variant.variant_id == str(variant.get("id", "")):
                        normalized_variant.gtin = trace.record(f"variants/{output_index}/gtin", f"/variants/{index}/barcode", restored, operation="restore_upc_leading_zero")
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

    if identifier_notes:
        product.raw_data = {**raw, "_identifier_normalization": identifier_notes}
    if not _is_valid_product(product):
        return None
    product.attributes = trace.emit('attributes', '/attributes', default={},
                                    convert=lambda v: dict(v) if isinstance(v, dict) else None)
    product.pack_quantity = trace.emit('pack_quantity', '/pack_quantity')
    product.bundle_components = trace.emit('bundle_components', '/bundle_components',
                                          default=[], convert=lambda v: list(v or []))
    if not product.vendor:
        product.vendor = trace.emit('vendor', '/vendor',
                                    *(['/brand'] if isinstance(raw.get('brand'), str) else []), truthy=True)
    for field in ('attributes', 'bundle_components', 'tags', 'additional_images', 'category_path'):
        trace.record_nested(field, getattr(product, field))
    scope = raw.get("supplier_id") or shop_url or product.product_url
    if scope:
        assign_identity(product, scope)
    from ._capture import attach_contract
    attach_contract(product, raw, trace.outcomes)
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
        if isinstance(variant.get("available"), bool):
            if variant["available"]:
                return True
            continue
        inventory_qty = variant.get("inventory_quantity")
        if inventory_qty is None or inventory_qty > 0:
            return True
    return False


def _record_items(trace, field, source, items, paths, operation):
    trace.record(field, source, items, operation=operation)
    for i, path in enumerate(paths):
        trace.record(f'{field}/{i}', path, items[i], operation=operation)
    return items


def _variant_stock(trace, *, shopify):
    if shopify:
        availability = trace.select('/available')
        if isinstance(availability.value, bool):
            return trace.record('in_stock', availability, availability.value)
        quantity = trace.select('/inventory_quantity')
        value = quantity.value is None or quantity.value > 0
        return trace.record('in_stock', quantity, value,
                            accepted=quantity.present and quantity.value is not None,
                            operation='Inventory quantity greater than zero')
    return trace.emit('in_stock', '/in_stock', default=True, convert=bool,
                      operation='Convert explicit Shopware in_stock to boolean')


def _variants(raw, trace, *, shopify):
    variants = []
    for source_index, v in enumerate(raw.get('variants') or []):
        if not isinstance(v, dict):
            continue
        item = Normalizer(v)
        try:
            price = item.money('price', '/price', stringify=not shopify, truthy=not shopify, strict=True)
            stock = _variant_stock(item, shopify=shopify)
            attributes = {}
            if shopify:
                for i in range(1, 4):
                    if v.get(f'option{i}'):
                        attributes[f'option{i}'] = item.emit(f'attributes/option{i}', f'/option{i}', convert=str)
            variant = Variant(
                variant_id=item.emit('variant_id', *(['/id'] if shopify else ['/variant_id', '/id']),
                                     default='', convert=str, truthy=not shopify),
                title=item.emit('title', *(['/title'] if shopify else ['/title', '/name']),
                                default='', truthy=not shopify),
                price=price, sku=item.emit('sku', '/sku'), in_stock=stock,
                gtin=item.emit('gtin', '/barcode', convert=_validate_gtin) if shopify else None,
                attributes=attributes)
        except (ValueError, TypeError, InvalidOperation) as exc:
            logger.debug('Failed to parse variant %s: %s', v.get('id', '?'), exc)
            continue
        trace.inherit(item, f'/variants/{len(variants)}', f'/variants/{source_index}')
        variants.append(variant)
    trace.record('variants', '/variants', variants, operation='Normalize variants; omit invalid items')
    return variants


def _normalize_shopify(raw: dict, shop_url: str) -> dict | None:
    t = Normalizer(raw)
    title = t.emit('title', '/title', default='', convert=str.strip)
    if not title:
        return None
    variants_raw = raw.get('variants', [])
    images = raw.get('images', [])
    additional = [img['src'] for img in images[1:] if img.get('src')]
    image_paths = [f'/images/{i}/src' for i,img in enumerate(images) if i > 0 and img.get('src')]
    if isinstance(raw.get('available'), bool):
        stock = t.emit('in_stock', '/available')
    else:
        stock_inputs = []
        for i, variant in enumerate(variants_raw):
            path = f'/variants/{i}/available' if isinstance(variant.get('available'), bool) else f'/variants/{i}/inventory_quantity'
            stock_inputs.append(t.select(path))
        stock = t.record_inputs('in_stock', stock_inputs, _shopify_stock_status(variants_raw),
                                accepted=all(s.value is not None for s in stock_inputs),
                                operation='Aggregate explicit variant availability/inventory')
    tags = raw.get('tags', '')
    parsed_tags = [tag.strip() for tag in tags.split(',') if tag.strip()] if isinstance(tags, str) else list(tags) if tags else []
    tag_paths = ['/tags']*len(parsed_tags) if isinstance(tags, str) else [f'/tags/{i}' for i in range(len(parsed_tags))]
    category = [raw['product_type']] if raw.get('product_type') else []
    return t.result({
        'external_id': t.emit('external_id', '/id', default='', convert=str),
        'title': title,
        'description': t.emit('description', '/body_html', default='', convert=_strip_html, operation='Strip HTML and whitespace'),
        'price': t.money('price', '/variants/0/price'),
        'compare_at_price': t.money('compare_at_price', '/variants/0/compare_at_price', default=None, truthy=True),
        'currency': t.emit('currency', '/variants/0/price_currency', '/currency', '/_shop_currency', default='USD', truthy=True),
        'image_url': t.emit('image_url', '/images/0/src', default=''),
        'product_url': t.emit('product_url', '/handle', default=shop_url, truthy=True,
                              convert=lambda handle: f"{shop_url.rstrip('/')}/products/{handle}", operation='Resolve product handle using configured shop URL'),
        'sku': t.emit('sku', '/variants/0/sku'),
        'gtin': t.emit('gtin', '/variants/0/barcode', convert=_validate_gtin, operation='Validate GTIN; pad 12-digit UPC with zero'),
        'vendor': t.emit('vendor', '/vendor'),
        'product_type': t.emit('product_type', '/product_type'),
        'in_stock': stock,
        'variants': _variants(raw, t, shopify=True),
        'tags': _record_items(t, 'tags', '/tags', parsed_tags, tag_paths, 'Parse/trim tags'),
        'additional_images': _record_items(t, 'additional_images', '/images', additional, image_paths, 'Project remaining image URLs'),
        'category_path': _record_items(t, 'category_path', '/product_type', category, ['/product_type']*len(category), 'Project product category'),
    })


def _normalize_woocommerce(raw: dict, shop_url: str) -> dict | None:
    t = Normalizer(raw)
    title = t.emit('title', '/title', '/name', default='', truthy=True, convert=str.strip)
    if not title:
        return None
    admin = raw.get('_source') == 'woocommerce_admin_api' or (isinstance(raw.get('price'), str) and 'prices' not in raw)
    if admin:
        price = t.money('price', '/price', truthy=True)
        compare = t.money('compare_at_price', '/compare_at_price', default=None, truthy=True)
        currency = t.emit('currency', '/currency', default='USD')
    else:
        minor_unit = raw.get('prices', {}).get('currency_minor_unit', 2)
        divisor = 10**minor_unit
        operation = f'Parse decimal minor-unit amount; divide by 10 ** currency_minor_unit ({minor_unit})'
        price = t.money('price', '/prices/price', divisor=divisor, operation=operation)
        compare = t.money('compare_at_price', '/prices/regular_price', default=None,
                          truthy=True, divisor=divisor, operation=operation)
        currency = t.emit('currency', '/prices/currency_code', default='USD')
    if compare == price:
        compare = None
    images = raw.get('images', [])
    if images and isinstance(images[0], dict):
        image = t.emit('image_url', '/images/0/src', default='')
        additional = [img['src'] for img in images[1:] if img.get('src')]
        paths = [f'/images/{i}/src' for i,img in enumerate(images) if i > 0 and img.get('src')]
        additional = _record_items(t, 'additional_images', '/images', additional, paths, 'Project remaining image URLs')
    else:
        image = t.emit('image_url', '/image_url', default='')
        additional = t.emit('additional_images', '/additional_images', default=[], operation='Retain additional images')
        for i, value in enumerate(additional):
            t.record(f'additional_images/{i}', f'/additional_images/{i}', value)
    tags_raw = raw.get('tags', [])
    if tags_raw and isinstance(tags_raw[0], dict):
        positions = [i for i,v in enumerate(tags_raw) if isinstance(v, dict)]
        tags = [tags_raw[i].get('name', '') for i in positions]
        paths = [f'/tags/{i}/name' for i in positions]
    else:
        tags, paths = tags_raw, [f'/tags/{i}' for i in range(len(tags_raw))]
    categories = raw.get('categories', [])
    if categories and isinstance(categories[0], dict):
        positions = [i for i,v in enumerate(categories) if isinstance(v, dict) and v.get('name')]
        category = [categories[i]['name'] for i in positions]
        cat_paths = [f'/categories/{i}/name' for i in positions]
    else:
        category, cat_paths = categories, [f'/categories/{i}' for i in range(len(categories))]
    return t.result({
        'external_id': t.emit('external_id', '/id', default='', convert=str), 'title':title,
        'description': t.emit('description', '/description', default='', convert=_strip_html, operation='Strip HTML and whitespace'),
        'price':price, 'compare_at_price':compare, 'currency':currency, 'image_url':image,
        'product_url': t.emit('product_url', '/permalink', '/product_url', default='', truthy=True),
        'sku': t.emit('sku', '/sku'),
        'gtin': t.emit('gtin', '/gtin', '/ean', '/barcode', truthy=True, convert=_validate_gtin, operation='Validate GTIN; pad 12-digit UPC with zero'),
        'mpn': t.emit('mpn', '/mpn', truthy=True),
        'in_stock': t.emit('in_stock', '/is_in_stock', default=True, convert=lambda v: v if isinstance(v, bool) else None),
        'tags': _record_items(t, 'tags', '/tags', tags, paths, 'Project tag names'),
        'additional_images':additional,
        'category_path': _record_items(t, 'category_path', '/categories', category, cat_paths, 'Project category names'),
    })


def _normalize_magento_graphql(raw: dict, shop_url: str) -> dict | None:
    """Normalize public Magento GraphQL products using their native field paths."""
    t = Normalizer(raw)
    title = t.emit('title', '/name', default='', convert=str.strip)
    if not title:
        return None
    price_path = '/price_range/minimum_price/final_price'
    key, suffix = t.select('/url_key'), t.select('/url_suffix')
    product_url = urljoin(shop_url.rstrip('/') + '/', str(key.value or '') + str(suffix.value or ''))
    t.record_inputs('product_url', [key, suffix], product_url,
                    accepted=bool(key.value), operation='Resolve Magento URL key and configured suffix')
    variants = []
    for i, entry in enumerate(raw.get('variants') or []):
        child = entry.get('product') if isinstance(entry, dict) else None
        if not isinstance(child, dict):
            continue
        data = _normalize_magento_graphql(child, shop_url)
        if not data:
            continue
        v = Variant(variant_id=data.get('sku', ''), title=data['title'],
                    price=data['price'], sku=data.get('sku'), in_stock=data['in_stock'])
        t.inherit(data, f'/variants/{len(variants)}', f'/variants/{i}/product')
        t.record(f'variants/{len(variants)}/variant_id', f'/variants/{i}/product/sku', v.variant_id)
        for j, attr in enumerate(entry.get('attributes') or []):
            if attr.get('code') and attr.get('value_index') is not None:
                code = str(attr['code'])
                v.attributes[code] = str(attr['value_index'])
                token = code.replace('~', '~0').replace('/', '~1')
                t.record(f'variants/{len(variants)}/attributes/{token}',
                         f'/variants/{i}/attributes/{j}/value_index', str(attr['value_index']),
                         operation='Represent Magento option value index as string')
        variants.append(v)
    return t.result({
        'external_id': t.emit('external_id', '/sku', default=''),
        'sku': t.emit('sku', '/sku'), 'title': title,
        'price': t.money('price', price_path + '/value', stringify=True),
        'currency': t.emit('currency', price_path + '/currency', default='USD'),
        'description': t.emit('description', '/description/html', default='',
                              convert=_strip_html, operation='Strip HTML and whitespace'),
        'image_url': t.emit('image_url', '/image/url', default=''),
        'product_url': product_url, 'variants': variants,
        'in_stock': t.emit('in_stock', '/stock_status', default=True,
                           convert=lambda v: {'IN_STOCK': True, 'OUT_OF_STOCK': False}.get(v),
                           operation='Map Magento stock status'),
    })


def _normalize_shopware_store_api(raw: dict, shop_url: str) -> dict | None:
    """Keep Shopware availability and calculated prices tied to native API fields."""
    t = Normalizer(raw)
    title = t.emit('title', '/translated/name', '/name', default='', truthy=True, convert=str.strip)
    if not title:
        return None
    variants = []
    for i, child in enumerate(raw.get('children') or []):
        if not isinstance(child, dict):
            continue
        v = Normalizer(child)
        variant = Variant(
            variant_id=v.emit('variant_id', '/id', default='', convert=str),
            title=v.emit('title', '/translated/name', '/name', default='', truthy=True),
            price=v.money('price', '/calculatedPrice/unitPrice', stringify=True),
            sku=v.emit('sku', '/productNumber'),
            gtin=v.emit('gtin', '/ean', truthy=True, convert=_validate_gtin,
                        operation='Validate GTIN; pad 12-digit UPC with zero'),
            in_stock=v.emit('in_stock', '/available', default=True,
                            convert=lambda x: x if isinstance(x, bool) else None),
        )
        t.inherit(v, f'/variants/{len(variants)}', f'/children/{i}')
        variants.append(variant)
    return t.result({
        'external_id': t.emit('external_id', '/id', default='', convert=str),
        'title': title, 'sku': t.emit('sku', '/productNumber'),
        'description': t.emit('description', '/translated/description', '/description',
                              default='', truthy=True, convert=_strip_html,
                              operation='Strip HTML and whitespace'),
        'price': t.money('price', '/calculatedPrice/unitPrice', stringify=True),
        'compare_at_price': t.money('compare_at_price', '/calculatedPrice/listPrice/price',
                                    default=None, stringify=True),
        'currency': t.emit('currency', '/currency', default='EUR', truthy=True),
        'image_url': t.emit('image_url', '/cover/media/url', default='', truthy=True),
        'product_url': t.emit('product_url', '/seoUrls/0/seoPathInfo', default=shop_url,
                              truthy=True, convert=lambda v: urljoin(shop_url.rstrip('/') + '/', v),
                              operation='Resolve Shopware SEO path'),
        'gtin': t.emit('gtin', '/ean', truthy=True, convert=_validate_gtin,
                       operation='Validate GTIN; pad 12-digit UPC with zero'),
        'vendor': t.emit('vendor', '/manufacturer/translated/name', '/manufacturer/name', truthy=True),
        'in_stock': t.emit('in_stock', '/available', default=True,
                           convert=lambda v: v if isinstance(v, bool) else None),
        'variants': variants,
    })


def _normalize_bigcommerce(raw: dict, shop_url: str) -> dict | None:
    if 'entityId' not in raw:
        return None
    t = Normalizer(raw)
    title = t.emit('title', '/name', default='', convert=str.strip)
    if not title:
        return None
    variants = []
    for i, edge in enumerate((raw.get('variants') or {}).get('edges') or []):
        child = edge.get('node') if isinstance(edge, dict) else None
        if not isinstance(child, dict):
            continue
        v = Normalizer(child)
        item = Variant(
            variant_id=v.emit('variant_id', '/entityId', default='', convert=str),
            title=v.emit('title', '/sku', default='', operation='Use variant SKU as display label'),
            sku=v.emit('sku', '/sku'),
            price=v.money('price', '/prices/price/value', stringify=True),
            gtin=v.emit('gtin', '/upc', truthy=True, convert=_validate_gtin,
                        operation='Validate GTIN; pad 12-digit UPC with zero'),
            in_stock=v.emit('in_stock', '/inventory/isInStock', default=True,
                            convert=lambda x: x if isinstance(x, bool) else None))
        t.inherit(v, f'/variants/{len(variants)}', f'/variants/edges/{i}/node')
        variants.append(item)
    return t.result({
        'external_id': t.emit('external_id', '/entityId', default='', convert=str),
        'title': title, 'sku': t.emit('sku', '/sku'),
        'description': t.emit('description', '/description', default='', convert=_strip_html,
                              operation='Strip HTML and whitespace'),
        'price': t.money('price', '/prices/price/value', stringify=True),
        'currency': t.emit('currency', '/prices/price/currencyCode', default='USD'),
        'image_url': t.emit('image_url', '/defaultImage/urlOriginal', default=''),
        'product_url': t.emit('product_url', '/path', default=shop_url,
                              convert=lambda v: urljoin(shop_url, v),
                              operation='Resolve BigCommerce storefront product path'),
        'gtin': t.emit('gtin', '/upc', truthy=True, convert=_validate_gtin,
                       operation='Validate GTIN; pad 12-digit UPC with zero'),
        'vendor': t.emit('vendor', '/brand/name', truthy=True),
        'in_stock': t.emit('in_stock', '/inventory/isInStock', default=True,
                           convert=lambda x: x if isinstance(x, bool) else None),
        'variants': variants,
    })


def _normalize_magento(raw: dict, shop_url: str) -> dict | None:
    if isinstance(raw.get("price_range"), dict):
        return _normalize_magento_graphql(raw, shop_url)
    t = Normalizer(raw)
    title = t.emit('title', '/name', default='', convert=str.strip)
    if not title:
        return None
    attr_paths = {}
    for i, attr in enumerate(raw.get('custom_attributes', [])):
        if isinstance(attr, dict):
            field = {'description':'description','image':'image_url','url_key':'product_url',
                     'ean':'gtin','gtin':'gtin','barcode':'gtin','mpn':'mpn','manufacturer':'vendor'}.get(attr.get('attribute_code'))
            if field:
                attr_paths[field] = f'/custom_attributes/{i}/value'
    def attr(field, **kwargs):
        return t.emit(field, *([attr_paths[field]] if field in attr_paths else []), **kwargs)
    image_path = t.select(attr_paths['image_url']).value if 'image_url' in attr_paths else ''
    additional, paths = [], []
    for i, entry in enumerate(raw.get('media_gallery_entries', [])):
        if isinstance(entry, dict) and entry.get('file') and not entry.get('disabled') and entry['file'] != image_path:
            additional.append(f"{shop_url.rstrip('/')}/media/catalog/product{entry['file']}")
            paths.append(f'/media_gallery_entries/{i}/file')
    return t.result({
        'external_id':t.emit('external_id', '/sku', '/id', default='', convert=lambda v: v if 'sku' in raw else str(v)),
        'title':title, 'currency':t.emit('currency','/currency',default='USD'),
        'price':t.money('price','/price',stringify=True),
        'description':attr('description',default='',convert=_strip_html,operation='Strip HTML and whitespace'),
        'image_url':attr('image_url',default='',truthy=True,convert=lambda v:f"{shop_url.rstrip('/')}/media/catalog/product{v}",operation='Resolve Magento media path'),
        'product_url':attr('product_url',default=shop_url,truthy=True,convert=lambda v:f"{shop_url.rstrip('/')}/{v}.html",operation='Resolve Magento product URL key'),
        'sku':t.emit('sku','/sku'), 'gtin':attr('gtin',truthy=True),
        'mpn':attr('mpn',truthy=True), 'vendor':attr('vendor',truthy=True),
        'additional_images':_record_items(t,'additional_images','/media_gallery_entries',additional,paths,'Resolve remaining Magento media paths'),
    })


def _normalize_shopware(raw: dict, shop_url: str) -> dict | None:
    if isinstance(raw.get("calculatedPrice"), dict):
        return _normalize_shopware_store_api(raw, shop_url)
    t = Normalizer(raw)
    title = t.emit('title','/title','/name',default='',truthy=True,convert=str.strip)
    if not title:
        return None
    price = t.money('price','/price',stringify=True,truthy=True)
    compare = t.money('compare_at_price','/compare_at_price',default=None,stringify=True,truthy=True)
    if compare == price:
        compare = None
    return t.result({
        'external_id':t.emit('external_id','/id','/sku',default='',truthy=True,convert=str),
        'title':title, 'description':t.emit('description','/description',default='',truthy=True,convert=_strip_html,operation='Strip HTML and whitespace'),
        'price':price, 'compare_at_price':compare,
        'currency':t.emit('currency','/currency',default='EUR',truthy=True),
        'image_url':t.emit('image_url','/image_url',default='',truthy=True),
        'product_url':t.emit('product_url','/product_url',default=shop_url,truthy=True),
        'sku':t.emit('sku','/sku'),
        'gtin':t.emit('gtin','/gtin','/barcode','/ean',truthy=True,convert=_validate_gtin,operation='Validate GTIN; pad 12-digit UPC with zero'),
        'vendor':t.emit('vendor','/vendor',truthy=True),
        'in_stock':t.emit('in_stock','/in_stock',default=True,convert=bool),
        'condition':t.emit('condition','/condition',truthy=True),
        'variants':_variants(raw,t,shopify=False),
        'tags':t.emit('tags','/tags',default=[],convert=lambda v:list(v or [])),
        'additional_images':t.emit('additional_images','/additional_images',default=[],convert=lambda v:list(v or [])),
        'category_path':t.emit('category_path','/categories',default=[],convert=lambda v:list(v or [])),
    })


def _normalize_google_feed(raw: dict, shop_url: str) -> dict | None:
    t = Normalizer(raw)
    title = t.emit('title','/title',default='',truthy=True,convert=str.strip)
    if not title:
        return None
    price = t.money('price','/price',truthy=True)
    sale = t.money('sale_price','/sale_price',default=None,truthy=True)
    compare = None
    if sale is not None and 0 < sale < price:
        compare, price = price, sale
        t.outcomes['/compare_at_price'] = t.outcomes['/price']
        t.outcomes['/price'] = t.outcomes['/sale_price']
    t.outcomes.pop('/sale_price',None)
    def condition(value):
        value = value.lower()
        return next((result for source,result in [('new','NEW'),('refurbished','REFURBISHED'),('used','USED')] if source in value),None)
    product_type = raw.get('product_type','')
    category = [c.strip() for c in re.split(r'\s*>\s*',product_type) if c.strip()] if product_type else []
    return t.result({
        'external_id':t.emit('external_id','/id',default=''), 'title':title,
        'description':t.emit('description','/description',default='',convert=_strip_html,operation='Strip HTML and whitespace'),
        'price':price,'compare_at_price':compare,
        'currency':t.emit('currency','/currency',default='EUR',truthy=True),
        'image_url':t.emit('image_url','/image_link',default=''),
        'product_url':t.emit('product_url','/link',default=shop_url,truthy=True),
        'sku':t.emit('sku','/id',default=''),
        'gtin':t.emit('gtin','/gtin',convert=_validate_gtin,operation='Validate GTIN; pad 12-digit UPC with zero'),
        'mpn':t.emit('mpn','/mpn',truthy=True), 'vendor':t.emit('vendor','/brand',truthy=True),
        'product_type':t.record('product_type','/product_type',category[0] if category else None,accepted=bool(category),operation='Select first feed category'),
        'in_stock':t.emit('in_stock','/availability',default=True,truthy=True,convert=lambda v:'in_stock' in v.lower().replace(' ','_'),operation='Map feed availability to boolean'),
        'condition':t.emit('condition','/condition',truthy=True,convert=condition,operation='Map recognized feed condition'),
        'additional_images':t.emit('additional_images','/additional_image_link',default=[]),
        'category_path':_record_items(t,'category_path','/product_type',category,['/product_type']*len(category),'Split feed category path'),
    })


def _normalize_generic(raw: dict, shop_url: str) -> dict | None:
    if raw.get('_source') == 'google_feed':
        return _normalize_google_feed(raw,shop_url)
    is_schema_org = 'name' in raw and ('offers' in raw
        or (isinstance(raw.get('@type'),str) and 'Product' in raw['@type'])
        or (isinstance(raw.get('@type'),list) and any('Product' in str(t) for t in raw['@type'])))
    if is_schema_org:
        return _normalize_schema_org(raw,shop_url)
    if 'og:title' in raw or 'product:price:amount' in raw:
        return _normalize_opengraph(raw,shop_url)
    return _normalize_css_generic(raw,shop_url)


def _parse_condition(condition_str: str) -> str | None:
    if not condition_str:
        return None
    condition_str = str(condition_str)
    if 'NewCondition' in condition_str:
        return 'NEW'
    if 'RefurbishedCondition' in condition_str:
        return 'REFURBISHED'
    if 'UsedCondition' in condition_str or 'DamagedCondition' in condition_str:
        return 'USED'
    return None


def _extract_image_url(img: str | dict) -> str:
    if isinstance(img,dict):
        return img.get('url') or img.get('contentUrl') or ''
    return str(img) if img else ''


def _normalize_schema_org(raw: dict, shop_url: str) -> dict | None:
    t = Normalizer(raw)
    title = t.emit('title','/name',default='',convert=str.strip)
    if not title:
        return None
    offer = '/offers/0' if isinstance(raw.get('offers'),list) else '/offers'
    image = raw.get('image','')
    primary = '/image/0' if isinstance(image,list) else '/image'
    image_url = t.emit('image_url',primary,default='',convert=_extract_image_url,operation='Project primary image URL')
    if not image_url:
        image_url = t.emit('image_url','/thumbnailUrl',default='')
    if not image_url:
        image_url = t.emit('image_url','/og:image',default='')
    images, image_paths = [], []
    if isinstance(image,list):
        for i,img in enumerate(image):
            if i > 0 and (url := _extract_image_url(img)):
                images.append(url)
                image_paths.append(f'/image/{i}')
    additional_paths = {}
    for i, prop in enumerate(raw.get('additionalProperty',[])):
        if isinstance(prop,dict):
            key = str(prop.get('propertyID','') or prop.get('name','')).lower()
            additional_paths[key] = f'/additionalProperty/{i}/value'
    gtin_keys = ('gtin13','gtin','gtin14','gtin12','gtin8','isbn')
    additional_keys = ('gtin13','gtin12','gtin14','gtin8','gtin','ean','isbn')
    gtin = t.emit('gtin', *['/'+k for k in gtin_keys],
                  *[offer+'/'+k for k in gtin_keys if k != 'isbn'],
                  *[additional_paths[k] for k in additional_keys if k in additional_paths],
                  truthy=True,convert=_validate_gtin,operation='Validate GTIN; pad 12-digit UPC with zero')
    sku = t.emit('sku','/sku',*([additional_paths['mpn']] if 'mpn' in additional_paths else []),truthy=True)
    external = t.emit('external_id','/sku','/productID',default='',truthy=True)
    if not external and gtin:
        external = gtin
        t.outcomes['/external_id'] = t.outcomes['/gtin']
    category = raw.get('category')
    if isinstance(category,str) and category.strip():
        categories = [c.strip() for c in re.split(r'[>/]',category) if c.strip()]
        cat_paths = ['/category']*len(categories)
    elif isinstance(category,list):
        positions = [i for i,c in enumerate(category) if c]
        categories = [str(category[i]) for i in positions]
        cat_paths = [f'/category/{i}' for i in positions]
    else:
        categories, cat_paths = [], []
    return t.result({
        'external_id':external,'title':title,
        'description':t.emit('description','/description',default='',convert=_strip_html,operation='Strip HTML and whitespace'),
        'price':t.money('price',offer+'/price',stringify=True),
        'currency':t.emit('currency',offer+'/priceCurrency',default='USD'),
        'image_url':image_url, 'product_url':t.emit('product_url','/url',default=shop_url),
        'sku':sku,'gtin':gtin,'mpn':t.emit('mpn','/mpn',offer+'/mpn',truthy=True),
        'vendor':t.emit('vendor',*(['/brand/name'] if isinstance(raw.get('brand'),dict) else ['/brand'])),
        'in_stock':t.emit('in_stock',offer+'/availability',default=True,truthy=True,convert=lambda v:'InStock' in str(v),operation='Map Schema.org availability'),
        'condition':t.emit('condition',offer+'/itemCondition',convert=_parse_condition,operation='Map recognized Schema.org condition'),
        'additional_images':_record_items(t,'additional_images','/image',images,image_paths,'Project remaining image URLs'),
        'category_path':_record_items(t,'category_path','/category',categories,cat_paths,'Split/project category path'),
    })


def _normalize_opengraph(raw: dict, shop_url: str) -> dict | None:
    t = Normalizer(raw)
    title = t.emit('title','/og:title',default='',convert=str.strip)
    if not title:
        return None
    # First price/currency uses `or`, second uses `get` semantics (explicit zero survives).
    price_path = '/og:price:amount' if raw.get('og:price:amount') else '/product:price:amount'
    currency_path = '/og:price:currency' if raw.get('og:price:currency') else '/product:price:currency'
    category = [raw['product:category']] if raw.get('product:category') else []
    return t.result({
        'external_id':t.emit('external_id','/og:product_id','/product:retailer_item_id',default=''),
        'title':title,'description':t.emit('description','/og:description',default='',convert=_strip_html,operation='Strip HTML and whitespace'),
        'price':t.money('price',price_path,stringify=True),
        'currency':t.emit('currency',currency_path,default='USD'),
        'image_url':t.emit('image_url','/og:image',default=''),
        'product_url':t.emit('product_url','/og:url',default=shop_url),
        'condition':t.emit('condition','/product:condition',truthy=True),
        'category_path':_record_items(t,'category_path','/product:category',category,['/product:category']*len(category),'Project product category'),
    })


def _normalize_css_generic(raw: dict, shop_url: str) -> dict | None:
    t = Normalizer(raw)
    title = t.emit('title','/title','/name','/product_name','/heading',default='',truthy=True,convert=str.strip)
    if not title:
        return None
    currency = t.emit('currency', '/currency', '/price_currency', default='USD', truthy=True)
    if not t.outcomes['/currency'].accepted:
        price_input = t.select('/price')
        symbols = [code for symbol, code in [('£', 'GBP'), ('€', 'EUR')]
                   if isinstance(price_input.value, str) and symbol in price_input.value]
        if len(symbols) == 1 and '$' not in price_input.value:
            currency = t.record('currency', price_input, symbols[0],
                                operation='Infer currency from unambiguous price symbol')
    return t.result({
        'external_id':t.emit('external_id','/sku','/id',default=''), 'title':title,
        'description':t.emit('description','/description',default='',convert=_strip_html,operation='Strip HTML and whitespace'),
        'price':t.money('price','/price',stringify=True,css=True),
        'currency':currency,
        'image_url':t.emit('image_url','/image','/image_url','/src',default='',truthy=True,
                           convert=lambda v: urljoin(shop_url, v), operation='Resolve image reference against fetched page URL'),
        'product_url':t.emit('product_url','/product_url','/url','/canonical',default=shop_url,truthy=True),
        'sku':t.emit('sku','/sku'),
        'gtin':t.emit('gtin','/gtin','/ean','/barcode',truthy=True,convert=_validate_gtin,operation='Validate GTIN; pad 12-digit UPC with zero'),
        'mpn':t.emit('mpn','/mpn',truthy=True),
    })
