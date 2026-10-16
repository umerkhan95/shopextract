"""Offline durable evidence, atomicity and retention checks."""
import importlib
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from shopextract._evidence import Evidence, FieldObservation, FieldResolution, TrustContract, ValidatedConfidence
from shopextract._models import Product, Variant
from shopextract.monitor.evidence import save_snapshot, load_snapshot, get_evidence, prune_evidence
from shopextract.monitor.snapshot import _get_connection

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def fixture_product():
    e = Evidence('e_' + str(uuid4()), 'https://shop.test/api', NOW, 'api', retained_data={'price': Decimal('12.00'), '$type': 'literal'}, pointer='/price', source_role='merchant')
    o = FieldObservation('o_' + str(uuid4()), '/price', 'observed', Decimal('12.00'), Decimal('12.00'), [e.evidence_id], validated_confidence=ValidatedConfidence(.9, 'test', 'test', '1'))
    c = TrustContract([e], [o], [FieldResolution('/price', 'observed', [o.observation_id], 'selected', o.observation_id)])
    p = Product(title='Widget', price=Decimal('12.00'), external_id='42', variants=[Variant(variant_id='v', price=Decimal('12.00'))])
    p.evidence_contract = c
    p.variants[0].evidence_contract = TrustContract.from_dict(c.to_dict())
    return p, e


def test_tiny_restart(tmp_path):
    path = str(tmp_path / 'db.sqlite')
    p, e = fixture_product()
    sid = save_snapshot([p], 'shop.test', db_path=path)
    restored = load_snapshot(sid, db_path=path)[0]
    assert restored.price == p.price
    assert restored.evidence_contract.to_dict() == p.evidence_contract.to_dict()
    assert restored.variants[0].evidence_contract.to_dict() == p.variants[0].evidence_contract.to_dict()
    lookup = get_evidence(e.evidence_id, snapshot_id=sid, record_key='product/0', db_path=path)
    assert lookup.status == 'available'
    assert lookup.evidence.resolve_pointer() == Decimal('12.00')
    assert lookup.evidence.retained_data['$type'] == 'literal'
    with pytest.raises(ValueError, match='Ambiguous'):
        get_evidence(e.evidence_id, db_path=path)


def test_retention_shared_payload_and_portable_tombstones(tmp_path):
    path = str(tmp_path / 'db.sqlite')
    p, e = fixture_product()
    sid = save_snapshot([p], 'shop.test', db_path=path)
    sid2 = save_snapshot([p], 'shop.test', db_path=path)
    cutoff = NOW + timedelta(days=1)
    dry = prune_evidence(db_path=path, before=cutoff, protect_references=False, batch_size=1)
    assert (dry.examined, dry.expired, dry.payloads_deleted, dry.has_more) == (1, 1, 0, True)
    assert get_evidence(e.evidence_id, snapshot_id=sid, record_key='product/0', db_path=path).status == 'available'
    protected = prune_evidence(db_path=path, before=cutoff, dry_run=False, batch_size=1)
    assert protected.protected == 1 and protected.expired == 0
    report = prune_evidence(db_path=path, before=cutoff, protect_references=False, dry_run=False, batch_size=1)
    assert report.expired == 1 and report.payloads_deleted == 0
    loaded = load_snapshot(sid, db_path=path)[0]
    assert loaded.evidence_contract.observations[0].state == 'expired'
    assert loaded.evidence_contract.observations[0].validated_confidence is None
    assert loaded.evidence_contract.resolutions[0].selected_observation_id is None
    assert loaded.trust_view()['/price']['state'] == 'expired'
    assert loaded.variants[0].trust_view()['/price']['state'] == 'observed'
    assert get_evidence(e.evidence_id, snapshot_id=sid2, record_key='product/0', db_path=path).status == 'available'
    # Offline codec transport and resave must preserve lookup tombstones.
    from shopextract._portable import product_from_record, product_to_record
    transported = product_from_record(product_to_record(loaded))
    sid3 = save_snapshot([transported], 'shop.test', db_path=path)
    found = get_evidence(e.evidence_id, snapshot_id=sid3, record_key='product/0', db_path=path)
    assert found.status == 'expired' and found.evidence is None
    assert found.expired_at == loaded.evidence_availability[0]['expired_at']
    prune_evidence(db_path=path, before=cutoff, protect_references=False, dry_run=False)
    with sqlite3.connect(path) as conn:
        assert conn.execute('SELECT count(*) FROM evidence_payloads').fetchone()[0] == 0
        assert conn.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert conn.execute('PRAGMA foreign_key_check').fetchall() == []
    again = load_snapshot(sid3, db_path=path)[0]
    assert len(again.evidence_availability) == 1
    assert again.variants[0].trust_view()['/price']['state'] == 'expired'


