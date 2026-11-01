"""Bounded version-one Product transport shared by bundles and SQLite.

Values use the evidence codec; contracts are encoded exactly once. Import never
reruns resolution or refreshes capture times. Arbitrary Python objects, tuples,
sets and bytes are intentionally outside this transport contract.
"""
from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
import math
import types
from typing import get_args, get_origin, Union

from ._evidence import TrustContract, decode_value, encode_value, trust_view, _id, _utc, _record_values
from ._models import Product, Variant, Platform
from ._schemas import schema_hints

PORTABLE_RECORD_VERSION = 1
MAX_PORTABLE_DEPTH = 64
MAX_PORTABLE_NODES = 1_000_000


def validate_tree(value, *, encoded=False):
    """Check recursive resource bounds before calling the recursive codec."""
    stack = [(value, 0)]
    count = 0
    while stack:
        item, depth = stack.pop()
        count += 1
        if count > MAX_PORTABLE_NODES or depth > MAX_PORTABLE_DEPTH:
            raise ValueError("Portable value exceeds depth or node limit")
        if isinstance(item, dict):
            if any(not isinstance(k, str) for k in item):
                raise ValueError("Portable object keys must be strings")
            if encoded and "$type" in item:
                if set(item) != {"$type", "value"}:
                    raise ValueError("Malformed typed value")
                kind, payload = item["$type"], item["value"]
                if kind in ("decimal", "datetime"):
                    if not isinstance(payload, str):
                        raise ValueError("Typed decimal/datetime requires text")
                elif kind == "mapping":
                    if not isinstance(payload, dict) or any(not isinstance(k, str) for k in payload):
                        raise ValueError("Typed mapping requires string-keyed object")
                    # Its root is literal user data, not another tag.
                    stack.extend((v, depth + 2) for v in payload.values())
                    continue
                else:
                    raise ValueError("Unknown typed value")
            stack.extend((v, depth + 1) for v in item.values())
        elif isinstance(item, list):
            stack.extend((v, depth + 1) for v in item)
        elif item is None or isinstance(item, (str, bool, int, Enum)):
            pass
        elif isinstance(item, float) and math.isfinite(item):
            pass
        elif not encoded and isinstance(item, (Decimal, datetime)):
            encode_value(item)  # finite Decimal and UTC timestamp checks
        else:
            raise ValueError("Unsupported or nonfinite portable value")


def _check_type(value, annotation, path):
    origin, args = get_origin(annotation), get_args(annotation)
    if origin in (Union, types.UnionType):
        for choice in args:
            try:
                _check_type(value, choice, path)
                return
            except ValueError:
                pass
        raise ValueError(f"Invalid type at {path}")
    if origin is list:
        if not isinstance(value, list):
            raise ValueError(f"Expected list at {path}")
        for index, child in enumerate(value):
            _check_type(child, args[0], f"{path}/{index}")
    elif origin is dict or annotation is dict:
        if not isinstance(value, dict):
            raise ValueError(f"Expected object at {path}")
        if args:
            for key, child in value.items():
                _check_type(key, args[0], path)
                _check_type(child, args[1], f"{path}/{key}")
    elif annotation is object:
        validate_tree(value)
    elif isinstance(annotation, type) and issubclass(annotation, Enum):
        if not isinstance(value, annotation):
            raise ValueError(f"Expected {annotation.__name__} at {path}")
    elif isinstance(annotation, type) and is_dataclass(annotation):
        if not isinstance(value, annotation):
            raise ValueError(f"Expected {annotation.__name__} at {path}")
        for name, kind in schema_hints(annotation).items():
            _check_type(getattr(value, name), kind, f"{path}/{name}")
    elif annotation is float:
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError(f"Expected finite number at {path}")
    elif type(value) is not annotation:
        raise ValueError(f"Invalid type at {path}")


def _contract_to_dict(owner):
    contract = getattr(owner, "evidence_contract", None)
    if contract is None:
        return None
    _check_type(contract, TrustContract, "evidence_contract")
    trust_view(owner, contract)
    # trust_view validated this contract synchronously; preserve the same values.
    return encode_value(_record_values(contract))


def _contract_from_dict(value, owner):
    if value is None:
        return
    if not isinstance(value, dict):
        raise ValueError("evidence_contract must be an object or null")
    contract = TrustContract.from_dict(value)
    _check_type(contract, TrustContract, "evidence_contract")
    trust_view(owner, contract)
    owner.evidence_contract = contract


