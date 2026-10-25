"""Small shared identity formatting helpers; platform payload semantics stay in adapters."""
from dataclasses import asdict
import hashlib
import json
from urllib.parse import quote
from .._scope import catalog_scope
from .contracts import CategoryScope


def merchant_scope(scope: CategoryScope) -> str:
    result = catalog_scope(scope.store_url, scope.platform)
    return result if scope.catalog is None else result + ':catalog-id:' + quote(scope.catalog, safe='')


def observation_id(scope: CategoryScope, namespace: str, relation: str, pointer: str = '') -> str:
    payload = json.dumps([asdict(scope), namespace, relation, pointer], default=str, sort_keys=True, ensure_ascii=False)
    return 'c_' + hashlib.sha256(payload.encode()).hexdigest()


def nonblank_text(value):
    if isinstance(value, str) and value.strip():
        return value
    raise ValueError('Category value must be nonempty text')


def native_id(value):
    if type(value) is int and value > 0:
        return str(value)
    return nonblank_text(value)
