"""Whole normalized catalog integrity; no lookup, network or filesystem mutation."""
from .contracts import TaxonomyIntegrityError,TaxonomyCounts
from .identity import NAMESPACE,fingerprint
from .resource import safe_release,hex_digest,validate_source_hashes



def _record(value,fields):
    if type(value) is not dict or set(value)!=set(fields.split()):
        raise TaxonomyIntegrityError('Invalid normalized record fields')


def _text(value, *, nonempty=True):
    if type(value) is not str or (nonempty and not value):
        raise TaxonomyIntegrityError('Normalized metadata must be immutable text')


def _gid(value,kind):
    _text(value)
    prefix='gid://shopify/'+kind+'/'
    suffix=value[len(prefix):]
    if not value.startswith(prefix) or not suffix or any(c.isspace() or c in '/?#' for c in suffix):
        raise TaxonomyIntegrityError('Invalid '+kind+' ID suffix')


def _strings(value,kind=None):
    if type(value) is not list:raise TaxonomyIntegrityError('Normalized string sequence required')
    for item in value:
        if kind:_gid(item,kind)
        else:_text(item)


def _record_types(data):
    for name in ('categories','attributes','extensions','values','return_reasons'):
        if type(data[name]) is not list:raise TaxonomyIntegrityError('Normalized record array required')
    for item in data['categories']:
        _record(item,'id short_id name full_name level parent_id child_ids source_ancestor_ids return_reason_ids binding_refs')
        _gid(item['id'],'TaxonomyCategory')
        for key in ('short_id','name','full_name'):_text(item[key])
        if item['short_id']!=item['id'].rsplit('/',1)[-1]:raise TaxonomyIntegrityError('Category short-ID alias mismatch')
        if type(item['level']) is not int or item['level']<0:raise TaxonomyIntegrityError('Invalid category level type')
        if item['parent_id'] is not None:_gid(item['parent_id'],'TaxonomyCategory')
        _strings(item['child_ids'],'TaxonomyCategory');_strings(item['source_ancestor_ids'],'TaxonomyCategory')
        _strings(item['return_reason_ids'],'ReturnReasonDefinition')
        if type(item['binding_refs']) is not list:raise TaxonomyIntegrityError('Context binding array required')
        for pair in item['binding_refs']:
            if type(pair) is not list or len(pair)!=2:raise TaxonomyIntegrityError('Context binding pair required')
            _gid(pair[0],'TaxonomyAttribute')
            if pair[1] is not None:_text(pair[1])
    for item in data['attributes']:
        _record(item,'id handle friendly_id name description value_ids extension_handles')
        _gid(item['id'],'TaxonomyAttribute')
        for key in ('handle','friendly_id','name'):_text(item[key])
        _text(item['description'],nonempty=False)
        _strings(item['value_ids'],'TaxonomyValue');_strings(item['extension_handles'])
    for item in data['extensions']:
        _record(item,'handle friendly_id name description values_from base_attribute_id')
        for key in ('handle','friendly_id','name','values_from'):_text(item[key])
        _text(item['description'],nonempty=False);_gid(item['base_attribute_id'],'TaxonomyAttribute')
    for item in data['values']:
        _record(item,'id handle name');_gid(item['id'],'TaxonomyValue')
        _text(item['handle']);_text(item['name'])
    for item in data['return_reasons']:
        _record(item,'id name handle description');_gid(item['id'],'ReturnReasonDefinition')
        _text(item['name']);_text(item['handle']);_text(item['description'],nonempty=False)

def _index(records,kind):
    result={}
    for record in records:
        native=record['id']
        if not isinstance(native,str) or not native.startswith('gid://shopify/'+kind+'/') or native in result:
            raise TaxonomyIntegrityError('Duplicate or invalid '+kind+' ID')
        result[native]=record
    return result


