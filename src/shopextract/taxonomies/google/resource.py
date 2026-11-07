"""Strict bounded local resource decoding and independent integrity checks."""
from dataclasses import asdict
import json
from pathlib import Path

from .catalog import catalog_from_payload
from .contracts import (MAX_CATALOG_BYTES, MAX_MANIFEST_BYTES, GoogleTaxonomyIntegrityError,
                        canonical, digest)


def read_bounded(path, maximum):
    path = Path(path)
    if path.is_symlink():
        raise GoogleTaxonomyIntegrityError("Taxonomy resource symlink rejected")
    with path.open("rb") as stream:
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise GoogleTaxonomyIntegrityError("Taxonomy resource byte limit exceeded")
    return data


def strict_json(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise GoogleTaxonomyIntegrityError("Duplicate taxonomy JSON key")
            result[key] = value
        return result

    def invalid_constant(value):
        raise GoogleTaxonomyIntegrityError("Nonfinite taxonomy JSON value")

    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=pairs, parse_constant=invalid_constant)
    except (UnicodeError, ValueError, RecursionError) as error:
        if isinstance(error, GoogleTaxonomyIntegrityError):
            raise
        raise GoogleTaxonomyIntegrityError("Malformed taxonomy JSON") from error


def read_resource(directory, *, expected=None):
    directory = Path(directory)
    if directory.is_symlink():
        raise GoogleTaxonomyIntegrityError("Taxonomy directory symlink rejected")
    try:
        manifest_bytes = read_bounded(directory / "manifest.json", MAX_MANIFEST_BYTES)
        catalog_bytes = read_bounded(directory / "catalog.json", MAX_CATALOG_BYTES)
        manifest = strict_json(manifest_bytes)
        payload = strict_json(catalog_bytes)
        catalog = catalog_from_payload(payload)
        actual = asdict(catalog.manifest)
        if (manifest != actual or type(manifest.get("schema_version")) is not int or
                any(type(value) is not int for value in manifest.get("counts", {}).values()) or
                digest(catalog_bytes) != catalog.manifest.fingerprint or
                canonical(payload) != catalog_bytes):
            raise GoogleTaxonomyIntegrityError("Taxonomy manifest/payload integrity mismatch")
        for key, value in (expected or {}).items():
            if actual.get(key) != value:
                raise GoogleTaxonomyIntegrityError("Taxonomy resource identity mismatch: " + key)
        return catalog
    except (OSError, UnicodeError, TypeError, KeyError, AttributeError, OverflowError, RecursionError) as error:
        raise GoogleTaxonomyIntegrityError("Cannot read valid Google taxonomy resource") from error
