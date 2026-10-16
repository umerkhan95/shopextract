"""Opt-in, versioned offline evidence bundles and digest-bound feed mappings."""
from __future__ import annotations

import csv
import io
import xml.etree.ElementTree as ET
import hashlib
import json
from pathlib import Path

from .._models import Product
from .._portable import product_from_record, product_to_record, validate_tree

BUNDLE_TYPE = "shopextract.evidence"
BUNDLE_SCHEMA_VERSION = 1
MAX_BUNDLE_BYTES = 64 * 1024 * 1024
MAX_BUNDLE_RECORDS = 100_000


def _json_bytes(value):
    validate_tree(value, encoded=True)
    try:
        result = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True,
                            separators=(",", ":")).encode("utf-8")
    except (TypeError, UnicodeError, RecursionError) as exc:
        raise ValueError(f"Invalid bundle JSON: {exc}") from exc
    if len(result) > MAX_BUNDLE_BYTES:
        raise ValueError("Evidence bundle exceeds byte limit")
    return result


def _record_key(product, record):
    # Scoped canonical identities survive scalar changes. Unkeyed records use
    # content hashes (local sorted JSON, not RFC 8785 canonicalization); these
    # change when any value/contract changes. Repeated identities get an explicit
    # occurrence suffix, stable only within the same ordered catalog.
    if product.supplier_id and product.canonical_product_id:
        identity = json.dumps([product.supplier_id, product.canonical_product_id], ensure_ascii=False)
        return "canonical:" + hashlib.sha256(identity.encode("utf-8")).hexdigest()
    return "content:" + hashlib.sha256(_json_bytes(record)).hexdigest()


def create_evidence_bundle(products: list[Product]) -> dict:
    """Create a lossless bundle, retaining duplicate identities in input order."""
    if not isinstance(products, list) or len(products) > MAX_BUNDLE_RECORDS:
        raise ValueError("Expected a bounded list of products")
    records, occurrences = [], {}
    for product in products:
        record = product_to_record(product)
        base = _record_key(product, record)
        occurrence = occurrences.get(base, 0)
        occurrences[base] = occurrence + 1
        key = f"{base}:{occurrence}"
        records.append({"record_key": key, "record": record})
    bundle = {"bundle_type": BUNDLE_TYPE, "schema_version": BUNDLE_SCHEMA_VERSION,
              "records": records}
    _json_bytes(bundle)
    return bundle


def load_evidence_bundle(bundle: dict) -> list[Product]:
    """Validate envelope, unique identities, types, graphs and retained pointers."""
    _json_bytes(bundle)
    if not isinstance(bundle, dict) or set(bundle) != {"bundle_type", "schema_version", "records"}:
        raise ValueError("Malformed evidence bundle envelope")
    if bundle["bundle_type"] != BUNDLE_TYPE or type(bundle["schema_version"]) is not int or bundle["schema_version"] != BUNDLE_SCHEMA_VERSION:
        raise ValueError("Unsupported evidence bundle type or version")
    records = bundle["records"]
    if not isinstance(records, list) or len(records) > MAX_BUNDLE_RECORDS:
        raise ValueError("Evidence bundle record limit exceeded or invalid records")
    keys, products = set(), []
    for index, item in enumerate(records):
        if not isinstance(item, dict) or set(item) != {"record_key", "record"}:
            raise ValueError(f"Malformed bundle entry at index {index}")
        key = item["record_key"]
        if not isinstance(key, str) or not key.strip() or key in keys:
            raise ValueError("Record keys must be nonempty and unique")
        keys.add(key)
        try:
            products.append(product_from_record(item["record"]))
        except ValueError as exc:
            raise ValueError(f"Invalid bundle record {key}: {exc}") from exc
    return products


def write_evidence_bundle(products: list[Product], path: str | Path) -> None:
    """Write an explicitly opted-in UTF-8 portable bundle."""
    Path(path).write_bytes(_json_bytes(create_evidence_bundle(products)))


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"Nonfinite JSON constant: {value}")


