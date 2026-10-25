"""Immutable Shopify metadata and source/build contracts; no data loading."""
from dataclasses import dataclass
from pathlib import Path


class TaxonomyError(ValueError):
    """Invalid catalog operation."""


class TaxonomyLookupError(TaxonomyError):
    """Missing, ambiguous or unsupported catalog lookup."""


class TaxonomyIntegrityError(TaxonomyError):
    """Source or catalog integrity failed."""


class TaxonomyPublicationError(TaxonomyError):
    """Prepared catalog could not be published."""


@dataclass(frozen=True)
class TaxonomyCounts:
    categories: int
    base_attributes: int
    extensions: int
    values: int
    context_links: int
    parent_links: int
    ancestor_links: int
    return_reason_links: int


@dataclass(frozen=True)
class TaxonomyManifest:
    schema_version: int
    namespace: str
    release: str
    commit: str
    fingerprint: str
    source_hashes: tuple[tuple[str,str],...]
    counts: TaxonomyCounts


@dataclass(frozen=True)
class CategoryRecord:
    id: str
    short_id: str
    name: str
    full_name: str
    level: int
    parent_id: str | None
    child_ids: tuple[str,...]
    source_ancestor_ids: tuple[str,...]
    return_reason_ids: tuple[str,...]


@dataclass(frozen=True)
class AttributeRecord:
    id: str
    handle: str
    friendly_id: str
    name: str
    description: str
    value_ids: tuple[str,...]
    extension_handles: tuple[str,...]


@dataclass(frozen=True)
class ValueRecord:
    id: str
    handle: str
    name: str


@dataclass(frozen=True)
class AttributeExtension:
    handle: str
    friendly_id: str
    name: str
    description: str
    values_from: str
    base_attribute_id: str
    value_ids: tuple[str,...]


@dataclass(frozen=True)
class CategoryAttributeBinding:
    category_id: str
    base_attribute_id: str
    handle: str
    name: str
    description: str
    extended: bool
    extension_handle: str | None
    value_ids: tuple[str,...]


@dataclass(frozen=True)
class CategorySchema:
    category: CategoryRecord
    attributes: tuple[CategoryAttributeBinding,...]


@dataclass(frozen=True)
class ShopifyReleaseSource:
    version: str
    commit: str
    taxonomy_sha256: str
    extensions_sha256: str
    license_sha256: str


@dataclass(frozen=True)
class DownloadedRelease:
    source: ShopifyReleaseSource
    taxonomy_path: Path
    extensions_path: Path
    license_path: Path


@dataclass(frozen=True)
class StagedTaxonomy:
    path: Path
    manifest: TaxonomyManifest


@dataclass(frozen=True)
class ProductTaxonomySchema:
    catalog_identity: str
    resolved: tuple[CategorySchema,...]
    unresolved: tuple[object,...]
