"""Atomic publication of new immutable catalog directories; no old overwrite."""
from dataclasses import asdict
import os
from pathlib import Path
import shutil
import tempfile

from .catalog import catalog_payload
from .contracts import (GoogleTaxonomyIntegrityError, GoogleTaxonomyPublicationError,
                        canonical, fingerprint_text, locale_text, version_text)
from .resource import read_resource


def safe_identity_directory(catalog_root, version, locale):
    version_text(version)
    locale_text(locale)
    root = Path(catalog_root)
    if root.is_symlink():
        raise GoogleTaxonomyIntegrityError("Taxonomy root symlink rejected")
    root = root.resolve()
    base = root / version / locale
    for directory in (root / version, base):
        if directory.is_symlink():
            raise GoogleTaxonomyIntegrityError("Taxonomy identity directory symlink rejected")
    return base


def publish_catalog(catalog, catalog_root):
    manifest = catalog.manifest
    fingerprint_text(manifest.fingerprint)
    base = safe_identity_directory(catalog_root, manifest.version, manifest.locale)
    destination = base / manifest.fingerprint
    expected = dict(version=manifest.version, locale=manifest.locale, fingerprint=manifest.fingerprint)
    staging = None
    try:
        base.mkdir(parents=True, exist_ok=True)
        if destination.exists() or destination.is_symlink():
            read_resource(destination, expected=expected)
            return destination
        staging = Path(tempfile.mkdtemp(prefix=".stage-", dir=base))
        (staging / "catalog.json").write_bytes(canonical(catalog_payload(catalog)))
        (staging / "manifest.json").write_bytes(canonical(asdict(manifest)))
        read_resource(staging, expected=expected)
        try:
            os.rename(staging, destination)
        except OSError:
            # Another publisher may have committed the identical immutable identity.
            if destination.exists():
                read_resource(destination, expected=expected)
            else:
                raise
        return destination
    except (OSError, ValueError, TypeError) as error:
        raise GoogleTaxonomyPublicationError("Google taxonomy publication failed") from error
    finally:
        if staging is not None and staging.exists():
            shutil.rmtree(staging)
