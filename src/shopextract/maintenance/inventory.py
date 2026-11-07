"""Offline hash-pinned coverage metadata; never selects or executes domain policy."""
from pathlib import Path
from typing import Iterable
from types import MappingProxyType


BRANCH_FILES = ('el_electronics.yml', 'aa_apparel_accessories.yml', 'hg_home_garden.yml')
REFERENCE_IDS = ('el-6-6', 'aa-8-3', 'hg-11-7-41')


SOURCE_PINS = MappingProxyType({
    'el_electronics.yml': (555297, '08f92912aac14164afbd7704067c586499da9f5591df96def1a25adda908469f'),
    'aa_apparel_accessories.yml': (285314, '3746bf9fab3920b9f529caef076f91225b4f954e6f7e238668aaf49ed90419a6'),
    'hg_home_garden.yml': (877783, '355d32fbc787812c83ff5446dbe7d964d798f8508ec95ee5306f07da8e907a35'),
    'attributes.yml': (4769315, '91ef3829a6621fbc98b46c6447c9702e394fd7c55bfbd56fd2df0545ea9e16b6'),
    'LICENSE': (1046, '6a2261660cc6cb406ed6ef788347d8cb35e939f4537def9e699abf88ed025273'),
})

class InventoryError(ValueError):
    """Offline input failure with a stable diagnostic code."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def build_inventory(source_dir: Path, *, branch_files: Iterable[str] = BRANCH_FILES,
                    selected_ids: Iterable[str] | None = None, include_current_policy: bool = False) -> dict:
    """Build deterministic metadata without downloading or changing runtime state."""
    import hashlib
    import json
    from dataclasses import asdict
    from itertools import islice
    from .profiles import profile

    try:
        names = tuple(islice(branch_files, 4))
        selected = None if selected_ids is None else tuple(islice(selected_ids, 5001))
        if (len(names) != len(BRANCH_FILES) or set(names) != set(BRANCH_FILES)
                or selected is not None and (not selected or len(selected) > 5000 or len(set(selected)) != len(selected)
                    or any(not isinstance(key, str) for key in selected))):
            raise InventoryError('invalid_selection')
    except TypeError as error:
        raise InventoryError('invalid_selection') from error

    # Verify bounded bytes BEFORE parsing even when only one reference is wanted.
    contents, files, total = {}, [], 0
    for name, (size, expected) in sorted(SOURCE_PINS.items()):
        try:
            with (Path(source_dir) / name).open('rb') as stream:
                data = stream.read(size + 1)
        except OSError as error:
            raise InventoryError('source_mismatch') from error
        if len(data) != size or hashlib.sha256(data).hexdigest() != expected:
            raise InventoryError('source_mismatch')
        total += len(data)
        if total > 8 * 1024 * 1024:
            raise InventoryError('source_mismatch')
        contents[name] = data
        files.append({'name': name, 'bytes': size, 'sha256': expected})

    try:
        import yaml
    except ImportError as error:
        raise InventoryError('dependency_unavailable') from error

    def strings(values):
        return (isinstance(values, list) and all(isinstance(value, str) and value for value in values)
                and len(set(values)) == len(values))

    try:
        definitions = yaml.safe_load(contents['attributes.yml'])
        if not isinstance(definitions, dict):
            raise ValueError('Attribute definitions required')
        handles = set()
        for group in ('base_attributes', 'extended_attributes'):
            records = definitions.get(group, [])
            if not isinstance(records, list):
                raise ValueError('Invalid attribute group')
            for record in records:
                handle = record.get('friendly_id') if isinstance(record, dict) else None
                if not isinstance(handle, str) or not handle or handle in handles:
                    raise ValueError('Invalid or repeated attribute identity')
                handles.add(handle)
        del definitions
        nodes, branches, parents = {}, {}, {}
        for name in sorted(names):
            records = yaml.safe_load(contents[name])
            if not isinstance(records, list) or not records:
                raise ValueError('Category list required')
            branches[name] = len(records)
            for record in records:
                if not isinstance(record, dict):
                    raise ValueError('Invalid category')
                key = record.get('id')
                if not isinstance(key, str) or not key or key in nodes:
                    raise ValueError('Invalid or repeated category identity')
                if (not isinstance(record.get('name'), str) or not record['name']
                        or not strings(record.get('children')) or not strings(record.get('attributes'))):
                    raise ValueError('Malformed category fields')
                if not set(record['attributes']) <= handles:
                    raise ValueError('Unresolved attribute')
                nodes[key] = {**record, 'source_file': name}
                if len(nodes) > 5000:
                    raise ValueError('Category node cap exceeded')
        for key, record in nodes.items():
            for child in record['children']:
                if child not in nodes or nodes[child]['source_file'] != record['source_file'] or child in parents:
                    raise ValueError('Dangling child, cross-branch edge or multiple parents')
                parents[child] = key
        for name in names:
            roots = [key for key, record in nodes.items() if record['source_file'] == name and key not in parents]
            if len(roots) != 1:
                raise ValueError('One branch root required')
        # Parent walking detects disconnected cycles as well as root-reachable ones.
        complete = set()
        for key in nodes:
            visiting = set()
            while key is not None and key not in complete:
                if key in visiting:
                    raise ValueError('Category cycle')
                visiting.add(key)
                key = parents.get(key)
            complete.update(visiting)
    except (yaml.YAMLError, ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        raise InventoryError('invalid_source') from error

    if selected is not None and not set(selected) <= nodes.keys():
        raise InventoryError('invalid_selection')
    assessments = {
        'el-6-6': ('hardware', 'hardware-v1'),
        'aa-8-3': ('footwear', 'footwear-v1'),
        'hg-11-7-41': ('refrigeration', None),
    }
    rows = []
    counts = dict(binding_only=0, existing_extension=0, new_profile=0, review_pending=0)
    for key in sorted(nodes if selected is None else selected):
        record = nodes[key]
        family, policy = assessments.get(key, (None, None))
        rules = {path: asdict(rule) for path, rule in sorted(profile(policy).fields.items())} if policy else {}
        candidates = sorted(path for path in rules if path.startswith('attributes/'))
        gaps, excluded = {}, {}
        if key == 'hg-11-7-41':
            candidates = ['attributes/' + field for field in ('capacity', 'depth', 'height', 'model', 'width')]
            gaps = {field: 'profile_missing' for field in candidates}
            if 'umbrella_opening_mechanism' in record['attributes']:
                excluded['umbrella_opening_mechanism'] = 'irrelevant_to_refrigerator_policy'
        elif key == 'el-6-6':
            gaps['attributes/ram'] = 'numeric_capacity_policy_missing'
        elif key == 'aa-8-3':
            gaps['attributes/size'] = 'size_system_semantics_require_explicit_input'
        backlog = 'existing_extension' if policy else 'new_profile' if family else 'review_pending'
        counts[backlog] += 1
        rows.append(dict(category_id=key, name=record['name'], source_file=record['source_file'],
            source_locator=record['source_file'] + '#id=' + key, parent_id=parents.get(key),
            children=sorted(record['children']), declared_attributes=sorted(record['attributes']),
            family=family, profile=policy, policy_coverage='partial' if policy else 'missing' if family else 'unassessed',
            backlog_kind=backlog, semantic_review='pending', candidate_fields=candidates,
            reviewed_rules=rules, field_gaps=gaps, excluded_attributes=excluded,
            extraction_availability={platform: 'not_audited' for platform in
                ('shopify', 'woocommerce', 'magento', 'shopware', 'bigcommerce', 'generic')},
            binding_status='not_configured', checked_fields=[], live_observation='not_run'))
    result = dict(schema_version=1,
        source=dict(namespace='shopify:product-taxonomy', version='2026-08',
            commit='2e9aa2e9b882383952c63d212add13eb80f46cf9', files=files),
        denominator=dict(branch_nodes=branches, category_nodes=len(nodes), selected_rows=len(rows),
            selection='all_saved_branch_nodes' if selected is None else 'explicit_ids'),
        rows=rows, summary=dict(backlog_counts=counts, reviewed_policy_family_count=0,
            remaining_profile_count=None, generic_coverage='common_fields_only'),
        unassessed=dict(scope='all_other_taxonomy_branches', category_count=None))
    if len(json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False).encode('utf-8')) > 8 * 1024 * 1024:
        raise InventoryError('invalid_source')
    if type(include_current_policy) is not bool:
        raise InventoryError('invalid_selection')
    if include_current_policy:
        baseline = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
        result['baseline_digest'] = hashlib.sha256(baseline.encode()).hexdigest()
        result['schema_version'] = 2
        result['summary']['baseline_backlog_counts'] = result['summary'].pop('backlog_counts')
        for row in rows:
            if row['category_id'] == 'hg-11-7-41':
                from .contracts import MaintenanceError
                try:
                    definition = profile('refrigerator-v1')
                except MaintenanceError as error:
                    raise InventoryError('invalid_selection') from error
                from .store import _profile_record, digest
                row.update(profile_definition_digest=digest(_profile_record(definition)), profile=definition.name, policy_coverage='implemented_selected_fields',
                           whole_family_coverage='incomplete', implemented_fields=sorted(definition.fields),
                           reviewed_rules={path: asdict(rule) for path, rule in sorted(definition.fields.items())})
        if len(json.dumps(result, ensure_ascii=False, allow_nan=False).encode()) > 8 * 1024 * 1024:
            raise InventoryError('invalid_source')
    return result
