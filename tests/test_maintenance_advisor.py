"""Actual injected advisory boundary; no remote provider or model is started."""
import asyncio
from dataclasses import replace
import pytest
from shopextract.maintenance import AdvisorBound, AdvisorResult, AdvisorUsage, Budgets
from tests.test_maintenance_acceptance import Harness, baseline, goal, NOW


def ambiguous_goal(**changes):
    record = baseline()
    for name in ('external_id', 'sku', 'gtin'):
        record.pop(name)
    return goal(baseline=(record,), profiles={'0': 'hardware-v1'},
                budgets=changes.pop('budgets', Budgets(tokens=128, cost_micros=100)), **changes)


class Advisor:
    def __init__(self, mode='known'):
        self.mode, self.calls, self.payloads = mode, 0, []
    def bound(self, payload):
        return AdvisorBound(32, 32, 10, 'synthetic-v1', 'price-v1')
    async def investigate(self, payload, *, reservation, timeout):
        self.calls += 1
        self.payloads.append(payload)
        assert reservation.bound == self.bound(payload) and reservation.reservation_id
        assert 0 < timeout <= 10
        if self.mode == 'timeout':
            await asyncio.Event().wait()
        usage = None if self.mode == 'unknown' else AdvisorUsage(32, 4, 5)
        ids = tuple(value['evidence_id'] for value in payload['evidence'])
        model = 'wrong-model' if self.mode == 'model_change' else 'synthetic-v1'
        if self.mode == 'overrun':
            usage = AdvisorUsage(32, 80, 15)
        advisory = {'reason': 'Needs manual variant confirmation'}
        if self.mode == 'injection':
            advisory = {'budget': 'unlimited', 'relation': 'exact', 'write': 'store'}
        if self.mode == 'forged_evidence':
            ids = ('not-an-allowed-evidence-id',)
        return AdvisorResult(model, 'price-v1', advisory, ids, usage)


@pytest.mark.asyncio
async def test_known_usage_settles_actual_cost_and_caches_exact_advisory(tmp_path):
    advisor = Advisor()
    h = Harness(tmp_path / 'jobs.db', investigator=advisor)
    _, first = await h.run(ambiguous_goal())
    assert advisor.calls == 1
    assert first['usage']['tokens'] == 36 and first['usage']['cost_micros'] == 5
    assert first['usage']['reserved_tokens'] == 0
    assert first['findings'][0]['status'] == 'needs_review'
    _, second = await h.run(ambiguous_goal())
    assert advisor.calls == 1
    assert second['usage']['tokens'] == second['usage']['cost_micros'] == 0
    assert second['findings'][0]['advisory'] == first['findings'][0]['advisory']
    assert second['pending_steps'] == []


@pytest.mark.asyncio
@pytest.mark.parametrize('mode', ['model_change', 'injection', 'forged_evidence'])
async def test_invalid_advice_never_changes_authority_or_refunds_unknown_usage(tmp_path, mode):
    advisor = Advisor(mode)
    _, report = await Harness(tmp_path / 'jobs.db', investigator=advisor).run(ambiguous_goal())
    finding, = report['findings']
    assert advisor.calls == 1
    assert finding['status'] == 'needs_review' and finding['reason'] == 'identity_unresolved'
    assert finding['advisory']['status'] == 'invalid_result'
    assert report['usage']['reserved_tokens'] == 64
    assert report['usage']['reserved_cost_micros'] == 10


@pytest.mark.asyncio
async def test_overrun_records_actual_violation_and_stops_second_model_dispatch(tmp_path):
    advisor = Advisor('overrun')
    configured = ambiguous_goal()
    record = configured.baseline[0]
    configured = replace(configured, baseline=(record, dict(record, description='Different request')),
                         profiles={'0': 'hardware-v1', '1': 'hardware-v1'})
    _, report = await Harness(tmp_path / 'jobs.db', investigator=advisor).run(configured)
    assert advisor.calls == 1
    assert report['coverage']['source_complete'] is False
    assert report['state'] == 'partial' and report['stop_reason'] == 'budget_violation'
    assert report['usage']['tokens'] == 112 and report['usage']['cost_micros'] == 15
    assert report['usage']['violations'] == 1
    assert all(value['status'] == 'needs_review' for value in report['findings'])


