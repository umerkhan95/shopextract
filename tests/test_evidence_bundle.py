"""Offline portability and corruption checks; no capture/model/network calls."""
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import json

import pytest

from shopextract._evidence import (Evidence, FieldObservation, FieldResolution,
                                   SupportState, TrustContract)
from shopextract._models import Product, Variant, Platform
from shopextract._portable import product_to_record, product_from_record
from shopextract.export import (create_evidence_bundle, load_evidence_bundle,
                                write_evidence_bundle, read_evidence_bundle,
                                create_evidence_sidecar, load_evidence_sidecar,
                                to_csv, to_feed)

NOW = datetime(2026, 10, 16, 12, 1, 2, 123456, tzinfo=timezone.utc)
E = 'e_00000000-0000-0000-0000-000000000001'
O = 'o_00000000-0000-0000-0000-000000000001'
O2 = 'o_00000000-0000-0000-0000-000000000002'


def fixture_product():
    p = Product(title='Thing', price=Decimal('1.2300'), scraped_at=NOW,
                external_id='duplicate', platform=Platform.SHOPIFY,
                raw_data={'$type': 'literal', 'nested': [Decimal('2.00'), NOW]},
                variants=[Variant(title='Red', price=Decimal('1.2300'))])
    evidence = Evidence(E, 'https://example.org/item', NOW, 'api',
                        retained_data={'a/b': [{'~': '1.2300'}]}, pointer='/a~1b/0/~0')
    p.evidence_contract = TrustContract([evidence], [
        FieldObservation(O, '/price', SupportState.OBSERVED, '1.2300', Decimal('1.2300'), [E]),
        FieldObservation(O2, '/price', SupportState.OBSERVED, '2.00', Decimal('2.00'), [E]),
    ], [FieldResolution('/price', SupportState.OBSERVED, [O, O2], 'Prefer API', O, 'api', '2')])
    p.variants[0].evidence_contract = TrustContract([deepcopy(evidence)], [
        FieldObservation(O, '/price', SupportState.OBSERVED, '1.2300', Decimal('1.2300'), [E])])
    return p


def test_semantic_roundtrip_and_file(tmp_path):
    p = fixture_product()
    bundle = create_evidence_bundle([p])
    restored = load_evidence_bundle(json.loads(json.dumps(bundle)))[0]
    assert restored == p
    assert type(restored.platform) is Platform
    assert type(restored.variants[0]) is Variant
    assert str(restored.price) == '1.2300'
    assert restored.raw_data == p.raw_data
    assert restored.evidence_contract.to_dict() == p.evidence_contract.to_dict()
    assert restored.variants[0].evidence_contract.to_dict() == p.variants[0].evidence_contract.to_dict()
    target = tmp_path / 'bundle.json'
    write_evidence_bundle([p], target)
    assert read_evidence_bundle(target)[0] == p


def test_missing_and_expired_availability():
    p = Product(scraped_at=NOW, variants=[Variant()])
    p.evidence_availability = [{'evidence_id': E, 'status': 'expired', 'reason': 'retention',
                                'expired_at': NOW, 'metadata': {'source_url': 'https://example.org',
                                                             'observed_at': NOW, 'method': 'api'}}]
    p.evidence_contract = TrustContract(observations=[FieldObservation(
        O, '/title', SupportState.EXPIRED, reason='retention')])
    p.variants[0].evidence_availability = deepcopy(p.evidence_availability)
    loaded = product_from_record(product_to_record(p))
    assert loaded.evidence_availability == p.evidence_availability
    assert loaded.variants[0].evidence_availability == p.variants[0].evidence_availability
    assert loaded.trust_view()['/title']['state'] == 'expired'
    assert not loaded.evidence_contract.evidence
    legacy = load_evidence_bundle(create_evidence_bundle([Product(scraped_at=NOW)]))[0]
    assert not hasattr(legacy, 'evidence_contract')
    assert legacy.trust_view()['/title']['state'] == 'unsupported'
    assert load_evidence_bundle(create_evidence_bundle([])) == []


@pytest.mark.parametrize('change', [
    lambda r: r.update(schema_version=True),
    lambda r: r.update(unknown=1),
    lambda r: r['product'].update(platform='bogus'),
    lambda r: r['product'].update(price={'$type': 'decimal', 'value': 'NaN'}),
    lambda r: r['product'].update(scraped_at={'$type': 'datetime', 'value': '2026-01-01'}),
    lambda r: r['product'].update(in_stock='true'),
    lambda r: r['product'].update(tags=[4]),
    lambda r: r['product'].update(price={'$type': 'unknown', 'value': '1'}),
    lambda r: r['product'].update(extra=1),
    lambda r: r.update(variant_contracts=[]),
    lambda r: r['evidence_contract']['evidence'][0].update(pointer='/absent'),
    lambda r: r['evidence_contract']['observations'][0].update(evidence_ids=[]),
    lambda r: r['evidence_contract']['observations'][0].update(field_path='/absent'),
    lambda r: r['evidence_contract']['resolutions'][0].update(observation_ids=[O]),
    lambda r: r['evidence_contract']['evidence'].append(deepcopy(r['evidence_contract']['evidence'][0])),
])
def test_reject_corruption(change):
    record = product_to_record(fixture_product())
    change(record)
    with pytest.raises(ValueError):
        product_from_record(record)


