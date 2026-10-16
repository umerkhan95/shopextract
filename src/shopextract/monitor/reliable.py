"""Explicit evidence-backed snapshot comparisons and durable publication."""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re

from .._evidence import decode_value, encode_value, _utc
from .._portable import validate_tree
from .._resolution import resolve_fields, _equivalent_key
from ..identity import supplier_scope
from .evidence import _ensure_evidence_schema, _load_snapshot, _legacy_product
from .snapshot import _get_connection, _ensure_snapshot_metadata

DEFAULT_DB_PATH = "~/.shopextract/snapshots.db"
POLICY_VERSION = "reliable-change-v1"
MAX_SNAPSHOT_BYTES = 16 * 1024 * 1024
MAX_REPORT_BYTES = 16 * 1024 * 1024
MAX_REPORT_ENTRIES = 10_000


def _before_commit(connection) -> None:
    """Private fault-injection seam after ledger writes, before commit."""


def _json(value):
    return json.dumps(encode_value(value), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False)


def _identifier(*parts):
    return hashlib.sha256(_json(list(parts)).encode()).hexdigest()


def _parse(payload):
    value = json.loads(payload)
    validate_tree(value)
    return value


def _bounded(size):
    if size > MAX_SNAPSHOT_BYTES:
        raise ValueError("Selected snapshot exceeds size limit")


def _metadata(conn, sid, supplier):
    row = conn.execute("SELECT domain,created_at,observation_scope,catalog_complete,incompleteness_reasons_json,length(CAST(products_json AS BLOB)) FROM snapshots WHERE id=?", (sid,)).fetchone()
    if row is None:
        raise KeyError(sid)
    domain, captured, scope, complete, reasons, size = row
    _bounded(size + sum(len((value or '').encode()) for value in (domain, captured, scope, reasons)))
    if supplier_scope(domain) != supplier:
        raise ValueError("Snapshots must have the same supplier")
    stamp = datetime.fromisoformat(captured)
    _utc(stamp)
    if scope is not None and not isinstance(scope, str):
        raise ValueError("Invalid observation scope")
    if complete not in (None, 0, 1):
        raise ValueError("Invalid catalog completeness")
    reasons = _parse(reasons or '[]')
    if not isinstance(reasons, list) or any(not isinstance(r, str) for r in reasons):
        raise ValueError("Invalid incompleteness reasons")
    return dict(snapshot_id=sid, created_at=stamp, observation_scope=scope,
                catalog_complete=None if complete is None else bool(complete),
                incompleteness_reasons=reasons)


def _identities(products, supplier):
    seen = set()
    for p in products:
        if not isinstance(p, dict) or not isinstance(p.get('canonical_product_id'), str) or not p['canonical_product_id'].strip():
            raise ValueError("Persisted canonical product identity required")
        if p['canonical_product_id'] in seen:
            raise ValueError("Duplicate canonical product identity")
        seen.add(p['canonical_product_id'])
        if p.get('supplier_id') != supplier:
            raise ValueError("Conflicting supplier identity")
        variants = set()
        for v in p.get('variants', []):
            vid = v.get('canonical_variant_id')
            if not isinstance(vid, str) or not vid.strip() or vid in variants:
                raise ValueError("Missing or duplicate canonical variant identity")
            variants.add(vid)


def _load(conn, meta, supplier):
    sid = meta['snapshot_id']
    # Count bytes in SQLite before retrieving or decoding any selected graph.
    scalar_size = conn.execute('SELECT length(CAST(products_json AS BLOB)) FROM snapshots WHERE id=?', (sid,)).fetchone()[0]
    total = scalar_size
    for sql in (
        'SELECT coalesce(sum(length(CAST(record_json AS BLOB))),0) FROM evidence_products WHERE snapshot_id=?',
        'SELECT coalesce(sum(length(CAST(graph_json AS BLOB))),0) FROM evidence_owners WHERE snapshot_id=?',
        'SELECT coalesce(sum(length(CAST(metadata_json AS BLOB))),0) FROM evidence_records WHERE snapshot_id=?',
        'SELECT coalesce(sum(length(CAST(p.encoded_payload AS BLOB))),0) FROM evidence_records r JOIN evidence_payloads p ON p.payload_hash=r.payload_hash WHERE r.snapshot_id=?',
    ):
        total += conn.execute(sql, (sid,)).fetchone()[0]
        _bounded(total)
    raw = _parse(conn.execute('SELECT products_json FROM snapshots WHERE id=?', (sid,)).fetchone()[0])
    if not isinstance(raw, list):
        raise ValueError('Invalid scalar snapshot')
    _identities(raw, supplier)
    positions = conn.execute('SELECT position FROM evidence_products WHERE snapshot_id=? ORDER BY position', (sid,)).fetchall()
    if positions and [p[0] for p in positions] != list(range(len(raw))):
        raise ValueError('Portable/scalar record count or position mismatch')
    products = _load_snapshot(conn, sid)
    if positions:
        for scalar, product in zip(raw, products):
            if asdict(_legacy_product(scalar)) != asdict(product):
                raise ValueError('Portable/scalar snapshot inconsistency')
    _capture_bounds(products)
    entities = {}
    for i, p in enumerate(products):
        pid = p.canonical_product_id
        entities[(pid, None)] = _fields(p, meta, f'product/{i}', False)
        for j, v in enumerate(p.variants):
            entities[(pid, v.canonical_variant_id)] = _fields(v, meta, f'product/{i}/variant/{j}', True)
    return entities


