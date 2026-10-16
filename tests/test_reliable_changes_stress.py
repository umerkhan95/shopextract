"""Distinct, manifest-driven synthetic mechanism checks; no network or inference."""
from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from pathlib import Path
import random
import sqlite3
from unittest.mock import patch
from uuid import NAMESPACE_URL, uuid5

import pytest

from shopextract import Evidence, FieldObservation, Platform, SupportState
from shopextract._capture import capture
from shopextract._normalize import normalize
from shopextract.monitor import reliable
from shopextract.monitor.evidence import get_evidence, load_snapshot, prune_evidence, save_snapshot

BASE = 'https://synthetic.example'
DOMAIN = 'synthetic.example'
SCOPE = 'synthetic:reviewed-mechanism'
AT = datetime(2026, 10, 16, 10, tzinfo=timezone.utc)


def raw_product(key, prices=('100', '130'), stocks=None, currency='EUR', **extra):
    stocks = stocks or [True] * len(prices)
    return dict(id=key, title='Shared catalog title', handle='item-' + key,
        currency=currency, vendor='Synthetic supplier', body_html='<p>Fixture only</p>',
        variants=[dict(id=f'{key}-v{i}', title=f'Option {i}', sku=f'{key}-sku{i}',
            price=str(price), available=stocks[i], option1=f'size-{i}')
            for i, price in enumerate(prices)],
        synthetic_fields={'/pack_quantity': 1, '/attributes/warranty': '12 months'}, **extra)


def expected(pid, variant, path, old, new, state='confirmed', kind='field_changed'):
    return (pid, variant, kind, path, state, old, new)


def assert_reference_owner(candidate, loaded, ref):
    parts = ref['record_key'].split('/')
    assert len(parts) in {2, 4} and parts[0] == 'product'
    product = loaded[int(parts[1])]
    assert product.canonical_product_id == candidate['canonical_product_id']
    if len(parts) == 4:
        assert parts[2] == 'variant'
        assert product.variants[int(parts[3])].canonical_variant_id == candidate['canonical_variant_id']
    else:
        assert candidate['canonical_variant_id'] is None