@pytest.mark.parametrize('offset,expired', [(0,0), (1,2)])
def test_strict_microsecond_cutoff(tmp_path, offset, expired):
    path = str(tmp_path / 'db.sqlite')
    p, _ = fixture_product()
    save_snapshot([p], 'shop.test', db_path=path)
    result = prune_evidence(db_path=path, before=NOW + timedelta(microseconds=offset), protect_references=False)
    assert result.expired == expired


def test_legacy_migration_idempotent(tmp_path):
    path = str(tmp_path / 'db.sqlite')
    payload = json.dumps([{'title': 'Old', 'price': '1.20', 'external_id': 'old', 'variants': [{'price': '1.10'}]}])
    with sqlite3.connect(path) as conn:
        conn.execute('CREATE TABLE snapshots (id INTEGER PRIMARY KEY,domain TEXT,products_json TEXT,created_at TEXT)')
        conn.execute('INSERT INTO snapshots VALUES (7,?,?,?)', ('shop.test', payload, '2020-01-01'))
    for _ in range(2):
        conn = _get_connection(path)
        assert conn.execute('SELECT products_json,created_at FROM snapshots').fetchone() == (payload, '2020-01-01')
        assert conn.execute('SELECT count(*) FROM evidence_owners').fetchone()[0] == 2
        conn.close()
    loaded = load_snapshot(7, db_path=path)[0]
    assert loaded.price == Decimal('1.20') and loaded.variants[0].price == Decimal('1.10')
    assert not hasattr(loaded, 'evidence_contract')
    assert get_evidence('unknown', snapshot_id=7, record_key='product/0', db_path=path).status == 'unsupported'
    assert get_evidence('unknown', snapshot_id=8, record_key='product/0', db_path=path).status == 'missing'
    with pytest.raises(KeyError):
        load_snapshot(8, db_path=path)


@pytest.mark.parametrize('table', ['snapshots', 'evidence_references'])
def test_transaction_failure_rolls_back_every_write(tmp_path, monkeypatch, table):
    path = str(tmp_path / 'db.sqlite')
    p, _ = fixture_product()
    module = importlib.import_module('shopextract.monitor.snapshot')
    original = module._get_connection
    def failing_connection(*args, **kwargs):
        conn = original(*args, **kwargs)
        def deny(action, name, *unused):
            return sqlite3.SQLITE_DENY if action == sqlite3.SQLITE_INSERT and name == table else sqlite3.SQLITE_OK
        conn.set_authorizer(deny)
        return conn
    # Establish all tables first, then fail after identity work or graph inserts.
    original(path).close()
    monkeypatch.setattr(module, '_get_connection', failing_connection)
    with pytest.raises(sqlite3.DatabaseError):
        save_snapshot([p], 'shop.test', db_path=path)
    with sqlite3.connect(path) as conn:
        for name in ('snapshots', 'evidence_owners', 'evidence_products', 'evidence_payloads', 'evidence_records', 'evidence_references'):
            assert conn.execute(f'SELECT count(*) FROM {name}').fetchone()[0] == 0
        assert conn.execute("SELECT count(*) FROM sqlite_master WHERE name='identity_aliases'").fetchone()[0] == 0


def test_corruption_and_unsupported_version(tmp_path):
    path = str(tmp_path / 'db.sqlite')
    p, e = fixture_product()
    sid = save_snapshot([p], 'shop.test', db_path=path)
    with sqlite3.connect(path) as conn:
        conn.execute("UPDATE evidence_payloads SET encoded_payload='{}'")
    with pytest.raises(ValueError, match='Corrupt'):
        get_evidence(e.evidence_id, snapshot_id=sid, record_key='product/0', db_path=path)
    with pytest.raises(ValueError, match='Corrupt'):
        load_snapshot(sid, db_path=path)
    with sqlite3.connect(path) as conn:
        conn.execute('UPDATE evidence_schema SET version=2')
    with pytest.raises(ValueError, match='Unsupported'):
        load_snapshot(sid, db_path=path)


def test_bounds_are_pretransaction(tmp_path, monkeypatch):
    import shopextract.monitor.evidence as storage
    path = str(tmp_path / 'db.sqlite')
    p, _ = fixture_product()
    with pytest.raises(ValueError, match='Unknown'):
        save_snapshot([p], 'shop.test', db_path=path, metadata={'unexpected': 1})
    assert not (tmp_path / 'db.sqlite').exists()
    monkeypatch.setattr(storage, 'MAX_SNAPSHOT_BYTES', 10)
    with pytest.raises(ValueError, match='16 MiB'):
        save_snapshot([p], 'shop.test', db_path=path)
    assert not (tmp_path / 'db.sqlite').exists()
    with pytest.raises(ValueError):
        prune_evidence(db_path=path, before=NOW, batch_size=1001)
    with pytest.raises(ValueError):
        prune_evidence(db_path=path, before=datetime(2026,1,1))
