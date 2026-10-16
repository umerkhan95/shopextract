"""Creation-time category policy identity and conservative profile review."""
from ._codec import digest
from .config import runtime_record, options_digest
from .contracts import CategoryError, CategorizedProduct, CategoryRuntimeConfig
from .portable import categorized_product_to_record


def category_policy_digest(config: CategoryRuntimeConfig) -> str:
    return digest({'schema_version':1,'config':runtime_record(config)})


def category_review_reasons(value: CategorizedProduct, *, selected_profile: str | None,
                            config: CategoryRuntimeConfig) -> tuple[str, ...]:
    categorized_product_to_record(value)
    if value.config_digest != options_digest(config.options):
        raise CategoryError('Category review policy differs from source companion')
    reasons = []
    if selected_profile is None:
        reasons.append('category_profile_missing')
    assignments = [d for d in value.mappings if d.term is not None]
    if not assignments:
        reasons.append('category_unavailable')
    bindings = dict(config.profile_bindings)
    for decision in assignments:
        if decision.status != 'mapped':
            reasons.append('category_' + decision.status)
        if decision.partial:
            reasons.append('category_incomplete')
        for target in decision.target_ids:
            if target not in bindings:
                reasons.append('profile_binding_missing')
            elif selected_profile is not None and bindings[target] != selected_profile:
                reasons.append('category_profile_conflict')
    return tuple(sorted(set(reasons)))
