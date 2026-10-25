"""Predesigned #25 acceptance cases. Synthetic transport only; workflow remains real."""
import json
from dataclasses import replace
from datetime import datetime, timezone

import httpx
import pytest

from shopextract.maintenance import (AdvisorBound, AdvisorResult, AdvisorUsage, Budgets, Goal, MaintenanceEngine,
                                   MaintenanceError, MaintenanceStore)
from shopextract.maintenance.profiles import CategoryProfile, FieldRule, compare_field, profile
from shopextract.tools import ToolConfig

ORIGIN = 'https://supplier.example'
NOW = datetime(2026, 10, 16, 10, tzinfo=timezone.utc)


def baseline(description='Operating temperature: 0–40°C', **extra):
    return dict(external_id='S1', title='Industrial Sensor', sku='S1',
                gtin='4006381333931', vendor='Acme', description=description,
                price='10', currency='EUR', supplier_id=ORIGIN, **extra)


def goal(**overrides):
    defaults = dict(baseline=(baseline(),), supplier_origin=ORIGIN,
                    product_urls=(ORIGIN + '/products/p1',), profiles={'S1': 'hardware-v1'},
                    deadline='2026-10-16T10:01:00+00:00')
    defaults.update(overrides)
    return Goal(**defaults)


def supplier_html(description='Operating temperature: 0–45°C', attributes=None, category=None):
    product = {'@context': 'https://schema.org', '@type': 'Product',
               'name': 'Industrial Sensor', 'sku': 'S1', 'gtin13': '4006381333931',
               'brand': {'@type': 'Brand', 'name': 'Acme'}, 'description': description,
               'offers': {'@type': 'Offer', 'price': '10', 'priceCurrency': 'EUR'}}
    if attributes is not None:
        product['attributes'] = attributes
    if category is not None:
        product['category'] = category
    return '<script type="application/ld+json">' + json.dumps(product) + '</script>'


def parsed_supplier():
    from shopextract.tools.domain import synchronous
    from shopextract._portable import product_from_record
    records = synchronous({'operation': 'parse', 'mode': 'html', 'platform': 'generic',
        'html': supplier_html(), 'url': ORIGIN + '/products/p1', 'origin': ORIGIN,
        'observed_at': NOW.isoformat(), 'maximum': 1})
    return product_from_record(records[0])


def assert_exact_fixture():
    from shopextract.compare.identity_match import classify_match, MatchRelation
    decision = classify_match(baseline(), parsed_supplier())
    assert decision.relation == MatchRelation.EXACT and not decision.needs_review, decision


class Harness:
    def __init__(self, path, *, description='Operating temperature: 0–45°C',
                 status=200, investigator=None, failure_hook=None, attributes=None, category=None):
        self.requests = []
        self.status_code = status
        self.description = description
        self.store = MaintenanceStore(path)
        async def resolver(host, context):
            return ['93.184.216.34']
        def response(request):
            self.requests.append(str(request.url))
            html = supplier_html(self.description, attributes, category)
            return httpx.Response(self.status_code, text=html, headers={'content-type': 'text/html'})
        self.engine = MaintenanceEngine(self.store, tool_config=ToolConfig(allowed_origins=(ORIGIN,)),
            resolver=resolver, wire_transport=httpx.MockTransport(response), utc_now=lambda: NOW,
            investigator=investigator, failure_hook=failure_hook)

    async def run(self, configured=None):
        key = self.store.create(configured or goal())
        return key, await self.engine.run(key)


@pytest.mark.asyncio
async def test_supported_spec_correction_and_durable_evidence(tmp_path):
    assert_exact_fixture()
    h = Harness(tmp_path / 'jobs.db')
    key, report = await h.run()
    finding, = report['findings']
    assert finding['status'] == 'proposed_correction'
    assert finding['before'] == 'Operating temperature: 0–40°C'
    assert finding['after'] == 'Operating temperature: 0–45°C'
    assert finding['baseline_support']['kind'] == 'supplied'
    assert finding['baseline_support']['observed_at'] is None
    assert h.store.evidence(key, finding['evidence_ids'][0])['source_url'].startswith(ORIGIN)


