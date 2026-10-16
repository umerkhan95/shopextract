"""Offline acceptance fixtures for #34's public contract."""
from datetime import datetime, timezone
from decimal import Decimal
import json
from uuid import uuid4

import pytest
from shopextract import (Evidence, FieldObservation, FieldResolution, Product,
                        SupportState, TrustContract, ValidatedConfidence, Variant,
                        factual_paths, normalize, assign_identity)


def eid():
    return 'e_' + str(uuid4())


def oid():
    return 'o_' + str(uuid4())


def evidence(**overrides):
    return Evidence(**dict(dict(evidence_id=eid(), source_url='https://shop.test/api/products',
                               observed_at=datetime(2026, 10, 4, tzinfo=timezone.utc),
                               method='api', excerpt='price: 0, in_stock: false'), **overrides))


def observed(path, value, source):
    return FieldObservation(oid(), path, SupportState.OBSERVED, value, value, [source.evidence_id])


def test_missing_normalized_and_literal_zero_false_are_distinct():
    p = normalize({'title': 'Missing', 'sku': 'missing-price-item', 'product_url': 'https://shop.test/p'})
    view = p.trust_view()
    for path in ('/price', '/currency', '/in_stock'):
        assert view[path]['state'] == 'unsupported'
        assert view[path]['value'] is None
    e = evidence()
    p = Product(price=Decimal('0'), in_stock=False)
    c = TrustContract([e], [observed('/price', Decimal('0'), e), observed('/in_stock', False, e),
                          FieldObservation(oid(), '/currency', 'unknown', reason='Not present in response')])
    view = p.trust_view(c)
    assert view['/price']['value'] == Decimal('0')
    assert view['/in_stock']['value'] is False
    assert view['/currency']['state'] == 'unknown'


def test_nested_coverage_and_derived_fields():
    p = Product(tags=['sale'], attributes={'size/color~': 'L'}, variants=[Variant(attributes={'color': 'red'})])
    view = p.trust_view()
    assert '/attributes/size~1color~0' in view
    assert '/variants/0/attributes/color' in view
    assert '/tags/0' in view and '/additional_images' in view
    assert '/variants/0/price' in view
    assert all(v['reason'] and v['state'] == 'unsupported' for v in view.values())
    assert '/canonical_product_id' not in view and '/scraped_at' not in view
    assert '/canonical_variant_id' not in Variant().trust_view()
    e = evidence()
    o = observed('/variants/0/attributes/color', 'red', e)
    assert p.trust_view(TrustContract([e], [o]))[o.field_path]['value'] == 'red'


def test_typed_round_trip_and_uncalibrated_scores():
    e = evidence(excerpt=None, retained_data={'items': [{'price': '0'}], '$type': 'user key'}, pointer='/items/0/price')
    o = observed('/price', Decimal('0.00'), e)
    o.score, o.score_kind = 42.5, 'model'
    c = TrustContract([e], [o])
    loaded = TrustContract.from_dict(json.loads(json.dumps(c.to_dict(), allow_nan=False)))
    assert loaded == c
    assert loaded.observations[0].validated_confidence is None
    assert loaded.evidence[0].resolve_pointer() == '0'
    assert str(loaded.observations[0].normalized_value) == '0.00'
    o.validated_confidence = ValidatedConfidence(.8, 'held-out calibration', 'fixture-v1', '1')
    assert TrustContract.from_dict(c.to_dict()) == c


def test_conflicts_preserved_and_explicit_selection():
    e = evidence()
    a, b = observed('/price', Decimal('1'), e), observed('/price', Decimal('2'), e)
    c = TrustContract([e], [a, b])
    assert Product().trust_view(c)['/price']['state'] == 'conflicting'
    c.resolutions = [FieldResolution('/price', 'observed', [a.observation_id, b.observation_id],
                                    'Supplier offer selected', a.observation_id, 'supplier-offer', '1')]
    view = Product().trust_view(c)['/price']
    assert view['value'] == Decimal('1')
    assert view['observation_ids'] == [a.observation_id, b.observation_id]
    c.resolutions[0].state = SupportState.CONFLICTING
    c.resolutions[0].selected_observation_id = None
    assert Product().trust_view(c)['/price']['value'] is None


@pytest.mark.parametrize('overrides', [
    {'evidence_id': 'e_bad'}, {'source_url': '/api'},
    {'observed_at': datetime(2026, 10, 4)}, {'method': ''},
    {'excerpt': None}, {'pointer': '/missing', 'retained_data': {}},
    {'pointer': '/x', 'retained_data': None},
    {'pointer': '/~2', 'retained_data': {}},
])
def test_malformed_evidence_rejected(overrides):
    with pytest.raises(ValueError):
        evidence(**overrides)


@pytest.mark.parametrize('overrides', [
    {'observation_id': 'bad'}, {'field_path': 'price'}, {'state': 'invented'},
    {'evidence_ids': []}, {'normalized_value': None},
    {'score': float('nan'), 'score_kind': 'model'}, {'score': .9},
])
def test_malformed_observation_rejected(overrides):
    data = dict(observation_id=oid(), field_path='/price', state='observed', normalized_value=0, evidence_ids=[eid()])
    data.update(overrides)
    with pytest.raises(ValueError):
        FieldObservation(**data)


