"""Marketplace feed export (Google Shopping XML, idealo TSV)."""

from __future__ import annotations

import csv
import xml.etree.ElementTree as ET

_SUPPORTED_FORMATS = ("google_shopping", "idealo")

_GOOGLE_NS = "http://base.google.com/ns/1.0"


def _write_feed(
    products: list[dict], path: str, format: str = "google_shopping",
) -> None:
    """Write products as a marketplace feed file.

    Args:
        products: List of product dicts.
        path: Output file path.
        format: "google_shopping" for RSS 2.0 XML or "idealo" for TSV.
    """
    if format not in _SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported feed format: {format!r}. "
            f"Supported: {list(_SUPPORTED_FORMATS)}"
        )

    if format == "google_shopping":
        _write_google_shopping_xml(products, path)
    else:
        _write_idealo_tsv(products, path)


def _write_google_shopping_xml(products: list[dict], path: str) -> None:
    """Write Google Shopping RSS 2.0 XML feed."""
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:g", _GOOGLE_NS)
    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Product Feed"
    ET.SubElement(channel, "link").text = ""
    ET.SubElement(channel, "description").text = "Product data feed"

    for product in products:
        item = ET.SubElement(channel, "item")
        _add_google_item_fields(item, product)

    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="unicode", xml_declaration=True)


def _add_google_item_fields(item: ET.Element, product: dict) -> None:
    """Add Google Shopping fields to an XML item element."""
    field_map = {
        "external_id": f"{{{_GOOGLE_NS}}}id",
        "title": "title",
        "description": "description",
        "product_url": "link",
        "image_url": f"{{{_GOOGLE_NS}}}image_link",
        "price": f"{{{_GOOGLE_NS}}}price",
        "brand": f"{{{_GOOGLE_NS}}}brand",
        "gtin": f"{{{_GOOGLE_NS}}}gtin",
        "mpn": f"{{{_GOOGLE_NS}}}mpn",
        "condition": f"{{{_GOOGLE_NS}}}condition",
        "product_type": f"{{{_GOOGLE_NS}}}product_type",
    }

    for src_field, xml_tag in field_map.items():
        value = product.get(src_field)
        if value is not None and str(value).strip():
            el = ET.SubElement(item, xml_tag)
            el.text = _format_price(value, product) if src_field == "price" else str(value)

    # Availability
    in_stock = product.get("in_stock", True)
    avail = ET.SubElement(item, f"{{{_GOOGLE_NS}}}availability")
    avail.text = "in stock" if in_stock else "out of stock"


def _format_price(price: object, product: dict) -> str:
    """Format price with currency for Google Shopping feed."""
    currency = product.get("currency", "USD")
    return f"{price} {currency}"


def _write_idealo_tsv(products: list[dict], path: str) -> None:
    """Write idealo TSV feed."""
    fieldnames = [
        "sku", "title", "price", "currency", "product_url",
        "image_url", "brand", "gtin", "delivery_time",
        "delivery_cost", "description", "condition",
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter="\t",
                                extrasaction="ignore")
        writer.writeheader()
        for product in products:
            row = _map_idealo_row(product, fieldnames)
            writer.writerow(row)


def _map_idealo_row(product: dict, fieldnames: list[str]) -> dict:
    """Map product dict to idealo TSV row."""
    row: dict[str, str] = {}
    for key in fieldnames:
        value = product.get(key)
        if key == "sku" and not value:
            value = product.get("external_id", "")
        row[key] = str(value) if value is not None else ""
    return row
