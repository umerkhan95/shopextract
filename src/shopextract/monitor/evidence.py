"""Atomic SQLite evidence storage with scoped identities and explicit retention.

Payload hashes check stored bytes, not source authenticity. Retention removes
supported access, not residual copies in compatibility JSON or raw_data.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable, Literal, Mapping

from .._evidence import Evidence, TrustContract, decode_value, encode_value, _utc
from .._models import Product, Variant, Platform
from .._portable import product_from_record, product_to_record
from ..identity import identify_records, migrate_snapshot_identities, supplier_scope

DEFAULT_DB_PATH = "~/.shopextract/snapshots.db"
MAX_SNAPSHOT_BYTES = 16 * 1024 * 1024
MAX_PRUNE_BATCH = 1000
_REASON = "legacy_snapshot_without_captured_graph"

@dataclass(frozen=True)
class EvidenceLookup:
    status: Literal["available", "expired", "missing", "unsupported"]
    evidence_id: str
    reason: str
    evidence: Evidence | None = None
    snapshot_id: int | None = None
    record_key: str | None = None
    expired_at: datetime | None = None

@dataclass(frozen=True)
class PruneReport:
    examined: int
    protected: int
    expired: int
    payloads_deleted: int
    dry_run: bool
    has_more: bool


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _ensure_evidence_schema(conn, *, backfill=True):
    """Additive, module-versioned migration; caller owns the transaction."""
    conn.execute("CREATE TABLE IF NOT EXISTS evidence_schema (singleton INTEGER PRIMARY KEY CHECK(singleton=1), version INTEGER NOT NULL)")
    version = conn.execute("SELECT version FROM evidence_schema WHERE singleton=1").fetchone()
    if version and version[0] != 1:
        raise ValueError("Unsupported evidence storage schema version")
    statements = [
        "CREATE TABLE IF NOT EXISTS evidence_products (snapshot_id INTEGER NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE, position INTEGER NOT NULL, record_json TEXT NOT NULL, PRIMARY KEY(snapshot_id,position))",
        "CREATE TABLE IF NOT EXISTS evidence_owners (snapshot_id INTEGER NOT NULL REFERENCES snapshots(id) ON DELETE CASCADE, record_key TEXT NOT NULL, graph_json TEXT, reason TEXT NOT NULL, PRIMARY KEY(snapshot_id,record_key))",
        "CREATE TABLE IF NOT EXISTS evidence_payloads (payload_hash TEXT PRIMARY KEY, encoded_payload TEXT NOT NULL, byte_size INTEGER NOT NULL)",
        "CREATE TABLE IF NOT EXISTS evidence_records (snapshot_id INTEGER NOT NULL, record_key TEXT NOT NULL, evidence_id TEXT NOT NULL, metadata_json TEXT NOT NULL, payload_hash TEXT, observed_at TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('available','expired')), reason TEXT NOT NULL, expired_at TEXT, PRIMARY KEY(snapshot_id,record_key,evidence_id), FOREIGN KEY(snapshot_id,record_key) REFERENCES evidence_owners(snapshot_id,record_key) ON DELETE CASCADE, FOREIGN KEY(payload_hash) REFERENCES evidence_payloads(payload_hash))",
        "CREATE TABLE IF NOT EXISTS evidence_references (snapshot_id INTEGER NOT NULL, record_key TEXT NOT NULL, observation_id TEXT NOT NULL, evidence_id TEXT NOT NULL, PRIMARY KEY(snapshot_id,record_key,observation_id,evidence_id), FOREIGN KEY(snapshot_id,record_key,evidence_id) REFERENCES evidence_records(snapshot_id,record_key,evidence_id) ON DELETE CASCADE)",
        "CREATE INDEX IF NOT EXISTS evidence_lookup ON evidence_records(evidence_id)",
        "CREATE INDEX IF NOT EXISTS evidence_payload_refs ON evidence_records(payload_hash,status)",
        "CREATE INDEX IF NOT EXISTS evidence_ref_lookup ON evidence_references(snapshot_id,record_key,evidence_id)",
        "CREATE INDEX IF NOT EXISTS evidence_cutoff ON evidence_records(status,observed_at)",
    ]
    for sql in statements:
        conn.execute(sql)
    # Existing scalar rows never imply captured support. Migration leaves their
    # JSON, IDs and timestamps alone; identity migration remains caller-owned.
    for sid, payload in (conn.execute("SELECT id,products_json FROM snapshots WHERE NOT EXISTS (SELECT 1 FROM evidence_owners WHERE snapshot_id=snapshots.id)").fetchall() if backfill else []):
        for i, product in enumerate(json.loads(payload)):
            for key in [f"product/{i}"] + [f"product/{i}/variant/{j}" for j in range(len(product.get("variants", [])))]:
                conn.execute("INSERT OR IGNORE INTO evidence_owners VALUES (?,?,NULL,?)", (sid, key, _REASON))
    conn.execute("INSERT OR IGNORE INTO evidence_schema VALUES (1,1)")


def _prepare(products, metadata):
    from .snapshot import _DecimalEncoder
    products = list(products)
    metadata = dict(metadata or {})
    allowed = {"observation_scope", "catalog_complete", "incompleteness_reasons", "max_urls"}
    if set(metadata) - allowed:
        raise ValueError("Unknown snapshot metadata")
    if metadata.get("observation_scope") is not None and not isinstance(metadata["observation_scope"], str):
        raise ValueError("observation_scope must be text")
    if metadata.get("catalog_complete") is not None and type(metadata["catalog_complete"]) is not bool:
        raise ValueError("catalog_complete must be boolean or None")
    reasons = metadata.get("incompleteness_reasons", [])
    if not isinstance(reasons, list) or any(not isinstance(r, str) for r in reasons):
        raise ValueError("incompleteness_reasons must be a list of text")
    if metadata.get("max_urls") is not None and (type(metadata["max_urls"]) is not int or metadata["max_urls"] < 1):
        raise ValueError("max_urls must be a positive integer")
    records = [product_to_record(p) for p in products]
    legacy = [asdict(p) for p in products]
    size = len(_json(records).encode()) + len(json.dumps(legacy, cls=_DecimalEncoder).encode())
    if size > MAX_SNAPSHOT_BYTES:
        raise ValueError("Serialized snapshot exceeds 16 MiB")
    for record in records:
        total = 0
        seen = set()
        for graph in [record.get("evidence_contract")] + list(record.get("variant_contracts", [])):
            if graph is None:
                continue
            for evidence in graph["evidence"]:
                identity = _json(evidence)
                if identity in seen:
                    continue
                seen.add(identity)
                raw = decode_value(evidence)
                # Capture's actual text budget excludes typed transport overhead.
                actual = len((raw.get("excerpt") or "").encode()) + (len(_json(encode_value(raw["retained_data"])).encode()) if raw.get("retained_data") is not None else 0)
                if actual > 4096:
                    raise ValueError("Evidence fragment exceeds 4096 bytes")
                total += actual
        if total > 65536:
            raise ValueError("Product capture exceeds 65536 bytes")
    return records, legacy, metadata


def _persist_snapshot(conn, products, domain, metadata=None, *, prepared=None):
    from .snapshot import _DecimalEncoder
    records, legacy, metadata = prepared or _prepare(products, metadata)
    domain = supplier_scope(domain)
    migrate_snapshot_identities(conn, domain)
    identify_records(conn, legacy, domain, legacy_titles=True)
    # Derived identities are represented in both views without modifying inputs.
    for record, scalar in zip(records, legacy):
        record["product"]["canonical_product_id"] = scalar["canonical_product_id"]
        record["product"]["supplier_id"] = scalar["supplier_id"]
        for variant, old in zip(record["product"]["variants"], scalar.get("variants", [])):
            variant["canonical_variant_id"] = old["canonical_variant_id"]
    sid = conn.execute("INSERT INTO snapshots (domain,products_json,created_at,observation_scope,catalog_complete,incompleteness_reasons_json,max_urls) VALUES (?,?,?,?,?,?,?)", (domain, json.dumps(legacy, cls=_DecimalEncoder), datetime.now(timezone.utc).isoformat(), metadata.get("observation_scope"), metadata.get("catalog_complete"), _json(metadata.get("incompleteness_reasons", [])), metadata.get("max_urls"))).lastrowid
    for i, record in enumerate(records):
        graphs = [(f"product/{i}", record.pop("evidence_contract", None))]
        graphs += [(f"product/{i}/variant/{j}", g) for j, g in enumerate(record.pop("variant_contracts", []))]
        conn.execute("INSERT INTO evidence_products VALUES (?,?,?)", (sid, i, _json(record)))
        availability = [decode_value(record.get("evidence_availability", []))]
        availability += [decode_value(item) if item is not None else [] for item in record.get("variant_evidence_availability", [None] * (len(graphs) - 1))]
        for (key, graph), tombstones in zip(graphs, availability):
            captures = [] if graph is None else graph.pop("evidence")
            conn.execute("INSERT INTO evidence_owners VALUES (?,?,?,?)", (sid, key, None if graph is None else _json(graph), _REASON if graph is None else ""))
            for encoded in captures:
                data = decode_value(encoded)
                fragment = {k: data.pop(k) for k in ("excerpt", "retained_data")}
                payload = _json(encode_value(fragment))
                digest = hashlib.sha256(payload.encode()).hexdigest()
                conn.execute("INSERT OR IGNORE INTO evidence_payloads VALUES (?,?,?)", (digest, payload, len(payload.encode())))
                conn.execute("INSERT INTO evidence_records VALUES (?,?,?,?,?,?, 'available','',NULL)", (sid, key, data["evidence_id"], _json(encode_value(data)), digest, data["observed_at"].isoformat(timespec="microseconds")))
            for tombstone in tombstones:
                data = tombstone["metadata"]
                if conn.execute("SELECT 1 FROM evidence_records WHERE snapshot_id=? AND record_key=? AND evidence_id=?", (sid,key,tombstone["evidence_id"])).fetchone():
                    raise ValueError("Expired capture conflicts with available capture")
                conn.execute("INSERT INTO evidence_records VALUES (?,?,?,?,NULL,?,'expired',?,?)", (sid,key,tombstone["evidence_id"],_json(encode_value(data)),data["observed_at"].isoformat(timespec="microseconds"),tombstone["reason"],tombstone["expired_at"].isoformat(timespec="microseconds")))
            if graph:
                for observation in graph["observations"]:
                    for eid in observation["evidence_ids"]:
                        conn.execute("INSERT INTO evidence_references VALUES (?,?,?,?)", (sid, key, observation["observation_id"], eid))
    return sid


def save_snapshot(products: Iterable[Product], domain: str, *, db_path=DEFAULT_DB_PATH, metadata: Mapping[str, object] | None = None) -> int:
    from .snapshot import _get_connection, _ensure_snapshot_metadata, _CREATE_TABLE
    prepared = _prepare(products, metadata)
    conn = _get_connection(db_path, initialize=False)
    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(_CREATE_TABLE)
            _ensure_snapshot_metadata(conn)
            _ensure_evidence_schema(conn)
            return _persist_snapshot(conn, [], domain, prepared=prepared)
    finally:
        conn.close()


def _read_capture(conn, row):
    sid, key, eid, metadata, digest, observed, status, reason, expired = row
    data = decode_value(json.loads(metadata))
    if data.get("evidence_id") != eid or data.get("observed_at") != datetime.fromisoformat(observed):
        raise ValueError("Corrupt evidence metadata")
    _utc(data["observed_at"])
    if status == "expired":
        expiration = datetime.fromisoformat(expired)
        _utc(expiration)
        if not reason or digest is not None:
            raise ValueError("Corrupt evidence tombstone")
        return None, {"evidence_id": eid, "status": "expired", "reason": reason, "expired_at": expiration, "metadata": data}
    payload = conn.execute("SELECT encoded_payload,byte_size FROM evidence_payloads WHERE payload_hash=?", (digest,)).fetchone()
    if not payload or hashlib.sha256(payload[0].encode()).hexdigest() != digest or len(payload[0].encode()) != payload[1]:
        raise ValueError("Corrupt evidence payload")
    data.update(decode_value(json.loads(payload[0])))
    return Evidence(**data), None


def _owner_graph(conn, sid, key):
    owner = conn.execute("SELECT graph_json FROM evidence_owners WHERE snapshot_id=? AND record_key=?", (sid, key)).fetchone()
    if not owner:
        raise ValueError("Missing evidence owner")
    if owner[0] is None:
        return None, []
    graph = json.loads(owner[0])
    evidence, tombstones = [], []
    for row in conn.execute("SELECT * FROM evidence_records WHERE snapshot_id=? AND record_key=? ORDER BY evidence_id", (sid, key)):
        capture, tombstone = _read_capture(conn, row)
        if capture:
            evidence.append(encode_value(asdict(capture)))
        else:
            tombstones.append(tombstone)
    expired = {t["evidence_id"] for t in tombstones}
    invalid = set()
    for observation in graph["observations"]:
        if expired.intersection(observation["evidence_ids"]):
            invalid.add(observation["observation_id"])
            observation.update(state="expired", reason="required_evidence_expired", evidence_ids=[], validated_confidence=None)
    for resolution in graph["resolutions"]:
        if resolution.get("selected_observation_id") in invalid:
            resolution.update(state="expired", reason="required_evidence_expired", selected_observation_id=None)
    graph["evidence"] = evidence
    TrustContract.from_dict(graph)
    return graph, tombstones


def _legacy_product(data):
    data = dict(data)
    for key in ("price", "compare_at_price"):
        if data.get(key) is not None:
            data[key] = Decimal(str(data[key]))
    if isinstance(data.get("scraped_at"), str):
        data["scraped_at"] = datetime.fromisoformat(data["scraped_at"])
    if "platform" in data:
        data["platform"] = Platform(data["platform"])
    data["variants"] = [Variant(**dict(v, price=Decimal(str(v.get("price", "0"))))) for v in data.get("variants", [])]
    return Product(**data)


def _load_snapshot(conn, snapshot_id):
    """Load one selected snapshot using the caller-owned transaction."""
    row = conn.execute("SELECT products_json FROM snapshots WHERE id=?", (snapshot_id,)).fetchone()
    if row is None:
        raise KeyError(snapshot_id)
    records = conn.execute("SELECT position,record_json FROM evidence_products WHERE snapshot_id=? ORDER BY position", (snapshot_id,)).fetchall()
    if not records:
        return [_legacy_product(p) for p in json.loads(row[0])]
    result = []
    for i, payload in records:
        record = json.loads(payload)
        record["evidence_contract"], tombstones = _owner_graph(conn, snapshot_id, f"product/{i}")
        if tombstones:
            old = decode_value(record.get("evidence_availability", []))
            record["evidence_availability"] = encode_value([t for t in old if t["evidence_id"] not in {n["evidence_id"] for n in tombstones}] + tombstones)
        variants, availabilities = [], []
        for j in range(len(record["product"]["variants"])):
            graph, availability = _owner_graph(conn, snapshot_id, f"product/{i}/variant/{j}")
            variants.append(graph)
            availabilities.append(availability)
        record["variant_contracts"] = variants
        existing = decode_value(record.get("variant_evidence_availability", [None] * len(variants)))
        if "variant_evidence_availability" in record or any(availabilities):
            record["variant_evidence_availability"] = [encode_value([t for t in (old or []) if t["evidence_id"] not in {n["evidence_id"] for n in new}] + new) if old is not None or new else None for old, new in zip(existing, availabilities)]
        result.append(product_from_record(record))
    return result


def load_snapshot(snapshot_id: int, *, db_path=DEFAULT_DB_PATH) -> list[Product]:
    from .snapshot import _get_connection
    conn = _get_connection(db_path)
    try:
        with conn:
            conn.execute("BEGIN")
            return _load_snapshot(conn, snapshot_id)
    except (TypeError, AttributeError, json.JSONDecodeError) as exc:
        raise ValueError("Corrupt evidence storage") from exc
    finally:
        conn.close()


def get_evidence(evidence_id: str, *, snapshot_id=None, record_key=None, db_path=DEFAULT_DB_PATH) -> EvidenceLookup:
    from .snapshot import _get_connection
    conn = _get_connection(db_path)
    try:
        conn.execute("BEGIN")
        where, args = ["evidence_id=?"], [evidence_id]
        for name, value in (("snapshot_id", snapshot_id), ("record_key", record_key)):
            if value is not None:
                where.append(name + "=?")
                args.append(value)
        rows = conn.execute("SELECT * FROM evidence_records WHERE " + " AND ".join(where) + " LIMIT 2", args).fetchall()
        if len(rows) > 1:
            raise ValueError("Ambiguous evidence ID; specify snapshot_id and record_key")
        if not rows:
            owner = conn.execute("SELECT graph_json,reason FROM evidence_owners WHERE snapshot_id=? AND record_key=?", (snapshot_id, record_key)).fetchone()
            status = "unsupported" if owner and owner[0] is None else "missing"
            return EvidenceLookup(status, evidence_id, owner[1] if status == "unsupported" else "evidence_not_found", snapshot_id=snapshot_id, record_key=record_key)
        evidence, tombstone = _read_capture(conn, rows[0])
        return EvidenceLookup("available" if evidence else "expired", evidence_id, "retained_capture" if evidence else tombstone["reason"], evidence, rows[0][0], rows[0][1], None if evidence else tombstone["expired_at"])
    except (TypeError, AttributeError, json.JSONDecodeError) as exc:
        raise ValueError("Corrupt evidence storage") from exc
    finally:
        conn.close()


def prune_evidence(*, db_path=DEFAULT_DB_PATH, before: datetime, protect_references=True, dry_run=True, batch_size=100) -> PruneReport:
    """Inspect one bounded prefix; protected prefixes may remain on later calls."""
    from .snapshot import _get_connection
    _utc(before)
    if type(batch_size) is not int or not 1 <= batch_size <= MAX_PRUNE_BATCH:
        raise ValueError("batch_size must be between 1 and 1000")
    if type(protect_references) is not bool or type(dry_run) is not bool:
        raise ValueError("Retention options must be boolean")
    conn = _get_connection(db_path)
    try:
        conn.execute("BEGIN IMMEDIATE")
        rows = conn.execute("SELECT * FROM evidence_records WHERE status='available' AND observed_at<? ORDER BY observed_at,snapshot_id,record_key,evidence_id LIMIT ?", (before.isoformat(timespec="microseconds"), batch_size + 1)).fetchall()
        candidates, protected, hashes = [], 0, set()
        for row in rows[:batch_size]:
            _read_capture(conn, row)
            referenced = conn.execute("SELECT 1 FROM evidence_references WHERE snapshot_id=? AND record_key=? AND evidence_id=? LIMIT 1", row[:3]).fetchone()
            if protect_references and referenced:
                protected += 1
                continue
            candidates.append(row)
            hashes.add(row[4])
            conn.execute("UPDATE evidence_records SET status='expired',reason='explicit_retention_expiry',expired_at=?,payload_hash=NULL WHERE snapshot_id=? AND record_key=? AND evidence_id=?", (datetime.now(timezone.utc).isoformat(), *row[:3]))
        deleted = 0
        for digest in hashes:
            if not conn.execute("SELECT 1 FROM evidence_records WHERE payload_hash=? AND status='available' LIMIT 1", (digest,)).fetchone():
                deleted += conn.execute("DELETE FROM evidence_payloads WHERE payload_hash=?", (digest,)).rowcount
        report = PruneReport(min(len(rows), batch_size), protected, len(candidates), deleted, dry_run, len(rows) > batch_size)
        conn.rollback() if dry_run else conn.commit()
        return report
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
