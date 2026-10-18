"""Atomic publication of fully verified explicit catalog artifacts."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import shutil
import tempfile

from .contracts import TaxonomyPublicationError
from .identity import canonical
from .resource import read_gzip,verify_resource_files,validate_manifest_identity
from .validation import validate_resource_data


def _verified(directory,expected):
    record=verify_resource_files(directory,expected=expected)
    validate_resource_data(json.loads(read_gzip(Path(directory)/'catalog.json.gz')),record)
    return record


def publish_shopify_taxonomy(staged, *, catalog_root):
    # Complete identity AND logical content are checked before creating any path.
    try:
        identity=json.loads(canonical(asdict(staged.manifest)))
        validate_manifest_identity(identity)
        expected=_verified(staged.path,identity)
    except (ValueError,TypeError,KeyError,OSError) as error:
        raise TaxonomyPublicationError('Invalid staged catalog: '+str(error)) from error
    release=Path(catalog_root)/identity['release']
    release.mkdir(parents=True,exist_ok=True)
    destination=release/identity['fingerprint']
    lock=release/('.'+identity['fingerprint']+'.lock')
    try:
        descriptor=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError as error:
        raise TaxonomyPublicationError('Catalog publication already reserved') from error
    temporary=None
    try:
        os.close(descriptor)
        if destination.exists():
            _verified(destination,expected)
            return staged.manifest
        temporary=Path(tempfile.mkdtemp(prefix='.publishing-',dir=release))
        for name in ('catalog.json.gz','LICENSE','manifest.json'):
            with (temporary/name).open('wb') as handle:
                handle.write((staged.path/name).read_bytes());handle.flush();os.fsync(handle.fileno())
        # Staging may have changed during copy: bytes, complete metadata AND
        # normalized logical identity must still match the pre-reservation proof.
        _verified(temporary,expected)
        os.rename(temporary,destination)
        temporary=None
        directory=os.open(release,os.O_RDONLY)
        try:os.fsync(directory)
        finally:os.close(directory)
        return staged.manifest
    except (ValueError,TypeError,KeyError,OSError) as error:
        raise TaxonomyPublicationError('Catalog publication failed: '+str(error)) from error
    finally:
        if temporary is not None:shutil.rmtree(temporary,ignore_errors=True)
        lock.unlink(missing_ok=True)
