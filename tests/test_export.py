"""Tests for CSV, JSON, and feed export."""

from __future__ import annotations

import csv
import json
import xml.etree.ElementTree as ET

import pytest

from shopextract.export import to_csv, to_json, to_feed


class TestToCsv:
    def test_basic_export(self, tmp_path, product_dicts_for_export):
        path = str(tmp_path / "products.csv")
        to_csv(product_dicts_for_export, path)

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["title"] == "Export Product 1"
        assert rows[0]["price"] == "19.99"
        assert rows[1]["external_id"] == "P002"

    def test_csv_headers(self, tmp_path, product_dicts_for_export):
        path = str(tmp_path / "products.csv")
        to_csv(product_dicts_for_export, path)

        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            headers = next(reader)

        assert "title" in headers
        assert "price" in headers
        assert "external_id" in headers

    def test_list_fields_flattened(self, tmp_path):
        products = [{"title": "A", "tags": ["tag1", "tag2"]}]
        path = str(tmp_path / "products.csv")
        to_csv(products, path)

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert rows[0]["tags"] == "tag1; tag2"

    def test_none_values(self, tmp_path):
        products = [{"title": "A", "gtin": None}]
        path = str(tmp_path / "products.csv")
        to_csv(products, path)

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert rows[0]["gtin"] == ""

    def test_empty_products(self, tmp_path):
        path = str(tmp_path / "products.csv")
        to_csv([], path)

        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert content == ""


class TestToJson:
    def test_basic_export(self, tmp_path, product_dicts_for_export):
        path = str(tmp_path / "products.json")
        to_json(product_dicts_for_export, path)

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 2
        assert data[0]["title"] == "Export Product 1"
        assert data[1]["title"] == "Export Product 2"

    def test_valid_json(self, tmp_path, product_dicts_for_export):
        path = str(tmp_path / "products.json")
        to_json(product_dicts_for_export, path)

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, list)

    def test_custom_indent(self, tmp_path):
        products = [{"title": "A"}]
        path = str(tmp_path / "products.json")
        to_json(products, path, indent=4)

        with open(path, encoding="utf-8") as f:
            content = f.read()

        assert "    " in content

    def test_empty_products(self, tmp_path):
        path = str(tmp_path / "products.json")
        to_json([], path)

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        assert data == []


class TestToFeedGoogleShopping:
    def test_basic_xml(self, tmp_path, product_dicts_for_export):
        path = str(tmp_path / "feed.xml")
        to_feed(product_dicts_for_export, path, format="google_shopping")

        tree = ET.parse(path)
        root = tree.getroot()
        assert root.tag == "rss"
        assert root.get("version") == "2.0"

    def test_xml_items(self, tmp_path, product_dicts_for_export):
        path = str(tmp_path / "feed.xml")
        to_feed(product_dicts_for_export, path, format="google_shopping")

        tree = ET.parse(path)
        root = tree.getroot()
        items = root.findall(".//item")
        assert len(items) == 2

    def test_xml_has_title(self, tmp_path, product_dicts_for_export):
        path = str(tmp_path / "feed.xml")
        to_feed(product_dicts_for_export, path, format="google_shopping")

        tree = ET.parse(path)
        root = tree.getroot()
        item = root.findall(".//item")[0]
        title_el = item.find("title")
        assert title_el is not None
        assert title_el.text == "Export Product 1"

    def test_xml_availability(self, tmp_path, product_dicts_for_export):
        path = str(tmp_path / "feed.xml")
        to_feed(product_dicts_for_export, path, format="google_shopping")

        ns = {"g": "http://base.google.com/ns/1.0"}
        tree = ET.parse(path)
        root = tree.getroot()
        items = root.findall(".//item")

        avail_0 = items[0].find("g:availability", ns)
        assert avail_0.text == "in stock"

        avail_1 = items[1].find("g:availability", ns)
        assert avail_1.text == "out of stock"

    def test_xml_price_format(self, tmp_path):
        products = [{"title": "A", "price": "19.99", "currency": "EUR", "external_id": "1"}]
        path = str(tmp_path / "feed.xml")
        to_feed(products, path, format="google_shopping")

        ns = {"g": "http://base.google.com/ns/1.0"}
        tree = ET.parse(path)
        root = tree.getroot()
        price_el = root.find(".//item/g:price", ns)
        assert price_el is not None
        assert "EUR" in price_el.text


class TestToFeedIdealo:
    def test_basic_tsv(self, tmp_path, product_dicts_for_export):
        path = str(tmp_path / "feed.tsv")
        to_feed(product_dicts_for_export, path, format="idealo")

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            rows = list(reader)

        assert len(rows) == 2

    def test_tsv_headers(self, tmp_path, product_dicts_for_export):
        path = str(tmp_path / "feed.tsv")
        to_feed(product_dicts_for_export, path, format="idealo")

        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            headers = next(reader)

        expected = ["sku", "title", "price", "currency", "product_url",
                     "image_url", "brand", "gtin", "delivery_time",
                     "delivery_cost", "description", "condition"]
        assert headers == expected

    def test_sku_fallback_to_external_id(self, tmp_path):
        products = [{"external_id": "EXT-1", "title": "A"}]
        path = str(tmp_path / "feed.tsv")
        to_feed(products, path, format="idealo")

        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            rows = list(reader)

        assert rows[0]["sku"] == "EXT-1"


class TestToFeedEdgeCases:
    def test_unsupported_format(self, tmp_path):
        with pytest.raises(ValueError, match="Unsupported feed format"):
            to_feed([], str(tmp_path / "feed.txt"), format="unknown")

    def test_empty_products(self, tmp_path):
        path = str(tmp_path / "feed.xml")
        to_feed([], path, format="google_shopping")
        tree = ET.parse(path)
        items = tree.findall(".//item")
        assert len(items) == 0