@pytest.mark.asyncio
async def test_cost_reservation_denies_before_model_dispatch(tmp_path):
    advisor = Advisor()
    _, report = await Harness(tmp_path / 'jobs.db', investigator=advisor).run(
        ambiguous_goal(budgets=Budgets(tokens=128, cost_micros=9)))
    assert advisor.calls == 0
    assert report['coverage']['source_complete'] is False
    assert report['stop_reason'] == 'cost_budget'
    assert report['usage']['tokens'] == report['usage']['cost_micros'] == 0


@pytest.mark.asyncio
async def test_timeout_retains_full_reservation_with_bounded_call(tmp_path):
    advisor = Advisor('timeout')
    h = Harness(tmp_path / 'jobs.db', investigator=advisor)
    configured = ambiguous_goal(budgets=Budgets(tokens=128, cost_micros=100, attempt_seconds=2))
    # Source parsing is real and first cached, so the short advisor timeout does
    # not constrain initial spawn startup unpredictably.
    await h.run(goal())
    configured = replace(configured, budgets=replace(configured.budgets, attempt_seconds=.02))
    _, report = await h.run(configured)
    assert advisor.calls == 1
    assert report['findings'][0]['advisory']['status'] == 'timeout'
    assert report['usage']['reserved_tokens'] == 64


@pytest.mark.asyncio
async def test_payload_is_selected_structured_evidence_without_raw_catalog(tmp_path):
    advisor = Advisor()
    h = Harness(tmp_path / 'jobs.db', investigator=advisor)
    _, report = await h.run(ambiguous_goal())
    payload, = advisor.payloads
    assert set(payload) == {'schema_version','profile','field','product_key','before','after','reason','match_reason','evidence'}
    assert payload['field'] == 'description'
    assert all(set(item) == {'evidence_id','source_url','observed_at','pointer'} for item in payload['evidence'])
    assert 'raw_data' not in str(payload) and 'retained_data' not in str(payload)
    assert report['findings'][0]['status'] == 'needs_review'


@pytest.mark.asyncio
async def test_model_crash_resumes_without_replay_or_refunding_unknown_spend(tmp_path):
    class Crash(BaseException):
        pass
    def crash(event, payload):
        if event == 'advisor_after_dispatch':
            raise Crash()
    first = Advisor()
    h = Harness(tmp_path / 'jobs.db', investigator=first, failure_hook=crash)
    key = h.store.create(ambiguous_goal())
    with pytest.raises(Crash):
        await h.engine.run(key)
    second = Advisor()
    reopened = Harness(tmp_path / 'jobs.db', investigator=second)
    report = await reopened.engine.resume(key)
    assert first.calls == 1 and second.calls == 0
    assert reopened.requests == []
    assert report['usage']['reserved_tokens'] == 64
    assert report['usage']['reserved_cost_micros'] == 10
    assert report['findings'][0]['advisory']['status'] == 'outcome_unknown'


@pytest.mark.asyncio
async def test_advisor_price_identity_change_invalidates_cached_advice(tmp_path):
    first = Advisor()
    h = Harness(tmp_path / 'jobs.db', investigator=first)
    await h.run(ambiguous_goal())
    class RevisedPrice(Advisor):
        def bound(self, payload):
            return replace(super().bound(payload), price_version='price-v2')
        async def investigate(self, payload, **kwargs):
            return replace(await super().investigate(payload, **kwargs), price_version='price-v2')
    revised = RevisedPrice()
    h.engine.investigator = revised
    _, report = await h.run(ambiguous_goal())
    assert first.calls == revised.calls == 1
    assert report['usage']['tokens'] == 36
    assert report['findings'][0]['advisory']['price_version'] == 'price-v2'


