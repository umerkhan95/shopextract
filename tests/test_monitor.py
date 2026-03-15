"""Tests for snapshot storage and change detection."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from shopextract._models import ChangeType, NewProduct, PriceChange, RemovedProduct
from shopextract.monitor.changes import (
    _detect_changes,
    _products_by_title,
    changes,
    price_history,
)
from shopextract.monitor.snapshot import (
    _DecimalEncoder,
    _domain_from_url,
    _expand_path,
    _get_connection,
)


class TestDomainFromUrl:
    def test_full_url(self):
        assert _domain_from_url("https://example.com/path") == "example.com"

    def test_bare_domain(self):
        assert _domain_from_url("example.com") == "example.com"

    def test_with_www(self):
        assert _domain_from_url("https://www.example.com") == "www.example.com"


class TestDecimalEncoder:
    def test_decimal(self):
        result = json.dumps({"price": Decimal("19.99")}, cls=_DecimalEncoder)
        assert '"19.99"' in result

    def test_datetime(self):
        dt = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
        result = json.dumps({"ts": dt}, cls=_DecimalEncoder)
        assert "2026-03-15" in result


class TestGetConnection:
    def test_creates_db(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        conn = _get_connection(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "snapshots" in tables
        conn.close()


class TestProductsByTitle:
    def test_indexes_by_title(self):
        products = [
            {"title": "Widget A", "price": "10"},
            {"title": "Widget B", "price": "20"},
        ]
        by_title = _products_by_title(products)
        assert "widget a" in by_title
        assert "widget b" in by_title

    def test_skips_empty_titles(self):
        products = [{"title": "", "price": "10"}, {"price": "20"}]
        by_title = _products_by_title(products)
        assert len(by_title) == 0


class TestDetectChanges:
    def test_price_change(self):
        prev = {"widget": {"title": "Widget", "price": "10.00", "currency": "USD"}}
        curr = {"widget": {"title": "Widget", "price": "15.00", "currency": "USD"}}
        result = _detect_changes(prev, curr)
        assert len(result) == 1
        assert isinstance(result[0], PriceChange)
        assert result[0].old_price == Decimal("10.00")
        assert result[0].new_price == Decimal("15.00")

    def test_new_product(self):
        prev = {}
        curr = {"widget": {"title": "Widget", "price": "10.00", "currency": "USD"}}
        result = _detect_changes(prev, curr)
        assert len(result) == 1
        assert isinstance(result[0], NewProduct)
        assert result[0].price == Decimal("10.00")

    def test_removed_product(self):
        prev = {"widget": {"title": "Widget", "price": "10.00", "currency": "USD"}}
        curr = {}
        result = _detect_changes(prev, curr)
        assert len(result) == 1
        assert isinstance(result[0], RemovedProduct)
        assert result[0].last_price == Decimal("10.00")

    def test_no_changes(self):
        data = {"widget": {"title": "Widget", "price": "10.00"}}
        result = _detect_changes(data, data)
        assert len(result) == 0

    def test_mixed_changes(self):
        prev = {
            "widget a": {"title": "Widget A", "price": "10"},
            "widget b": {"title": "Widget B", "price": "20"},
        }
        curr = {
            "widget a": {"title": "Widget A", "price": "15"},
            "widget c": {"title": "Widget C", "price": "30"},
        }
        result = _detect_changes(prev, curr)
        types = {type(c) for c in result}
        assert PriceChange in types
        assert NewProduct in types
        assert RemovedProduct in types


class TestChangesFromDb:
    def _insert_snapshot(self, conn, domain, products, created_at):
        conn.execute(
            "INSERT INTO snapshots (domain, products_json, created_at) VALUES (?, ?, ?)",
            (domain, json.dumps(products), created_at),
        )
        conn.commit()

    def test_changes_with_two_snapshots(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        conn = _get_connection(db_path)

        old_products = [{"title": "Widget", "price": "10.00", "currency": "USD"}]
        new_products = [{"title": "Widget", "price": "15.00", "currency": "USD"}]

        self._insert_snapshot(conn, "example.com", old_products, "2026-03-14T00:00:00")
        self._insert_snapshot(conn, "example.com", new_products, "2026-03-15T00:00:00")
        conn.close()

        result = changes("example.com", db_path=db_path)
        assert len(result) == 1
        assert isinstance(result[0], PriceChange)

    def test_changes_with_one_snapshot(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        conn = _get_connection(db_path)
        self._insert_snapshot(conn, "example.com", [{"title": "A", "price": "10"}], "2026-03-15T00:00:00")
        conn.close()

        result = changes("example.com", db_path=db_path)
        assert result == []

    def test_changes_db_not_found(self, tmp_path):
        db_path = str(tmp_path / "nonexistent.db")
        with pytest.raises(FileNotFoundError):
            changes("example.com", db_path=db_path)


class TestPriceHistory:
    def _insert_snapshot(self, conn, domain, products, created_at):
        conn.execute(
            "INSERT INTO snapshots (domain, products_json, created_at) VALUES (?, ?, ?)",
            (domain, json.dumps(products), created_at),
        )
        conn.commit()

    def test_price_history_multiple_snapshots(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        conn = _get_connection(db_path)

        for i, (price, ts) in enumerate([
            ("10.00", "2026-03-13T00:00:00"),
            ("12.00", "2026-03-14T00:00:00"),
            ("15.00", "2026-03-15T00:00:00"),
        ]):
            self._insert_snapshot(conn, "example.com", [{"title": "Widget", "price": price}], ts)
        conn.close()

        history = price_history("example.com", "Widget", db_path=db_path)
        assert len(history) == 3
        assert history[0][1] == 10.0
        assert history[2][1] == 15.0
        assert isinstance(history[0][0], datetime)

    def test_price_history_product_not_found(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        conn = _get_connection(db_path)
        self._insert_snapshot(conn, "example.com", [{"title": "Other", "price": "10"}], "2026-03-15T00:00:00")
        conn.close()

        history = price_history("example.com", "Widget", db_path=db_path)
        assert history == []

    def test_price_history_case_insensitive(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        conn = _get_connection(db_path)
        self._insert_snapshot(conn, "example.com", [{"title": "Widget", "price": "10"}], "2026-03-15T00:00:00")
        conn.close()

        history = price_history("example.com", "widget", db_path=db_path)
        assert len(history) == 1
