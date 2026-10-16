"""Explicit opt-in category API; legacy top-level APIs remain unchanged."""
from .api import extract_with_categories, normalize_with_categories, validate_options
from .contracts import (
    AdapterContext, CategorizedExtractionResult, CategorizedProduct, CategoryError,
    CategoryFact, CategoryFactBinding, CategoryLimits, CategoryObservation, CategoryOptions,
    CategoryRuntimeConfig, CategoryPolicySnapshot, CategoryScope, CategorySelector, CategoryTerm,
    CategoryTermRef, MappingDecision, MappingRule, NativeCategoryError, TargetRegistry,
)
from .mapping import map_categories
from .portable import categorized_product_from_record, categorized_product_to_record
