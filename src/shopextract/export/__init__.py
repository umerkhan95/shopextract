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
                      _json_bytes,prepare_evidence_snapshot,subset_evidence_snapshot,_create_sidecar_from_snapshot)

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
    *, evidence_path: str | None = None, context=None,
) -> dict:
    """Export products as a marketplace feed.

    Args:
        products: List of product dicts.
        path: Output file path.
        format: Feed format - "google_shopping" (RSS 2.0 XML) or "idealo" (TSV).
    """
    from ..validate._destination import assess_google
    prepared,snapshot=_prepare(products,path,evidence_path)
    selected=[];indices=[];issues=[]
    for index,product in enumerate(products):
        assessment=assess_google(product,context=context)
        applicable=assessment['issues'] if format=='google_shopping' else [i for i in assessment['issues'] if i['rule_id'] in ('missing_id','invalid_price','invalid_currency','unsupported_gtin','unsupported_mpn') and not (i['rule_id']=='missing_id' and assessment['projection'].get('sku'))]
        issues.extend(dict(i,product_index=index) for i in applicable)
        blocked=assessment['subset_status']=='blocked' if format=='google_shopping' else any(i['rule_id'] in ('invalid_price','invalid_currency') or i['rule_id']=='missing_id' and not assessment['projection'].get('sku') for i in assessment['issues'])
        if not blocked:selected.append(assessment['projection']);indices.append(index)
    _write_feed(selected,path,format)
    if snapshot is not None:snapshot=subset_evidence_snapshot(snapshot,indices)
    _companion(snapshot,path,evidence_path,format)
    return dict(retained=len(selected),skipped=len(products)-len(selected),issues=issues)


def _prepare(products, path, evidence_path):
    if evidence_path is not None:
        if Path(path).resolve() == Path(evidence_path).resolve():
            raise ValueError("Evidence path must differ from export path")
        # Validate before writing the projection so failure cannot silently
        # discard trust metadata from a requested companion.
        snapshot=prepare_evidence_snapshot(products)
    else:snapshot=None
    return [asdict(p) if isinstance(p, Product) else p for p in products], snapshot


def _companion(products, path, evidence_path, format):
    if evidence_path is not None:
        if Path(path).resolve() == Path(evidence_path).resolve():
            raise ValueError("Evidence path must differ from export path")
        payload = _create_sidecar_from_snapshot(products, Path(path).read_bytes(), format=format)
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
