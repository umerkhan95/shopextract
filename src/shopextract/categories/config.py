"""Exact trusted category configuration and bounded canonical policy snapshots."""
from urllib.parse import urlsplit
from ._codec import wire, typed, canonical, digest
from .contracts import CategoryError, CategoryOptions, CategoryRuntimeConfig


def validate_options(options: CategoryOptions) -> None:
    try:
        if not isinstance(options, CategoryOptions):
            raise CategoryError('CategoryOptions required')
        encoded = wire(options)
        typed(CategoryOptions, encoded)
        limits = options.limits
        for name, maximum in [('terms',100),('relation_refs',200),('ancestry_depth',8),
                              ('record_bytes',262144),('rules',1000),('targets',1000),('config_bytes',262144)]:
            value = getattr(limits, name)
            if type(value) is not int or not 0 <= value <= maximum:
                raise CategoryError('Invalid category limit: ' + name)
        parts = urlsplit(options.scope.store_url)
        if parts.scheme not in ('http','https') or not parts.netloc or parts.username or parts.password:
            raise CategoryError('Invalid category store scope')
        for value in (options.scope.catalog, options.scope.channel, options.scope.locale):
            if value is not None and (not isinstance(value, str) or not value):
                raise CategoryError('Invalid optional category scope')
        registry = options.registry
        if not registry.namespace or not registry.version:
            raise CategoryError('Target namespace and version required')
        if len(registry.target_ids) > limits.targets or len(set(registry.target_ids)) != len(registry.target_ids):
            raise CategoryError('Invalid target registry size/duplicates')
        if any(not t for t in registry.target_ids) or len(options.rules) > limits.rules:
            raise CategoryError('Invalid category registry/rules')
        seen = set()
        for rule in options.rules:
            selector = rule.selector
            if not rule.rule_id or not rule.version or rule.rule_id in seen:
                raise CategoryError('Invalid or duplicate category rule identity')
            seen.add(rule.rule_id)
            if not selector.namespace or sum(v is not None for v in (selector.native_id,selector.raw_label,selector.raw_path)) != 1:
                raise CategoryError('Exactly one category selector representation required')
            if any(v == '' for v in (selector.native_id,selector.raw_label,selector.raw_path) if v is not None):
                raise CategoryError('Empty category selector')
            if selector.taxonomy_version is None and not selector.allow_unknown_version:
                raise CategoryError('Unknown taxonomy version must be explicitly allowed')
            if not rule.target_ids or len(set(rule.target_ids)) != len(rule.target_ids) or not set(rule.target_ids) <= set(registry.target_ids):
                raise CategoryError('Invalid mapping target')
        if len(canonical(encoded).encode()) > limits.config_bytes:
            raise CategoryError('Category config byte limit exceeded')
    except (ValueError, TypeError, AttributeError, RecursionError, OverflowError) as error:
        raise CategoryError(str(error)) from error


def runtime_record(config: CategoryRuntimeConfig) -> dict:
    validate_options(config.options)
    record = wire(config)
    typed(CategoryRuntimeConfig, record)
    ids = set(config.options.registry.target_ids)
    if len({t for t, _ in config.profile_bindings}) != len(config.profile_bindings):
        raise CategoryError('Duplicate category profile binding')
    if any(t not in ids or not p for t, p in config.profile_bindings):
        raise CategoryError('Invalid category profile binding')
    if len(canonical(record).encode()) > config.options.limits.config_bytes:
        raise CategoryError('Category runtime config exceeds byte limit')
    return record


def runtime_from_record(record: dict) -> CategoryRuntimeConfig:
    try:
        config = typed(CategoryRuntimeConfig, record)
        runtime_record(config)
        return config
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        raise CategoryError(str(error)) from error


def options_digest(options):
    validate_options(options)
    return digest(wire(options))
