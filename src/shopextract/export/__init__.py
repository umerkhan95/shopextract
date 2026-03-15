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

from ._csv import _write_csv
from ._feed import _write_feed
from ._json import _write_json


def to_csv(products: list[dict], path: str) -> None:
    """Export products to CSV file.

    Args:
        products: List of product dicts.
        path: Output file path.
    """
    _write_csv(products, path)


def to_json(products: list[dict], path: str, indent: int = 2) -> None:
    """Export products to JSON file.

    Args:
        products: List of product dicts.
        path: Output file path.
        indent: JSON indentation level.
    """
    _write_json(products, path, indent)


def to_feed(
    products: list[dict], path: str, format: str = "google_shopping",
) -> None:
    """Export products as a marketplace feed.

    Args:
        products: List of product dicts.
        path: Output file path.
        format: Feed format - "google_shopping" (RSS 2.0 XML) or "idealo" (TSV).
    """
    _write_feed(products, path, format)


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
    "to_csv",
    "to_dataframe",
    "to_feed",
    "to_json",
    "to_parquet",
]
