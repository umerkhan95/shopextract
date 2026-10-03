"""SQLite snapshot storage (#11)."""

from __future__ import annotations

import json
import logging
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

from .._extract import extract
from .._scope import catalog_scope
from ..identity import identify_records, migrate_snapshot_identities, supplier_scope

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


def _get_connection(db_path: str) -> sqlite3.Connection:
    """Open SQLite connection and ensure schema exists."""
    path = _expand_path(db_path)
    conn = sqlite3.connect(str(path))
    conn.execute(_CREATE_TABLE)
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        _ensure_snapshot_metadata(conn)
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
) -> int:
    """Take a snapshot of a store's products and save to SQLite.

    Stores nullable completeness, catalog scope, budget and incompleteness reasons.
    Returns the number of observed products stored, not a full catalog guarantee.
    """
    result = await extract(url, max_urls=max_urls)
    domain = supplier_scope(_domain_from_url(url))
    products_data = [asdict(p) for p in result.products]
    scope = result.observation_scope or catalog_scope(url, result.platform)
    reasons = list(result.incompleteness_reasons)
    if not reasons and result.catalog_complete is not True:
        reasons = ["source_incomplete" if result.catalog_complete is False else "catalog_coverage_unverified"]
    complete = result.catalog_complete if not reasons else (False if result.catalog_complete is not None else None)

    conn = _get_connection(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        migrate_snapshot_identities(conn, domain)
        identify_records(conn, products_data, domain, legacy_titles=True)
        conn.execute(
            "INSERT INTO snapshots (domain, products_json, created_at, observation_scope, catalog_complete, incompleteness_reasons_json, max_urls) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (domain, json.dumps(products_data, cls=_DecimalEncoder), datetime.now(timezone.utc).isoformat(),
             scope, complete, json.dumps(reasons), max_urls),
        )
        conn.commit()
    finally:
        conn.close()

    logger.info("Snapshot saved: %s, %d products", domain, len(products_data))
    return len(products_data)
