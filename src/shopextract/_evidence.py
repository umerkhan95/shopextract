"""Version-one field trust contracts; capture and policy are separate concerns."""
from __future__ import annotations

from dataclasses import dataclass, field, fields, asdict
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
import math
import re
from urllib.parse import urlsplit
from uuid import UUID


class SupportState(str, Enum):
    OBSERVED = "observed"
    UNKNOWN = "unknown"
    UNSUPPORTED = "unsupported"
    CONFLICTING = "conflicting"
    EXPIRED = "expired"


def _id(value: str, prefix: str) -> None:
    if not isinstance(value, str) or not value.startswith(prefix):
        raise ValueError(f"ID must start with {prefix}")
    try:
        parsed = UUID(value[len(prefix):])
    except (ValueError, AttributeError) as exc:
        raise ValueError("ID must contain a canonical UUID") from exc
    if str(parsed) != value[len(prefix):]:
        raise ValueError("ID must contain a canonical UUID")


def _text(value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Nonempty text required")


def _utc(value: datetime) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() != timezone.utc.utcoffset(value):
        raise ValueError("Timezone-aware UTC timestamp required")


def _path(value: str) -> None:
    # RFC 6901 JSON Pointer, relative to the product or standalone variant.
    if not isinstance(value, str) or not value.startswith("/") or re.search(r"~(?![01])", value):
        raise ValueError("Field path must be an escaped JSON Pointer")


@dataclass
class ValidatedConfidence:
    value: float
    method: str
    dataset: str
    version: str

    def __post_init__(self):
        if isinstance(self.value, bool) or not isinstance(self.value, (int, float)) or not math.isfinite(self.value) or not 0 <= self.value <= 1:
            raise ValueError("Validated confidence must be finite and between 0 and 1")
        for text in (self.method, self.dataset, self.version):
            _text(text)


@dataclass
class Evidence:
    evidence_id: str
    source_url: str
    observed_at: datetime
    method: str
    excerpt: str | None = None
    retained_data: object = None
    pointer: str | None = None
    source_role: str = "unverified"
    truncated: bool = False

    def __post_init__(self):
        _id(self.evidence_id, "e_")
        parts = urlsplit(self.source_url)
        if parts.scheme not in ("http", "https") or not parts.netloc:
            raise ValueError("Absolute HTTP(S) source URL required")
        _utc(self.observed_at)
        _text(self.method)
        _text(self.source_role)
        if self.excerpt is not None:
            _text(self.excerpt)
        if self.pointer is not None:
            if self.retained_data is None:
                raise ValueError("Pointer requires retained source data")
            self.resolve_pointer()
        if self.excerpt is None and self.pointer is None:
            raise ValueError("Evidence requires an excerpt or retained-data pointer")
        if not isinstance(self.truncated, bool):
            raise ValueError("truncated must be boolean")
        encode_value(self.retained_data)

    def resolve_pointer(self):
        if self.pointer == "":
            return self.retained_data
        _path(self.pointer)
        value = self.retained_data
        try:
            for token in self.pointer[1:].split("/"):
                token = token.replace("~1", "/").replace("~0", "~")
                if isinstance(value, list):
                    if not re.fullmatch(r"0|[1-9][0-9]*", token):
                        raise ValueError("Invalid array index")
                    value = value[int(token)]
                elif isinstance(value, dict):
                    value = value[token]
                else:
                    raise ValueError("Pointer traverses a scalar")
        except (KeyError, IndexError, TypeError) as exc:
            raise ValueError("Pointer does not resolve in retained data") from exc
        return value


@dataclass
class FieldObservation:
    observation_id: str
    field_path: str
    state: SupportState
    raw_value: object = None
    normalized_value: object = None
    evidence_ids: list[str] = field(default_factory=list)
    reason: str = ""
    transformations: list[str] = field(default_factory=list)
    score: float | None = None
    score_kind: str | None = None
    validated_confidence: ValidatedConfidence | None = None

    def __post_init__(self):
        _id(self.observation_id, "o_")
        _path(self.field_path)
        self.state = SupportState(self.state)
        for evidence_id in self.evidence_ids:
            _id(evidence_id, "e_")
        if self.state == SupportState.OBSERVED:
            if not self.evidence_ids or self.normalized_value is None:
                raise ValueError("Observed facts require evidence and a non-null value")
        else:
            _text(self.reason)
        if self.state != SupportState.OBSERVED and self.validated_confidence is not None:
            raise ValueError("Only observed support can carry validated confidence")
        if self.score is not None:
            if isinstance(self.score, bool) or not isinstance(self.score, (int, float)) or not math.isfinite(self.score):
                raise ValueError("Score must be finite")
            if self.score_kind not in ("model", "rule"):
                raise ValueError("Score requires model or rule kind")
        elif self.score_kind is not None:
            raise ValueError("Score kind requires a score")
        for transformation in self.transformations:
            _text(transformation)
        encode_value(self.raw_value)
        encode_value(self.normalized_value)


@dataclass
class FieldResolution:
    field_path: str
    state: SupportState
    observation_ids: list[str]
    reason: str
    selected_observation_id: str | None = None
    policy: str = "unresolved"
    policy_version: str = "1"

    def __post_init__(self):
        _path(self.field_path)
        self.state = SupportState(self.state)
        for observation_id in self.observation_ids:
            _id(observation_id, "o_")
        for text in (self.reason, self.policy, self.policy_version):
            _text(text)
        if self.selected_observation_id is not None and self.selected_observation_id not in self.observation_ids:
            raise ValueError("Selected observation must be retained among alternatives")
        if self.state == SupportState.OBSERVED and self.selected_observation_id is None:
            raise ValueError("Observed resolution requires a selected observation")
        if self.state != SupportState.OBSERVED and self.selected_observation_id is not None:
            raise ValueError("Unresolved states cannot assert a selected fact")
        if self.state == SupportState.CONFLICTING and len(set(self.observation_ids)) < 2:
            raise ValueError("Conflict requires competing observations")


@dataclass
class TrustContract:
    evidence: list[Evidence] = field(default_factory=list)
    observations: list[FieldObservation] = field(default_factory=list)
    resolutions: list[FieldResolution] = field(default_factory=list)
    schema_version: int = 1

    def __post_init__(self):
        self.validate()

    def validate(self):
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("Unsupported trust schema version")
        for records, key in ((self.evidence, "evidence_id"), (self.observations, "observation_id"), (self.resolutions, "field_path")):
            ids = [getattr(record, key) for record in records]
            if len(ids) != len(set(ids)):
                raise ValueError(f"Duplicate {key}")
            for record in records:
                record.__post_init__()
        evidence = {e.evidence_id for e in self.evidence}
        observations = {o.observation_id: o for o in self.observations}
        for observation in self.observations:
            if not set(observation.evidence_ids) <= evidence:
                raise ValueError("Dangling evidence reference")
            if observation.validated_confidence is not None:
                observation.validated_confidence.__post_init__()
        for resolution in self.resolutions:
            if any(i not in observations or observations[i].field_path != resolution.field_path for i in resolution.observation_ids):
                raise ValueError("Resolution references missing or different-field observations")
            candidates = {o.observation_id for o in self.observations if o.field_path == resolution.field_path}
            if set(resolution.observation_ids) != candidates:
                raise ValueError("Resolution must retain all field observations")
            selected = resolution.selected_observation_id
            if selected is not None and observations[selected].state != SupportState.OBSERVED:
                raise ValueError("Selected fact must have observed support")

    def to_dict(self) -> dict:
        self.validate()
        return encode_value(asdict(self))

    @classmethod
    def from_dict(cls, payload: dict) -> TrustContract:
        data = decode_value(payload)
        if not isinstance(data, dict) or set(data) - {"schema_version", "evidence", "observations", "resolutions"}:
            raise ValueError("Malformed trust contract object")
        if "schema_version" not in data:
            raise ValueError("Serialized trust contract requires schema_version")
        observations = []
        for item in data.get("observations", []):
            item = dict(item)
            if item.get("validated_confidence") is not None:
                item["validated_confidence"] = ValidatedConfidence(**item["validated_confidence"])
            observations.append(FieldObservation(**item))
        return cls(evidence=[Evidence(**e) for e in data.get("evidence", [])],
                   observations=observations,
                   resolutions=[FieldResolution(**r) for r in data.get("resolutions", [])],
                   schema_version=data["schema_version"])


def encode_value(value):
    """JSON-safe tagged values, including dictionaries that resemble tags."""
    if isinstance(value, Enum):
        return encode_value(value.value)
    if isinstance(value, Decimal):
        if not value.is_finite():
            raise ValueError("Nonfinite Decimal")
        return {"$type": "decimal", "value": str(value)}
    if isinstance(value, datetime):
        _utc(value)
        return {"$type": "datetime", "value": value.isoformat()}
    if isinstance(value, dict):
        if any(not isinstance(k, str) for k in value):
            raise ValueError("JSON object keys must be strings")
        data = {k: encode_value(v) for k, v in value.items()}
        return {"$type": "mapping", "value": data} if "$type" in data else data
    if isinstance(value, list):
        return [encode_value(v) for v in value]
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float) and math.isfinite(value):
        return value
    raise ValueError("Unsupported or nonfinite contract value")