def test_references_versions_and_confidence_validation():
    e = evidence()
    o = observed('/price', 0, e)
    with pytest.raises(ValueError):
        TrustContract([], [o])
    with pytest.raises(ValueError):
        TrustContract([e, e])
    with pytest.raises(ValueError):
        TrustContract(schema_version=2)
    with pytest.raises(ValueError):
        TrustContract.from_dict({})
    with pytest.raises(ValueError):
        ValidatedConfidence(.9, '', 'dataset', '1')
    with pytest.raises(ValueError):
        FieldObservation(oid(), '/price', 'unsupported', reason='LLM has no source span',
                         validated_confidence=ValidatedConfidence(.9, 'method', 'dataset', '1'))
    with pytest.raises(ValueError):
        Product().trust_view(TrustContract([e], [observed('/invalid', 0, e)]))
    with pytest.raises(ValueError):
        TrustContract([e], [o], [FieldResolution('/currency', 'observed', [o.observation_id], 'Wrong field', o.observation_id)])


def test_legacy_constructors_identity_and_serialization_unchanged():
    from dataclasses import asdict
    p = Product('Widget', Decimal('0'), product_url='https://shop.test/p', variants=[Variant('v1')])
    before = asdict(p)
    p.trust_view()
    assert asdict(p) == before
    assign_identity(p)
    canonical = p.canonical_product_id
    assign_identity(p)
    assert p.canonical_product_id == canonical
    assert not any(k.startswith('trust') for k in asdict(p))


def test_expired_unknown_and_unsupported_reasons_survive():
    c = TrustContract(observations=[FieldObservation(oid(), '/price', state, reason='Unavailable')
                                   for state in ('expired', 'unknown', 'unsupported')])
    assert TrustContract.from_dict(c.to_dict()) == c


def test_no_silent_candidate_loss_or_mutation():
    e = evidence()
    a, b = observed('/price', 1, e), observed('/price', 2, e)
    with pytest.raises(ValueError, match='retain all'):
        TrustContract([e], [a, b], [FieldResolution('/price', 'observed', [a.observation_id],
                                                 'Dropped alternative', a.observation_id)])
    c = TrustContract([e], [a])
    a.evidence_ids = [eid()]
    with pytest.raises(ValueError, match='Dangling'):
        c.to_dict()
    with pytest.raises(ValueError):
        TrustContract.from_dict({'schema_version': 1, 'unknown_key': 'bad'})


def test_retained_pointer_escaping_and_collection_semantics():
    e = evidence(excerpt=None, retained_data={'a/b~': [False, 0]}, pointer='/a~1b~0/0')
    assert e.resolve_pointer() is False
    with pytest.raises(ValueError):
        evidence(pointer='/items/01', retained_data={'items': [0, 1]})
    p = Product(tags=[])
    o = observed('/tags', [], e)
    assert p.trust_view(TrustContract([e], [o]))['/tags']['value'] == []
    paths = factual_paths(p)
    from dataclasses import fields
    from shopextract._evidence import DERIVED_FIELDS
    assert {f'/{f.name}' for f in fields(p) if f.name not in DERIVED_FIELDS} <= paths.keys()


@pytest.mark.parametrize('value', [
    Decimal('12.30'), datetime(2026, 10, 4, tzinfo=timezone.utc),
    {'$type': 'decimal', 'value': 'source text'},
    [Decimal('0.00'), {'$type': 'user key'}],
])
def test_enum_values_use_recursive_codec(value):
    from enum import Enum
    from shopextract._evidence import encode_value, decode_value
    member = Enum('SourceValue', {'ITEM': value}).ITEM
    encoded = encode_value(member)
    assert encoded == encode_value(value)
    assert decode_value(json.loads(json.dumps(encoded, allow_nan=False))) == value


@pytest.mark.parametrize('value', [float('nan'), Decimal('Infinity'), object(), {'bad': float('inf')}])
def test_enum_values_cannot_bypass_validation(value):
    from enum import Enum
    from shopextract._evidence import encode_value
    member = Enum('InvalidValue', {'ITEM': value}).ITEM
    with pytest.raises(ValueError):
        encode_value(member)


@pytest.mark.parametrize('state', ['unknown', 'unsupported', 'expired', 'conflicting'])
def test_only_observed_state_accepts_validated_confidence(state):
    confidence = ValidatedConfidence(.8, 'calibration', 'held-out-v1', '1')
    with pytest.raises(ValueError, match='validated confidence'):
        FieldObservation(oid(), '/price', state, reason='No resolved supported fact',
                         validated_confidence=confidence)
    e = evidence()
    o = observed('/price', Decimal('0'), e)
    o.validated_confidence = confidence
    c = TrustContract([e], [o])
    assert TrustContract.from_dict(c.to_dict()) == c
    o.state, o.reason = SupportState(state), 'Support no longer observed'
    with pytest.raises(ValueError, match='validated confidence'):
        c.to_dict()