class Batch:
    """Persist native synthetic observations, recording bounded reproducible inputs."""
    def __init__(self, path, name):
        self.root = Path(path)
        self.root.mkdir(parents=True, exist_ok=True)
        self.db = str(self.root / (name + '.db'))
        self.manifest = {'scenario': name, 'provenance': 'synthetic', 'snapshots': []}
        self.mapping, self.sources = {}, {}
        self.bytes = 0

    def save(self, raws, tick, complete=True, reasons=(), unsupported_price=False):
        assert len(raws) <= 20 and len(self.manifest['snapshots']) < 6
        assert all(len(r['variants']) <= 4 for r in raws)
        record = {'tick': tick, 'rows': deepcopy(raws), 'complete': complete,
                  'reasons': list(reasons), 'unsupported_price': unsupported_price}
        self.bytes += len(json.dumps(record, ensure_ascii=False).encode())
        assert self.bytes <= 2 * 1024 * 1024
        self.manifest['snapshots'].append(record)
        self.flush()
        products = []
        source_url = BASE + f'/synthetic/products?capture={tick}'
        at = AT + timedelta(hours=tick)
        for original in raws:
            raw = deepcopy(original)
            supplemental = raw.pop('synthetic_fields')
            capture(raw, source_url, 'synthetic_fixture', observed_at=at)
            product = normalize(raw, Platform.SHOPIFY, BASE)
            assert product is not None
            graph = product.evidence_contract
            for path, value in supplemental.items():
                if path == '/pack_quantity':
                    product.pack_quantity = value
                else:
                    product.attributes[path.split('/', 2)[2]] = value
                token = str(uuid5(NAMESPACE_URL, f'{original["id"]}:{tick}:{path}'))
                evidence = Evidence('e_' + token, source_url, at, 'synthetic_supplement',
                    retained_data={'value': value}, pointer='/value', source_role='supplier')
                graph.evidence.append(evidence)
                graph.observations.append(FieldObservation('o_' + token, path, 'observed', value, value, [evidence.evidence_id]))
            for owner in [product, *product.variants]:
                if unsupported_price:
                    for observation in owner.evidence_contract.observations:
                        if observation.field_path == '/price':
                            observation.state = SupportState.UNSUPPORTED
                            observation.normalized_value = None
                            observation.evidence_ids = []
                            observation.reason = 'synthetic unsupported-price boundary'
            products.append(product)
        sid = save_snapshot(products, DOMAIN, db_path=self.db, metadata={
            'observation_scope': SCOPE, 'catalog_complete': complete,
            'incompleteness_reasons': list(reasons)})
        with sqlite3.connect(self.db) as conn:
            conn.execute('UPDATE snapshots SET created_at=? WHERE id=?', (at.isoformat(), sid))
        loaded = load_snapshot(sid, db_path=self.db)
        for p in loaded:
            logical = str(p.external_id)
            previous = self.mapping.setdefault(p.canonical_product_id, logical)
            assert previous == logical
            assert sum(v == logical for v in self.mapping.values()) == 1
            for v in p.variants:
                logical_v = str(v.variant_id)
                assert self.mapping.setdefault(v.canonical_variant_id, logical_v) == logical_v
                assert sum(x == logical_v for x in self.mapping.values()) == 1
        self.sources[sid] = (source_url, at)
        return sid

    def flush(self):
        (self.root / 'current-manifest.json').write_text(json.dumps(self.manifest, ensure_ascii=False, indent=2))

    def report(self, a, b, c=None):
        return reliable.reliable_changes(DOMAIN, previous_snapshot_id=a,
            current_snapshot_id=b, recheck_snapshot_id=c, db_path=self.db)

    def assert_set(self, report, wanted):
        actual = set()
        for c in report['candidates']:
            old, new = c['old']['value'], c['new']['value']
            if c['kind'] != 'field_changed':
                old, new = c['old']['state'], c['new']['state']
                present = c['old'] if c['kind'] == 'product_removed' else c['new']
                absent = c['new'] if c['kind'] == 'product_removed' else c['old']
                present_sid = c['previous_snapshot_id'] if c['kind'] == 'product_removed' else c['current_snapshot_id']
                absent_sid = c['current_snapshot_id'] if c['kind'] == 'product_removed' else c['previous_snapshot_id']
                assert present['state'] == 'unknown' and present['value'] is None
                assert present['references'] and all(ref['snapshot_id'] == present_sid for ref in present['references'])
                assert present['coverage']['snapshot_id'] == present_sid
                assert absent['state'] == 'absent' and absent['value'] is None and not absent['references']
                assert absent['coverage']['snapshot_id'] == absent_sid
            actual.add((self.mapping[c['canonical_product_id']], self.mapping.get(c['canonical_variant_id']),
                c['kind'], c['field_path'], c['state'], old, new))
        assert actual == set(wanted), {'expected': repr(set(wanted)), 'actual': repr(actual)}
        order = [(c['canonical_product_id'], c['canonical_variant_id'] or '', c['field_path'], c['kind']) for c in report['candidates']]
        assert order == sorted(order)
        assert report['events'] == [c for c in report['candidates'] if c['state'] == 'confirmed']

    def check_refs(self, report, expired=False):
        checks = 0
        loaded_cache = {}
        for candidate in report['candidates']:
            for side in ['old', 'new', 'recheck']:
                value = candidate[side]
                if value is None:
                    continue
                for ref in value['references']:
                    if ref['snapshot_id'] not in loaded_cache:
                        loaded_cache[ref['snapshot_id']] = load_snapshot(ref['snapshot_id'], db_path=self.db)
                    loaded = loaded_cache[ref['snapshot_id']]
                    assert_reference_owner(candidate, loaded, ref)
                    parts = ref['record_key'].split('/')
                    owner = loaded[int(parts[1])]
                    if len(parts) == 4:
                        owner = owner.variants[int(parts[3])]
                    graph = owner.evidence_contract
                    observation = next(o for o in graph.observations if o.observation_id == ref['observation_id'])
                    if not expired:
                        assert observation.evidence_ids == ref['evidence_ids']
                    for eid in ref['evidence_ids']:
                        result = get_evidence(eid, snapshot_id=ref['snapshot_id'], record_key=ref['record_key'], db_path=self.db)
                        if expired:
                            assert result.status == 'expired'
                        else:
                            assert result.status == 'available'
                            evidence = result.evidence
                            assert (evidence.source_url, evidence.observed_at) == self.sources[ref['snapshot_id']]
                            assert evidence.source_role == ('supplier' if evidence.method == 'synthetic_supplement' else 'unverified')
                            assert evidence.method in {'synthetic_fixture', 'synthetic_supplement'}
                            assert evidence.resolve_pointer() == evidence.retained_data['value']
                        checks += 1
        assert checks > 0
        return checks


def dump(db):
    with sqlite3.connect(db) as conn:
        return list(conn.iterdump())


