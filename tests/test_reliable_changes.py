"""Predesigned SC01–18 acceptance: missing behavior must fail, never xfail."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import sqlite3
from uuid import UUID
from threading import Barrier

import pytest

from shopextract import Evidence, FieldObservation, Product, TrustContract, Variant
from shopextract.monitor import reliable
from shopextract.monitor.evidence import get_evidence, prune_evidence, save_snapshot

DOMAIN = 'shop.example'
SCOPE = 'catalog:shop.example:all'
T0 = datetime(2026, 10, 16, 10, tzinfo=timezone.utc)


def graph(values, tick=0, *, role='supplier', state='observed', age=0, start=1):
    evidence, observations = [], []
    for number, (path, value) in enumerate(values.items(), start):
        eid, oid = 'e_' + str(UUID(int=number)), 'o_' + str(UUID(int=number))
        evidence.append(Evidence(eid, 'https://shop.example/source',
                                 T0 + timedelta(hours=tick, seconds=-age), 'fixture',
                                 retained_data={'value': value}, pointer='/value', source_role=role))
        observations.append(FieldObservation(oid, path, state, value, value,
                            [eid] if state == 'observed' else [],
                            reason='' if state == 'observed' else 'Fixture unavailable'))
    return TrustContract(evidence, observations)


def product(price='10', *, tick=0, key='a', title='Widget', currency='EUR',
            fields=None, state='observed', age=0, variants=()):
    values = {'/price': Decimal(price), '/currency': currency}
    if fields is not None:
        values = fields
    p = Product(title=title, price=Decimal(price), currency=currency, external_id=key,
                product_url=f'https://shop.example/products/{key}',
                canonical_product_id='p_' + key, supplier_id=DOMAIN, variants=list(variants))
    for path, value in values.items():
        if path.startswith('/attributes/'):
            p.attributes[path.split('/', 2)[2].replace('~1', '/').replace('~0', '~')] = str(value)
        elif path in {'/in_stock', '/pack_quantity'}:
            setattr(p, path[1:], value if (path == '/in_stock' and isinstance(value, bool)) or (path == '/pack_quantity' and type(value) is int and value > 0) else (True if path == '/in_stock' else 1))
    p.evidence_contract = graph(values, tick, state=state, age=age)
    return p


def variant(key, price, tick=0):
    v = Variant(variant_id=key, canonical_variant_id='v_' + key, price=Decimal(price))
    v.evidence_contract = graph({'/price': Decimal(price)}, tick)
    return v


@pytest.fixture
def db(tmp_path):
    return str(tmp_path / 'snapshots.db')


def save(db, products, tick, *, complete=True, scope=SCOPE, domain=DOMAIN):
    sid = save_snapshot(products, domain, db_path=db, metadata={
        'observation_scope': scope, 'catalog_complete': complete})
    with sqlite3.connect(db) as conn:
        conn.execute('UPDATE snapshots SET created_at=? WHERE id=?',
                     ((T0 + timedelta(hours=tick)).isoformat(), sid))
    return sid


def pair(db, old=None, new=None, **metadata):
    a = save(db, old if old is not None else [product()], 0, **metadata)
    b = save(db, new if new is not None else [product('11', tick=1)], 1, **metadata)
    return a, b


def assert_contract(r):
    assert set(r) == {'report_id', 'policy_version', 'supplier', 'previous_snapshot_id',
        'current_snapshot_id', 'status', 'reason', 'candidates', 'events', 'new_events', 'diagnostics'}
    assert all(isinstance(r[k], str) and r[k] for k in ['report_id', 'policy_version', 'supplier', 'status', 'reason'])
    assert all(type(r[k]) is int for k in ['previous_snapshot_id', 'current_snapshot_id'])
    assert all(isinstance(r[k], list) for k in ['candidates', 'events', 'new_events', 'diagnostics'])
    assert r['status'] in {'compared', 'suppressed'}
    for c in r['candidates']:
        assert set(c) == {'candidate_id', 'event_id', 'kind', 'state', 'reason', 'supplier',
            'canonical_product_id', 'canonical_variant_id', 'field_path', 'previous_snapshot_id',
            'current_snapshot_id', 'old', 'new', 'recheck'}
        assert c['state'] in {'confirmed', 'pending', 'rejected'}
        assert c['kind'] in {'field_changed', 'product_added', 'product_removed'}
        assert all(isinstance(c[k], str) and c[k] for k in ['candidate_id', 'event_id', 'reason', 'canonical_product_id'])
        assert c['canonical_variant_id'] is None or isinstance(c['canonical_variant_id'], str)
        assert isinstance(c['field_path'], str) and c['supplier'] == r['supplier']
        assert c['previous_snapshot_id'] == r['previous_snapshot_id']
        assert c['current_snapshot_id'] == r['current_snapshot_id']
        for side in [c['old'], c['new']] + ([c['recheck']] if c['recheck'] else []):
            assert set(side) == {'state', 'value', 'references', 'coverage'}
            assert side['state'] in {'observed', 'unknown', 'absent'}
            assert isinstance(side['references'], list)
            assert (side['value'] is None) == (side['state'] != 'observed')
            for ref in side['references']:
                assert set(ref) == {'snapshot_id', 'record_key', 'observation_id', 'evidence_ids'}
                assert type(ref['snapshot_id']) is int
                assert isinstance(ref['record_key'], str) and isinstance(ref['observation_id'], str)
                assert isinstance(ref['evidence_ids'], list) and ref['evidence_ids']
                assert ref['observation_id'].startswith('o_')
                assert all(isinstance(e, str) and e.startswith('e_') for e in ref['evidence_ids'])
            if side['coverage'] is not None:
                assert set(side['coverage']) == {'snapshot_id', 'observation_scope', 'catalog_complete', 'incompleteness_reasons'}
    assert r['events'] == [c for c in r['candidates'] if c['state'] == 'confirmed']
    assert all(e in r['events'] for e in r['new_events'])
    for d in r['diagnostics']:
        assert set(d) == {'canonical_product_id', 'canonical_variant_id', 'field_path', 'reason', 'details'}
        assert isinstance(d['reason'], str) and d['reason']
        assert isinstance(d['details'], dict)
    keys = [(c['canonical_product_id'], c['canonical_variant_id'] or '', c['field_path'], c['kind']) for c in r['candidates']]
    assert keys == sorted(keys)


def report(db, a, b, recheck=None):
    r = reliable.reliable_changes(DOMAIN, previous_snapshot_id=a,
        current_snapshot_id=b, recheck_snapshot_id=recheck, db_path=db)
    assert_contract(r)
    return r


def only(report, collection='events'):
    assert len(report[collection]) == 1
    return report[collection][0]


def test_sc01_price_evidence_and_durable_reopen(db):
    a, b = pair(db)
    first = report(db, a, b)
    event = only(first)
    assert first['policy_version'] == 'reliable-change-v1'
    assert event['field_path'] == '/price' and event['canonical_product_id'] == 'p_a'
    assert event['old']['value'] == Decimal('10') and event['new']['value'] == Decimal('11')
    for side, sid in [('old', a), ('new', b)]:
        ref = only({'events': event[side]['references']})
        assert ref['snapshot_id'] == sid and ref['record_key'] == 'product/0'
        assert ref['observation_id'].startswith('o_')
        lookup = get_evidence(ref['evidence_ids'][0], snapshot_id=sid,
                              record_key=ref['record_key'], db_path=db)
        assert lookup.status == 'available'
        assert lookup.evidence.source_url == 'https://shop.example/source'
        assert lookup.evidence.observed_at == T0 + timedelta(hours=0 if side == 'old' else 1)
    assert first['new_events'] == first['events']
    replay = report(db, a, b)
    assert replay['report_id'] == first['report_id']
    assert replay['events'] == first['events'] and replay['new_events'] == []


def test_sc01_title_rename_and_shared_display_title(db):
    old = [product(key='a'), product(key='b')]
    new = [product(key='a', title='Renamed', tick=1), product('11', key='b', tick=1)]
    a, b = pair(db, old, new)
    assert only(report(db, a, b))['canonical_product_id'] == 'p_b'


def test_sc02_variant_reordering(db):
    a, b = pair(db, [product(variants=[variant('x', '10'), variant('y', '10')])],
        [product(tick=1, variants=[variant('y', '10', 1), variant('x', '11', 1)])])
    e = only(report(db, a, b))
    assert e['canonical_variant_id'] == 'v_x' and e['field_path'] == '/price'
    assert e['old']['references'][0]['record_key'] == 'product/0/variant/0'
    assert e['new']['references'][0]['record_key'] == 'product/0/variant/1'


@pytest.mark.parametrize('path,left,right', [('/in_stock', True, False),
    ('/pack_quantity', 1, 2), ('/attributes/warranty', '12 months', '24 months'),
    ('/attributes/pack_size', '1 L', '1000 ml'), ('/attributes/a~1b~0c', 'x', 'y')])
def test_sc03_tracked_leaf_changes(db, path, left, right):
    a, b = pair(db, [product(fields={path: left})], [product(fields={path: right}, tick=1)])
    e = only(report(db, a, b))
    assert e['field_path'] == path and e['state'] == 'confirmed'
    assert e['old']['value'] == left and e['new']['value'] == right


@pytest.mark.parametrize('fields', [{}, {'/price': True, '/currency': 'EUR'},
    {'/price': Decimal('-1'), '/currency': 'EUR'}, {'/pack_quantity': True},
    {'/in_stock': 0}, {'/currency': 'eur'}, {'/attributes/warranty': None}])
def test_sc04_invalid_or_missing_never_becomes_default(db, fields):
    # Observed null is forbidden by TrustContract: represent it as unknown support.
    state = 'unknown' if None in fields.values() else 'observed'
    a, b = pair(db, [product()], [product(tick=1, fields=fields, state=state)])
    r = report(db, a, b)
    assert r['events'] == [] and r['diagnostics']


@pytest.mark.parametrize('state,age', [('unknown', 0), ('unsupported', 0),
    ('conflicting', 0), ('observed', 86401), ('observed', -1)])
def test_sc05_unavailable_support(db, state, age):
    a, b = pair(db, [product()], [product('11', tick=1, state=state, age=age)])
    r = report(db, a, b)
    assert r['events'] == [] and r['diagnostics']


def test_sc05_selected_refs_exclude_competing_evidence(db):
    new = product('11', tick=1)
    extra = graph({'/price': Decimal('99')}, 1, role='unverified', start=9)
    new.evidence_contract.evidence.extend(extra.evidence)
    new.evidence_contract.observations.extend(extra.observations)
    a, b = pair(db, new=[new])
    e = only(report(db, a, b))
    assert e['new']['references'][0]['evidence_ids'] == [new.evidence_contract.evidence[0].evidence_id]
    assert extra.evidence[0].evidence_id not in json.dumps(e['new']['references'])


@pytest.mark.parametrize('left,right,equal', [(Decimal('10.00'), 10, True),
    (' Café ', 'Cafe\u0301', True), ({'b': 2, 'a': 1}, {'a': 1, 'b': 2}, True),
    ([1, 2], [2, 1], False), (False, 0, False)])
def test_sc06_typed_equivalence(db, left, right, equal):
    path = '/attributes/test'
    a, b = pair(db, [product(fields={path: left})], [product(tick=1, fields={path: right})])
    assert len(report(db, a, b)['events']) == (0 if equal else 1)


@pytest.mark.parametrize('currency', ['USD', None])
def test_sc07_currency_gates_price(db, currency):
    fields = {'/price': Decimal('12')}
    if currency is not None:
        fields['/currency'] = currency
    a, b = pair(db, new=[product('12', tick=1, fields=fields)])
    r = report(db, a, b)
    assert r['events'] == []
    assert not any(c['field_path'] == '/price' for c in r['candidates'])
    if currency:
        assert only(r, 'candidates')['state'] == 'pending'
    assert any(d['reason'] == ('currency_mismatch' if currency else 'currency_unverified')
               for d in r['diagnostics'])


@pytest.mark.parametrize('complete', [False, None, True])
def test_sc08_missing_products_never_immediate_removal(db, complete):
    a = save(db, [product(key=str(i)) for i in range(5)], 0)
    b = save(db, [], 1, complete=complete)
    r = report(db, a, b)
    assert r['events'] == []
    if complete is True:
        assert len(r['candidates']) == 5
        assert {c['state'] for c in r['candidates']} == {'pending'}
    else:
        assert r['diagnostics']


def test_sc09_confirmed_removal_with_two_complete_absences(db):
    a, b = pair(db, new=[])
    c = save(db, [], 2)
    e = only(report(db, a, b, c))
    assert e['kind'] == 'product_removed' and e['new']['state'] == 'absent'
    assert e['new']['references'] == []
    assert e['new']['coverage']['snapshot_id'] == b
    assert e['recheck']['coverage']['snapshot_id'] == c


@pytest.mark.parametrize('reappears,complete,expected', [(True, True, 'rejected'),
    (False, False, 'pending'), (False, None, 'pending')])
def test_sc10_removal_recheck_health(db, reappears, complete, expected):
    a, b = pair(db, new=[])
    c = save(db, [product(tick=2)] if reappears else [], 2, complete=complete)
    r = report(db, a, b, c)
    assert r['events'] == [] and only(r, 'candidates')['state'] == expected


@pytest.mark.parametrize('complete,expected', [(True, 1), (False, 0), (None, 0)])
def test_sc11_addition_requires_complete_baseline(db, complete, expected):
    a = save(db, [], 0, complete=complete)
    b = save(db, [product(tick=1)], 1, complete=False)
    r = report(db, a, b)
    assert len(r['events']) == expected
    if expected:
        assert only(r)['old']['state'] == 'absent'


def test_sc11_variant_absence_is_diagnostic(db):
    a, b = pair(db, [product(variants=[variant('x', '10')])], [product(tick=1)])
    r = report(db, a, b)
    assert r['events'] == [] and r['diagnostics']


@pytest.mark.parametrize('scope', [None, 'different'])
def test_sc12_scope_suppression(db, scope):
    a = save(db, [product()], 0)
    b = save(db, [product('11', tick=1)], 1, scope=scope)
    r = report(db, a, b)
    assert r['status'] == 'suppressed' and not r['events'] and not r['candidates']


@pytest.mark.parametrize('bad', ['missing', 'reversed', 'equal', 'supplier'])
def test_sc12_invalid_pairs(db, bad):
    a, b = pair(db)
    if bad == 'missing':
        b = 99999
    elif bad == 'reversed':
        a, b = b, a
    elif bad == 'equal':
        b = a
    else:
        b = save(db, [product('11', tick=2)], 2, domain='else.example')
    with pytest.raises((ValueError, KeyError)):
        report(db, a, b)


@pytest.mark.parametrize('price,pending', [('50', True), ('200', True),
    ('50.01', False), ('199.99', False), ('0', True)])
def test_sc13_suspicious_boundaries(db, price, pending):
    a, b = pair(db, [product('100')], [product(price, tick=1)])
    r = report(db, a, b)
    assert only(r, 'candidates')['state'] == ('pending' if pending else 'confirmed')
    assert len(r['events']) == (0 if pending else 1)


@pytest.mark.parametrize('value,currency,state', [('50', 'EUR', 'confirmed'),
    ('100', 'EUR', 'rejected'), ('75', 'EUR', 'rejected'), ('50', 'USD', 'pending'),
    ('50', None, 'pending')])
def test_sc14_recheck_price_requires_same_currency(db, value, currency, state):
    a, b = pair(db, [product('100')], [product('50', tick=1)])
    fields = {'/price': Decimal(value)}
    if currency:
        fields['/currency'] = currency
    c = save(db, [product(value, tick=2, fields=fields)], 2)
    r = report(db, a, b, c)
    candidate = only(r, 'candidates')
    assert candidate['state'] == state
    if currency != 'EUR':
        assert candidate['reason'] == ('currency_mismatch' if currency else 'currency_unverified')
    elif value == '75':
        assert candidate['reason'] == 'superseded_value'
    if currency == 'EUR':
        ref = candidate['recheck']['references'][0]
        assert ref == {'snapshot_id': c, 'record_key': 'product/0',
            'observation_id': 'o_' + str(UUID(int=1)), 'evidence_ids': ['e_' + str(UUID(int=1))]}
    assert len(r['events']) == (state == 'confirmed')


@pytest.mark.parametrize('bad', ['missing', 'old', 'supplier', 'scope'])
def test_sc14_invalid_recheck_is_atomic(db, bad):
    a, b = pair(db, [product('100')], [product('50', tick=1)])
    original = report(db, a, b)
    c = save(db, [product('50', tick=2)], 2,
             domain='other.example' if bad == 'supplier' else DOMAIN,
             scope='other' if bad == 'scope' else SCOPE)
    c = 9999 if bad == 'missing' else a if bad == 'old' else c
    with pytest.raises((ValueError, KeyError)):
        report(db, a, b, c)
    assert report(db, a, b)['candidates'] == original['candidates']


def test_sc15_terminal_recheck_replay_and_reversals(db):
    a, b = pair(db, [product('100')], [product('50', tick=1)])
    c = save(db, [product('50', tick=2)], 2)
    first = report(db, a, b, c)
    assert len(first['new_events']) == 1
    assert report(db, a, b, c)['new_events'] == []
    d = save(db, [product('100', tick=3)], 3)
    assert report(db, a, b, d)['events'] == first['events']
    assert report(db, b, c)['events'] == []
    e = save(db, [product('100', tick=4)], 4)
    assert only(report(db, c, d, e))['event_id'] != only(first)['event_id']


def test_sc16_race_has_one_publisher(db):
    a, b = pair(db)
    barrier = Barrier(2)
    def run(_):
        barrier.wait(timeout=5)
        return report(db, a, b)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run, range(2)))
    assert sum(len(r['new_events']) for r in results) == 1
    assert results[0]['events'] == results[1]['events']


def test_sc16_rollback_after_ledger_write(db, monkeypatch):
    a, b = pair(db)
    class InjectedFailure(Exception):
        pass
    def fail(connection):
        raise InjectedFailure('injected-before-commit')
    with monkeypatch.context() as patch:
        patch.setattr(reliable, '_before_commit', fail)
        with pytest.raises(InjectedFailure, match='injected-before-commit'):
            report(db, a, b)
    assert len(report(db, a, b)['new_events']) == 1


@pytest.mark.parametrize('limit', ['MAX_SNAPSHOT_BYTES', 'MAX_REPORT_BYTES', 'MAX_REPORT_ENTRIES'])
def test_sc16_limits_are_atomic_errors(db, monkeypatch, limit):
    a, b = pair(db)
    with monkeypatch.context() as patch:
        patch.setattr(reliable, limit, 0 if limit == 'MAX_REPORT_ENTRIES' else 1)
        with pytest.raises(ValueError, match='limit|exceed|size|bound'):
            report(db, a, b)
    assert len(report(db, a, b)['new_events']) == 1


def test_sc17_frozen_reports_survive_pruning_and_detached_mutation(db):
    a, b = pair(db)
    r = report(db, a, b)
    expected = deepcopy(r['events'])
    ref = only(r)['old']['references'][0]
    prune_evidence(db_path=db, before=T0 + timedelta(days=1),
                   protect_references=False, dry_run=False)
    r['events'][0]['new']['value'] = Decimal('999')
    replay = report(db, a, b)
    assert replay['events'] == expected and replay['new_events'] == []
    assert get_evidence(ref['evidence_ids'][0], snapshot_id=a,
                        record_key=ref['record_key'], db_path=db).status == 'expired'


@pytest.mark.parametrize('legacy_domain', ['unrelated.example', DOMAIN])
def test_sc18_unrelated_bad_legacy_history_not_migrated(db, legacy_domain):
    a, b = pair(db)
    with sqlite3.connect(db) as conn:
        conn.execute("INSERT INTO snapshots(domain,products_json,created_at) VALUES (?,?,?)",
                     (legacy_domain, 'not-json', T0.isoformat()))
    assert len(report(db, a, b)['events']) == 1
    with sqlite3.connect(db) as conn:
        assert conn.execute("SELECT count(*) FROM snapshots WHERE products_json='not-json'").fetchone()[0] == 1


@pytest.mark.parametrize('old,new,count,pending', [('0', '0', 0, False), ('0', '1', 0, True), ('11', '10', 1, False)])
def test_sc04_sc13_zero_and_ordinary_prices(db, old, new, count, pending):
    a, b = pair(db, [product(old)], [product(new, tick=1)])
    r = report(db, a, b)
    assert len(r['events']) == count
    if pending:
        assert only(r, 'candidates')['state'] == 'pending'


def test_sc05_equal_authority_conflict_and_expired_source(db):
    new = product('11', tick=1)
    competing = graph({'/price': Decimal('12')}, 1, start=9)
    new.evidence_contract.evidence.extend(competing.evidence)
    new.evidence_contract.observations.extend(competing.observations)
    a, b = pair(db, new=[new])
    assert report(db, a, b)['events'] == []
    c, d = pair(db)
    prune_evidence(db_path=db, before=T0 + timedelta(days=1),
                   protect_references=False, dry_run=False)
    r = report(db, c, d)
    assert r['events'] == [] and r['diagnostics']


def test_sc12_duplicate_identity_and_corrupt_graph_errors(db):
    a, b = pair(db)
    with sqlite3.connect(db) as conn:
        payload = json.loads(conn.execute('SELECT products_json FROM snapshots WHERE id=?', (b,)).fetchone()[0])
        conn.execute('UPDATE snapshots SET products_json=? WHERE id=?', (json.dumps(payload * 2), b))
    with pytest.raises(ValueError):
        report(db, a, b)
    with sqlite3.connect(db) as conn:
        conn.execute('UPDATE snapshots SET products_json=? WHERE id=?', (json.dumps(payload), b))
        conn.execute("UPDATE evidence_owners SET graph_json='not-json' WHERE snapshot_id=?", (b,))
    with pytest.raises(ValueError):
        report(db, a, b)


@pytest.mark.parametrize('currency', ['USD', None])
def test_sc14_variant_recheck_uses_parent_currency(db, currency):
    a, b = pair(db, [product(variants=[variant('x', '100')])],
                     [product(tick=1, variants=[variant('x', '50', 1)])])
    values = {'/currency': currency} if currency else {}
    c = save(db, [product(tick=2, fields=values, variants=[variant('x', '50', 2)])], 2)
    r = report(db, a, b, c)
    assert r['events'] == []
    candidate = only(r, 'candidates')
    assert candidate['state'] == 'pending'
    assert candidate['reason'] == ('currency_mismatch' if currency else 'currency_unverified')


def test_sc16_sqlite_lock_is_bounded(db):
    import time
    a, b = pair(db)
    blocker = sqlite3.connect(db)
    blocker.execute('BEGIN IMMEDIATE')
    started = time.monotonic()
    try:
        with pytest.raises(sqlite3.OperationalError, match='locked'):
            report(db, a, b)
    finally:
        blocker.rollback()
        blocker.close()
    assert time.monotonic() - started < 7


def test_sc18_selected_legacy_scalars_are_unsupported(db):
    a, b = pair(db)
    with sqlite3.connect(db) as conn:
        conn.execute('DELETE FROM evidence_products WHERE snapshot_id IN (?,?)', (a, b))
        conn.execute('DELETE FROM evidence_owners WHERE snapshot_id IN (?,?)', (a, b))
    r = report(db, a, b)
    assert not r['events'] and r['diagnostics']


@pytest.mark.parametrize('currency,state,reason', [('USD', 'confirmed', None),
    ('EUR', 'rejected', None), ('GBP', 'rejected', 'superseded_value'),
    (None, 'pending', 'unverified_recheck')])
def test_sc14_currency_candidate_recheck(db, currency, state, reason):
    a, b = pair(db, [product(currency='EUR')], [product(tick=1, currency='USD')])
    fields = {'/currency': currency} if currency else {}
    c = save(db, [product(tick=2, fields=fields)], 2)
    candidate = only(report(db, a, b, c), 'candidates')
    assert candidate['field_path'] == '/currency' and candidate['state'] == state
    if reason:
        assert candidate['reason'] == reason
    if currency:
        ref = candidate['recheck']['references'][0]
        assert ref == {'snapshot_id': c, 'record_key': 'product/0',
            'observation_id': 'o_' + str(UUID(int=1)), 'evidence_ids': ['e_' + str(UUID(int=1))]}
        source = get_evidence(ref['evidence_ids'][0], snapshot_id=c, record_key='product/0', db_path=db)
        assert source.evidence.observed_at == T0 + timedelta(hours=2)


def test_sc14_unsupported_price_recheck(db):
    a, b = pair(db, [product('100')], [product('50', tick=1)])
    c = save(db, [product('50', tick=2, fields={'/currency': 'EUR'})], 2)
    candidate = only(report(db, a, b, c), 'candidates')
    assert candidate['state'] == 'pending' and candidate['reason'] == 'unverified_recheck'


def test_sc11_unsupported_new_record_is_not_addition(db):
    a = save(db, [], 0)
    b = save(db, [product(tick=1, fields={})], 1)
    r = report(db, a, b)
    assert not r['events'] and not r['candidates'] and r['diagnostics']


def test_sc12_missing_identity_rejects_without_database_changes(db):
    a, b = pair(db)
    with sqlite3.connect(db) as conn:
        products = json.loads(conn.execute('SELECT products_json FROM snapshots WHERE id=?', (b,)).fetchone()[0])
        products[0]['canonical_product_id'] = ''
        conn.execute('UPDATE snapshots SET products_json=? WHERE id=?', (json.dumps(products), b))
        record = json.loads(conn.execute('SELECT record_json FROM evidence_products WHERE snapshot_id=?', (b,)).fetchone()[0])
        record['product']['canonical_product_id'] = ''
        conn.execute('UPDATE evidence_products SET record_json=? WHERE snapshot_id=?', (json.dumps(record), b))
        before = list(conn.iterdump())
    with pytest.raises(ValueError, match='identity|canonical'):
        report(db, a, b)
    with sqlite3.connect(db) as conn:
        assert list(conn.iterdump()) == before


def test_sc12_nonfinite_stored_graph_rejected_atomically(db):
    a, b = pair(db)
    with sqlite3.connect(db) as conn:
        stored = json.loads(conn.execute('SELECT graph_json FROM evidence_owners WHERE snapshot_id=?', (b,)).fetchone()[0])
        stored['observations'][0]['normalized_value'] = {'$type': 'decimal', 'value': 'NaN'}
        conn.execute('UPDATE evidence_owners SET graph_json=? WHERE snapshot_id=?', (json.dumps(stored), b))
        before = list(conn.iterdump())
    with pytest.raises(ValueError):
        report(db, a, b)
    with sqlite3.connect(db) as conn:
        assert list(conn.iterdump()) == before


def test_sc16_simultaneous_recheck_has_one_publisher(db):
    a, b = pair(db, [product('100')], [product('50', tick=1)])
    assert only(report(db, a, b), 'candidates')['state'] == 'pending'
    c = save(db, [product('50', tick=2)], 2)
    barrier = Barrier(2)
    def run(_):
        barrier.wait(timeout=5)
        return report(db, a, b, c)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(run, range(2)))
    assert sum(len(r['new_events']) for r in results) == 1
    assert results[0]['events'] == results[1]['events']


def test_sc17_deterministic_entity_field_order(db):
    a, b = pair(db, [product(key='z'), product(key='a')],
                     [product('11', key='a', tick=1), product('12', key='z', tick=1)])
    r = report(db, a, b)
    assert [e['canonical_product_id'] for e in r['events']] == ['p_a', 'p_z']


@pytest.mark.parametrize('unhealthy_side', ['previous', 'current', 'recheck'])
def test_sc08_failure_reasons_override_complete_flag(db, unhealthy_side):
    if unhealthy_side == 'previous':
        a = save(db, [], 0)
        b = save(db, [product(tick=1)], 1)
        selected, recheck = a, None
    else:
        a, b = pair(db, new=[])
        recheck = save(db, [], 2)
        selected = b if unhealthy_side == 'current' else recheck
    with sqlite3.connect(db) as conn:
        conn.execute('UPDATE snapshots SET incompleteness_reasons_json=? WHERE id=?',
                     (json.dumps(['source_timeout']), selected))
    r = report(db, a, b, recheck)
    assert not r['events']
    assert not any(c['state'] == 'confirmed' for c in r['candidates'])


@pytest.mark.parametrize('domain', [None, 42, '   ', 'http://'])
def test_sc12_invalid_domain_is_value_error_without_writes(db, domain):
    a, b = pair(db)
    with sqlite3.connect(db) as conn:
        before = list(conn.iterdump())
    with pytest.raises(ValueError):
        reliable.reliable_changes(domain, previous_snapshot_id=a,
                                 current_snapshot_id=b, db_path=db)
    with sqlite3.connect(db) as conn:
        assert list(conn.iterdump()) == before


def test_sc16_oversized_ledger_rejected_before_materializing_text(db, monkeypatch):
    a, b = pair(db)
    report(db, a, b)
    oversized = 'oversized-corrupt-ledger-' * 20
    with sqlite3.connect(db) as conn:
        conn.execute('UPDATE reliable_reports SET payload=?', (oversized,))
        before = list(conn.iterdump())
    original = reliable._get_connection
    def guarded_connection(*args, **kwargs):
        conn = original(*args, **kwargs)
        def bounded_text(value):
            if value == oversized.encode():
                raise AssertionError('Oversized report text materialized before size rejection')
            return value.decode()
        conn.text_factory = bounded_text
        return conn
    monkeypatch.setattr(reliable, '_get_connection', guarded_connection)
    monkeypatch.setattr(reliable, 'MAX_REPORT_BYTES', 64)
    with pytest.raises(ValueError, match='size|exceed|limit'):
        report(db, a, b)
    with sqlite3.connect(db) as conn:
        assert list(conn.iterdump()) == before
