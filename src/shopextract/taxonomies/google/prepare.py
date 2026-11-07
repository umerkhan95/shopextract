"""Explicit local source preparation, leaving loading and publication separate."""
from .contracts import MAX_SOURCE_BYTES, GoogleTaxonomyIntegrityError
from .publish import publish_catalog
from .resource import read_bounded
from .source import parse_google_taxonomy


def prepare_google_taxonomy(source_file, catalog_root, *, locale="en-US",
                            expected_sha256=None, source_url="", provenance=None):
    try:
        text = read_bounded(source_file, MAX_SOURCE_BYTES).decode("utf-8")
    except (OSError, UnicodeError) as error:
        raise GoogleTaxonomyIntegrityError("Cannot read Google taxonomy source") from error
    catalog = parse_google_taxonomy(text, locale=locale, source_url=source_url,
                                    expected_sha256=expected_sha256, provenance=provenance)
    return publish_catalog(catalog, catalog_root)
