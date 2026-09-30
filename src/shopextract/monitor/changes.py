"""Price change detection between snapshots (#12)."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .._models import Change, NewProduct, PriceChange, RemovedProduct
from ..identity import migrate_snapshot_identities, supplier_scope
from .snapshot import _ensure_snapshot_metadata

logger = logging.getLogger(__name__)

_DEFAULT_DB_PATH = "~/.shopextract/snapshots.db"


def _open_db(db_path: str) -> sqlite3.Connection:
    """Open the snapshot database."""
    path = Path(db_path).expanduser()
    if not path.exists():
        msg = f"Snapshot database not found: {path}"
        raise FileNotFoundError(msg)
    return sqlite3.connect(str(path))


def _load_latest_snapshots(
    conn: sqlite3.Connection,
    domain: str,
    count: int = 2,
) -> list[tuple[list[dict], str | None, bool | None]]:
    """Load the N most recent snapshots for a domain."""
    rows = conn.execute(
        "SELECT products_json, observation_scope, catalog_complete FROM snapshots WHERE domain = ? ORDER BY created_at DESC, id DESC LIMIT ?",
        (domain, count),
    ).fetchall()
    return [(json.loads(payload), scope, True if complete == 1 else False if complete == 0 else None)
            for payload, scope, complete in rows]


def _products_by_title(products: list[dict]) -> dict[str, dict]:
    """Index products by lowercase title."""
    return {p.get("title", "").lower().strip(): p for p in products if p.get("title")}


def _products_by_identity(products: list[dict]) -> dict[str, dict]:
    """Index migrated records without collapsing identical display titles."""
    return {p["canonical_product_id"]: p for p in products}


def changes(
    domain: str,
    *,
    db_path: str = _DEFAULT_DB_PATH,
) -> list[Change]:
    """Compare latest two snapshots and return detected changes.

    Membership events require matching known scopes. Removal requires a complete
    current catalog; addition requires a complete previous catalog. Shared prices
    remain observable in partial/legacy history. Different known scopes are skipped.
    Returns PriceChange, NewProduct, and RemovedProduct objects.
    """
    domain = supplier_scope(domain)
    conn = _open_db(db_path)
    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            _ensure_snapshot_metadata(conn)
            migrate_snapshot_identities(conn, domain)
            snapshots = _load_latest_snapshots(conn, domain, count=2)
    finally:
        conn.close()

    if len(snapshots) < 2:
        logger.info("Need at least 2 snapshots for %s, found %d", domain, len(snapshots))
        return []

    current_products, current_scope, current_complete = snapshots[0]
    previous_products, previous_scope, previous_complete = snapshots[1]
    if current_scope and previous_scope and current_scope != previous_scope:
        logger.info("Snapshot scopes differ for %s; comparison suppressed", domain)
        return []
    comparable_scope = bool(current_scope and current_scope == previous_scope)
    current = _products_by_identity(current_products)
    previous = _products_by_identity(previous_products)
    allow_removals = comparable_scope and current_complete is True
    if previous.keys() - current.keys() and not allow_removals:
        logger.info("Unobserved products not marked removed for %s: complete=%s, comparable_scope=%s",
                    domain, current_complete, comparable_scope)
    return _detect_changes(previous, current,
                           allow_removals=allow_removals,
                           allow_additions=comparable_scope and previous_complete is True)


def _detect_changes(
    previous: dict[str, dict],
    current: dict[str, dict],
    *,
    allow_removals: bool = True,
    allow_additions: bool = True,
) -> list[Change]:
    """Detect price changes, new products, and removed products."""
    result: list[Change] = []

    for title_key, cur_prod in current.items():
        if title_key not in previous:
            if not allow_additions:
                continue
            result.append(NewProduct(
                title=cur_prod.get("title", ""),
                price=_safe_decimal(cur_prod.get("price", 0)),
                currency=cur_prod.get("currency", "USD"),
            ))
        else:
            prev_prod = previous[title_key]
            _check_price_change(result, prev_prod, cur_prod)

    for title_key, prev_prod in previous.items():
        if title_key not in current and allow_removals:
            result.append(RemovedProduct(
                title=prev_prod.get("title", ""),
                last_price=_safe_decimal(prev_prod.get("price", 0)),
                currency=prev_prod.get("currency", "USD"),
            ))

    return result


def _safe_decimal(value: object) -> Decimal:
    """Convert a value to Decimal, returning 0 for non-numeric values."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        logger.debug("Non-numeric price value: %r, defaulting to 0", value)
        return Decimal("0")


def _check_price_change(
    result: list[Change],
    prev: dict,
    cur: dict,
) -> None:
    """Append a PriceChange if prices differ."""
    old_price = _safe_decimal(prev.get("price", 0))
    new_price = _safe_decimal(cur.get("price", 0))
    if old_price != new_price:
        result.append(PriceChange(
            title=cur.get("title", ""),
            old_price=old_price,
            new_price=new_price,
            currency=cur.get("currency", "USD"),
        ))


def price_history(
    domain: str,
    product_title: str = "",
    *,
    db_path: str = _DEFAULT_DB_PATH,
    canonical_product_id: str | None = None,
) -> list[tuple[datetime, float]]:
    """Get identity-based history, resolving any historical display title.

    Ambiguous titles raise ValueError; pass canonical_product_id instead.
    Returns list of (timestamp, price) tuples in chronological order.
    """
    domain = supplier_scope(domain)
    conn = _open_db(db_path)
    try:
        with conn:
            migrate_snapshot_identities(conn, domain)
        rows = conn.execute(
            "SELECT products_json, created_at FROM snapshots WHERE domain = ? ORDER BY created_at ASC, id ASC",
            (domain,),
        ).fetchall()
    finally:
        conn.close()

    decoded = [(json.loads(payload), ts) for payload, ts in rows]
    if canonical_product_id is None:
        title = product_title.casefold().strip()
        ids = {p["canonical_product_id"] for products, _ in decoded for p in products
               if str(p.get("title", "")).casefold().strip() == title}
        if len(ids) > 1:
            raise ValueError("Ambiguous product title; use canonical_product_id")
        canonical_product_id = next(iter(ids), None)
    history = []
    for products, created_at in decoded:
        for p in products:
            if p["canonical_product_id"] == canonical_product_id:
                history.append((datetime.fromisoformat(created_at), float(_safe_decimal(p.get("price", 0)))))
    return history