def decode_value(value):
    if isinstance(value, list):
        return [decode_value(v) for v in value]
    if isinstance(value, dict):
        if "$type" in value:
            if set(value) != {"$type", "value"}:
                raise ValueError("Malformed typed value")
            kind, data = value["$type"], value["value"]
            if kind == "decimal":
                return Decimal(data)
            if kind == "datetime":
                return datetime.fromisoformat(data)
            if kind == "mapping" and isinstance(data, dict):
                return {k: decode_value(v) for k, v in data.items()}
            raise ValueError("Unknown typed value")
        return {k: decode_value(v) for k, v in value.items()}
    return value


# Derived metadata is deliberately excluded from claims about source facts.
DERIVED_FIELDS = frozenset({"canonical_product_id", "canonical_variant_id", "supplier_id", "platform", "scraped_at", "raw_data"})


def factual_paths(record) -> dict[str, object]:
    """All factual leaves plus collection containers (including empty ones)."""
    result = {}

    def visit(value, path):
        result[path] = value
        if isinstance(value, dict):
            for key, item in value.items():
                visit(item, path + "/" + key.replace("~", "~0").replace("/", "~1"))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if hasattr(item, "__dataclass_fields__"):
                    walk(item, path + f"/{index}")
                else:
                    visit(item, path + f"/{index}")

    def walk(obj, prefix):
        for f in fields(obj):
            if f.name not in DERIVED_FIELDS:
                visit(getattr(obj, f.name), prefix + "/" + f.name)

    walk(record, "")
    return result