@pytest.mark.asyncio
async def test_deterministic_no_llm_and_unchanged(tmp_path):
    assert_exact_fixture()
    class Forbidden:
        def bound(self, payload):
            pytest.fail('deterministic cases must not enter investigator')
    h = Harness(tmp_path / 'jobs.db', investigator=Forbidden())
    _, report = await h.run(goal(baseline=(baseline('Operating temperature: 0–45°C'),)))
    assert report['findings'][0]['status'] == 'unchanged'
    assert report['usage']['tokens'] == 0


@pytest.mark.asyncio
async def test_resume_skips_committed_external_work(tmp_path):
    h = Harness(tmp_path / 'jobs.db')
    key, original = await h.run()
    reopened = Harness(tmp_path / 'jobs.db')
    resumed = await reopened.engine.resume(key)
    assert resumed['findings'] == original['findings']
    assert reopened.requests == []


@pytest.mark.asyncio
@pytest.mark.parametrize('before', [None, {}])
async def test_missing_baseline_never_becomes_default_fact(tmp_path, before):
    record = baseline()
    if before is None:
        record.pop('description')
    else:
        record['description'] = None
    _, report = await Harness(tmp_path / 'jobs.db').run(goal(baseline=(record,)))
    assert report['findings'][0]['status'] == 'needs_review'
    assert report['findings'][0]['reason'] == 'baseline_missing'


@pytest.mark.asyncio
async def test_unknown_dispatch_is_not_replayed(tmp_path):
    class SyntheticCrash(BaseException):
        pass
    def crash(event, payload):
        if event == 'after_dispatch':
            raise SyntheticCrash('synthetic process-loss boundary')
    h = Harness(tmp_path / 'jobs.db', failure_hook=crash)
    key = h.store.create(goal())
    with pytest.raises(SyntheticCrash):
        await h.engine.run(key)
    reopened = Harness(tmp_path / 'jobs.db')
    report = await reopened.engine.resume(key)
    assert reopened.requests == []
    assert report['usage']['unknown_requests'] >= 1
    assert report['state'] == 'partial'


@pytest.mark.asyncio
async def test_zero_request_budget_preserves_partial_report(tmp_path):
    h = Harness(tmp_path / 'jobs.db')
    _, report = await h.run(goal(budgets=Budgets(requests=0)))
    assert h.requests == []
    assert report['state'] == 'partial'
    assert report['stop_reason'] == 'request_budget'


@pytest.mark.asyncio
async def test_cancelled_job_cannot_resume_or_dispatch(tmp_path):
    h = Harness(tmp_path / 'jobs.db')
    key = h.store.create(goal())
    await h.engine.cancel(key)
    with pytest.raises(MaintenanceError, match='invalid_state'):
        await h.engine.resume(key)
    assert h.requests == []


@pytest.mark.asyncio
async def test_source_auth_failure_has_no_retry(tmp_path):
    h = Harness(tmp_path / 'jobs.db', status=401)
    _, report = await h.run()
    assert len(h.requests) == 1
    assert report['state'] == 'partial'
    assert not any(f['status'] == 'proposed_correction' for f in report['findings'])


@pytest.mark.asyncio
async def test_fresh_cache_retains_original_capture_time(tmp_path):
    h = Harness(tmp_path / 'jobs.db')
    _, first = await h.run()
    count = len(h.requests)
    _, second = await h.run()
    assert len(h.requests) == count
    assert second['findings'][0]['supplier_support']['observed_at'] == first['findings'][0]['supplier_support']['observed_at']


@pytest.mark.parametrize('changed', [dict(baseline_mode='invalid'), dict(fields=('attributes/no_such_key',)),
                                     dict(budgets=Budgets(requests=True)),
                                     dict(profiles={'S1': 'unknown-v1'})])
def test_invalid_goals_rejected_before_dispatch(tmp_path, changed):
    with pytest.raises(MaintenanceError, match='invalid_argument'):
        MaintenanceStore(tmp_path / 'jobs.db').create(goal(**changed))


