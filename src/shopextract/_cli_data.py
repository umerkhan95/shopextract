"""Bounded CLI JSON and native Product transport; shared by domain commands."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import click

from ._cli_core import CliFailure
from ._evidence import decode_value, encode_value
from ._portable import product_from_record, product_to_record, validate_tree

MAX_BYTES = 33554432
MAX_RECORDS = 1000
MAX_NODES = 1000000


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate key')
        result[key] = value
    return result


def bounded_tree(value):
    stack = [(value, 0)]; count = 0
    while stack:
        item, depth = stack.pop(); count += 1
        if count > MAX_NODES or depth > 64:
            raise ValueError('JSON structure exceeds bounds')
        if isinstance(item, dict):
            stack.extend((v, depth + 1) for v in item.values())
        elif isinstance(item, list):
            stack.extend((v, depth + 1) for v in item)
    validate_tree(value, encoded=True)


def read_json_file(path):
    try:
        if path == '-':
            raw = click.get_binary_stream('stdin').read(MAX_BYTES + 1)
        else:
            with open(path, 'rb') as stream:
                raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES or raw.startswith(b'\xef\xbb\xbf'):
            raise ValueError()
        from ._bounded_json import preflight_catalog_json
        preflight_catalog_json(raw)
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        bounded_tree(value)
        from ._compact_catalog import decode_compact_catalog, canonical, CompactLimits, _cost
        if isinstance(value,dict) and value.get('schema_version')=='catalog-1':
            value=decode_compact_catalog(raw)
        elif isinstance(value,dict) and isinstance(value.get('data'),dict) and value['data'].get('schema_version')=='catalog-1':
            outer=dict(value,data=None)
            size,nodes,depth=_cost(outer,CompactLimits())
            value['data']=decode_compact_catalog(canonical(value['data']),limits=CompactLimits(
                max_expanded_bytes=MAX_BYTES-(size-4),max_nodes=MAX_NODES-(nodes-1),max_depth=63))
        bounded_tree(value)
        return value
    except (OSError, UnicodeError, ValueError, RecursionError):
        raise CliFailure('E_USAGE', 'Expected bounded UTF-8 JSON; consult command help and file schema.') from None


def raw_records(value):
    try:
        bounded_tree(value)
        records = value if isinstance(value, list) else [value]
        if len(records) > MAX_RECORDS or any(not isinstance(v, dict) or 'product' in v and 'schema_version' in v for v in records):
            raise ValueError()
        decoded = decode_value(records)
        validate_tree(decoded)
        if any(not isinstance(v, dict) for v in decoded):
            raise ValueError()
        return decoded
    except (ValueError, TypeError, ArithmeticError, RecursionError):
        raise CliFailure('E_USAGE', 'Expected raw product object or array; portable records require their documented consumer.') from None


def load_products(path):
    value=read_json_file(path)
    if has_categories(value):
        values=categorized_from_value(value)
        category_policy_from_value(value,values)
        return [v.product for v in values]
    return products_from_value(value)


def products_from_value(value):
    try:
        if isinstance(value, dict) and 'data' in value:
            if value.get('schema_version') != '1.0' or not isinstance(value['data'], dict):
                raise ValueError()
            value = value['data']['products']
        if not isinstance(value, list) or len(value) > MAX_RECORDS:
            raise ValueError()
        return [product_from_record(record) for record in value]
    except (ValueError, TypeError, KeyError, RecursionError):
        raise CliFailure('E_USAGE', 'Expected native portable product records or a product result envelope.') from None


def extraction_data(result):
    from ._execution import safe_error
    import json
    records=[product_to_record(p) for p in result.products]
    def order(record):
        values=record['product']
        facts={k:v for k,v in values.items() if k not in {'raw_data','scraped_at'}}
        return (values.get('canonical_product_id') or values.get('external_id') or '',
                values.get('product_url') or '',
                json.dumps(facts,sort_keys=True,separators=(',',':'),allow_nan=False))
    return dict(products=sorted(records,key=order),
                raw_products=encode_value(result.raw_products), platform=result.platform.value,
                tier=result.tier.value, quality_score=result.quality_score,
                urls_attempted=result.urls_attempted, urls_succeeded=result.urls_succeeded,
                errors=[safe_error(error) for error in result.errors],
                observation_scope=result.observation_scope, catalog_complete=result.catalog_complete,
                incompleteness_reasons=list(result.incompleteness_reasons), product_count=result.product_count)


def atomic_json(path, data, *, compact=False):
    temporary = None
    try:
        encoded = json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(',', ':') if compact else None)
        target = Path(path)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=target.parent,
                                         prefix=f'.{target.name}.', delete=False) as stream:
            temporary = stream.name
            stream.write(encoded); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, target)
    except (OSError, ValueError, TypeError):
        raise CliFailure('E_OPERATION', 'Cannot write result file; existing output was preserved.') from None
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)


from dataclasses import dataclass, asdict, fields
from decimal import Decimal
from datetime import datetime
from ._models import Product, Variant, Platform


@dataclass
class CatalogInput:
    records: list[dict]
    products: list[Product] | None = None
    categorized_records: list[dict] | None = None
    category_policy: dict | None = None


def flat_to_products(records, *, reject_extensions=True):
    """Concrete Product projection; never infer evidence or normalize identifiers."""
    allowed = {f.name for f in fields(Product)}
    variant_allowed = {f.name for f in fields(Variant)}
    products = []
    try:
        for record in records:
            if reject_extensions and record.keys() - allowed:
                raise ValueError()
            data = {k:v for k,v in record.items() if k in allowed}
            for key in ('price','compare_at_price'):
                if key in data and data[key] is not None:
                    if type(data[key]) not in (str,int,float,Decimal):
                        raise ValueError()
                    data[key] = Decimal(str(data[key]))
            if 'platform' in data:
                data['platform'] = Platform(data['platform'])
            if 'scraped_at' in data and isinstance(data['scraped_at'],str):
                data['scraped_at'] = datetime.fromisoformat(data['scraped_at'].replace('Z','+00:00'))
            if 'variants' in data:
                if not isinstance(data['variants'],list):
                    raise ValueError()
                variants = []
                for raw in data['variants']:
                    if not isinstance(raw,dict) or raw.keys() - variant_allowed:
                        raise ValueError()
                    item = dict(raw)
                    if 'price' in item:
                        if type(item['price']) not in (str,int,float,Decimal):
                            raise ValueError()
                        item['price'] = Decimal(str(item['price']))
                    variants.append(Variant(**item))
                data['variants'] = variants
            product = Product(**data)
            product_to_record(product)  # concrete native type and finite-value validation
            products.append(product)
        return products
    except (ValueError,TypeError,ArithmeticError,AttributeError):
        raise CliFailure('E_USAGE','Invalid typed product fields; money must be finite, identifiers strings and variants typed objects.') from None


def categorized_from_value(value):
    """Strict categorized authority: never fall back after a category claim."""
    from .categories.portable import categorized_product_from_record
    try:
        bounded_tree(value)
        projected = None
        has_projection = False
        if isinstance(value,dict) and 'data' in value:
            if value.get('schema_version') != '1.0' or not isinstance(value['data'],dict):
                raise ValueError()
            value = value['data']
        if isinstance(value,dict):
            has_projection = 'products' in value
            projected = value.get('products')
            if 'categorized_products' not in value:
                raise ValueError()
            value = value['categorized_products']
        if not isinstance(value,list) or len(value)>MAX_RECORDS:
            raise ValueError()
        values = [categorized_product_from_record(record) for record in value]
        if has_projection and projected != [product_to_record(v.product) for v in values]:
            raise ValueError()
        return values
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError):
        raise CliFailure('E_USAGE','Expected intact native categorized records with matching product projection.') from None


def category_policy_from_value(value, values):
    """Validate optional runtime policy metadata; never confuse its digest with options."""
    from .categories.config import runtime_from_record, runtime_record, options_digest
    from .categories.maintenance import category_policy_digest
    try:
        if isinstance(value,dict) and 'data' in value:
            value=value['data']
        if not isinstance(value,dict) or not ('policy_digest' in value or 'config' in value):
            return None
        config=runtime_from_record(value['config'])
        policy_digest=category_policy_digest(config)
        if value['policy_digest']!=policy_digest or any(v.scope!=config.options.scope or v.config_digest!=options_digest(config.options) for v in values):
            raise ValueError()
        return dict(config=runtime_record(config),policy_digest=policy_digest)
    except (ValueError,TypeError,KeyError,AttributeError,RecursionError):
        raise CliFailure('E_USAGE','Category runtime policy metadata differs from retained companions.') from None


def has_categories(value):
    if isinstance(value,dict):
        value=value.get('data',value)
        return isinstance(value,dict) and 'categorized_products' in value
    return isinstance(value,list) and any(isinstance(v,dict) and ('observations' in v or 'config_digest' in v) for v in value)


def catalog_from_value(value):
    if has_categories(value):
        values=categorized_from_value(value)
        products=[v.product for v in values]
        from .categories.portable import categorized_product_to_record
        return CatalogInput([asdict(p) for p in products], products, [categorized_product_to_record(v) for v in values], category_policy_from_value(value,values))
    if isinstance(value,dict) and 'data' in value or isinstance(value,list) and value and isinstance(value[0],dict) and 'schema_version' in value[0] and 'product' in value[0]:
        products = products_from_value(value)
        return CatalogInput([asdict(p) for p in products], products)
    records = raw_records(value)
    flat_to_products(records, reject_extensions=False)  # validate all known fields before effects
    # Preserve native raw presence/shape: do not inject constructor defaults.
    return CatalogInput(records)


def load_catalog(path):
    return catalog_from_value(read_json_file(path))
