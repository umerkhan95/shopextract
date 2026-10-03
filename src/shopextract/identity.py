"""Title-independent, supplier-scoped identities and conservative snapshot migration."""
from __future__ import annotations

import json
import sqlite3
from collections import Counter
from dataclasses import asdict
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from uuid import NAMESPACE_URL, uuid4, uuid5

from ._models import Product


def supplier_scope(value: str) -> str:
    """Normalize URL suppliers by host; explicit supplier keys remain case sensitive."""
    value = value.strip()
    if "://" in value:
        return urlsplit(value).netloc.lower()
    return value.lower() if "." in value else value


def _url_key(value: str) -> str:
    parts = urlsplit(value)
    if not parts.netloc or parts.path in ("", "/"):
        return ""
    query = [(k, v) for k, v in parse_qsl(parts.query) if not k.startswith("utm_") and k not in {"gclid", "fbclid"}]
    return urlunsplit(("", parts.netloc.lower(), parts.path.rstrip("/"), urlencode(sorted(query)), ""))


def _aliases(record: dict, *, variant: bool = False) -> list[tuple[str, str]]:
    aliases = []
    source = record.get("variant_id" if variant else "external_id")
    if source:
        platform = record.get("platform", "generic")
        platform = getattr(platform, "value", platform)
        aliases.append((f"source:{platform}", str(source).strip()))
    if record.get("sku"):
        aliases.append(("sku", str(record["sku"]).strip()))
    if not variant and record.get("product_url"):
        url = _url_key(record["product_url"])
        if url:
            aliases.append(("url", url))
    return [(k, v) for k, v in aliases if v]


def _id(scope: str, alias: tuple[str, str] | None, prefix: str) -> str:
    # Without a stable anchor, allocate identity rather than hashing a mutable title.
    return prefix + str(uuid5(NAMESPACE_URL, json.dumps([scope, alias])) if alias else uuid4())


def assign_identity(product: Product, supplier_id: str = "") -> Product:
    """Assign IDs in place. Pass the same supplier key on every extraction.

    Existing IDs survive edits. Stateless IDs use source ID, scoped SKU, then URL.
    Persistent monitoring additionally remembers aliases across identifier changes.
    """
    scope = supplier_scope(supplier_id or product.supplier_id or product.product_url)
    if not scope:
        raise ValueError("supplier_id or an absolute product_url is required")
    if product.supplier_id and supplier_scope(product.supplier_id) != scope:
        raise ValueError("Cannot move an identity to a different supplier")
    product.supplier_id = scope
    aliases = _aliases(asdict(product))
    if not product.canonical_product_id:
        product.canonical_product_id = _id(scope, aliases[0] if aliases else None, "p_")
    for variant in product.variants:
        aliases = _aliases(asdict(variant), variant=True)
        if not variant.canonical_variant_id:
            variant.canonical_variant_id = _id(product.canonical_product_id, aliases[0] if aliases else None, "v_")
    return product


_SCHEMA = """CREATE TABLE IF NOT EXISTS identity_aliases (
    scope TEXT NOT NULL, kind TEXT NOT NULL, value TEXT NOT NULL,
    canonical_id TEXT NOT NULL, PRIMARY KEY (scope, kind, value)
)"""


def _resolve(conn: sqlite3.Connection, scope: str, record: dict, *, variant: bool = False,
             legacy_title: bool = False) -> str:
    aliases = _aliases(record, variant=variant)
    field = "canonical_variant_id" if variant else "canonical_product_id"
    # A unique title is a one-time bridge only for records lacking stable anchors.
    title = str(record.get("title", "")).strip().casefold()
    bridge = ("legacy_title", title)
    lookup = aliases + ([bridge] if legacy_title and title else [])
    ids = {row[0] for kind, value in lookup for row in conn.execute(
        "SELECT canonical_id FROM identity_aliases WHERE scope=? AND kind=? AND value=?",
        (scope, kind, value))}
    if len(ids) > 1:
        raise ValueError("Conflicting identity aliases; manual reconciliation required")
    canonical = next(iter(ids), None) or record.get(field) or _id(
        scope, aliases[0] if aliases else None, "v_" if variant else "p_")
    record[field] = canonical
    if aliases and legacy_title and title:
        # Consume a legacy bridge once promoted so a later reused title cannot
        # attach a new source record to the previous identity.
        conn.execute("DELETE FROM identity_aliases WHERE scope=? AND kind=? AND value=?",
                     (scope, *bridge))
    for kind, value in aliases + ([bridge] if legacy_title and title and not aliases else []):
        conn.execute("INSERT OR IGNORE INTO identity_aliases VALUES (?, ?, ?, ?)",
                     (scope, kind, value, canonical))
    return canonical


def identify_records(conn: sqlite3.Connection, products: list[dict], supplier_id: str,
                     *, legacy_titles: bool = False) -> list[dict]:
    """Assign persistent IDs inside the caller's transaction; reject duplicate anchors."""
    conn.execute(_SCHEMA)
    scope = supplier_scope(supplier_id)
    counts = Counter(str(p.get("title", "")).strip().casefold() for p in products)
    seen = set()
    for product in products:
        product["supplier_id"] = scope
        canonical = _resolve(conn, scope, product, legacy_title=legacy_titles and counts[
            str(product.get("title", "")).strip().casefold()] == 1)
        if canonical in seen:
            raise ValueError("Duplicate product identity in snapshot; manual review required")
        seen.add(canonical)
        variants_seen = set()
        for variant in product.get("variants", []):
            vid = _resolve(conn, canonical, variant, variant=True)
            if vid in variants_seen:
                raise ValueError("Duplicate variant identity in snapshot")
            variants_seen.add(vid)
    return products


def migrate_snapshot_identities(conn: sqlite3.Connection, domain: str | None = None) -> int:
    """Backfill snapshot JSON chronologically, preserving prices/timestamps.

    The caller owns commit/rollback. Re-running is safe. Conflicting aliases stop
    migration. Identifier-free unique titles can bridge unchanged legacy titles;
    a title-only rename cannot be recovered automatically.
    """
    conn.execute(_SCHEMA)
    query = "SELECT id, domain, products_json FROM snapshots"
    args = ()
    if domain is not None:
        query += " WHERE domain=?"
        args = (domain,)
    rows = conn.execute(query + " ORDER BY created_at ASC, id ASC", args).fetchall()
    updated = 0
    for row_id, scope, payload in rows:
        products = json.loads(payload)
        before = json.dumps(products, sort_keys=True)
        identify_records(conn, products, scope, legacy_titles=True)
        if json.dumps(products, sort_keys=True) != before:
            conn.execute("UPDATE snapshots SET products_json=? WHERE id=?", (json.dumps(products), row_id))
            updated += 1
    return updated