def read_evidence_bundle(path: str | Path) -> list[Product]:
    """Bound bytes before parsing and reject duplicate keys/nonfinite JSON."""
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_BUNDLE_BYTES + 1)
    if len(data) > MAX_BUNDLE_BYTES:
        raise ValueError("Evidence bundle exceeds byte limit")
    try:
        bundle = json.loads(data, object_pairs_hook=_unique_object, parse_constant=_reject_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError(f"Invalid evidence bundle JSON: {exc}") from exc
    return load_evidence_bundle(bundle)


def _row_id(product, format):
    return (product.sku or product.external_id) if format == "idealo" else product.external_id


def _verify_projection(products, payload, format):
    if len(payload) > MAX_BUNDLE_BYTES:
        raise ValueError("Export projection exceeds byte limit")
    try:
        text = payload.decode("utf-8")
        if format == "google_shopping":
            if "<!DOCTYPE" in text or "<!ENTITY" in text:
                raise ValueError("Export projection must not contain XML declarations")
            root = ET.fromstring(text)
            if root.tag != "rss":
                raise ValueError("Expected RSS export projection")
            ids = [item.findtext("{http://base.google.com/ns/1.0}id", "")
                   for item in root.findall("channel/item")]
        else:
            reader = csv.DictReader(io.StringIO(text, newline=""), delimiter="\t" if format == "idealo" else ",")
            key = "sku" if format == "idealo" else "external_id"
            ids = [row.get(key, "") for row in reader]
        if ids != [_row_id(p, format) for p in products]:
            raise ValueError("Export projection rows/identifiers do not match bundle")
    except (UnicodeError, ET.ParseError, csv.Error) as exc:
        raise ValueError(f"Invalid export projection: {exc}") from exc


def create_evidence_sidecar(products: list[Product], exported_bytes: bytes, *, format: str) -> dict:
    """Bind a one-row-per-product projection to its exact bytes with SHA-256.

    Row indices are zero-based; repeated marketplace IDs stay separate. The
    digest establishes correspondence, not capture authenticity or confidence.
    """
    if type(exported_bytes) is not bytes:
        raise ValueError("Export payload must be bytes")
    if not isinstance(format, str) or format not in {"csv", "google_shopping", "idealo"}:
        raise ValueError("Unsupported sidecar format")
    bundle = create_evidence_bundle(products)
    _verify_projection(products, exported_bytes, format)
    sidecar = {"sidecar_type": "shopextract.evidence-sidecar", "schema_version": 1,
               "format": format, "sha256": hashlib.sha256(exported_bytes).hexdigest(),
               "rows": [{"row_index": i, "record_key": item["record_key"],
                         "external_id": _row_id(product, format)}
                        for i, (product, item) in enumerate(zip(products, bundle["records"]))],
               "bundle": bundle}
    _json_bytes(sidecar)
    return sidecar


def load_evidence_sidecar(sidecar: dict, exported_bytes: bytes) -> list[Product]:
    """Verify exact bytes and complete, ordered mapping before returning facts."""
    _json_bytes(sidecar)
    fields = {"sidecar_type", "schema_version", "format", "sha256", "rows", "bundle"}
    if not isinstance(sidecar, dict) or set(sidecar) != fields:
        raise ValueError("Malformed evidence sidecar")
    if sidecar["sidecar_type"] != "shopextract.evidence-sidecar" or type(sidecar["schema_version"]) is not int or sidecar["schema_version"] != 1:
        raise ValueError("Unsupported sidecar type or version")
    if not isinstance(sidecar["format"], str) or sidecar["format"] not in {"csv", "google_shopping", "idealo"}:
        raise ValueError("Unsupported sidecar format")
    if type(exported_bytes) is not bytes or sidecar["sha256"] != hashlib.sha256(exported_bytes).hexdigest():
        raise ValueError("Sidecar export digest mismatch")
    products = load_evidence_bundle(sidecar["bundle"])
    _verify_projection(products, exported_bytes, sidecar["format"])
    rows = sidecar["rows"]
    if not isinstance(rows, list) or len(rows) != len(products):
        raise ValueError("Sidecar must map every product row")
    for index, (row, product, entry) in enumerate(zip(rows, products, sidecar["bundle"]["records"])):
        if (not isinstance(row, dict) or set(row) != {"row_index", "record_key", "external_id"}
                or type(row["row_index"]) is not int or row["row_index"] != index
                or row["record_key"] != entry["record_key"]
                or row["external_id"] != _row_id(product, sidecar["format"])):
            raise ValueError(f"Corrupt sidecar row mapping at index {index}")
    return products
