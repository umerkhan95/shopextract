"""Offline pinned resource discovery and immutable process-local catalog cache."""
from importlib.resources import files
import json
from pathlib import Path
from threading import RLock

from .catalog import catalog_from_data
from .contracts import TaxonomyIntegrityError,TaxonomyLookupError,TaxonomyManifest
from .resource import read_gzip,verify_resource_files
from .validation import validate_resource_data

_CACHE={}
_LOCK=RLock()


def load_shopify_taxonomy(version='2026-08', *, catalog_root=None, fingerprint=None):
    if not isinstance(version,str) or (fingerprint is not None and not isinstance(fingerprint,str)):
        raise TypeError('Catalog version/fingerprint must be text')
    if not version or '/' in version or '\\' in version or version in ('.','..'):
        raise TaxonomyLookupError('Unsupported release identifier')
    if fingerprint is not None and (len(fingerprint)!=64 or any(c not in '0123456789abcdef' for c in fingerprint)):
        raise TaxonomyLookupError('Invalid content fingerprint')
    expected={'release':version}
    if fingerprint is not None:expected['fingerprint']=fingerprint
    if catalog_root is None:
        directory=Path(str(files('shopextract.taxonomies.shopify').joinpath('data')))
        if not (directory/'manifest.json').is_file():
            raise TaxonomyLookupError('Pinned taxonomy resource unavailable; prepare source build or install published package')
    else:
        release=Path(catalog_root)/version
        if fingerprint is None:
            candidates=[p for p in release.glob('*/manifest.json') if not p.parent.name.startswith('.')]
            if len(candidates)!=1:raise TaxonomyLookupError('Catalog release missing or ambiguous; supply exact fingerprint')
            directory=candidates[0].parent
        else:directory=release/fingerprint
        if not (directory/'manifest.json').is_file():raise TaxonomyLookupError('Unknown pinned catalog identity')
    try:
        # Recheck byte integrity even on cache hits; cached objects never bless a changed file.
        record=verify_resource_files(directory,expected=expected)
        key=(str(directory.resolve()),record['fingerprint'])
        with _LOCK:
            if key in _CACHE:return _CACHE[key]
            data=json.loads(read_gzip(directory/'catalog.json.gz'))
            counts=validate_resource_data(data,record)
            manifest=TaxonomyManifest(record['schema_version'],record['namespace'],record['release'],record['commit'],
                record['fingerprint'],tuple(tuple(pair) for pair in record['source_hashes']),counts)
            catalog=catalog_from_data(data,manifest)
            _CACHE[key]=catalog
            return catalog
    except (ValueError,KeyError,TypeError,OSError) as error:
        if isinstance(error,TaxonomyIntegrityError):raise
        raise TaxonomyIntegrityError(str(error)) from error
