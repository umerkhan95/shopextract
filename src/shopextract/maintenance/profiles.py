"""Finite declarative category profiles; comparison does not authorize identity."""
from dataclasses import dataclass
from typing import Literal, Mapping


@dataclass(frozen=True)
class FieldRule:
    kind: Literal['text', 'decimal', 'mass']
    role: Literal['comparable', 'identity_variant', 'price_context']
    normalization: str = 'exact'


@dataclass(frozen=True)
class CategoryProfile:
    name: str
    fields: Mapping[str, FieldRule]


def profile(name: str) -> CategoryProfile:
    from types import MappingProxyType
    from .contracts import MaintenanceError
    shared = {'description': FieldRule('text', 'comparable'),
              'title': FieldRule('text', 'comparable'),
              'price': FieldRule('decimal', 'comparable', 'decimal'),
              'currency': FieldRule('text', 'price_context')}
    if name == 'hardware-v1':
        shared.update({'attributes/' + key: FieldRule('text', 'identity_variant')
                       for key in ('ram', 'storage', 'model')})
        shared['attributes/material'] = FieldRule('text', 'comparable')
    elif name == 'footwear-v1':
        shared.update({'attributes/' + key: FieldRule('text', 'identity_variant')
                       for key in ('size', 'size_system', 'color', 'fit')})
        shared.update({'attributes/' + key: FieldRule('text', 'comparable')
                       for key in ('material', 'construction')})
    elif name != 'generic-v1':
        raise MaintenanceError('invalid_argument', 'Unknown category profile')
    if name != 'generic-v1':
        shared['attributes/weight'] = FieldRule('mass', 'comparable', 'mass_kg')
    return CategoryProfile(name, MappingProxyType(shared))


def compare_field(rule: FieldRule, before, after) -> dict:
    """Result includes comparison, normalized values and transform trace; no identity authorization."""
    from decimal import Decimal, InvalidOperation
    import re
    result = {'comparison': 'unknown', 'normalized_before': before,
              'normalized_after': after, 'trace': []}
    if before is None or after is None:
        return result
    def normalized(value):
        if rule.kind == 'text':
            return value if isinstance(value, str) else None
        if isinstance(value, bool):
            return None
        try:
            if rule.kind == 'decimal':
                number = Decimal(str(value))
            else:
                found = re.fullmatch(r'([0-9]+(?:\.[0-9]+)?)\s*(g|kg)', str(value))
                if not found:
                    return None
                number = Decimal(found[1]) / (1000 if found[2] == 'g' else 1)
            return format(number.normalize(), 'f') if number.is_finite() else None
        except (InvalidOperation, ValueError):
            return None
    left, right = normalized(before), normalized(after)
    result.update(normalized_before=left, normalized_after=right)
    if left is not None and right is not None:
        result['comparison'] = 'equal' if left == right else 'different'
        if rule.kind != 'text':
            result['trace'] = [{'operation': rule.normalization, 'before': before,
                                'after': after, 'unit': 'kg' if rule.kind == 'mass' else None}]
    return result