def smoke(path):
    b = Batch(path, 'SM01')
    a0 = raw_product('a', ('20', '30'), [True, False])
    z0 = raw_product('b', ('40', '50'))
    a1, z1 = deepcopy(a0), deepcopy(z0)
    a1['title'] = 'Renamed but same identity'
    a1['variants'][0].update(price='21', available=False)
    a1['variants'].reverse()
    z1['synthetic_fields'] = {'/pack_quantity': 2, '/attributes/warranty': '24 months'}
    a, c = b.save([a0, z0], 0), b.save([z1, a1], 1)
    wanted = [expected('a', None, '/price', Decimal('20'), Decimal('30')),
        expected('a', None, '/in_stock', True, False),
        expected('a', 'a-v0', '/price', Decimal('20'), Decimal('21')),
        expected('a', 'a-v0', '/in_stock', True, False),
        expected('b', None, '/pack_quantity', 1, 2),
        expected('b', None, '/attributes/warranty', '12 months', '24 months')]
    r = b.report(a, c)
    b.assert_set(r, wanted)
    checks = b.check_refs(r)
    assert len(r['new_events']) == 6 and not b.report(a, c)['new_events']
    return {'scenario': 'SM01', 'events': 6, 'reference_checks': checks, 'input_bytes': b.bytes}


def price_setup(path, name, removal=False):
    b = Batch(path, name)
    old = [raw_product('a'), raw_product('b')]
    if removal:
        old.append(raw_product('gone'))
    new = deepcopy(old[:2])
    new[0]['variants'][0]['price'] = '50'
    new[1]['synthetic_fields']['/attributes/warranty'] = '24 months'
    a, c = b.save(old, 0), b.save(new, 1)
    wanted = [expected('a', None, '/price', Decimal('100'), Decimal('50'), 'pending'),
        expected('a', 'a-v0', '/price', Decimal('100'), Decimal('50'), 'pending'),
        expected('b', None, '/attributes/warranty', '12 months', '24 months')]
    if removal:
        wanted.append(expected('gone', None, '', 'unknown', 'absent', 'pending', 'product_removed'))
    return b, a, c, new, wanted


def recheck_chain(path):
    b, a, c, new, wanted = price_setup(path, 'SM02')
    first = b.report(a, c)
    b.assert_set(first, wanted)
    assert len(first['new_events']) == 1
    usd = deepcopy(new)
    usd[0]['currency'] = 'USD'
    u = b.save(usd, 2)
    missing = b.save(new, 3, unsupported_price=True)
    final = b.save(new, 4)
    for sid, reason in [(u, 'currency_mismatch'), (missing, 'unverified_recheck')]:
        r = b.report(a, c, sid)
        b.assert_set(r, wanted)
        assert [x['reason'] for x in r['candidates'] if x['state'] == 'pending'] == [reason] * 2
        assert not r['new_events'] and not b.report(a, c, sid)['new_events']
    r = b.report(a, c, final)
    b.assert_set(r, [(*x[:4], 'confirmed', *x[5:]) for x in wanted])
    assert len(r['new_events']) == 2 and not b.report(a, c, final)['new_events']
    return {'scenario': 'SM02', 'rechecks': 3, 'reference_checks': b.check_refs(r)}


def terminal_expiry(path):
    b, a, c, new, wanted = price_setup(path, 'SM03', removal=True)
    b.report(a, c)
    final = b.save(new, 2)
    r = b.report(a, c, final)
    b.assert_set(r, [(*x[:4], 'confirmed', *x[5:]) for x in wanted])
    assert len(r['events']) == 4
    frozen = deepcopy(r['events'])
    pruned = prune_evidence(db_path=b.db, before=AT + timedelta(days=1), protect_references=False, dry_run=False, batch_size=1000)
    assert not pruned.has_more
    with sqlite3.connect(b.db) as conn:
        assert conn.execute("SELECT count(*) FROM evidence_records WHERE status='available'").fetchone()[0] == 0
    reversing = deepcopy(new)
    reversing[0]['variants'][0]['price'] = '100'
    reversing.append(raw_product('gone'))
    late = b.save(reversing, 3)
    replay = b.report(a, c, late)
    assert replay['events'] == frozen and not replay['new_events']
    return {'scenario': 'SM03', 'frozen_events': 4, 'expired_reference_checks': b.check_refs(replay, expired=True)}


