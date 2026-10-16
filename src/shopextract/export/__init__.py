"""Multi-format product data export.

Public API:
    to_csv(products, path) -> None
    to_json(products, path, indent) -> None
    to_feed(products, path, format) -> None
    to_dataframe(products) -> pandas.DataFrame
    to_parquet(products, path) -> None
"""

from __future__ import annotations

from typing import Any
from dataclasses import asdict
from pathlib import Path

from .._models import Product
from ._bundle import (create_evidence_bundle, load_evidence_bundle, write_evidence_bundle,
                      read_evidence_bundle, create_evidence_sidecar, load_evidence_sidecar,
                      _json_bytes)

from ._csv import _write_csv
from ._feed import _write_feed
from ._json import _write_json


def to_csv(products: list[dict] | list[Product], path: str, *, evidence_path: str | None = None) -> None:
    """Export products to CSV file.

    Args:
        products: List of product dicts.
        path: Output file path.
    """
    prepared, bundle_products = _prepare(products, path, evidence_path)
    _write_csv(prepared, path)
    _companion(bundle_products, path, evidence_path, "csv")


def to_json(products: list[dict], path: str, indent: int = 2) -> None:
    """Export products to JSON file.

    Args:
        products: List of product dicts.
        path: Output file path.
        indent: JSON indentation level.
    """
    _write_json(products, path, indent)


def to_feed(
    products: list[dict] | list[Product], path: str, format: str = "google_shopping",
    *, evidence_path: str | None = None,
) -> None:
    """Export products as a marketplace feed.

    Args:
        products: List of product dicts.
        path: Output file path.
        format: Feed format - "google_shopping" (RSS 2.0 XML) or "idealo" (TSV).
    """
    prepared, bundle_products = _prepare(products, path, evidence_path)
    _write_feed(prepared, path, format)
    _companion(bundle_products, path, evidence_path, format)


def _prepare(products, path, evidence_path):
    if evidence_path is not None:
        if Path(path).resolve() == Path(evidence_path).resolve():
            raise ValueError("Evidence path must differ from export path")
        # Validate before writing the projection so failure cannot silently
        # discard trust metadata from a requested companion.
        create_evidence_bundle(products)
    return [asdict(p) if isinstance(p, Product) else p for p in products], products


def _companion(products, path, evidence_path, format):
    if evidence_path is not None:
        if Path(path).resolve() == Path(evidence_path).resolve():
            raise ValueError("Evidence path must differ from export path")
        payload = create_evidence_sidecar(products, Path(path).read_bytes(), format=format)
        Path(evidence_path).write_bytes(_json_bytes(payload))


def to_dataframe(products: list[dict]) -> Any:
    """Convert products to a pandas DataFrame.

    Args:
        products: List of product dicts.

    Returns:
        pandas.DataFrame

    Raises:
        ImportError: If pandas is not installed.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for to_dataframe(). "
            "Install it with: pip install shopextract[data]"
        ) from None
    return pd.DataFrame(products)


def to_parquet(products: list[dict], path: str) -> None:
    """Export products to Parquet file via pandas.

    Args:
        products: List of product dicts.
        path: Output file path.

    Raises:
        ImportError: If pandas or pyarrow is not installed.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for to_parquet(). "
            "Install it with: pip install shopextract[data]"
        ) from None
    df = pd.DataFrame(products)
    df.to_parquet(path, index=False)


__all__ = [
    "create_evidence_bundle",
    "load_evidence_bundle",
    "write_evidence_bundle",
    "read_evidence_bundle",
    "create_evidence_sidecar",
    "load_evidence_sidecar",
    "to_csv",
    "to_dataframe",
    "to_feed",
    "to_json",
    "to_parquet",
]