@pytest.mark.asyncio
async def test_missing_trustworthy_bound_never_dispatches_model(tmp_path):
    class NoBound(Advisor):
        def bound(self, payload):
            return AdvisorBound(True, 32, 10, 'synthetic-v1', '')
    advisor = NoBound()
    _, report = await Harness(tmp_path / 'jobs.db', investigator=advisor).run(ambiguous_goal())
    assert advisor.calls == 0
    assert report['findings'][0]['advisory']['reason'] == 'unknown_bound'
    assert report['usage']['tokens'] == report['usage']['cost_micros'] == 0


@pytest.mark.asyncio
async def test_explicit_unknown_advisor_retry_preserves_base_finding_and_old_charge(tmp_path):
    """FR05 remaining requirement: do not hide this gap behind no-replay success."""
    class Crash(BaseException):
        pass
    def crash(event, payload):
        if event == 'advisor_after_dispatch':
            raise Crash()
    h = Harness(tmp_path / 'jobs.db', investigator=Advisor(), failure_hook=crash)
    key = h.store.create(ambiguous_goal())
    with pytest.raises(Crash):
        await h.engine.run(key)
    advisor = Advisor()
    reopened = Harness(tmp_path / 'jobs.db', investigator=advisor)
    partial = await reopened.engine.resume(key)
    original, = partial['findings']
    step = next(row['id'] for row in reopened.store.steps(key) if row['kind'].startswith('advisor:'))
    retried = await reopened.engine.retry_unknown(key, step)
    current, = retried['findings']
    assert advisor.calls == 1
    assert current['finding_id'] == original['finding_id']
    assert current['status'] == original['status'] == 'needs_review'
    assert current['before'] == original['before'] and current['after'] == original['after']
    assert current['advisory']['status'] == 'available'
    assert retried['usage']['tokens'] == 100 and retried['usage']['reserved_tokens'] == 64


async def crashed_advisor_job(tmp_path, *, configured=None, advisor=None):
    class Crash(BaseException):
        pass
    def crash(event, payload):
        if event == 'advisor_after_dispatch':
            raise Crash()
    h = Harness(tmp_path / 'jobs.db', investigator=advisor or Advisor(), failure_hook=crash)
    key = h.store.create(configured or ambiguous_goal())
    with pytest.raises(Crash):
        await h.engine.run(key)
    reopened = Harness(tmp_path / 'jobs.db', investigator=Advisor())
    await reopened.engine.resume(key)
    step = next(row['id'] for row in reopened.store.steps(key) if row['kind'].startswith('advisor:'))
    return reopened, key, step


@pytest.mark.asyncio
async def test_second_unknown_advisor_attempt_blocks_third_and_keeps_pagination(tmp_path):
    from shopextract.maintenance import MaintenanceError
    h, key, step = await crashed_advisor_job(tmp_path)
    h.engine.investigator = Advisor('unknown')
    report = await h.engine.retry_unknown(key, step)
    assert report['state'] == 'partial'
    assert report['usage']['reserved_tokens'] == 128
    assert h.store.report(key, offset=0, limit=1)['findings'] == report['findings']
    assert h.store.report(key, offset=1, limit=1)['findings'] == []
    with pytest.raises(MaintenanceError, match='retry_exhausted'):
        await h.engine.retry_unknown(key, step)


@pytest.mark.asyncio
@pytest.mark.parametrize('changed,expected', [('deadline','deadline'), ('budget','token_budget'),
                                             ('model','retry_mismatch'), ('cancel','invalid_state')])
