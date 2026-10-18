"""Standalone stdlib-only prepared-resource verification, shared by loader/build hook."""
import gzip
import hashlib
import json
import re
from pathlib import Path

COMPRESSED_LIMIT = 8*1024*1024
DECODED_LIMIT = 128*1024*1024


class ResourceIntegrityError(ValueError):
    pass


COUNT_FIELDS={'categories','base_attributes','extensions','values','context_links','parent_links','ancestor_links','return_reason_links'}
IDENTITY_FIELDS={'schema_version','namespace','release','commit','fingerprint','source_hashes','counts'}


def safe_release(value):
    if not isinstance(value,str) or re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,63}',value) is None:
        raise ResourceIntegrityError('Unsafe catalog release component')


def hex_digest(value, *, length=64):
    if not isinstance(value,str) or re.fullmatch('[0-9a-f]{'+str(length)+'}',value) is None:
        raise ResourceIntegrityError('Invalid catalog hexadecimal identity')


def validate_source_hashes(value):
    if not isinstance(value,(list,tuple)) or len(value)!=3:
        raise ResourceIntegrityError('Invalid source hash references')
    names=[]
    for pair in value:
        if not isinstance(pair,(list,tuple)) or len(pair)!=2 or not isinstance(pair[0],str):
            raise ResourceIntegrityError('Invalid source hash pair')
        names.append(pair[0]);hex_digest(pair[1])
    if set(names)!={'taxonomy.en.json.gz','attributes.yml','LICENSE'} or len(set(names))!=3:
        raise ResourceIntegrityError('Incomplete source hash identities')


def validate_manifest_identity(manifest):
    if not isinstance(manifest,dict) or set(manifest)!=IDENTITY_FIELDS:
        raise ResourceIntegrityError('Invalid staged manifest identity fields')
    if type(manifest['schema_version']) is not int or manifest['schema_version']!=1:
        raise ResourceIntegrityError('Invalid manifest version type')
    if not isinstance(manifest['namespace'],str) or not manifest['namespace']:
        raise ResourceIntegrityError('Invalid manifest namespace')
    safe_release(manifest['release']);hex_digest(manifest['fingerprint']);hex_digest(manifest['commit'],length=40)
    validate_source_hashes(manifest['source_hashes'])
    counts=manifest['counts']
    if not isinstance(counts,dict) or set(counts)!=COUNT_FIELDS or any(type(v) is not int or v<0 for v in counts.values()):
        raise ResourceIntegrityError('Invalid catalog counts')


def read_gzip(path, *, compressed_limit=COMPRESSED_LIMIT, decoded_limit=DECODED_LIMIT):
    path=Path(path)
    if path.stat().st_size > compressed_limit:
        raise ResourceIntegrityError('Compressed catalog byte cap exceeded')
    with gzip.open(path,'rb') as handle:
        data=handle.read(decoded_limit+1)
    if len(data)>decoded_limit:
        raise ResourceIntegrityError('Decoded catalog byte cap exceeded')
    return data


def verify_resource_files(directory, *, expected=None):
    directory=Path(directory)
    manifest_path=directory/'manifest.json'
    if manifest_path.stat().st_size>65536:
        raise ResourceIntegrityError('Manifest byte cap exceeded')
    manifest=json.loads(manifest_path.read_text())
    required={'schema_version','namespace','release','commit','fingerprint','source_hashes','counts','resource_sha256','license_sha256'}
    if not isinstance(manifest,dict) or set(manifest)!=required:
        raise ResourceIntegrityError('Invalid catalog manifest schema')
    validate_manifest_identity({key:manifest[key] for key in IDENTITY_FIELDS})
    hex_digest(manifest['resource_sha256']);hex_digest(manifest['license_sha256'])
    if expected is not None:
        for key,value in expected.items():
            if manifest.get(key)!=value:
                raise ResourceIntegrityError('Catalog differs from pinned '+key)
    for name,key,limit in [('catalog.json.gz','resource_sha256',COMPRESSED_LIMIT),('LICENSE','license_sha256',8192)]:
        path=directory/name
        if path.stat().st_size>limit or hashlib.sha256(path.read_bytes()).hexdigest()!=manifest[key]:
            raise ResourceIntegrityError('Catalog resource hash/size mismatch: '+name)
    return manifest