def _capture_bounds(products):
    """Apply the writer's retained-text budgets to direct database inputs too."""
    for product in products:
        seen, total = set(), 0
        for owner in [product, *product.variants]:
            contract = getattr(owner, 'evidence_contract', None)
            for evidence in contract.evidence if contract else []:
                identity = _json(asdict(evidence))
                if identity in seen:
                    continue
                seen.add(identity)
                actual = len((evidence.excerpt or '').encode())
                if evidence.retained_data is not None:
                    actual += len(_json(evidence.retained_data).encode())
                if actual > 4096:
                    raise ValueError('Evidence fragment exceeds 4096 byte limit')
                total += actual
        if total > 65536:
            raise ValueError('Product capture exceeds 65536 byte limit')


def _tracked(path, variant=False):
    return path in ({'/price', '/in_stock'} if variant else {'/price', '/currency', '/in_stock', '/pack_quantity'}) or bool(re.fullmatch(r'/attributes/(?:[^~/]|~[01])*', path))


def _valid(path, value):
    if path == '/price':
        if isinstance(value, bool) or not isinstance(value, (int, float, Decimal)):
            return False
        number = Decimal(str(value))
        return number.is_finite() and number >= 0
    if path == '/currency':
        return isinstance(value, str) and bool(re.fullmatch('[A-Z]{3}', value))
    if path == '/in_stock':
        return type(value) is bool
    if path == '/pack_quantity':
        return type(value) is int and value > 0
    return value is not None


def _side(state='unknown', value=None, references=None, coverage=None):
    return dict(state=state, value=value, references=references or [], coverage=coverage)


def _fields(owner, meta, key, variant):
    contract = getattr(owner, 'evidence_contract', None)
    if contract is None:
        return {}
    resolved = resolve_fields(contract, as_of=meta['created_at'])
    observations = {o.observation_id: o for o in resolved.observations}
    result = {}
    for r in resolved.resolutions:
        if not _tracked(r.field_path, variant):
            continue
        selected = observations.get(r.selected_observation_id)
        side = _side()
        reason = r.reason
        if selected is not None and _valid(r.field_path, selected.normalized_value):
            value = selected.normalized_value
            if r.field_path == '/price':
                value = Decimal(str(value))
            side = _side('observed', value, [dict(snapshot_id=meta['snapshot_id'], record_key=key,
                observation_id=selected.observation_id, evidence_ids=list(selected.evidence_ids))])
        elif selected is not None:
            reason = 'invalid_field_type: ' + reason
        result[r.field_path] = (side, dict(reason=reason,
            observations=[asdict(o) for o in resolved.observations if o.field_path == r.field_path]))
    return result


def _value(fields, path):
    return fields.get(path, (_side(), {'reason': 'missing_field', 'observations': []}))


def _coverage(meta):
    return {k: meta[k] for k in ('snapshot_id', 'observation_scope', 'catalog_complete', 'incompleteness_reasons')}


def _healthy(meta):
    return meta["catalog_complete"] is True and not meta["incompleteness_reasons"]


def _presence(fields, meta):
    references = [ref for side, _ in fields.values() for ref in side['references']]
    # Presence is a captured identity; no observed scalar is invented for it.
    return _side(coverage=_coverage(meta), references=references)


def _diagnostic(report, entity, path, reason, **details):
    report['diagnostics'].append(dict(canonical_product_id=entity[0], canonical_variant_id=entity[1],
        field_path=path, reason=reason, details=details))
    _entries(report)


def _entries(report):
    if len(report['candidates']) + len(report['diagnostics']) > MAX_REPORT_ENTRIES:
        raise ValueError('Report entries exceed limit')


def _candidate(report, entity, path, kind, old, new, pending=False):
    cid = _identifier(report['report_id'], *entity, path, kind)
    report['candidates'].append(dict(candidate_id=cid, event_id=_identifier(cid, 'event'), kind=kind,
        state='pending' if pending else 'confirmed', reason='awaiting_recheck' if pending else 'supported_change',
        supplier=report['supplier'], canonical_product_id=entity[0], canonical_variant_id=entity[1],
        field_path=path, previous_snapshot_id=report['previous_snapshot_id'],
        current_snapshot_id=report['current_snapshot_id'], old=old, new=new, recheck=None))
    _entries(report)


