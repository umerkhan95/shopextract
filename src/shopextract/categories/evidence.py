"""Thin native-facet adapter over the ordinary capture and Normalizer primitives."""
from dataclasses import replace
from typing import Callable
from .._normalization import Normalizer
from .._capture import _support_outcome
from .contracts import CategoryFact, CategoryFactBinding


def source_fact(raw: dict, pointer: str, *, binding: CategoryFactBinding,
                convert: Callable | None = None, operation: str = '') -> CategoryFact:
    trace = Normalizer(raw)
    value = trace.emit('category_fact', pointer, convert=convert, operation=operation)
    outcome = trace.outcomes['/category_fact']
    state, evidence, reason, transforms, _, _ = _support_outcome(raw, outcome, normalized_value=value)
    outcome = replace(outcome, transformations=list(transforms))
    selected = trace.select(pointer)
    return CategoryFact(pointer, selected.value, state, binding, outcome, evidence, reason)
