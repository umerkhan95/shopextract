"""CSV export for product data."""

from __future__ import annotations

import csv


def _write_csv(products: list[dict], path: str) -> None:
    """Write products to a CSV file.

    Collects all unique keys across products as column headers.

    Args:
        products: List of product dicts.
        path: Output file path.
    """
    if not products:
        with open(path, "w", newline="", encoding="utf-8") as f:
            f.write("")
        return

    fieldnames = _collect_fieldnames(products)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for product in products:
            row = _flatten_product(product, fieldnames)
            writer.writerow(row)


def _collect_fieldnames(products: list[dict]) -> list[str]:
    """Collect all unique field names preserving insertion order."""
    seen: dict[str, None] = {}
    for product in products:
        for key in product:
            if key not in seen:
                seen[key] = None
    return list(seen)


def _flatten_product(product: dict, fieldnames: list[str]) -> dict:
    """Flatten a product dict for CSV output.

    Converts lists to semicolon-separated strings.
    """
    row: dict[str, str] = {}
    for key in fieldnames:
        value = product.get(key)
        if isinstance(value, list):
            row[key] = "; ".join(str(v) for v in value)
        elif value is None:
            row[key] = ""
        else:
            row[key] = str(value)
    return row
