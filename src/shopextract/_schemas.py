"""Bounded immutable type metadata for the two existing strict transport codecs."""
from dataclasses import is_dataclass
from functools import lru_cache
from types import MappingProxyType
from typing import get_type_hints


@lru_cache(maxsize=128)
def _static_hints(kind):
    return MappingProxyType(get_type_hints(kind))


def schema_hints(kind):
    # Values are always validated recursively by the caller. External/dynamic
    # classes are not retained in the application schema cache.
    if is_dataclass(kind) and kind.__module__.startswith('shopextract.'):
        return _static_hints(kind)
    return MappingProxyType(get_type_hints(kind))


schema_hints.cache_info=_static_hints.cache_info
schema_hints.cache_clear=_static_hints.cache_clear
