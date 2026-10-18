"""Immutable metadata indexes and exact relation lookup; no I/O or mapping rules."""
from dataclasses import dataclass
from types import MappingProxyType

from .contracts import (AttributeExtension,AttributeRecord,CategoryAttributeBinding,CategoryRecord,
                        TaxonomyLookupError,ValueRecord)
from .identity import registry_version


def _alias(index,key,value):
    if key not in index:index[key]=value
    elif index[key]!=value:index[key]=False


def _lookup(index,key):
    if not isinstance(key,str):raise TypeError('Taxonomy ID must be text')
    if not key:raise TaxonomyLookupError('Taxonomy ID must be nonempty')
    value=index.get(key)
    if value is False:raise TaxonomyLookupError('Ambiguous taxonomy alias: '+key)
    return value


@dataclass(frozen=True)
class ShopifyTaxonomy:
    manifest: object
    _categories: object
    _attributes: object
    _values: object
    _category_aliases: object
    _attribute_aliases: object
    _value_aliases: object
    _extensions: object
    _bindings: object

    @property
    def version(self):return self.manifest.release
    @property
    def fingerprint(self):return self.manifest.fingerprint
    @property
    def registry_version(self):return registry_version(self.version,self.fingerprint)
    def category(self,key):return _lookup(self._category_aliases,key)
    def attribute(self,key):return _lookup(self._attribute_aliases,key)
    def value(self,key):return _lookup(self._value_aliases,key)
    def iter_categories(self):return iter(self._categories.values())
    def iter_attributes(self,*,include_extensions=True):
        yield from self._attributes.values()
        if include_extensions:yield from self._extensions.values()
    def iter_values(self):return iter(self._values.values())
    def _required_category(self,key):
        category=self.category(key)
        if category is None:raise TaxonomyLookupError('Unknown category: '+key)
        return category
    def attributes_for(self,key):return self._bindings[self._required_category(key).id]
    def values_for(self,key):
        attribute=self.attribute(key)
        if attribute is None:raise TaxonomyLookupError('Unknown attribute: '+key)
        return tuple(self._values[native] for native in attribute.value_ids)
    def extensions_for(self,key):
        attribute=self.attribute(key)
        if attribute is None:raise TaxonomyLookupError('Unknown attribute: '+key)
        native=attribute.base_attribute_id if isinstance(attribute,AttributeExtension) else attribute.id
        return tuple(e for e in self._extensions.values() if e.base_attribute_id==native)
    def ancestors(self,key):
        category=self._required_category(key)
        return tuple(self._categories[native] for native in reversed(category.source_ancestor_ids))
    def schema_for(self,value):
        from .schema import schema_for
        return schema_for(self,value)


def catalog_from_data(data,manifest):
    categories={};attributes={};values={};extensions={};bindings={}
    ca={};aa={};va={}
    for item in data['values']:
        record=ValueRecord(**item);values[record.id]=record
        for alias in (record.id,record.id.rsplit('/',1)[-1],record.handle):_alias(va,alias,record)
    for item in data['attributes']:
        record=AttributeRecord(**{**item,'value_ids':tuple(item['value_ids']),'extension_handles':tuple(item['extension_handles'])})
        attributes[record.id]=record
        for alias in (record.id,record.id.rsplit('/',1)[-1],record.handle,record.friendly_id):_alias(aa,alias,record)
    for item in data['extensions']:
        record=AttributeExtension(**item,value_ids=attributes[item['base_attribute_id']].value_ids)
        extensions[record.handle]=record
        for alias in (record.handle,record.friendly_id):_alias(aa,alias,record)
    for item in data['categories']:
        record=CategoryRecord(**{k:tuple(v) if isinstance(v,list) else v for k,v in item.items() if k!='binding_refs'})
        categories[record.id]=record
        for alias in (record.id,record.short_id):_alias(ca,alias,record)
        declared=[]
        for native,handle in item['binding_refs']:
            source=extensions[handle] if handle else attributes[native]
            declared.append(CategoryAttributeBinding(record.id,native,source.handle,source.name,source.description,
                handle is not None,handle,source.value_ids))
        bindings[record.id]=tuple(declared)
    return ShopifyTaxonomy(manifest,*(MappingProxyType(x) for x in (categories,attributes,values,ca,aa,va,extensions,bindings)))