def test_limits_invalid_values_and_duplicate_json(tmp_path, monkeypatch):
    import shopextract._portable as portable
    import shopextract.export._bundle as bundles
    p = Product(scraped_at=NOW)
    with pytest.raises(ValueError):
        product_to_record(Product(scraped_at=NOW, raw_data={'x': (1, 2)}))
    with pytest.raises(ValueError):
        product_to_record(Product(scraped_at=datetime(2026, 1, 1)))
    with pytest.raises(ValueError):
        product_to_record(Product(scraped_at=NOW, raw_data={'x': float('inf')}))
    monkeypatch.setattr(portable, 'MAX_PORTABLE_DEPTH', 5)
    for _ in range(7):
        p.raw_data = {'x': p.raw_data}
    with pytest.raises(ValueError, match='limit'):
        product_to_record(p)
    target = tmp_path / 'invalid.json'
    target.write_text('{"schema_version":1,"schema_version":1}')
    with pytest.raises(ValueError, match='Duplicate'):
        read_evidence_bundle(target)
    target.write_text('{"x":NaN}')
    with pytest.raises(ValueError, match='Nonfinite'):
        read_evidence_bundle(target)
    monkeypatch.setattr(bundles, 'MAX_BUNDLE_BYTES', 3)
    with pytest.raises(ValueError, match='byte limit'):
        read_evidence_bundle(target)


def test_bundle_duplicate_keys_and_versions():
    bundle = create_evidence_bundle([Product(scraped_at=NOW), Product(scraped_at=NOW)])
    assert len({e['record_key'] for e in bundle['records']}) == 2
    bundle['records'][1]['record_key'] = bundle['records'][0]['record_key']
    with pytest.raises(ValueError, match='unique'):
        load_evidence_bundle(bundle)
    bundle = create_evidence_bundle([])
    bundle['schema_version'] = 99
    with pytest.raises(ValueError, match='version'):
        load_evidence_bundle(bundle)


@pytest.mark.parametrize('format', ['csv', 'google_shopping', 'idealo'])
def test_sidecar_all_rows_and_duplicate_ids(tmp_path, format):
    products = [fixture_product(), fixture_product()]
    path, companion = tmp_path / 'feed', tmp_path / 'evidence.json'
    if format == 'csv':
        to_csv(products, str(path), evidence_path=str(companion))
    else:
        to_feed(products, str(path), format, evidence_path=str(companion))
    sidecar = json.loads(companion.read_text())
    payload = path.read_bytes()
    assert len(load_evidence_sidecar(sidecar, payload)) == 2
    assert sidecar['rows'][0]['external_id'] == sidecar['rows'][1]['external_id']
    assert sidecar['rows'][0]['record_key'] != sidecar['rows'][1]['record_key']
    with pytest.raises(ValueError, match='digest'):
        load_evidence_sidecar(sidecar, payload + b'x')
    for key, value in [('row_index', 4), ('record_key', 'wrong'), ('external_id', 'wrong')]:
        corrupt = deepcopy(sidecar)
        corrupt['rows'][0][key] = value
        with pytest.raises(ValueError, match='mapping'):
            load_evidence_sidecar(corrupt, payload)
    corrupt = deepcopy(sidecar)
    corrupt['rows'].pop()
    with pytest.raises(ValueError, match='every'):
        load_evidence_sidecar(corrupt, payload)


def test_same_path_rejected_before_write(tmp_path):
    path = tmp_path / 'existing'
    path.write_text('keep')
    for writer in (to_csv, to_feed):
        with pytest.raises(ValueError, match='differ'):
            writer([Product(scraped_at=NOW)], str(path), evidence_path=str(path))
        assert path.read_text() == 'keep'


def test_mapping_literal_keys_and_projection_mismatch():
    record = product_to_record(Product(scraped_at=NOW))
    record['product']['raw_data'] = {'$type': 'mapping', 'value': {1: 'invalid'}}
    with pytest.raises(ValueError):
        product_from_record(record)
    with pytest.raises(ValueError, match='projection'):
        create_evidence_sidecar([Product(scraped_at=NOW)], b'external_id\n', format='csv')
