"""Explicit offline release normalization; optional YAML dependency stays here."""
from dataclasses import asdict
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from .contracts import TaxonomyIntegrityError,TaxonomyManifest,StagedTaxonomy
from .identity import NAMESPACE,canonical,fingerprint
from .resource import read_gzip,verify_resource_files
from .validation import validate_catalog


def _hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _unique(records,key,kind):
    result={}
    for record in records:
        native=record[key]
        if native in result:
            raise TaxonomyIntegrityError('Duplicate '+kind)
        result[native]=record
    return result


def build_shopify_taxonomy(download, *, staging_root):
    """Generate one complete deterministic resource from verified explicit sources."""
    try:
        import yaml
    except ImportError as error:
        raise TaxonomyIntegrityError('Source preparation requires the taxonomy-build extra (PyYAML)') from error
    source=download.source
    paths=[download.taxonomy_path,download.extensions_path,download.license_path]
    hashes=(source.taxonomy_sha256,source.extensions_sha256,source.license_sha256)
    if any(_hash(path)!=expected for path,expected in zip(paths,hashes)):
        raise TaxonomyIntegrityError('Pinned source hash mismatch')
    if Path(download.extensions_path).stat().st_size>8*1024*1024 or Path(download.license_path).stat().st_size>8192:
        raise TaxonomyIntegrityError('Supplemental source byte cap exceeded')
    yaml_data=yaml.safe_load(Path(download.extensions_path).read_text())
    # Keep only alias/ID metadata before loading the large full JSON source.
    bases=_unique([{'id':a['id'],'friendly_id':a['friendly_id']} for a in yaml_data['base_attributes']],
                  'friendly_id','base attribute friendly ID')
    base_by_gid={f'gid://shopify/TaxonomyAttribute/{a["id"]}':a for a in bases.values()}
    extensions=[]
    extension_map={}
    for item in yaml_data['extended_attributes']:
        base=bases.get(item['values_from'])
        if base is None:
            raise TaxonomyIntegrityError('Extended values_from must resolve to a canonical base')
        extension={**item,'base_attribute_id':f'gid://shopify/TaxonomyAttribute/{base["id"]}'}
        if item['handle'] in extension_map:
            raise TaxonomyIntegrityError('Duplicate extension handle')
        extensions.append(extension);extension_map[item['handle']]=extension
    del yaml_data
    raw=json.loads(read_gzip(download.taxonomy_path))
    if raw.get('version')!=source.version:
        raise TaxonomyIntegrityError('Source release version mismatch')
    attributes=[];values={};canonical_attributes={}
    for item in raw['attributes']:
        if item['id'] not in base_by_gid:
            raise TaxonomyIntegrityError('Missing source base definition')
        base=base_by_gid[item['id']]
        handles=[e['handle'] for e in item['extended_attributes']]
        attribute={k:item[k] for k in ('id','handle','name','description')}
        attribute.update(friendly_id=base['friendly_id'],value_ids=[v['id'] for v in item['values']],extension_handles=handles)
        if attribute['id'] in canonical_attributes:
            raise TaxonomyIntegrityError('Duplicate canonical attribute ID')
        canonical_attributes[attribute['id']]=attribute;attributes.append(attribute)
        for value in item['values']:
            if value['id'] in values:
                raise TaxonomyIntegrityError('Duplicate value ID')
            values[value['id']]=value
    if set(base_by_gid)!=set(canonical_attributes):
        raise TaxonomyIntegrityError('Full canonical attribute set differs from pinned YAML')
    categories=[];return_reasons={}
    for vertical in raw['verticals']:
        for item in vertical['categories']:
            refs=[]
            for embedded in item['attributes']:
                base=canonical_attributes.get(embedded['id'])
                extension_handle=embedded['handle'] if embedded['extended'] else None
                definition=extension_map.get(extension_handle) if extension_handle else base
                if definition is None or (extension_handle and definition['base_attribute_id']!=embedded['id']):
                    raise TaxonomyIntegrityError('Unknown contextual attribute definition')
                if any(embedded[k]!=definition[k] for k in ('handle','name','description')):
                    raise TaxonomyIntegrityError('Context attribute override differs from pinned definition')
                refs.append([embedded['id'],extension_handle])
            category={k:item[k] for k in ('id','name','full_name','level','parent_id')}
            category.update(short_id=item['id'].rsplit('/',1)[-1],child_ids=[c['id'] for c in item['children']],
                source_ancestor_ids=[a['id'] for a in item['ancestors']],return_reason_ids=[r['id'] for r in item['return_reasons']],binding_refs=refs)
            categories.append(category)
            for reason in item['return_reasons']:
                if reason['id'] in return_reasons and return_reasons[reason['id']]!=reason:
                    raise TaxonomyIntegrityError('Competing return-reason definitions')
                return_reasons[reason['id']]=reason
    data=dict(schema_version=1,namespace=NAMESPACE,release=source.version,commit=source.commit,
        source_hashes=list(zip(('taxonomy.en.json.gz','attributes.yml','LICENSE'),hashes)),
        categories=sorted(categories,key=lambda c:c['id']),attributes=sorted(attributes,key=lambda a:a['id']),
        extensions=sorted(extensions,key=lambda e:e['handle']),values=sorted(values.values(),key=lambda v:v['id']),
        return_reasons=sorted(return_reasons.values(),key=lambda r:r['id']))
    del raw
    counts=validate_catalog(data)
    content=fingerprint(data)
    manifest=TaxonomyManifest(1,NAMESPACE,source.version,source.commit,content,
        tuple(tuple(pair) for pair in data['source_hashes']),counts)
    staging_root=Path(staging_root);staging_root.mkdir(parents=True,exist_ok=True)
    directory=Path(tempfile.mkdtemp(prefix='staged-',dir=staging_root))
    try:
        with (directory/'catalog.json.gz').open('wb') as output:
            with gzip.GzipFile(fileobj=output,mode='wb',mtime=0,filename='') as compressor:
                compressor.write(canonical(data))
        shutil.copyfile(download.license_path,directory/'LICENSE')
        record=asdict(manifest)
        record.update(resource_sha256=_hash(directory/'catalog.json.gz'),license_sha256=source.license_sha256)
        (directory/'manifest.json').write_bytes(canonical(record))
        verify_resource_files(directory)
    except BaseException:
        shutil.rmtree(directory,ignore_errors=True)
        raise
    return StagedTaxonomy(directory,manifest)