def health_interaction(path):
    b = Batch(path, 'SM04')
    old = [raw_product('a'), raw_product('b'), raw_product('gone')]
    new = deepcopy(old[:2])
    new[0]['variants'][0]['price'] = '50'
    new[1]['synthetic_fields']['/attributes/warranty'] = '24 months'
    new.append(raw_product('added'))
    a = b.save(old, 0)
    c = b.save(new, 1, reasons=['source_error'])
    sid = b.save(new, 2, complete=False, unsupported_price=True)
    r = b.report(a, c, sid)
    wanted = [expected('a', None, '/price', Decimal('100'), Decimal('50'), 'pending'),
        expected('a', 'a-v0', '/price', Decimal('100'), Decimal('50'), 'pending'),
        expected('b', None, '/attributes/warranty', '12 months', '24 months'),
        expected('added', None, '', 'absent', 'unknown', kind='product_added')]
    b.assert_set(r, wanted)
    assert len(r['events']) == 2 and all(x['reason'] == 'unverified_recheck' for x in r['candidates'] if x['state'] == 'pending')
    assert any(d['reason'] == 'absence_unverified' for d in r['diagnostics'])
    return {'scenario': 'SM04', 'confirmed': 2, 'pending': 2, 'reference_checks': b.check_refs(r)}


def boundary(path, byte_limit=False):
    name = 'SM06' if byte_limit else 'SM05'
    b = Batch(path, name)
    a0 = raw_product('a', ('20', '30'), [True, False])
    z0 = raw_product('b', ('40', '50'))
    a1, z1 = deepcopy(a0), deepcopy(z0)
    a1['title'] = 'Renamed same anchored product'
    a1['variants'][0].update(price='21', available=False)
    a1['variants'].reverse()
    z1['synthetic_fields'] = {'/pack_quantity': 2, '/attributes/warranty': 'Garantía Café 24 mois'}
    a, c = b.save([a0, z0], 0), b.save([z1, a1], 1)
    wanted = [expected('a', None, '/price', Decimal('20'), Decimal('30')),
        expected('a', None, '/in_stock', True, False),
        expected('a', 'a-v0', '/price', Decimal('20'), Decimal('21')),
        expected('a', 'a-v0', '/in_stock', True, False),
        expected('b', None, '/pack_quantity', 1, 2),
        expected('b', None, '/attributes/warranty', '12 months', 'Garantía Café 24 mois')]
    r = b.report(a, c)
    b.assert_set(r, wanted)
    with sqlite3.connect(b.db) as conn:
        payload = conn.execute('SELECT payload FROM reliable_reports').fetchone()[0]
    limit = len(payload.encode()) if byte_limit else len(r['candidates']) + len(r['diagnostics'])
    constant = 'MAX_REPORT_BYTES' if byte_limit else 'MAX_REPORT_ENTRIES'
    for offset in [-1, 0, 1]:
        with sqlite3.connect(b.db) as conn:
            conn.execute('DELETE FROM reliable_reports')
        before = dump(b.db)
        with patch.object(reliable, constant, limit + offset):
            if offset < 0:
                with pytest.raises(ValueError):
                    b.report(a, c)
                assert dump(b.db) == before
            else:
                accepted = b.report(a, c)
                b.assert_set(accepted, wanted)
                assert len(accepted['new_events']) == 6
                assert not b.report(a, c)['new_events']
        # Exercise already persisted payload boundary independently from cold generation.
        if offset < 0:
            b.report(a, c)
            before = dump(b.db)
            with patch.object(reliable, constant, limit - 1):
                with pytest.raises(ValueError):
                    b.report(a, c)
            assert dump(b.db) == before
    assert not byte_limit or len(payload.encode()) > len(payload)
    return {'scenario': name, 'exact_limit': limit, 'offsets': [-1, 0, 1], 'utf8': byte_limit}


def rollback_update(path):
    b, a, c, new, wanted = price_setup(path, 'SM07')
    assert len(b.report(a, c)['new_events']) == 1
    sid = b.save(new, 2)
    before = dump(b.db)
    class Injected(Exception):
        pass
    def broken(conn):
        stored = conn.execute('SELECT payload FROM reliable_reports').fetchone()[0]
        assert 'confirmed_recheck' in stored
        raise Injected('real ledger update before commit')
    with patch.object(reliable, '_before_commit', broken):
        with pytest.raises(Injected):
            b.report(a, c, sid)
    assert dump(b.db) == before
    r = b.report(a, c, sid)
    b.assert_set(r, [(*x[:4], 'confirmed', *x[5:]) for x in wanted])
    assert len(r['new_events']) == 2 and not b.report(a, c, sid)['new_events']
    return {'scenario': 'SM07', 'atomic_update': True, 'new_events_after_retry': 2}


