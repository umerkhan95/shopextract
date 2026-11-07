"""Strict Google TXT source adapter; explicit provenance, no network access."""
import re

from .catalog import build_catalog
from .contracts import MAX_SOURCE_BYTES, GoogleTaxonomyIntegrityError, digest, fingerprint_text


def parse_google_taxonomy(text, *, locale="en-US", source_url="", expected_sha256=None, provenance=None):
    if not isinstance(text, str):
        raise TypeError("Google taxonomy source must be text")
    try:
        encoded = text.encode("utf-8")
    except UnicodeError:
        raise GoogleTaxonomyIntegrityError("Invalid Google taxonomy UTF-8") from None
    if len(encoded) > MAX_SOURCE_BYTES or text.startswith("\ufeff"):
        raise GoogleTaxonomyIntegrityError("Google taxonomy source size/encoding rejected")
    source_hash = digest(encoded)
    if expected_sha256 is not None and fingerprint_text(expected_sha256) != source_hash:
        raise GoogleTaxonomyIntegrityError("Google source SHA256 mismatch")
    lines = text.splitlines()
    match = re.fullmatch(r"# Google_Product_Taxonomy_Version: ([0-9]{4}-[0-9]{2}-[0-9]{2})", lines[0]) if lines else None
    if match is None:
        raise GoogleTaxonomyIntegrityError("Google taxonomy header missing or malformed")
    pairs = []
    for line in lines[1:]:
        if not line:
            continue
        row = re.fullmatch(r"([1-9][0-9]{0,31}) - (.+)", line)
        if row is None:
            raise GoogleTaxonomyIntegrityError("Malformed Google taxonomy row")
        pairs.append((row[1], row[2]))
    return build_catalog(pairs, version=match[1], locale=locale, source_url=source_url,
                         source_sha256=source_hash, provenance=provenance)
