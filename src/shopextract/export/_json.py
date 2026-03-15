"""JSON export for product data."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal


def _write_json(products: list[dict], path: str, indent: int = 2) -> None:
    """Write products to a JSON file.

    Args:
        products: List of product dicts.
        path: Output file path.
        indent: JSON indentation level.
    """
    with open(path, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=indent, default=_json_serializer, ensure_ascii=False)


def _json_serializer(obj: object) -> str:
    """Handle Decimal, datetime, and other non-serializable types."""
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