def _currency(entities, entity):
    return _value(entities.get((entity[0], None), {}), '/currency')[0]


def _currency_reason(left, right):
    if left['state'] != 'observed' or right['state'] != 'observed':
        return 'currency_unverified'
    if left['value'] != right['value']:
        return 'currency_mismatch'
    return None


def _compare(report, old, new, previous, current):
    if not previous['observation_scope'] or previous['observation_scope'] != current['observation_scope']:
        report.update(status='suppressed', reason='observation_scope_unverified_or_mismatched')
        return
    for entity in sorted(old.keys() | new.keys(), key=lambda e: (e[0], e[1] or '')):
        left, right = old.get(entity), new.get(entity)
        if left is None or right is None:
            if entity[1] is not None:
                _diagnostic(report, entity, '', 'variant_membership_unverified')
            elif left is None:
                if _healthy(previous) and any(s['state'] == 'observed' for s, _ in right.values()):
                    _candidate(report, entity, '', 'product_added', _side('absent', coverage=_coverage(previous)), _presence(right, current))
                else:
                    _diagnostic(report, entity, '', 'addition_unverified')
            elif _healthy(current):
                _candidate(report, entity, '', 'product_removed', _presence(left, previous), _side('absent', coverage=_coverage(current)), True)
            else:
                _diagnostic(report, entity, '', 'absence_unverified')
            continue
        # Include core fields so wholly missing or scalar-only graphs explain suppression.
        core = {'/price', '/in_stock'} if entity[1] else {'/price', '/currency', '/in_stock', '/pack_quantity'}
        for path in sorted(left.keys() | right.keys() | core):
            a, ad = _value(left, path)
            b, bd = _value(right, path)
            if a['state'] != 'observed' or b['state'] != 'observed':
                _diagnostic(report, entity, path, 'field_unverified', old=ad, new=bd)
                continue
            if _equivalent_key(a['value'], path) == _equivalent_key(b['value'], path):
                continue
            if len(ad['observations']) > 1 or len(bd['observations']) > 1:
                _diagnostic(report, entity, path, 'resolution_context', old=ad, new=bd)
            pending = path == '/currency'
            if path == '/price':
                reason = _currency_reason(_currency(old, entity), _currency(new, entity))
                if reason:
                    _diagnostic(report, entity, path, reason, old_currency=_currency(old, entity), new_currency=_currency(new, entity))
                    continue
                x, y = a['value'], b['value']
                pending = x == 0 or y == 0 or y <= x / 2 or y >= x * 2
            _candidate(report, entity, path, 'field_changed', a, b, pending)


def _recheck(report, entities, meta, candidate_currencies):
    for c in report['candidates']:
        if c['state'] != 'pending':
            continue
        entity = (c['canonical_product_id'], c['canonical_variant_id'])
        fields = entities.get(entity)
        if c['kind'] == 'product_removed':
            c['recheck'] = _presence(fields, meta) if fields is not None else _side('absent' if _healthy(meta) else 'unknown', coverage=_coverage(meta))
            if fields is not None:
                c.update(state='rejected', reason='product_reappeared')
            elif _healthy(meta):
                c.update(state='confirmed', reason='confirmed_absence')
            else:
                c['reason'] = 'unverified_recheck'
            continue
        side, _ = _value(fields or {}, c['field_path'])
        c['recheck'] = dict(side, coverage=_coverage(meta))
        if c['field_path'] == '/price':
            reason = _currency_reason(candidate_currencies.get(entity, _side()), _currency(entities, entity))
            if reason:
                c['reason'] = reason
                continue
        if side['state'] != 'observed':
            c['reason'] = 'unverified_recheck'
        elif _equivalent_key(side['value'], c['field_path']) == _equivalent_key(c['new']['value'], c['field_path']):
            c.update(state='confirmed', reason='confirmed_recheck')
        elif _equivalent_key(side['value'], c['field_path']) == _equivalent_key(c['old']['value'], c['field_path']):
            c.update(state='rejected', reason='reverted_value')
        else:
            c.update(state='rejected', reason='superseded_value')


def _schema(conn):
    conn.execute('CREATE TABLE IF NOT EXISTS reliable_schema (singleton INTEGER PRIMARY KEY CHECK(singleton=1), version INTEGER NOT NULL)')
    row = conn.execute('SELECT version FROM reliable_schema WHERE singleton=1').fetchone()
    if row and row[0] != 1:
        raise ValueError('Unsupported reliable report schema version')
    conn.execute('INSERT OR IGNORE INTO reliable_schema VALUES (1,1)')
    conn.execute('CREATE TABLE IF NOT EXISTS reliable_reports (supplier TEXT NOT NULL, previous_id INTEGER NOT NULL, current_id INTEGER NOT NULL, policy TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(supplier,previous_id,current_id,policy))')


