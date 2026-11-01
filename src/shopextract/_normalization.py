"""Conversion outcomes produced by normalizers, independent of evidence capture."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from decimal import Decimal, InvalidOperation
import re
from typing import Callable


@dataclass
class Selection:
    path: str | None
    value: object = None
    present: bool = False
    usable: bool = False


@dataclass
class ConversionOutcome:
    source_paths: tuple[str, ...]
    normalized_value: object
    accepted: bool
    reason: str = ''
    transformations: list[str] = field(default_factory=list)
    source_values: tuple[object, ...] = ()


class NormalizedData(dict):
    def __init__(self, values, outcomes):
        super().__init__(values)
        self.outcomes = outcomes


class Normalizer:
    """Select actual inputs once and record the conversion that produced each field."""
    def __init__(self, raw):
        self.raw = raw
        self.outcomes: dict[str, ConversionOutcome] = {}

    def select(self, *paths, truthy=False):
        absent = Selection(paths[0] if paths else None)
        for path in paths:
            value = self.raw
            try:
                for token in path[1:].split('/'):
                    token = token.replace('~1', '/').replace('~0', '~')
                    value = value[int(token)] if isinstance(value, list) else value[token]
            except (KeyError, IndexError, TypeError, ValueError):
                continue
            selection = Selection(path, value, True, not truthy or bool(value))
            if selection.usable:
                return selection
            if not absent.present:
                absent = selection
        return absent

    def record(self, field, selection, value, *, accepted=True, reason='', operation=''):
        if isinstance(selection, str):
            selection = self.select(selection)
        sources = (selection.path,) if selection.path else ()
        accepted = accepted and selection.usable
        if not accepted and not reason:
            reason = 'Source input was absent, rejected or replaced by a compatibility default'
        self.outcomes['/' + field.lstrip('/')] = ConversionOutcome(
            sources, value, accepted, reason, [operation] if operation else [],
            (selection.value,) if selection.path else ())
        return value

    def record_inputs(self, field, selections, value, *, accepted=True, operation=''):
        """Record the precise inputs used by an aggregate instead of their parent object."""
        accepted = bool(selections) and accepted and all(s.usable for s in selections)
        self.outcomes['/' + field.lstrip('/')] = ConversionOutcome(
            tuple(s.path for s in selections), value, accepted,
            '' if accepted else 'Aggregate requires explicit values for every source input',
            [operation] if operation else [], tuple(s.value for s in selections))
        return value

    def emit(self, field, *paths, default=None, convert: Callable | None = None,
             truthy=False, operation='', strict=False):
        selection = self.select(*paths, truthy=truthy)
        accepted, reason = selection.usable, ''
        value = default
        if selection.usable:
            try:
                value = convert(selection.value) if convert else selection.value
                accepted = value is not None
                if not accepted:
                    reason = 'Normalizer rejected source value; compatibility default has no support'
                    if convert:
                        value = default
            except (InvalidOperation, ValueError, TypeError, OverflowError):
                if strict:
                    raise
                accepted = False
                reason = 'Source conversion failed; compatibility default has no factual support'
                value = default
        return self.record(field, selection, value, accepted=accepted,
                           reason=reason, operation=operation)

    def currency(self, field, *paths):
        selections=[self.select(path) for path in paths]
        usable=[v for v in selections if v.present and v.value not in (None,'')]
        from ._currencies import is_pricing_currency
        valid=[v for v in usable if isinstance(v.value,str) and is_pricing_currency(v.value.strip())]
        codes={v.value.strip().upper() for v in valid}
        accepted=bool(valid) and len(valid)==len(usable) and len(codes)==1
        value=next(iter(codes)) if accepted else ''
        reason='' if accepted else ('Conflicting currency sources' if len(codes)>1 else 'Missing or invalid ISO4217 pricing currency')
        chosen=usable or selections[:1]
        self.outcomes['/'+field]=ConversionOutcome(tuple(v.path for v in chosen),value,accepted,reason,
            ['Uppercase source currency'] if accepted else [],tuple(v.value for v in chosen))
        return value

    def money(self, field, *paths, default=Decimal('0'), stringify=False,
              css=False, truthy=False, divisor=None, operation='', strict=False,
              currency=None, locale=None):
        def convert(value):
            if css and isinstance(value,str):
                rupee=bool(re.search(r'\bRs\.?',value,re.I))
                value=re.sub(r'\bRs\.?','',value,flags=re.I)
                value=value.replace('$','').replace('€','').replace('£','').strip()
                if re.search(r'(?<=\d)[ \u00a0](?=\d)',value):
                    if not locale or not re.fullmatch(r'\d{1,3}(?:[ \u00a0]\d{3})+(?:[.,]\d+)?',value):
                        raise ValueError('Unqualified or malformed space grouping')
                    value=value.replace(' ','').replace('\u00a0','')
                decimal_comma=bool(locale and locale.lower().startswith(('de','fr','it','es')))
                if ',' in value and '.' in value:
                    decimal=',' if value.rfind(',')>value.rfind('.') else '.'
                    grouping='.' if decimal==',' else ','
                    whole,fraction=value.rsplit(decimal,1)
                    if not fraction.isdigit() or not re.fullmatch(r'\d{1,3}(?:'+re.escape(grouping)+r'\d{3})+',whole):raise ValueError('Invalid grouped money')
                    value=whole.replace(grouping,'')+'.'+fraction
                elif ',' in value:
                    if decimal_comma:
                        if value.count(',')!=1:raise ValueError('Invalid decimal comma')
                        value=value.replace(',','.')
                    elif (rupee or currency in ('PKR','USD','GBP','INR','LKR')) and re.fullmatch(r'\d{1,3}(?:,\d{3})+',value):value=value.replace(',','')
                    else:raise ValueError('Ambiguous comma money')
            elif stringify:value=str(value)
            value=Decimal(value)
            if divisor is not None:value/=divisor
            if not value.is_finite() or value<0:raise ValueError('Invalid price')
            return value
        result=self.emit(field,*paths,default=default,convert=convert,truthy=truthy,
                         operation=operation or 'Parse contextual decimal amount',strict=strict)
        outcome=self.outcomes['/'+field]
        if outcome.accepted and result==0:outcome.reason='Explicit zero price; verify destination eligibility'
        return result

    def inherit(self, other, output_prefix, source_prefix):
        for path, outcome in other.outcomes.items():
            self.outcomes[output_prefix + path] = replace(
                outcome, source_paths=tuple(source_prefix + p for p in outcome.source_paths))

    def record_nested(self, field, value):
        """Extend an existing same-shape collection outcome to its factual children."""
        outcome = self.outcomes.get('/' + field)
        if not outcome or not outcome.accepted or len(outcome.source_paths) != 1:
            return

        def visit(value, original, target, pointer):
            if isinstance(value, dict) and isinstance(original, dict):
                for key, item in value.items():
                    token = key.replace('~', '~0').replace('/', '~1')
                    if key in original:
                        child = target + '/' + token
                        if child not in self.outcomes:
                            self.record(child, pointer + '/' + token, item)
                        visit(item, original[key], child, pointer + '/' + token)
            elif isinstance(value, list) and isinstance(original, list) and len(value) == len(original):
                for i, item in enumerate(value):
                    child = target + '/' + str(i)
                    if child not in self.outcomes:
                        self.record(child, pointer + '/' + str(i), item)
                    visit(item, original[i], child, pointer + '/' + str(i))

        visit(value, outcome.source_values[0], '/' + field, outcome.source_paths[0])

    def result(self, values):
        return NormalizedData(values, self.outcomes)
