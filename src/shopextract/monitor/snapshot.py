"""SQLite snapshot storage (#11)."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

from .._extract import extract
from .._scope import catalog_scope
from ..identity import supplier_scope

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = "~/.shopextract/snapshots.db"

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain TEXT NOT NULL,
    products_json TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


def _expand_path(db_path: str) -> Path:
    """Expand ~ and ensure parent directory exists."""
    path = Path(db_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _domain_from_url(url: str) -> str:
    """Extract domain from a URL."""
    parsed = urlparse(url if "://" in url else f"https://{url}")
    return parsed.netloc or parsed.path.split("/")[0]


def _get_connection(db_path: str, *, initialize: bool = True) -> sqlite3.Connection:
    """Open bounded SQLite connection; saves initialize within their transaction."""
    path = _expand_path(db_path)
    conn = sqlite3.connect(str(path), timeout=5)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    if initialize:
        try:
            with conn:
                conn.execute("BEGIN IMMEDIATE")
                conn.execute(_CREATE_TABLE)
                _ensure_snapshot_metadata(conn)
                from .evidence import _ensure_evidence_schema
                _ensure_evidence_schema(conn)
        except Exception:
            conn.close()
            raise
    return conn


def _ensure_snapshot_metadata(conn: sqlite3.Connection) -> None:
    """Add nullable observation metadata; legacy completeness stays unknown.

    Call inside a write transaction to serialize concurrent schema upgrades.
    """
    columns = {row[1] for row in conn.execute("PRAGMA table_info(snapshots)")}
    for name, sql_type in (("observation_scope", "TEXT"), ("catalog_complete", "INTEGER"),
                           ("incompleteness_reasons_json", "TEXT"), ("max_urls", "INTEGER")):
        if name not in columns:
            conn.execute(f"ALTER TABLE snapshots ADD COLUMN {name} {sql_type}")


class _DecimalEncoder(json.JSONEncoder):
    """JSON encoder that handles Decimal and datetime."""

    def default(self, o: object) -> object:
        if isinstance(o, Decimal):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


async def snapshot(
    url: str,
    *,
    db_path: str = _DEFAULT_DB_PATH,
    max_urls: int = 200,
    retain_limit: int | None = None,
) -> int:
    """Take a snapshot of a store's products and save to SQLite.

    Stores nullable completeness, catalog scope, budget and incompleteness reasons.
    Returns the number of observed products stored, not a full catalog guarantee.
    """
    if retain_limit is not None and (type(retain_limit) is not int or retain_limit < 1):
        raise ValueError('retain_limit must be positive')
    result = await extract(url, max_urls=max_urls)
    if retain_limit is not None and result.errors:
        if not result.products:
            raise ValueError('No usable products from failed source')
        result.catalog_complete = False
        result.incompleteness_reasons = list(result.incompleteness_reasons) + ['source_errors']
    if retain_limit is not None and len(result.products) > retain_limit:
        result.products = result.products[:retain_limit]
        result.catalog_complete = False
        result.incompleteness_reasons = list(result.incompleteness_reasons) + ['product_budget_exhausted']
    domain = supplier_scope(_domain_from_url(url))
    scope = result.observation_scope or catalog_scope(url, result.platform)
    reasons = list(result.incompleteness_reasons)
    if not reasons and result.catalog_complete is not True:
        reasons = ["source_incomplete" if result.catalog_complete is False else "catalog_coverage_unverified"]
    complete = result.catalog_complete if not reasons else (False if result.catalog_complete is not None else None)

    from .evidence import save_snapshot
    save_snapshot(result.products, domain, db_path=db_path, metadata={
        "observation_scope": scope, "catalog_complete": complete,
        "incompleteness_reasons": reasons, "max_urls": max_urls,
    })
    logger.info("Snapshot saved: %s, %d products", domain, len(result.products))
    return len(result.products)