def _availability(value, owner):
    if not isinstance(value, list):
        raise ValueError("Evidence availability must be a list")
    seen = set()
    live = {e.evidence_id for e in getattr(owner, "evidence_contract", TrustContract()).evidence}
    for item in value:
        if not isinstance(item, dict) or set(item) != {"evidence_id", "status", "reason", "expired_at", "metadata"}:
            raise ValueError("Malformed evidence availability tombstone")
        _id(item["evidence_id"], "e_")
        if item["evidence_id"] in seen or item["evidence_id"] in live:
            raise ValueError("Duplicate or live evidence availability ID")
        seen.add(item["evidence_id"])
        if item["status"] != "expired" or not isinstance(item["reason"], str) or not item["reason"].strip():
            raise ValueError("Invalid evidence availability status/reason")
        _utc(item["expired_at"])
        if not isinstance(item["metadata"], dict) or item["metadata"].keys() - {"evidence_id", "source_url", "observed_at", "method", "pointer", "source_role", "truncated"}:
            raise ValueError("Tombstone metadata must omit retained payload")
        validate_tree(item["metadata"])
    return value


def product_to_record(product: Product) -> dict:
    """Encode typed values and separately aligned dynamic trust attachments."""
    try:
        _check_type(product, Product, "product")
        values = _record_values(product)
        validate_tree(values)
        record = {"schema_version": PORTABLE_RECORD_VERSION,
                  "product": encode_value(values),
                  "evidence_contract": _contract_to_dict(product),
                  "variant_contracts": [_contract_to_dict(v) for v in product.variants]}
        for key, owner in (("evidence_availability", product),):
            if hasattr(owner, key):
                record[key] = encode_value(_availability(getattr(owner, key), owner))
        if any(hasattr(v, "evidence_availability") for v in product.variants):
            record["variant_evidence_availability"] = [encode_value(_availability(v.evidence_availability, v)) if hasattr(v, "evidence_availability") else None for v in product.variants]
        validate_tree(record, encoded=True)
        return record
    except (TypeError, AttributeError, OverflowError, RecursionError) as exc:
        raise ValueError(f"Invalid portable product: {exc}") from exc


def product_from_record(record: dict) -> Product:
    """Strictly reconstruct Product/Variant/Platform without changing history."""
    try:
        validate_tree(record, encoded=True)
        required = {"schema_version", "product", "evidence_contract", "variant_contracts"}
        optional = {"evidence_availability", "variant_evidence_availability"}
        if not isinstance(record, dict) or not required <= record.keys() or record.keys() - required - optional:
            raise ValueError("Malformed portable record fields")
        if type(record["schema_version"]) is not int or record["schema_version"] != PORTABLE_RECORD_VERSION:
            raise ValueError("Unsupported portable record version")
        data = decode_value(record["product"])
        validate_tree(data)
        if not isinstance(data, dict) or set(data) != {f.name for f in fields(Product)}:
            raise ValueError("Portable product requires exactly the Product fields")
        data["platform"] = Platform(data["platform"])
        if not isinstance(data["variants"], list):
            raise ValueError("variants must be a list")
        variants = []
        for item in data["variants"]:
            if not isinstance(item, dict) or set(item) != {f.name for f in fields(Variant)}:
                raise ValueError("Portable variant requires exactly the Variant fields")
            variants.append(Variant(**item))
        data["variants"] = variants
        product = Product(**data)
        _check_type(product, Product, "product")
        contracts = record["variant_contracts"]
        if not isinstance(contracts, list) or len(contracts) != len(variants):
            raise ValueError("Variant contracts must be index-aligned")
        _contract_from_dict(record["evidence_contract"], product)
        for variant, contract in zip(variants, contracts):
            _contract_from_dict(contract, variant)
        if "evidence_availability" in record:
            product.evidence_availability = _availability(decode_value(record["evidence_availability"]), product)
        if "variant_evidence_availability" in record:
            availability = record["variant_evidence_availability"]
            if not isinstance(availability, list) or len(availability) != len(variants):
                raise ValueError("Variant availability must be index-aligned")
            for variant, item in zip(variants, availability):
                if item is not None:
                    variant.evidence_availability = _availability(decode_value(item), variant)
        return product
    except (TypeError, AttributeError, KeyError, OverflowError, RecursionError, ArithmeticError) as exc:
        raise ValueError(f"Invalid portable record: {exc}") from exc