def test_exclusive_store_ownership(tmp_path):
    a = MaintenanceStore(tmp_path / 'jobs.db')
    b = MaintenanceStore(tmp_path / 'jobs.db')
    a.acquire()
    try:
        with pytest.raises(MaintenanceError, match='owner_busy'):
            b.acquire()
    finally:
        a.release()


@pytest.mark.parametrize('name,field,role', [('hardware-v1','attributes/ram','identity_variant'),
    ('hardware-v1','attributes/material','comparable'),
    ('footwear-v1','attributes/size','identity_variant'),
    ('footwear-v1','attributes/construction','comparable')])
def test_category_profile_field_roles(name, field, role):
    assert profile(name).fields[field].role == role


def test_exact_mass_conversion_does_not_authorize_identity():
    result = compare_field(profile('hardware-v1').fields['attributes/weight'], '1000 g', '1 kg')
    assert result['comparison'] == 'equal'
    assert result['normalized_before'] == result['normalized_after'] == '1'
    assert result['trace']
    assert 'match' not in result  # comparison cannot authorize a pair


def test_footwear_size_never_converts_between_systems():
    result = compare_field(profile('footwear-v1').fields['attributes/size'], 'US 9', 'UK 9')
    assert result['comparison'] != 'equal'


@pytest.mark.asyncio
async def test_missing_category_is_visible_review(tmp_path):
    _, report = await Harness(tmp_path / 'jobs.db').run(goal(profiles={}))
    assert report['findings'][0]['status'] == 'needs_review'
    assert report['findings'][0]['reason'] == 'category_missing'


@pytest.mark.asyncio
async def test_expired_deadline_resume_cannot_gain_time(tmp_path):
    h = Harness(tmp_path / 'jobs.db')
    key = h.store.create(goal(deadline='2026-10-16T09:59:00+00:00'))
    report = await h.engine.resume(key)
    assert report['state'] == 'partial'
    assert report['stop_reason'] == 'deadline'
    assert h.requests == []


@pytest.mark.asyncio
async def test_advisory_cannot_authorize_title_only_identity(tmp_path):
    class UntrustedAdvisor:
        calls = 0
        def bound(self, payload):
            return AdvisorBound(32, 32, 10, 'synthetic', 'fixture-v1')
        async def investigate(self, payload, *, reservation, timeout):
            self.calls += 1
            assert reservation.bound == AdvisorBound(32, 32, 10, 'synthetic', 'fixture-v1')
            assert reservation.reservation_id
            return AdvisorResult('synthetic', 'fixture-v1', {'relation': 'exact'},
                                 ('forged',), AdvisorUsage(32, 4, 5))
    record = baseline()
    for key in ('external_id', 'sku', 'gtin'):
        record.pop(key)
    advisor = UntrustedAdvisor()
    h = Harness(tmp_path / 'jobs.db', investigator=advisor)
    _, report = await h.run(goal(baseline=(record,), profiles={'0': 'hardware-v1'},
                                budgets=Budgets(tokens=128, cost_micros=100)))
    assert not any(f['status'] == 'proposed_correction' for f in report['findings'])
    assert report['findings'][0]['status'] == 'needs_review'
    assert advisor.calls == 1
    assert report['usage']['tokens'] <= 128


@pytest.mark.asyncio
async def test_stable_report_pagination_and_resume_ids(tmp_path):
    h = Harness(tmp_path / 'jobs.db')
    key, report = await h.run()
    first = h.store.report(key, offset=0, limit=1)
    assert first['findings'] == report['findings'][:1]
    assert h.store.report(key, offset=1, limit=1)['findings'] == []
    assert (await h.engine.resume(key))['findings'][0]['finding_id'] == first['findings'][0]['finding_id']


@pytest.mark.asyncio
async def test_missing_supplier_support_never_invents_removal(tmp_path):
    h = Harness(tmp_path / 'jobs.db', description=None)
    _, report = await h.run()
    assert report['findings'][0]['status'] == 'needs_review'
    assert report['findings'][0]['reason'] == 'supplier_unsupported'


