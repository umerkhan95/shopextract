"""G2 declarations only: captured source facts are separate from mapping decisions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .._evidence import Evidence, SupportState
from .._models import ExtractionResult, Platform, Product
from .._normalization import ConversionOutcome


class CategoryError(ValueError):
    """Invalid category configuration, source contract or portable envelope."""


@dataclass(frozen=True)
class CategoryScope:
    platform: Platform
    store_url: str
    catalog: str | None = None
    channel: str | None = None
    locale: str | None = None


@dataclass(frozen=True)
class CategoryLimits:
    terms: int = 100
    relation_refs: int = 200
    ancestry_depth: int = 8
    record_bytes: int = 256 * 1024
    rules: int = 1000
    targets: int = 1000
    config_bytes: int = 256 * 1024


@dataclass(frozen=True)
class CategoryTermRef:
    namespace: str
    taxonomy_version: str | None
    native_id: str | None
    merchant_scope: str | None


@dataclass(frozen=True)
class CategoryFactBinding:
    facet: Literal['native_id', 'label', 'code_context', 'raw_path', 'parent_id',
                   'child_id', 'source_state', 'completion']
    term: CategoryTermRef | None = None
    edge: tuple[CategoryTermRef, CategoryTermRef] | None = None


@dataclass(frozen=True)
class CategoryFact:
    pointer: str
    raw_value: object
    support: SupportState
    binding: CategoryFactBinding
    outcome: ConversionOutcome
    evidence: tuple[Evidence, ...] = ()
    reason: str = ''


@dataclass(frozen=True)
class CategoryTerm:
    ref: CategoryTermRef
    label: str | None
    facts: tuple[CategoryFact, ...]


@dataclass(frozen=True)
class CategoryObservation:
    observation_id: str
    scope: CategoryScope
    relation: Literal['label', 'memberships', 'ordered_path', 'parent_edges', 'index']
    taxonomy_kind: Literal['merchant', 'custom_type', 'standard', 'merchandising', 'structured_code']
    source_state: Literal['missing', 'null', 'empty', 'present', 'malformed']
    completeness: Literal['complete', 'partial', 'unknown']
    terms: tuple[CategoryTerm, ...] = ()
    parent_edges: tuple[tuple[CategoryTermRef, CategoryTermRef], ...] = ()
    facts: tuple[CategoryFact, ...] = ()
    reason: str = ''


@dataclass(frozen=True)
class CategorySelector:
    namespace: str
    taxonomy_version: str | None
    scope: CategoryScope | None = None
    native_id: str | None = None
    raw_label: str | None = None
    raw_path: str | None = None
    allow_unknown_version: bool = False


@dataclass(frozen=True)
class MappingRule:
    rule_id: str
    version: str
    selector: CategorySelector
    target_ids: tuple[str, ...]


@dataclass(frozen=True)
class TargetRegistry:
    namespace: str
    version: str
    target_ids: tuple[str, ...]


@dataclass(frozen=True)
class CategoryOptions:
    scope: CategoryScope
    registry: TargetRegistry
    rules: tuple[MappingRule, ...] = ()
    limits: CategoryLimits = CategoryLimits()


@dataclass(frozen=True)
class MappingDecision:
    observation_id: str
    term: CategoryTermRef | None
    status: Literal['mapped', 'unmapped', 'unavailable', 'ambiguous']
    target_ids: tuple[str, ...]
    target_namespace: str
    target_version: str
    rule_versions: tuple[tuple[str, str], ...]
    partial: bool
    source_pointers: tuple[str, ...] = ()
    reason: str = ''


@dataclass(frozen=True)
class CategorizedProduct:
    product: Product
    scope: CategoryScope
    observations: tuple[CategoryObservation, ...]
    mappings: tuple[MappingDecision, ...]
    config_digest: str
    original_binding: str
    schema_version: int = 1


@dataclass(frozen=True)
class CategorizedExtractionResult:
    result: ExtractionResult
    products: tuple[CategorizedProduct, ...]
    diagnostics: tuple[str, ...] = ()


@dataclass(frozen=True)
class NativeCategoryError:
    path: tuple[str | int, ...] | None
    code: str


@dataclass(frozen=True)
class AdapterContext:
    scope: CategoryScope
    limits: CategoryLimits = CategoryLimits()
    native_errors: tuple[NativeCategoryError, ...] = ()


@dataclass(frozen=True)
class CategoryRuntimeConfig:
    options: CategoryOptions
    profile_bindings: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class CategoryPolicySnapshot:
    mode: Literal['legacy', 'enabled']
    schema_version: int = 1
    config_json: str | None = None
    config_digest: str | None = None
