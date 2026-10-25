"""Thin adapters around existing normalization, identity, matching and reports."""
from dataclasses import asdict, is_dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
import json
from .contracts import ToolError, encoded
from .state import RetainedGraph
from .._portable import product_to_record, product_from_record


def json_value(value):
    if is_dataclass(value):
        return json_value(asdict(value))
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: json_value(v) for key, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(v) for v in value]
    return value


def synchronous(payload):
    operation = payload['operation']
    if operation == 'capture':
        from .captures import load_capture
        return load_capture(payload)
    if operation == 'parse':
        from .._normalize import normalize
        from .._models import Platform
        from .._capture import capture
        from ..identity import assign_identity
        category_config = None
        if payload.get('category_config') is not None:
            from ..categories.config import runtime_from_record
            category_config = runtime_from_record(payload['category_config'])
        raw = payload.get('raw')
        if raw is None:
            if payload['mode'] == 'html':
                from ..extractors.unified import UnifiedCrawlExtractor
                raw = UnifiedCrawlExtractor._extract_structured_from_html(payload['html'], payload['url'],include_categories=category_config is not None)
            else:
                from ..extractors.feed import GoogleFeedExtractor
                parser = GoogleFeedExtractor._parse_xml if payload['mode'] == 'xml' else GoogleFeedExtractor._parse_csv
                raw = parser(payload['html'], payload['url'],include_categories=True) if category_config is not None else parser(payload['html'],payload['url'])
            for item in raw:
                if item.get('_capture'):
                    item['_capture']['at'] = payload['observed_at']
        products = []
        for item in raw[:payload['maximum']]:
            companion = None
            if category_config is not None:
                from ..categories.api import normalize_with_categories
                companion = normalize_with_categories(item, Platform(payload['platform']), payload['origin'],category_options=category_config.options)
                product = companion.product if companion else None
            else:
                product = normalize(item, Platform(payload['platform']), payload['origin'])
            if product:
                assign_identity(product, payload['origin'])
                # The finalized portable view discards unused raw engine state.
                product.raw_data = {}
                if companion is not None:
                    from ..categories.portable import bind_product, categorized_product_to_record
                    companion = bind_product(product,companion.scope,companion.observations,companion.mappings,
                        companion.config_digest,limits=category_config.options.limits)
                    products.append(categorized_product_to_record(companion))
                else:
                    products.append(product_to_record(product))
        return products
    if operation == 'match':
        from ..compare.identity_match import match_products
        left = [product_from_record(v) for v in payload['left']]
        right = [product_from_record(v) for v in payload['right']]
        return json_value([asdict(v) for v in match_products(left, right)])
    if operation == 'changes':
        from ..monitor.reliable import reliable_changes
        try:
            return json_value(reliable_changes(**payload['arguments']))
        except ValueError:
            raise ToolError('invalid_argument', 'Invalid capture comparison') from None
    raise ToolError('invalid_argument')


def catalog_graph(records, store, *, complete=True, diagnostics=None, grant=None):
    from .._evidence import trust_view
    products, owners = [], {}
    def owner_record(product):
        handle = store.mint()
        contract = getattr(product, 'evidence_contract', None)
        evidence = {e.evidence_id: json_value(asdict(e)) for e in contract.evidence} if contract else {}
        available = getattr(product, 'evidence_availability', [])
        owners[handle] = {'evidence': evidence, 'availability': available}
        mapping = {}
        if contract:
            for observation in contract.observations:
                mapping.setdefault(observation.field_path, []).extend(observation.evidence_ids)
        return handle, evidence, mapping
    for record in records:
        product = product_from_record(record)
        handle, evidence, mapping = owner_record(product)
        values = json_value(asdict(product))
        values.pop('raw_data', None)
        values.pop('evidence_contract', None)
        values.update(owner_handle=handle, evidence_ids=list(evidence), field_evidence=mapping,
                      support=json_value(trust_view(product, getattr(product, 'evidence_contract', None))))
        variants = []
        for variant in product.variants:
            v_handle, v_evidence, v_mapping = owner_record(variant)
            value = json_value(asdict(variant))
            value.pop('evidence_contract', None)
            value.update(owner_handle=v_handle, evidence_ids=list(v_evidence), field_evidence=v_mapping,
                         support=json_value(trust_view(variant, getattr(variant, 'evidence_contract', None))))
            variants.append(value)
        values['variants'] = variants
        products.append(values)
    metadata = {'catalog_handle': store.mint()}
    if grant:
        metadata.update(capture_handle=store.mint(), grant=grant)
    return RetainedGraph({'products': products, 'diagnostics': diagnostics or []}, metadata,
        'complete' if complete else 'partial', records, owners)


class DomainAdapter:
    def __init__(self, store, sources):
        self.store, self.sources = store, sources

    async def execute(self, name, args, context):
        if name in {'discover', 'extract'}:
            result = await self.sources.execute(name, args['url'], args.get('max_items', 20), context)
            if name == 'discover':
                return RetainedGraph({'urls': result['urls'], 'diagnostics': result['diagnostics']}, {},
                    'complete' if result['complete'] else 'partial')
            return catalog_graph(result['products'], self.store, complete=result['complete'], diagnostics=result['diagnostics'])
        dependencies = []
        if name == 'match':
            data = {}
            for side in ('left', 'right'):
                job_id, _ = self.store.lookup(args[side + '_catalog'], 'catalog')
                dependencies.append(job_id)
                data[side] = self.store.get(job_id).products
            payload = {'operation': 'match', **data}
            serialized = encoded(payload)
            self.store.reserve(len(serialized))
            context.budget.graph_bytes_reserved += len(serialized)
            matches = json.loads(await context.auxiliary.run('domain', serialized, context))
            return RetainedGraph({'matches': matches}, {}, 'complete', dependencies=tuple(dependencies))
        grants = {}
        for field, param in [('previous_capture', 'previous_snapshot_id'), ('current_capture', 'current_snapshot_id'),
                             ('recheck_capture', 'recheck_snapshot_id')]:
            if field in args:
                job_id, grant = self.store.lookup(args[field], 'capture')
                dependencies.append(job_id)
                grants[param] = grant
        first = grants['previous_snapshot_id']
        if any(g['db_path'] != first['db_path'] or g['supplier'] != first['supplier'] for g in grants.values()):
            raise ToolError('invalid_argument', 'Captures must share configured supplier/database')
        arguments = {'domain': first['supplier'], 'db_path': first['db_path'],
                     **{key: grant['snapshot_id'] for key, grant in grants.items()}}
        report = json.loads(await context.auxiliary.run('domain', encoded({'operation': 'changes', 'arguments': arguments}), context))
        collections = {key: report.pop(key) for key in ('candidates', 'events', 'new_events', 'diagnostics')}
        return RetainedGraph(collections, report, 'complete', dependencies=tuple(dependencies))