async def test_advisor_retry_rechecks_fixed_policy_before_dispatch(tmp_path, changed, expected):
    from datetime import timedelta
    from shopextract.maintenance import MaintenanceError
    configured = ambiguous_goal(budgets=Budgets(tokens=64 if changed == 'budget' else 128, cost_micros=100))
    h, key, step = await crashed_advisor_job(tmp_path, configured=configured)
    adapter = Advisor()
    if changed == 'deadline':
        h.engine.utc_now = lambda: NOW + timedelta(minutes=2)
    elif changed == 'model':
        class ChangedModel(Advisor):
            def bound(self, payload):
                return replace(super().bound(payload), model='changed-model')
        adapter = ChangedModel()
    elif changed == 'cancel':
        await h.engine.cancel(key)
    h.engine.investigator = adapter
    before = h.store.report(key)['findings']
    with pytest.raises(MaintenanceError, match=expected):
        await h.engine.retry_unknown(key, step)
    assert adapter.calls == 0 and h.store.report(key)['findings'] == before


@pytest.mark.asyncio
async def test_retry_publication_failure_preserves_previous_composition_and_charge(tmp_path):
    class LargeAdvice(Advisor):
        def bound(self, payload):
            return AdvisorBound(32, 1024, 10, 'synthetic-v1', 'price-v1')
        async def investigate(self, payload, *, reservation, timeout):
            self.calls += 1
            return AdvisorResult('synthetic-v1', 'price-v1', {'explanation': 'x' * 1800}, (), AdvisorUsage(32, 900, 5))
    configured = ambiguous_goal(budgets=Budgets(tokens=3000, cost_micros=100, report_bytes=2500))
    h, key, step = await crashed_advisor_job(tmp_path, configured=configured, advisor=LargeAdvice())
    previous = h.store.report(key)['findings']
    h.engine.investigator = LargeAdvice()
    result = await h.engine.retry_unknown(key, step)
    assert h.engine.investigator.calls == 1
    assert result['stop_reason'] == 'report_budget'
    assert result['findings'] == previous
    assert result['usage']['reserved_tokens'] == 2112
    assert len(h.store.advisory_history(key, step)) == 1


@pytest.mark.asyncio
async def test_retry_cancellation_before_publication_keeps_prior_advisory(tmp_path):
    h, key, step = await crashed_advisor_job(tmp_path)
    previous = h.store.report(key)['findings']
    def cancel(event, payload):
        if event == 'advisor_before_publication':
            h.store.request_cancel(key)
    h.engine.failure_hook = cancel
    result = await h.engine.retry_unknown(key, step)
    assert result['state'] == 'cancelled'
    assert result['findings'] == previous
    assert result['usage']['reserved_tokens'] == 128
    assert len(h.store.advisory_history(key, step)) == 1


@pytest.mark.asyncio
async def test_retry_missing_profile_definition_refuses_before_model_call(tmp_path):
    from shopextract.maintenance import MaintenanceError, MaintenanceStore
    from shopextract.maintenance.profiles import CategoryProfile, FieldRule
    class Crash(BaseException):
        pass
    def crash(event, payload):
        if event == 'advisor_after_dispatch':
            raise Crash()
    configured = CategoryProfile('custom-v1', {'description': FieldRule('text','comparable')})
    h = Harness(tmp_path / 'jobs.db', investigator=Advisor(), failure_hook=crash)
    h.store = MaintenanceStore(tmp_path / 'jobs.db', custom_profiles={'custom-v1': configured})
    h.engine.store = h.store
    request = replace(ambiguous_goal(), profiles={'0': 'custom-v1'})
    key = h.store.create(request)
    with pytest.raises(Crash):
        await h.engine.run(key)
    h.engine.failure_hook = None
    await h.engine.resume(key)
    step = next(row['id'] for row in h.store.steps(key) if row['kind'].startswith('advisor:'))
    fresh = Harness(tmp_path / 'jobs.db', investigator=Advisor())
    with pytest.raises(MaintenanceError, match='profile_mismatch'):
        await fresh.engine.retry_unknown(key, step)
    assert fresh.engine.investigator.calls == 0