def trust_view(record, contract: TrustContract | None = None) -> dict[str, dict]:
    """Inspect facts without inferring support from compatibility defaults.

    Explicit observations/resolutions take precedence; uncovered fields always
    report unsupported. Multiple candidates require an explicit resolution.
    """
    if contract is not None:
        contract.validate()
    paths = factual_paths(record)
    observations = {}
    resolutions = {}
    if contract is not None:
        for o in contract.observations:
            if o.field_path not in paths:
                raise ValueError("Observation field path is outside this record")
            observations.setdefault(o.field_path, []).append(o)
        resolutions = {r.field_path: r for r in contract.resolutions}
        if not set(resolutions) <= paths.keys():
            raise ValueError("Resolution field path is outside this record")
    result = {}
    for path, value in paths.items():
        candidates = observations.get(path, [])
        resolution = resolutions.get(path)
        selected = None
        if resolution:
            state, reason = resolution.state, resolution.reason
            selected = next((o for o in candidates if o.observation_id == resolution.selected_observation_id), None)
        elif len(candidates) == 1:
            selected = candidates[0]
            state, reason = selected.state, selected.reason
        elif candidates:
            state, reason = SupportState.CONFLICTING, "Multiple observations require explicit resolution"
        else:
            state, reason = SupportState.UNSUPPORTED, "Legacy/default value; source provenance unavailable"
        result[path] = {"state": state.value, "reason": reason,
                        "value": selected.normalized_value if selected and state == SupportState.OBSERVED else None,
                        "legacy_value": value,
                        "observation_ids": [o.observation_id for o in candidates],
                        "evidence_ids": list(dict.fromkeys(e for o in candidates for e in o.evidence_ids))}
    return result
