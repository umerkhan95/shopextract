"""Finite declarative category profiles; comparison does not authorize identity."""
from dataclasses import dataclass
from typing import Literal, Mapping
from types import MappingProxyType


@dataclass(frozen=True)
class FieldRule:
    kind: Literal['text', 'decimal', 'mass', 'volume', 'length']
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
    elif name == 'refrigerator-v1':
        shared['attributes/capacity'] = FieldRule('volume', 'identity_variant', 'volume_total_l_v1')
        shared.update({'attributes/' + axis: FieldRule('length', 'identity_variant', 'length_' + axis + '_m_v1')
                       for axis in ('width', 'height', 'depth')})
        shared['attributes/model'] = FieldRule('text', 'identity_variant')
    elif name != 'generic-v1':
        raise MaintenanceError('invalid_argument', 'Unknown category profile')
    if name in {'hardware-v1', 'footwear-v1'}:
        shared['attributes/weight'] = FieldRule('mass', 'comparable', 'mass_kg')
    return CategoryProfile(name, MappingProxyType(shared))



QUANTITY_POLICIES = MappingProxyType({
    'volume_total_l_v1': ('volume', 'total_volume', 'L', MappingProxyType({'ml': -3, 'L': 0})),
    'length_width_m_v1': ('length', 'product_width', 'm', MappingProxyType({'mm': -3, 'cm': -2, 'm': 0})),
    'length_height_m_v1': ('length', 'product_height', 'm', MappingProxyType({'mm': -3, 'cm': -2, 'm': 0})),
    'length_depth_m_v1': ('length', 'product_depth', 'm', MappingProxyType({'mm': -3, 'cm': -2, 'm': 0})),
})
_UNSET = object()
MISSING_QUANTITY = object()


def _quantity(rule, value):
    from decimal import Decimal
    import math
    import re
    if value is MISSING_QUANTITY:
        return None, 'missing', 'missing'
    inner = value.get('value') if isinstance(value, dict) and 'value' in value else value
    state = 'null' if inner is None else 'empty' if isinstance(inner, str) and not inner.strip(' \t\r\n\v\f') else 'value'
    if isinstance(value, dict):
        if set(value) != {'value', 'semantic'}:
            return None, state, 'semantic_missing' if set(value) == {'value'} else 'invalid_type'
        semantic = value['semantic']
        if not isinstance(semantic, str) or len(semantic) > 32:
            return None, state, 'invalid_type'
    elif state not in {'null', 'empty'}:
        return None, state, 'semantic_missing' if isinstance(value, str) else 'invalid_type'
    if state in {'null', 'empty'}:
        return None, state, state
    if isinstance(inner, str) and len(inner) > 128:
        return None, state, 'input_too_long'
    if not semantic:
        return None, 'value', 'semantic_missing'
    policy = QUANTITY_POLICIES.get(rule.normalization)
    if not policy or policy[0] != rule.kind or semantic != policy[1]:
        return None, 'value', 'semantic_mismatch'
    if isinstance(inner, bool):
        return None, 'value', 'invalid_type'
    if isinstance(inner, (int, float)):
        return None, 'value', 'non_finite' if isinstance(inner, float) and not math.isfinite(inner) else 'unit_missing'
    if not isinstance(inner, str):
        return None, 'value', 'invalid_type'
    text = inner.strip(' \t\r\n\v\f')
    if text.casefold() in {'nan', 'infinity', 'inf', '+inf', '-inf', '+infinity', '-infinity'}:
        return None, 'value', 'non_finite'
    if text.startswith('-'):
        return None, 'value', 'negative'
    if re.search(r'[0-9]\s*[-–]\s*[0-9]', text):
        return None, 'value', 'range'
    match = re.fullmatch(r'([0-9]+(?:\.[0-9]+)?)[ \t\r\n\v\f]*([^0-9 \t\r\n\v\f]+)?', text)
    if not match:
        return None, 'value', 'invalid_syntax'
    unit = match[2]
    if not unit:
        return None, 'value', 'unit_missing'
    if unit not in policy[3]:
        known = {'g', 'kg', 'ml', 'L', 'mm', 'cm', 'm'}
        return None, 'value', 'unit_incompatible' if unit in known else 'unit_unsupported'
    number = Decimal(match[1]).as_tuple()
    # Construct exponent directly: neither division nor normalize uses a context.
    canonical = format(Decimal((number.sign, number.digits, number.exponent + policy[3][unit])), 'f')
    if '.' in canonical:
        canonical = canonical.rstrip('0').rstrip('.')
    return canonical, 'value', None


def _compare_quantity(rule, before, after, raw_before, raw_after):
    left, _, _ = _quantity(rule, before)
    right, _, _ = _quantity(rule, after)
    _, left_state, left_reason = _quantity(rule, before if raw_before is _UNSET else raw_before)
    _, right_state, right_reason = _quantity(rule, after if raw_after is _UNSET else raw_after)
    result = dict(comparison='unknown', normalized_before=left, normalized_after=right, trace=[],
        input_states={'before': left_state, 'after': right_state},
        input_reasons={'before': left_reason, 'after': right_reason})
    if left is not None and right is not None:
        result['comparison'] = 'equal' if left == right else 'different'
        result['trace'] = [dict(operation=rule.normalization, before=before, after=after,
            unit=QUANTITY_POLICIES[rule.normalization][2], normalized_before=left, normalized_after=right)]
    return result

def compare_field(rule: FieldRule, before, after, *, raw_before=_UNSET, raw_after=_UNSET) -> dict:
    """Result includes comparison, normalized values and transform trace; no identity authorization."""
    from decimal import Decimal, InvalidOperation
    import re
    if rule.kind in {'volume', 'length'}:
        return _compare_quantity(rule, before, after, raw_before, raw_after)
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