def validate_catalog(data):
    try:
        required={'schema_version','namespace','release','commit','source_hashes','categories','attributes','extensions','values','return_reasons'}
        if type(data) is not dict or set(data)!=required or type(data['schema_version']) is not int or data['schema_version']!=1 or data['namespace']!=NAMESPACE:
            raise TaxonomyIntegrityError('Invalid normalized catalog schema')
        safe_release(data['release']);hex_digest(data['commit'],length=40);validate_source_hashes(data['source_hashes'])
        _record_types(data)
        categories=_index(data['categories'],'TaxonomyCategory')
        attributes=_index(data['attributes'],'TaxonomyAttribute')
        values=_index(data['values'],'TaxonomyValue')
        reasons=_index(data['return_reasons'],'ReturnReasonDefinition') if data['return_reasons'] else {}
        extensions={}
        for extension in data['extensions']:
            handle=extension['handle']
            base=attributes.get(extension['base_attribute_id'])
            if handle in extensions or base is None or extension['values_from']!=base['friendly_id']:
                raise TaxonomyIntegrityError('Invalid extended attribute lineage')
            extensions[handle]=extension
        extensions_by_base={}
        for handle,extension in extensions.items():
            extensions_by_base.setdefault(extension['base_attribute_id'],set()).add(handle)
        children_by_parent={}
        for category in categories.values():
            children_by_parent.setdefault(category['parent_id'],set()).add(category['id'])
        for attribute in attributes.values():
            if len(set(attribute['value_ids']))!=len(attribute['value_ids']) or not set(attribute['value_ids'])<=values.keys():
                raise TaxonomyIntegrityError('Invalid attribute value reference')
            if set(attribute['extension_handles'])!=extensions_by_base.get(attribute['id'],set()):
                raise TaxonomyIntegrityError('Incomplete attribute extension references')
        links=parents=ancestors=reason_links=0
        for category in categories.values():
            expected=[];seen={category['id']};cursor=category['parent_id']
            while cursor is not None:
                if cursor not in categories or cursor in seen:
                    raise TaxonomyIntegrityError('Missing parent or cyclic category ancestry')
                seen.add(cursor);expected.append(cursor);cursor=categories[cursor]['parent_id']
            if category['source_ancestor_ids']!=expected or category['level']!=len(expected):
                raise TaxonomyIntegrityError('Category ancestor/level mismatch')
            expected_children=children_by_parent.get(category['id'],set())
            if len(set(category['child_ids']))!=len(category['child_ids']) or set(category['child_ids'])!=expected_children:
                raise TaxonomyIntegrityError('Category child reference mismatch')
            if not set(category['return_reason_ids'])<=reasons.keys():
                raise TaxonomyIntegrityError('Category return-reason reference missing')
            for native,extension_handle in category['binding_refs']:
                if native not in attributes or (extension_handle is not None and
                    (extension_handle not in extensions or extensions[extension_handle]['base_attribute_id']!=native)):
                    raise TaxonomyIntegrityError('Category contextual attribute reference missing')
            links+=len(category['binding_refs']);parents+=category['parent_id'] is not None
            ancestors+=len(expected);reason_links+=len(category['return_reason_ids'])
        return TaxonomyCounts(len(categories),len(attributes),len(extensions),len(values),links,parents,ancestors,reason_links)
    except (KeyError,TypeError,ValueError) as error:
        if isinstance(error,TaxonomyIntegrityError):raise
        raise TaxonomyIntegrityError('Malformed catalog: '+str(error)) from error


def validate_resource_data(data,manifest):
    """One logical/structural check shared by loader and atomic publisher."""
    counts=validate_catalog(data)
    if fingerprint(data)!=manifest['fingerprint']:
        raise TaxonomyIntegrityError('Catalog logical fingerprint mismatch')
    if counts!=TaxonomyCounts(**manifest['counts']):
        raise TaxonomyIntegrityError('Catalog count mismatch')
    if any(data[field]!=manifest[field] for field in ('schema_version','namespace','release','commit','source_hashes')):
        raise TaxonomyIntegrityError('Catalog manifest identity mismatch')
    return counts
