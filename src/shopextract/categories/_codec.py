"""Private bounded category dataclass codec using existing primitive value codecs."""
from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
import hashlib
import json
import types
from typing import Literal, Union, get_args, get_origin
from .._evidence import encode_value, decode_value
from .._portable import validate_tree
from .._schemas import schema_hints
from .contracts import CategoryError


def wire(value):
    if is_dataclass(value):
        return {f.name: wire(getattr(value, f.name)) for f in fields(value)}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (tuple, list)):
        return [wire(v) for v in value]
    return encode_value(value)


def canonical(value):
    validate_tree(value, encoded=True)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def typed(kind, value):
    origin, args = get_origin(kind), get_args(kind)
    if origin in (Union, types.UnionType):
        for choice in args:
            try:
                return typed(choice, value)
            except (ValueError, TypeError, KeyError):
                pass
        raise CategoryError('Invalid category union value')
    if origin is Literal:
        if not any(type(value) is type(v) and value == v for v in args):
            raise CategoryError('Invalid category enum')
        return value
    if origin in (tuple, list):
        if not isinstance(value, list):
            raise CategoryError('Category sequence required')
        if origin is tuple and args and args[-1] is not Ellipsis:
            if len(args) != len(value):
                raise CategoryError('Invalid category tuple arity')
            result = [typed(t, v) for t, v in zip(args, value)]
        else:
            result = [typed(args[0], v) for v in value]
        return tuple(result) if origin is tuple else result
    if isinstance(kind, type) and is_dataclass(kind):
        names = {f.name for f in fields(kind)}
        if not isinstance(value, dict) or set(value) != names:
            raise CategoryError('Invalid category record fields')
        hints = schema_hints(kind)
        return kind(**{k: typed(hints[k], v) for k, v in value.items()})
    if isinstance(kind, type) and issubclass(kind, Enum):
        return kind(value)
    if kind is object:
        result = decode_value(value)
        validate_tree(result)
        return result
    if kind is datetime:
        result = decode_value(value)
        if not isinstance(result, datetime):
            raise CategoryError('Category timestamp required')
        return result
    if type(value) is not kind:
        raise CategoryError('Invalid category primitive type')
    return value
