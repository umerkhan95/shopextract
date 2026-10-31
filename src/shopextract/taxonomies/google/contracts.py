"""Immutable Google category contracts and finite resource identities."""
from dataclasses import dataclass
from datetime import date
import hashlib
import json
import re
from urllib.parse import urlsplit

NAMESPACE = "google:product_category"
MAX_SOURCE_BYTES = 2 * 1024 * 1024
MAX_CATALOG_BYTES = 8 * 1024 * 1024
MAX_MANIFEST_BYTES = 64 * 1024


class GoogleTaxonomyError(ValueError):
    """Invalid Google taxonomy operation."""


class GoogleTaxonomyIntegrityError(GoogleTaxonomyError):
    """Source or retained resource failed integrity validation."""


class GoogleTaxonomyLookupError(GoogleTaxonomyError):
    """Missing, ambiguous or unsupported catalog identity."""


class GoogleTaxonomyPublicationError(GoogleTaxonomyError):
    """A verified resource could not be published."""


class GoogleTaxonomyDependencyError(GoogleTaxonomyError):
    """An explicitly requested source format needs an optional parser."""


@dataclass(frozen=True)
class GoogleCategory:
    id: str
    name: str
    full_name: str
    parent_id: str | None
    child_ids: tuple[str, ...]
    ancestor_ids: tuple[str, ...]


@dataclass(frozen=True)
class GoogleCounts:
    categories: int
    roots: int
    leaves: int
    parent_links: int


@dataclass(frozen=True)
class GoogleSourceProvenance:
    source_kind: str
    source_url: str
    source_commit: str | None
    source_sha256: str
    derived_sha256: str


@dataclass(frozen=True)
class GoogleManifest:
    schema_version: int
    namespace: str
    version: str
    locale: str
    source_url: str
    source_sha256: str
    fingerprint: str
    counts: GoogleCounts
    source_kind: str
    source_provenance: GoogleSourceProvenance | None
    catalog_sha256: str


def canonical(value) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def version_text(value):
    if not isinstance(value, str):
        raise TypeError("Google taxonomy version must be text")
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise GoogleTaxonomyIntegrityError("Invalid Google taxonomy version")
    try:
        date.fromisoformat(value)
    except ValueError:
        raise GoogleTaxonomyIntegrityError("Invalid Google taxonomy date") from None
    return value


def locale_text(value):
    if not isinstance(value, str):
        raise TypeError("Google taxonomy locale must be text")
    if not re.fullmatch(r"[a-z]{2,3}(?:-[A-Z]{2})?", value):
        raise GoogleTaxonomyIntegrityError("Invalid Google taxonomy locale")
    return value


def fingerprint_text(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise GoogleTaxonomyIntegrityError("Invalid taxonomy SHA256")
    return value


def category_id(value):
    if not isinstance(value, str):
        raise TypeError("Google category ID must be text")
    if not re.fullmatch(r"[1-9][0-9]{0,31}", value):
        raise GoogleTaxonomyIntegrityError("Invalid Google category ID")
    return value


def source_url_text(value):
    if not isinstance(value, str):
        raise TypeError("Source URL must be text")
    if value:
        parsed = urlsplit(value)
        if (parsed.scheme != "https" or not parsed.netloc or parsed.username or
                parsed.password or parsed.fragment or any(c.isspace() for c in value)):
            raise GoogleTaxonomyIntegrityError("Source URL must be absolute HTTPS")
    return value


def provenance_record(value, source_sha256, source_url):
    if value is None:
        return None
    keys = {"source_kind", "source_url", "source_commit", "source_sha256", "derived_sha256"}
    if not isinstance(value, dict) or set(value) != keys:
        raise GoogleTaxonomyIntegrityError("Invalid Google source provenance fields")
    kind = value["source_kind"]
    if kind not in {"google_txt", "shopify_google_snapshot"}:
        raise GoogleTaxonomyIntegrityError("Unknown Google source kind")
    url = source_url_text(value["source_url"])
    original = fingerprint_text(value["source_sha256"])
    derived = fingerprint_text(value["derived_sha256"])
    if derived != source_sha256 or source_url and url != source_url:
        raise GoogleTaxonomyIntegrityError("Google provenance does not match consumed source")
    commit = value["source_commit"]
    if kind == "shopify_google_snapshot":
        if not url or not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise GoogleTaxonomyIntegrityError("Snapshot provenance requires pinned source URL/commit")
    elif commit is not None or original != derived:
        raise GoogleTaxonomyIntegrityError("Original TXT provenance must describe original bytes")
    return GoogleSourceProvenance(kind, url, commit, original, derived)
