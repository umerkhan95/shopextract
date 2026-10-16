"""Conversion outcomes produced by normalizers, independent of evidence capture."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from decimal import Decimal, InvalidOperation
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

    def money(self, field, *paths, default=Decimal('0'), stringify=False,
              css=False, truthy=False, divisor=None, operation='', strict=False):
        def convert(value):
            if css and isinstance(value, str):
                value = value.replace('$', '').replace('€', '').replace('£', '').strip()
                value = value.replace(',', '') if '.' in value else value.replace(',', '.')
            elif stringify:
                value = str(value)
            value = Decimal(value)
            if divisor is not None:
                value /= divisor
            if not value.is_finite():
                raise ValueError('Nonfinite price')
            return value
        return self.emit(field, *paths, default=default, convert=convert, truthy=truthy,
                         operation=operation or 'Parse decimal amount' + ('; strip currency symbols and normalize separators' if css else ''), strict=strict)

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