def reliable_changes(domain: str, *, previous_snapshot_id: int, current_snapshot_id: int,
                     recheck_snapshot_id: int | None = None, db_path: str = DEFAULT_DB_PATH) -> dict:
    """Compare explicit persisted captures; rechecks never perform network requests."""
    if not isinstance(domain, str) or not domain.strip():
        raise ValueError('Domain must be a nonempty supplier string')
    for sid in (previous_snapshot_id, current_snapshot_id, recheck_snapshot_id):
        if sid is not None and (type(sid) is not int or sid < 1):
            raise ValueError('Snapshot IDs must be positive integers')
    if previous_snapshot_id is None or current_snapshot_id is None:
        raise ValueError('Two explicit snapshot IDs required')
    supplier = supplier_scope(domain)
    if not supplier.strip():
        raise ValueError('Domain must identify a nonempty supplier')
    if not Path(db_path).expanduser().is_file():
        raise FileNotFoundError(db_path)
    conn = _get_connection(db_path, initialize=False)
    try:
        with conn:
            conn.execute('BEGIN IMMEDIATE')
            _ensure_snapshot_metadata(conn)
            _ensure_evidence_schema(conn, backfill=False)
            previous = _metadata(conn, previous_snapshot_id, supplier)
            current = _metadata(conn, current_snapshot_id, supplier)
            if (previous['created_at'], previous_snapshot_id) >= (current['created_at'], current_snapshot_id):
                raise ValueError('Snapshot ordering must be previous before current')
            recheck = None
            if recheck_snapshot_id is not None:
                recheck = _metadata(conn, recheck_snapshot_id, supplier)
                if (recheck['created_at'], recheck_snapshot_id) <= (current['created_at'], current_snapshot_id):
                    raise ValueError('Recheck must be later than current')
                if not current['observation_scope'] or recheck['observation_scope'] != current['observation_scope'] or previous['observation_scope'] != current['observation_scope']:
                    raise ValueError('Recheck must have known matching scope')
            _schema(conn)
            key = (supplier, previous_snapshot_id, current_snapshot_id, POLICY_VERSION)
            stored_size = conn.execute('SELECT length(CAST(payload AS BLOB)) FROM reliable_reports WHERE supplier=? AND previous_id=? AND current_id=? AND policy=?', key).fetchone()
            if stored_size:
                if stored_size[0] > MAX_REPORT_BYTES:
                    raise ValueError('Stored report exceeds size limit')
                stored = conn.execute('SELECT payload FROM reliable_reports WHERE supplier=? AND previous_id=? AND current_id=? AND policy=?', key).fetchone()
                envelope = decode_value(_parse(stored[0]))
                report, currencies = envelope['report'], {tuple(k): v for k, v in envelope['currencies']}
                published = {c['event_id'] for c in report['candidates'] if c['state'] == 'confirmed'}
            else:
                old, new = _load(conn, previous, supplier), _load(conn, current, supplier)
                report = dict(report_id=_identifier(*key), policy_version=POLICY_VERSION, supplier=supplier,
                    previous_snapshot_id=previous_snapshot_id, current_snapshot_id=current_snapshot_id,
                    status='compared', reason='evaluated_supported_facts', candidates=[], events=[], new_events=[], diagnostics=[])
                _compare(report, old, new, previous, current)
                currencies = {entity: _currency(new, entity) for entity in new}
                published = set()
            if recheck:
                checked = _load(conn, recheck, supplier)
                _recheck(report, checked, recheck, currencies)
            report['candidates'].sort(key=lambda c: (c['canonical_product_id'], c['canonical_variant_id'] or '', c['field_path'], c['kind']))
            report['diagnostics'].sort(key=lambda d: (d['canonical_product_id'], d['canonical_variant_id'] or '', d['field_path'], d['reason']))
            report['events'] = [c for c in report['candidates'] if c['state'] == 'confirmed']
            report['new_events'] = []
            _entries(report)
            payload = _json(dict(report=report, currencies=[[list(k), v] for k, v in currencies.items()]))
            if len(payload.encode()) > MAX_REPORT_BYTES:
                raise ValueError('Serialized report exceeds size limit')
            conn.execute('INSERT OR REPLACE INTO reliable_reports VALUES (?,?,?,?,?)', (*key, payload))
            _before_commit(conn)
            report['new_events'] = [c for c in report['events'] if c['event_id'] not in published]
        return decode_value(json.loads(_json(report)))
    except (TypeError, AttributeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('Corrupt selected snapshot or evidence storage') from exc
    finally:
        conn.close()