def fault_sensitivity(path):
    b, a, c, new, wanted = price_setup(path, 'SM08')
    b.report(a, c)
    changed = deepcopy(new)
    changed[0]['currency'] = 'USD'
    sid = b.save(changed, 2)
    def critical(result):
        prices = [x for x in result['candidates'] if x['field_path'] == '/price']
        assert len(prices) == 2 and all(x['state'] == 'pending' and x['reason'] == 'currency_mismatch' for x in prices)
        assert not result['new_events']
    critical(b.report(a, c, sid))
    fault_db = str(Path(path) / 'SM08-fault.db')
    with sqlite3.connect(b.db) as source, sqlite3.connect(fault_db) as destination:
        source.backup(destination)
    original_db = b.db
    try:
        b.db = fault_db
        with patch.object(reliable, '_currency_reason', lambda *args: None):
            with pytest.raises(AssertionError):
                critical(b.report(a, c, sid))
    finally:
        b.db = original_db
    critical(b.report(a, c, sid))
    return {'scenario': 'SM08', 'fault': 'currency gate bypass', 'mutation': 'detected/killed', 'restored': 'passed'}


def seeded_batch(path, seed, index):
    rng = random.Random(seed * 100 + index)
    count = [4, 6, 8, 10, 12, 14, 16, 20][index]
    old = [raw_product(f'p{i}', ['100'] * (1 + i % 4)) for i in range(count)]
    new = deepcopy(old)
    mode = index % 4
    wanted = []
    new[2]['synthetic_fields']['/attributes/warranty'] = '24 months'
    wanted.append(expected('p2', None, '/attributes/warranty', '12 months', '24 months'))
    if mode in (0, 1):
        amount = '110' if mode == 0 else '50'
        new[0]['variants'][0]['price'] = amount
        state = 'confirmed' if mode == 0 else 'pending'
        wanted += [expected('p0', None, '/price', Decimal('100'), Decimal(amount), state),
            expected('p0', 'p0-v0', '/price', Decimal('100'), Decimal(amount), state)]
    if mode == 0:
        for variant in new[1]['variants']:
            variant['available'] = False
        wanted.append(expected('p1', None, '/in_stock', True, False))
        wanted += [expected('p1', f'p1-v{i}', '/in_stock', True, False) for i in range(2)]
    elif mode == 2:
        new[0]['currency'] = 'USD'
        new[0]['variants'][0]['price'] = '110'
        wanted.append(expected('p0', None, '/currency', 'EUR', 'USD', 'pending'))
    elif mode == 3:
        new.pop()
        new[0]['synthetic_fields']['/pack_quantity'] = 2
        wanted.append(expected('p0', None, '/pack_quantity', 1, 2))
    for row in new:
        row['title'] = 'Renamed shared title ' + str(index % 2)
        # Changed variant remains first by explicit action contract. Other arrays reorder.
        if row['id'] != 'p0':
            rng.shuffle(row['variants'])
    rng.shuffle(old)
    rng.shuffle(new)
    b = Batch(path, f'SM09-{seed}-{index}')
    b.manifest.update(seed=seed, index=index, interaction=mode, expected=repr(wanted))
    a, c = b.save(old, 0), b.save(new, 1, complete=mode != 3)
    r = b.report(a, c)
    b.assert_set(r, wanted)
    initial_new = sum(x[4] == 'confirmed' for x in wanted)
    assert len(r['new_events']) == initial_new and not b.report(a, c)['new_events']
    checks = b.check_refs(r)
    if mode in (1, 2):
        sid = b.save(new, 2)
        final = b.report(a, c, sid)
        b.assert_set(final, [(*x[:4], 'confirmed', *x[5:]) for x in wanted])
        assert len(final['new_events']) == (2 if mode == 1 else 1)
        replay = b.report(a, c)
        assert replay['events'] == final['events'] and replay['new_events'] == []
        checks += b.check_refs(final)
    return {'scenario': 'SM09', 'seed': seed, 'index': index, 'interaction': mode,
            'products': count, 'input_bytes': b.bytes, 'reference_checks': checks}


TARGETED = [recheck_chain, terminal_expiry, health_interaction,
            boundary, lambda path: boundary(path, byte_limit=True), rollback_update, fault_sensitivity]


def test_sm01_native_mixed_smoke(tmp_path):
    smoke(tmp_path)


@pytest.mark.parametrize('function', TARGETED, ids=['SM02', 'SM03', 'SM04', 'SM05', 'SM06', 'SM07', 'SM08'])
def test_targeted_interactions(tmp_path, function):
    function(tmp_path)


@pytest.mark.parametrize('seed,index', [(seed, index) for seed in [1701, 2909] for index in range(8)])
def test_sm09_seeded_event_oracle(tmp_path, seed, index):
    seeded_batch(tmp_path, seed, index)
