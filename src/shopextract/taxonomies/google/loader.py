"""Explicit offline catalog selection with integrity revalidation on every load."""
from importlib.resources import files
from pathlib import Path

from .contracts import (GoogleTaxonomyLookupError, fingerprint_text, locale_text, version_text)
from .publish import safe_identity_directory
from .resource import read_resource


def load_google_taxonomy(version="2021-09-21", *, locale="en-US", catalog_root=None, fingerprint=None):
    version_text(version)
    locale_text(locale)
    if fingerprint is not None:
        fingerprint_text(fingerprint)
    if catalog_root is None:
        directory = Path(str(files("shopextract.taxonomies.google").joinpath("data")))
        if not (directory / "manifest.json").is_file():
            raise GoogleTaxonomyLookupError(
                "Google catalog unavailable; prepare the complete operator-provided source and pass catalog_root")
    else:
        base = safe_identity_directory(catalog_root, version, locale)
        if fingerprint is None:
            candidates = sorted(base.iterdir()) if base.is_dir() else []
            candidates = [path for path in candidates if not path.name.startswith(".")]
            if len(candidates) != 1:
                raise GoogleTaxonomyLookupError("Google catalog missing or ambiguous; supply exact fingerprint")
            directory = candidates[0]
            fingerprint_text(directory.name)
        else:
            directory = base / fingerprint
        if not directory.exists():
            raise GoogleTaxonomyLookupError("Unknown Google taxonomy resource identity")
    expected = dict(version=version, locale=locale)
    if fingerprint is not None:
        expected["fingerprint"] = fingerprint
    elif catalog_root is not None:
        expected["fingerprint"] = directory.name
    return read_resource(directory, expected=expected)
