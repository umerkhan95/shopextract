"""Finite immutable schema cache never caches validation outcomes."""
import pytest
from shopextract.categories._codec import typed,wire
from shopextract.categories.contracts import CategoryLimits


def test_static_schema_cache_is_bounded_and_read_only():
    from shopextract._schemas import schema_hints
    schema_hints.cache_clear()
    first=schema_hints(CategoryLimits);second=schema_hints(CategoryLimits)
    assert first is second and schema_hints.cache_info().maxsize==128
    with pytest.raises(TypeError):first['terms']=str
    assert schema_hints.cache_info().hits>=1


def test_repeated_validation_rejects_value_mutation():
    value=wire(CategoryLimits())
    assert typed(CategoryLimits,value).terms==100
    value['terms']=True
    with pytest.raises(ValueError):typed(CategoryLimits,value)
    value['terms']=100;value['extra']='x'
    with pytest.raises(ValueError):typed(CategoryLimits,value)
