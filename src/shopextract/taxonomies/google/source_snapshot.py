"""Explicit local Shopify-maintained Google snapshot conversion/preparation."""
from .contracts import (
    MAX_SOURCE_BYTES, GoogleTaxonomyIntegrityError, category_id, digest,
    fingerprint_text, locale_text, version_text,
)
from .publish import publish_catalog
from .resource import read_bounded
from .source import parse_google_taxonomy
from .source_document import decode_source_document


def prepare_google_snapshot(source_file, catalog_root, *, source_commit, source_url,
                            expected_sha256, version="2021-09-21", locale="en-US"):
    """Convert exact {id,full_name} source rows with retained primary provenance."""
    fingerprint_text(expected_sha256)
    version_text(version)
    locale_text(locale)
    try:
        data = read_bounded(source_file, MAX_SOURCE_BYTES)
    except OSError as error:
        raise GoogleTaxonomyIntegrityError("Cannot read Google snapshot source") from error
    original_hash = digest(data)
    if original_hash != expected_sha256:
        raise GoogleTaxonomyIntegrityError("Google snapshot source SHA256 mismatch")
    rows = decode_source_document(data)
    if not isinstance(rows, list) or not rows:
        raise GoogleTaxonomyIntegrityError("Google snapshot must contain category rows")
    lines = ["# Google_Product_Taxonomy_Version: " + version]
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"id", "full_name"}:
            raise GoogleTaxonomyIntegrityError("Invalid Google snapshot row fields")
        identifier = str(row["id"]) if type(row["id"]) is int else row["id"]
        if not isinstance(identifier, str):
            raise GoogleTaxonomyIntegrityError("Invalid Google snapshot category ID")
        category_id(identifier)
        name = row["full_name"]
        if (not isinstance(name, str) or
                any(ord(char) < 32 or char in "\x85\u2028\u2029" for char in name)):
            raise GoogleTaxonomyIntegrityError("Invalid Google snapshot category path")
        lines.append(identifier + " - " + name)
    text = "\n".join(lines) + "\n"
    provenance = dict(source_kind="shopify_google_snapshot", source_url=source_url,
                      source_commit=source_commit, source_sha256=original_hash,
                      derived_sha256=digest(text.encode("utf-8")))
    catalog = parse_google_taxonomy(text, locale=locale, source_url=source_url,
                                    provenance=provenance)
    return publish_catalog(catalog, catalog_root)