@pytest.mark.asyncio
async def test_profile_identity_change_requires_new_job(tmp_path):
    h = Harness(tmp_path / 'jobs.db')
    original = goal()
    key, _ = await h.run(original)
    changed = replace(original, profiles={'S1': 'footwear-v1'})
    second = h.store.create(changed)
    assert second != key
    assert h.store.status(key)['goal_fingerprint'] != h.store.status(second)['goal_fingerprint']



def test_fixture_real_parser_and_matcher_positive_and_source_id_conflict():
    from shopextract.compare.identity_match import classify_match, MatchRelation
    assert_exact_fixture()
    changed = baseline()
    changed['external_id'] = 'different-source-id'
    negative = classify_match(changed, parsed_supplier())
    assert negative.relation != MatchRelation.EXACT
    assert negative.needs_review and 'supplier source ID differs' in negative.conflicts


@pytest.mark.asyncio
async def test_unknown_advisor_usage_retains_bound_and_blocks_second_call(tmp_path):
    class UnknownUsage:
        calls = 0
        def bound(self, payload):
            return AdvisorBound(32, 32, 10, 'synthetic', 'fixed-price-v1')
        async def investigate(self, payload, *, reservation, timeout):
            self.calls += 1
            assert reservation.bound == self.bound(payload)
            assert timeout <= 10
            return AdvisorResult('synthetic', 'fixed-price-v1', {'reason': 'uncertain'}, (), None)
    advisor = UnknownUsage()
    a = baseline()
    for name in ('external_id', 'sku', 'gtin'):
        a.pop(name)
    b = dict(a, description='Another supplied description')
    h = Harness(tmp_path / 'jobs.db', investigator=advisor)
    _, report = await h.run(goal(baseline=(a, b), profiles={'0': 'hardware-v1', '1': 'hardware-v1'},
                                budgets=Budgets(tokens=64, cost_micros=10)))
    assert advisor.calls == 1
    assert report['usage']['reserved_tokens'] == 64
    assert report['usage']['reserved_cost_micros'] == 10
    assert all(f['status'] != 'proposed_correction' for f in report['findings'])



def test_custom_profile_is_frozen_with_goal_before_execution(tmp_path):
    fields = {'description': FieldRule('text', 'comparable')}
    configured = CategoryProfile('accessory-v1', fields)
    store = MaintenanceStore(tmp_path / 'jobs.db', custom_profiles={'accessory-v1': configured})
    key = store.create(goal(profiles={'S1': 'accessory-v1'}))
    fields['attributes/color'] = FieldRule('text', 'identity_variant')
    persisted = store.status(key)['profile_definitions']['accessory-v1']
    assert persisted['name'] == 'accessory-v1'
    assert set(persisted['fields']) == {'description'}
    reopened = MaintenanceStore(tmp_path / 'jobs.db', custom_profiles={})
    assert reopened.status(key)['profile_definitions'] == store.status(key)['profile_definitions']


@pytest.mark.asyncio
@pytest.mark.parametrize('replacement', ['changed', 'missing'])
async def test_custom_profile_recovery_rejects_changed_or_missing_registry(tmp_path, replacement):
    original = CategoryProfile('accessory-v1', {'description': FieldRule('text', 'comparable')})
    store = MaintenanceStore(tmp_path / 'jobs.db', custom_profiles={'accessory-v1': original})
    key = store.create(goal(profiles={'S1': 'accessory-v1'}))
    active = {} if replacement == 'missing' else {'accessory-v1': CategoryProfile(
        'accessory-v1', {'description': FieldRule('text', 'identity_variant')})}
    h = Harness(tmp_path / 'jobs.db')
    h.store = MaintenanceStore(tmp_path / 'jobs.db', custom_profiles=active)
    h.engine.store = h.store
    with pytest.raises(MaintenanceError, match='profile_mismatch'):
        await h.engine.resume(key)
    assert h.requests == []
