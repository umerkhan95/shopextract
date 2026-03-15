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
    return conn


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

    Returns the number of products stored.
    """
    result = await extract(url, max_urls=max_urls)
    domain = _domain_from_url(url)
    products_data = [asdict(p) for p in result.products]

    conn = _get_connection(db_path)
    try:
        conn.execute(
            "INSERT INTO snapshots (domain, products_json, created_at) VALUES (?, ?, ?)",
            (domain, json.dumps(products_data, cls=_DecimalEncoder), datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
    finally:
        conn.close()

    logger.info("Snapshot saved: %s, %d products", domain, len(products_data))
    return len(products_data)
