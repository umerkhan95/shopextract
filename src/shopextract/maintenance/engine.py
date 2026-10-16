"""Bounded native-source reconciliation; optional investigation is separate."""
from __future__ import annotations

import asyncio
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..categories.contracts import CategoryRuntimeConfig

from .contracts import (AdvisorBound, AdvisorReservation, AdvisorResult, AdvisorUsage,
                        FailureHook, Investigator, MaintenanceError)
from .store import MaintenanceStore, digest, packed
from .profiles import FieldRule, compare_field


def json_value(value):
    from ..tools.domain import json_value as convert
    return convert(value)


def pointer(record, field):
    value = record
    for key in field.split('/'):
        key = key.replace('~1', '/').replace('~0', '~')
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


class _Accounting:
    def __init__(self, engine, job, step, retry):
        self.engine, self.job, self.step, self.retry = engine, job, step, retry
        self.attempts = {}
        self.counter = 0

    def before_request(self, method, url):
        e = self.engine
        e.store.check_cancel(self.job)
        self.counter += 1
        key = f'wire:{self.step}:{self.retry}:{self.counter}'
        e.store.add_step(self.job, key, 'wire:' + self.step)
        attempt = e.store.reserve(self.job, key, {'requests': 1}, now=e.now())
        self.attempts[attempt] = {'requests': 1}
        e.hook('intent_committed', job_id=self.job, step_id=self.step, attempt_id=attempt)
        e.hook('before_dispatch', job_id=self.job, step_id=self.step, attempt_id=attempt)
        return attempt

    def after_request(self, method, url, status):
        self.engine.hook('after_dispatch', job_id=self.job, step_id=self.step, status=status)


class MaintenanceEngine:
    def __init__(self, store: MaintenanceStore, *, tool_config, resolver=None,
                 wire_transport=None, utc_now=None, investigator: Investigator | None = None,
                 failure_hook: FailureHook | None = None,
                 category_config: CategoryRuntimeConfig | None = None):
        self._expected_category = None
        self._category_config = None
        if category_config is not None:
            from ..categories.config import runtime_record, runtime_from_record
            self._expected_category = runtime_from_record(runtime_record(category_config))
        self.store, self.tool_config = store, tool_config
        self.resolver, self.wire_transport = resolver, wire_transport
        self.utc_now = utc_now or (lambda: datetime.now(timezone.utc))
        self.investigator, self.failure_hook = investigator, failure_hook
        self._active = None
        self._task = None
        self._runtime = None
        self._cancel_event = None
        self._closed = False
        self._explicit_step = None
        self._model_stop = None

    def now(self):
        return self.utc_now()

    def hook(self, event, **payload):
        if self.failure_hook:
            self.failure_hook(event, payload)

    async def run(self, job_id):
        if self._closed:
            raise MaintenanceError('invalid_state')
        if self._active is not None:
            raise MaintenanceError('already_running')
        policy = self.store.category_policy(job_id)
        from ..categories.maintenance import category_policy_digest
        if self._expected_category is not None and (policy.mode != 'enabled' or
                policy.config_digest != category_policy_digest(self._expected_category)):
            raise MaintenanceError('category_policy_mismatch')
        self._category_config = None
        if policy.mode == 'enabled':
            import json
            from ..categories.config import runtime_from_record
            self._category_config = runtime_from_record(json.loads(policy.config_json))
        self._active = job_id
        self._task = asyncio.current_task()
        self._model_stop = None
        self._cancel_event = asyncio.Event()
        from ..tools import ToolRuntime
        from ..tools.contracts import ToolError
        acquired = False
        try:
            if self.store._lock is not None:
                raise MaintenanceError('owner_busy')
            self.store.acquire()
            acquired = True
            if not self.store.begin(job_id, now=self.now()):
                return self.store.report(job_id)
            goal = self.store.goal(job_id)
            self._model_stop = self.store.model_stop(job_id)
            self._runtime = ToolRuntime(self.tool_config, resolver=self.resolver,
                wire_transport=self.wire_transport, utc_now=self.utc_now,category_config=self._category_config)
            products, source_complete, reason = await self._collect(job_id, goal)
            if reason not in {'cancelled', 'deadline'}:
                await self._reconcile(job_id, goal, products)
            if self.store.status(job_id)['cancel_requested']:
                self.store.finish(job_id, 'cancelled', 'cancelled')
            else:
                if len(goal['baseline']) > goal['budgets']['products']:
                    reason = reason or 'product_budget'
                coverage = {'baseline_count': len(goal['baseline']),
                            'processed_products': min(len(goal['baseline']), goal['budgets']['products']),
                            'supplier_products': len(products), 'source_complete': source_complete}
                self._complete(job_id, source_reason=reason, coverage=coverage)
            return self.store.report(job_id)
        except asyncio.CancelledError:
            if acquired:
                self.store.request_cancel(job_id)
                self.store.finish(job_id, 'cancelled', 'cancelled')
                return self.store.report(job_id)
            raise
        except (MaintenanceError, ToolError) as error:
            if error.code in {'owner_busy', 'already_running', 'profile_mismatch', 'invalid_state'}:
                raise
            self.store.finish(job_id, 'cancelled' if error.code == 'cancelled' else 'partial', error.code)
            return self.store.report(job_id)
        finally:
            if self._runtime:
                await self._runtime.aclose()
                self._runtime = None
            if acquired:
                self.store.release()
            self._active = None
            self._task = None
            self._cancel_event = None

    def _complete(self, job, *, source_reason=None, coverage=None):
        state, reason, retained = self.store.completion(job, source_reason=source_reason,
            coverage=coverage, model_reason=self._model_stop)
        self.store.finish(job, state, reason, retained)

    async def resume(self, job_id):
        return await self.run(job_id)

    async def _source(self, job, goal, mode, url, maximum, *, explicit=False):
        from ..tools.context import OperationContext, OperationBudget
        from ..tools.contracts import ToolError
        if mode not in self.tool_config.allowed_tools:
            raise MaintenanceError('permission_denied')
        step = mode + ':' + digest(url)
        self.store.add_step(job, step, mode)
        state = next(row for row in self.store.steps(job) if row['id'] == step)
        if state['state'] == 'committed':
            return state['result'], None
        attempts = self.store.attempts(job, step)
        explicit = explicit or self._explicit_step == step
        if not explicit and any(row['state'] in {'intent', 'unknown'} for row in attempts):
            return None, 'outcome_unknown'
        # Authorize even a cache hit. Cached source never becomes an origin grant.
        deadline = datetime.fromisoformat(goal['deadline'])
        remaining = (deadline - self.now()).total_seconds()
        if remaining <= 0:
            return None, 'deadline'
        context = OperationContext(job, time.monotonic() + min(remaining, goal['budgets']['attempt_seconds']),
            self._cancel_event, OperationBudget(self.tool_config.limits), self._runtime.auxiliary, self.now())
        await self._runtime.guard.authorize(url, context)
        scope = {'url': url, 'mode': mode, 'maximum': maximum, 'profiles': self.store.status(job)['profile_definitions'],
                 'fields': goal['fields'], 'freshness_seconds': goal['freshness_seconds'],
                 'policy': asdict(self.tool_config), 'native_version': 1}
        if self._category_config is not None:
            from ..categories.maintenance import category_policy_digest
            scope['category_policy'] = category_policy_digest(self._category_config)
            scope['category_schema'] = 1
        cache_key = digest(scope)
        cached = self.store.cache_get(cache_key, now=self.now())
        if cached is not None:
            try:
                if mode == 'extract':
                    from .._portable import product_from_record
                    if not isinstance(cached.get('products'), list) or len(cached['products']) > maximum:
                        raise ValueError('Invalid cached product collection')
                    if self._category_config is not None:
                        from ..categories.portable import validate_categorized_products
                        validate_categorized_products(cached['products'],
                            options=self._category_config.options, maximum=maximum)
                    else:
                        for record in cached['products']:
                            product_from_record(record)
                elif not isinstance(cached.get('urls'), list) or not all(isinstance(url, str) for url in cached['urls']):
                    raise ValueError('Invalid cached source collection')
            except (ValueError, TypeError, KeyError):
                cached = None
        if cached is not None:
            self.store.checkpoint(job, step, cached)
            return cached, None
        logical_attempts = [row for row in attempts if row['step'] == step]
        for retry in range(len(logical_attempts), 2):
            accounting = _Accounting(self, job, step, retry)
            logical = self.store.reserve(job, step, {}, now=self.now(), explicit_retry=explicit)
            context = OperationContext(job, time.monotonic() + min((deadline - self.now()).total_seconds(),
                goal['budgets']['attempt_seconds']), self._cancel_event, OperationBudget(self.tool_config.limits),
                self._runtime.auxiliary, self.now(), accounting)
            received_result = False
            try:
                result = await asyncio.wait_for(self._runtime.sources.execute(mode, url, maximum, context),
                                                max(0, context.deadline - time.monotonic()))
                received_result = True
                settlements = dict(accounting.attempts, **{logical: {}})
                self.hook('before_checkpoint', job_id=job, step_id=step)
                self.store.checkpoint(job, step, result, settlements=settlements)
                self.hook('after_checkpoint', job_id=job, step_id=step)
                if result.get('complete'):
                    self.store.cache_put(cache_key, result,
                        expires=self.now() + timedelta(seconds=goal['freshness_seconds']))
                return result, None
            except (ToolError, asyncio.TimeoutError, MaintenanceError) as error:
                code = getattr(error, 'code', 'timeout')
                if code == 'cancelled':
                    raise
                # Completed failed attempts are charged; response receipt alone
                # never settles successful captures before the checkpoint.
                known = not received_result and code != 'timeout'
                self.store.fail_attempt(logical, code, known=known)
                for attempt in accounting.attempts:
                    self.store.fail_attempt(attempt, code, known=known)
                if code in {'request_budget', 'token_budget', 'cost_budget', 'deadline', 'evidence_budget', 'report_budget'}:
                    return None, code
                if code == 'timeout':
                    return None, 'outcome_unknown'
                transient = isinstance(error, ToolError) and error.retryable and code != 'timeout'
                if transient and retry == 0:
                    delay = .05
                    until = self.now() + timedelta(seconds=delay)
                    self.store.fail_attempt(logical, code, retry_at=until)
                    await asyncio.sleep(delay)
                    # Clock injection may be fixed; no busy-wait or reset.
                    if self.now() < until:
                        return None, code
                    continue
                failure = {'products': [], 'urls': [], 'complete': False, 'diagnostics': [{'code': code}]}
                # No inferred absence/removal from failed source.
                self.store.checkpoint(job, step, failure, settlements=dict(accounting.attempts, **{logical: {}}))
                return failure, code
        return None, 'retry_exhausted'

    async def _collect(self, job, goal):
        if goal['budgets']['products'] == 0:
            return [], False, 'product_budget'
        urls = goal['product_urls']
        maximum = min(self.tool_config.limits.item_count, max(2, goal['budgets']['products'] + 1))
        products, complete, reason = [], True, None
        if not urls:
            discovered, why = await self._source(job, goal, 'discover', goal['supplier_origin'], maximum)
            if discovered is None:
                return [], False, why
            urls = discovered.get('urls', [])
            complete = discovered.get('complete', False)
        if goal['budgets']['products'] == 0:
            return [], False, 'product_budget'
        for url in urls:
            self.store.check_cancel(job)
            result, why = await self._source(job, goal, 'extract', url, maximum)
            if result:
                products.extend(result.get('products', []))
                complete &= result.get('complete', False)
            if why:
                complete, reason = False, reason or why
                if why in {'request_budget', 'deadline', 'evidence_budget', 'report_budget'}:
                    break
        # Deduplicate the same immutable portable record, not distinct conflicting captures.
        unique = {digest(record): record for record in products}
        if len(unique) > goal['budgets']['products']:
            complete, reason = False, reason or 'product_budget'
        return list(unique.values()), complete, reason

    def _supported(self, product, field, goal):
        from .._evidence import trust_view
        from .._resolution import ResolutionPolicy, resolve_fields
        contract = getattr(product, 'evidence_contract', None)
        if contract:
            age = timedelta(seconds=max(goal['freshness_seconds'], .000001))
            contract = resolve_fields(contract, as_of=self.now(),
                policy=ResolutionPolicy(offer_max_age=age, specification_max_age=age))
        support = trust_view(product, contract).get('/' + field, {})
        evidences = {e.evidence_id: e for e in contract.evidence} if contract else {}
        ids = support.get('evidence_ids', [])
        if contract and support.get('state') == 'observed':
            resolution = next((r for r in contract.resolutions if r.field_path == '/' + field), None)
            selected = next((o for o in contract.observations if resolution and o.observation_id == resolution.selected_observation_id), None)
            if selected:
                ids = list(selected.evidence_ids)
        retained = [evidences[key] for key in ids if key in evidences]
        meta = {'kind': 'captured', 'evidence_ids': ids,
                'source_url': retained[0].source_url if retained else None,
                'observed_at': retained[0].observed_at.isoformat() if retained else None,
                'state': support.get('state', 'unsupported')}
        value = support.get('value')
        if goal['freshness_seconds'] > 0 and any((self.now() - item.observed_at).total_seconds() >= goal['freshness_seconds'] for item in retained):
            meta['state'], value = 'expired', None
        return value, meta, [json_value(asdict(value)) for value in retained]

    async def _reconcile(self, job, goal, records):
        from .._portable import product_from_record
        from ..compare.identity_match import match_products, MatchRelation
        companions = []
        if self._category_config is not None:
            from ..categories.portable import categorized_product_from_record
            companions = [categorized_product_from_record(record) for record in records]
            right = [value.product for value in companions]
            left = [categorized_product_from_record(record).product if goal['baseline_mode'] == 'captured' else record
                    for record in goal['baseline'][:goal['budgets']['products']]]
        else:
            right = [product_from_record(record) for record in records]
            left = [product_from_record(record) if goal['baseline_mode'] == 'captured' else record
                    for record in goal['baseline'][:goal['budgets']['products']]]
        # The matcher accepts full dictionaries. Materialize dataclasses once,
        # preserving every identity/variant field, rather than copying each pair.
        match_left = [asdict(value) if not isinstance(value, dict) else value for value in left]
        match_right = [asdict(value) for value in right]
        decisions = match_products(match_left, match_right)
        definitions = self.store.validate_profiles(job)
        pending_source = any(row['kind'] in {'extract', 'discover'} and row['state'] != 'committed'
                             for row in self.store.steps(job))
        for index, original in enumerate(goal['baseline'][:goal['budgets']['products']]):
            key = str(original.get('external_id') or original.get('canonical_product_id') or index)
            # Portable captured records keep scalar fields under product.
            if goal['baseline_mode'] == 'captured':
                plain = json_value(asdict(left[index]))
                key = str(plain.get('external_id') or plain.get('canonical_product_id') or index)
            else:
                plain = original
            candidates = [decision for decision in decisions if decision.index_a == index]
            candidate = candidates[0] if len(candidates) == 1 else None
            if candidate is None:
                # Context for review may use one uniquely identifier-anchored
                # candidate. Never change its relation or hide duplicate anchors.
                anchored = [decision for decision in candidates if any(
                    reason == 'validated GTIN agrees' or reason == 'brand and MPN agree'
                    or reason.startswith('supplier-scoped ') for reason in decision.evidence)]
                if len(anchored) == 1:
                    candidate = anchored[0]
            supplier = right[candidate.index_b] if candidate and candidate.index_b is not None else None
            if supplier is None and pending_source:
                continue
            category = goal['profiles'].get(key)
            for ordinal, field in enumerate(goal['fields']):
                step = 'compare:' + digest({'key': key, 'field': field})
                self.store.add_step(job, step, 'compare')
                if any(row['id'] == step and row['state'] == 'committed' for row in self.store.steps(job)):
                    continue
                self.store.check_cancel(job)
                after, support, evidence = self._supported(supplier, field, goal) if supplier else (None, {}, [])
                if goal['baseline_mode'] == 'captured':
                    before, baseline_support, before_evidence = self._supported(left[index], field, goal)
                    evidence.extend(before_evidence)
                else:
                    before = pointer(plain, field)
                    baseline_support = {'kind': 'supplied', 'source_url': None, 'observed_at': None,
                                        'evidence_ids': [], 'state': 'asserted' if before is not None else 'unknown'}
                definition = definitions.get(category, {})
                rule_value = definition.get('fields', {}).get(field)
                comparison = compare_field(FieldRule(**rule_value), before, after) if rule_value else {
                    'comparison': 'unknown', 'normalized_before': before, 'normalized_after': after, 'trace': []}
                missing_size_system = (category == 'footwear-v1' and field == 'attributes/size'
                    and (not pointer(plain, 'attributes/size_system') or supplier is None
                         or not supplier.attributes.get('size_system')))
                different_size_system = (category == 'footwear-v1' and field == 'attributes/size'
                    and not missing_size_system and pointer(plain, 'attributes/size_system') != supplier.attributes.get('size_system'))
                if missing_size_system or different_size_system:
                    comparison['comparison'] = 'unknown'
                category_reasons = ()
                if self._category_config is not None:
                    if supplier is None:
                        category_reasons = ('category_unavailable',)
                    else:
                        from ..categories.maintenance import category_review_reasons
                        category_reasons = category_review_reasons(companions[candidate.index_b],
                            selected_profile=category,config=self._category_config)
                reason = None
                if category_reasons:
                    reason = category_reasons[0]
                elif category is None:
                    reason = 'category_missing'
                elif supplier is not None and self._category_conflict(category, plain, supplier):
                    reason = 'category_mismatch'
                elif goal['baseline_mode'] == 'captured' and baseline_support.get('state') in {'unsupported', 'expired', 'conflicting'}:
                    reason = 'baseline_unsupported'
                elif before is None:
                    reason = 'baseline_missing'
                elif goal['baseline_mode'] == 'captured' and baseline_support.get('state') != 'observed':
                    reason = 'baseline_unsupported'
                elif supplier is None or support.get('state') != 'observed':
                    reason = 'supplier_unsupported'
                elif missing_size_system:
                    reason = 'size_system_unknown'
                elif different_size_system:
                    reason = 'size_system_mismatch'
                elif candidate.relation != MatchRelation.EXACT or candidate.needs_review:
                    reason = 'identity_unresolved'
                elif field == 'price' and self._supported(supplier, 'currency', goal)[1].get('state') != 'observed':
                    reason = 'currency_unsupported'
                elif field == 'price' and str(pointer(plain, 'currency')) != str(supplier.currency):
                    reason = 'currency_mismatch'
                elif rule_value['role'] == 'identity_variant' and comparison['comparison'] != 'equal':
                    reason = 'variant_specification'
                elif comparison['comparison'] == 'unknown':
                    reason = 'unsupported_value'
                # Exact identifier claims require real supplier identifier support.
                if reason is None and not self._identity_supported(candidate, supplier, goal):
                    reason = 'identifier_unsupported'
                if reason is None and goal['baseline_mode'] == 'captured' and not self._identity_supported(candidate, left[index], goal):
                    reason = 'baseline_identifier_unsupported'
                status = 'needs_review' if reason else ('unchanged' if comparison['comparison'] == 'equal' else 'proposed_correction')
                finding = {'finding_id': digest({'job': job, 'key': key, 'field': field}),
                    'ordinal': index * len(goal['fields']) + ordinal, 'product_key': key, 'profile': category,
                    'field': field, 'role': rule_value['role'] if rule_value else None, 'status': status,
                    'reason': reason, 'before': json_value(before), 'after': json_value(after), **json_value(comparison),
                    'baseline_support': baseline_support, 'supplier_support': support,
                    'evidence_ids': list(dict.fromkeys(e['evidence_id'] for e in evidence)),
                    'match_reason': {'evidence': candidate.evidence if candidate else [],
                                     'conflicts': candidate.conflicts if candidate else ['ambiguous candidates']}}
                if self._category_config is not None:
                    finding['category_review_reasons'] = list(category_reasons)
                finding, settlements, cached = await self._advise(job, step, goal, finding, evidence)
                publications = self._publication(job, step, finding, settlements)
                self.store.checkpoint(job, step, {'finding_id': finding['finding_id']}, evidence=evidence,
                                      findings=[finding], settlements=settlements,
                                      violations=tuple(settlements) if publications and publications[0]['payload'].get('status') == 'budget_violation' else (),
                                      advisories=publications)
                if cached:
                    cache_key, payload = cached
                    self.store.cache_put(cache_key, payload, expires=self.now() + timedelta(seconds=goal['freshness_seconds']))

    def _publication(self, job, compare_step, finding, settlements):
        advisory = finding.pop('advisory', None)
        if advisory is None:
            return ()
        step = 'advisor:' + finding['finding_id']
        self.store.add_step(job, step, 'advisor:' + compare_step)
        attempts = self.store.attempts(job, step)
        attempt_id = next(iter(settlements), attempts[-1]['id'] if attempts else None)
        return ({'step': step, 'attempt_id': attempt_id, 'finding_id': finding['finding_id'], 'payload': advisory},)

    async def _advise(self, job, compare_step, goal, finding, evidence, *, explicit=False):
        if self.store.model_stop(job) == 'budget_violation':
            self._model_stop = 'budget_violation'
            return finding, {}, None
        if self.investigator is None or finding['status'] != 'needs_review':
            return finding, {}, None
        if ((not explicit and self._model_stop not in {None, 'model_usage_unknown', 'model_outcome_unknown'}) or not evidence
            or finding['reason'] in {'category_missing', 'category_mismatch'}
            or goal['budgets']['tokens'] == 0 or goal['budgets']['cost_micros'] == 0):
            return finding, {}, None
        step = 'advisor:' + finding['finding_id']
        prior = self.store.attempts(job, step)
        if prior and not explicit:
            finding['advisory'] = {'status': 'outcome_unknown', 'reason': 'No automatic model replay'}
            self._model_stop = 'model_outcome_unknown'
            return finding, {}, None
        if self._model_stop == 'model_outcome_unknown' and not explicit:
            return finding, {}, None
        def clipped(value):
            return value[:2048] if isinstance(value, str) else value
        payload = {'schema_version': '1.0', 'profile': finding['profile'], 'field': finding['field'],
            'product_key': finding['product_key'], 'before': clipped(finding['before']),
            'after': clipped(finding['after']), 'reason': finding['reason'],
            'match_reason': finding['match_reason'],
            'evidence': [{k: item.get(k) for k in ('evidence_id', 'source_url', 'observed_at', 'pointer')}
                         for item in evidence[:8]]}
        if len(packed(payload).encode()) > min(8192, goal['budgets']['input_bytes']):
            finding['advisory'] = {'status': 'skipped', 'reason': 'advisor_payload_limit'}
            return finding, {}, None
        original_intent = None
        if explicit:
            original_intent = next(row['result'] for row in self.store.steps(job) if row['id'] == step)
            if (not original_intent or original_intent.get('payload_digest') != digest(payload)
                or original_intent.get('profile_digest') != digest(self.store.status(job)['profile_definitions'])
                or original_intent.get('policy_digest') != digest(asdict(self.tool_config))
                or original_intent.get('full_values_digest') != digest([finding['before'], finding['after']])):
                raise MaintenanceError('retry_mismatch')
            for item in evidence:
                if goal['freshness_seconds'] > 0 and (self.now() - datetime.fromisoformat(item['observed_at'])).total_seconds() >= goal['freshness_seconds']:
                    raise MaintenanceError('evidence_expired')
        try:
            bound = self.investigator.bound(payload)
        except Exception:
            if explicit:
                raise MaintenanceError('retry_mismatch')
            finding['advisory'] = {'status': 'unavailable'}
            return finding, {}, None
        if (not isinstance(bound, AdvisorBound) or not isinstance(bound.model, str) or not bound.model
            or len(bound.model) > 200 or not isinstance(bound.price_version, str) or not bound.price_version
            or len(bound.price_version) > 200
            or any(type(n) is not int or n < 0 for n in (bound.input_tokens, bound.max_output_tokens, bound.cost_micros))
            or bound.input_tokens + bound.max_output_tokens == 0):
            if explicit:
                raise MaintenanceError('retry_mismatch')
            finding['advisory'] = {'status': 'skipped', 'reason': 'unknown_bound'}
            return finding, {}, None
        if explicit and original_intent['bound'] != asdict(bound):
            raise MaintenanceError('retry_mismatch')
        cache_key = digest({'kind': 'advisor', 'payload': payload, 'bound': asdict(bound),
            'full_values': digest([finding['before'], finding['after']]),
            'profiles': self.store.status(job)['profile_definitions'],
            'prompt_version': 1, 'policy': asdict(self.tool_config)})
        cached = None if explicit else self.store.cache_get(cache_key, now=self.now())
        if cached:
            finding['advisory'] = cached['advisory']
            return finding, {}, None
        self.store.add_step(job, step, 'advisor:' + compare_step)
        self.store.prepare_step(job, step, {'bound': asdict(bound), 'payload': payload,
            'payload_digest': digest(payload), 'profile_digest': digest(self.store.status(job)['profile_definitions']),
            'policy_digest': digest(asdict(self.tool_config)), 'full_values_digest': digest([finding['before'], finding['after']])})
        try:
            attempt = self.store.reserve(job, step, {'tokens': bound.input_tokens + bound.max_output_tokens,
                                                   'cost_micros': bound.cost_micros}, now=self.now(), explicit_retry=explicit)
        except MaintenanceError as error:
            if explicit or error.code not in {'token_budget', 'cost_budget', 'deadline'}:
                raise
            finding['advisory'] = {'status': 'skipped', 'reason': error.code}
            self._model_stop = error.code
            return finding, {}, None
        reservation = AdvisorReservation(attempt, bound)
        self.hook('advisor_intent_committed', job_id=job, step_id=step, attempt_id=attempt)
        timeout = min(goal['budgets']['attempt_seconds'],
                      (datetime.fromisoformat(goal['deadline']) - self.now()).total_seconds())
        try:
            self.hook('advisor_before_dispatch', job_id=job, step_id=step, attempt_id=attempt)
            result = await asyncio.wait_for(self.investigator.investigate(payload,
                reservation=reservation, timeout=timeout), max(0, timeout))
            self.hook('advisor_after_dispatch', job_id=job, step_id=step, attempt_id=attempt)
        except (asyncio.TimeoutError, Exception) as error:
            finding['advisory'] = {'status': 'timeout' if isinstance(error, asyncio.TimeoutError) else 'failed'}
            self._model_stop = 'advisor_timeout' if isinstance(error, asyncio.TimeoutError) else 'advisor_failed'
            return finding, {attempt: None}, None
        valid_identity = (isinstance(result, AdvisorResult) and result.model == bound.model
                          and result.price_version == bound.price_version)
        valid_usage = valid_identity and (result.usage is None or (
            isinstance(result.usage, AdvisorUsage) and all(type(n) is int and n >= 0 for n in
                (result.usage.input_tokens, result.usage.output_tokens, result.usage.cost_micros))))
        overrun = bool(valid_usage and result.usage is not None and (
            result.usage.input_tokens > bound.input_tokens or result.usage.output_tokens > bound.max_output_tokens
            or result.usage.cost_micros > bound.cost_micros))
        if not valid_identity or not valid_usage or overrun:
            finding['advisory'] = {'status': 'budget_violation' if overrun else 'invalid_result'}
            if overrun:
                finding['advisory']['reported_usage'] = asdict(result.usage)
            self._model_stop = 'budget_violation' if overrun else 'advisor_invalid_result'
            actual = {'tokens': result.usage.input_tokens + result.usage.output_tokens,
                      'cost_micros': result.usage.cost_micros} if overrun else None
            return finding, {attempt: actual}, None
        allowed_ids = {item['evidence_id'] for item in payload['evidence']}
        schema_ok = (isinstance(result.advisory, dict) and
            set(result.advisory) <= {'reason', 'explanation', 'suggested_checks'} and
            all(isinstance(value, str) and len(value) <= 2048 for value in result.advisory.values()) and
            isinstance(result.evidence_ids, tuple) and len(result.evidence_ids) <= 8 and
            all(isinstance(key, str) and key in allowed_ids for key in result.evidence_ids) and
            len(set(result.evidence_ids)) == len(result.evidence_ids))
        if not schema_ok:
            finding['advisory'] = {'status': 'invalid_result'}
            self._model_stop = 'advisor_invalid_result'
            return finding, {attempt: None}, None
        advisory = {'status': 'available', 'content': dict(result.advisory),
                    'evidence_ids': list(result.evidence_ids), 'model': result.model,
                    'price_version': result.price_version}
        finding['advisory'] = advisory
        if result.usage is None:
            self._model_stop = 'model_usage_unknown'
            return finding, {attempt: None}, None
        usage = {'tokens': result.usage.input_tokens + result.usage.output_tokens,
                 'cost_micros': result.usage.cost_micros}
        return finding, {attempt: usage}, (cache_key, {'complete': True, 'advisory': advisory})

    def _identity_supported(self, candidate, product, goal):
        def observed(path):
            return self._supported(product, path, goal)[1].get('state') == 'observed'
        for reason in candidate.evidence:
            if reason == 'validated GTIN agrees' and observed('gtin'):
                return True
            if reason.startswith('supplier-scoped '):
                field = reason[len('supplier-scoped '):].split()[0]
                if observed('external_id' if field == 'canonical_product_id' else field):
                    return True
            if reason == 'brand and MPN agree' and observed('vendor') and observed('mpn'):
                return True
        return False

    def _category_conflict(self, category, baseline, supplier):
        # This is only a conflict veto for explicit category labels, not an
        # automatic profile selector. Unknown labels do not grant a profile.
        aliases = {'hardware': 'hardware-v1', 'electronics': 'hardware-v1',
                   'footwear': 'footwear-v1', 'boots': 'footwear-v1', 'shoes': 'footwear-v1'}
        labels = [baseline.get('product_type')] + list(getattr(supplier, 'category_path', []) or [])
        declared = {aliases.get(str(value).casefold()) for value in labels if value is not None}
        return any(value is not None and value != category for value in declared) if category in {'hardware-v1', 'footwear-v1'} else False

    async def retry_unknown(self, job_id, step_id):
        if self._active is not None:
            raise MaintenanceError('already_running')
        state = self.store.status(job_id)['state']
        if state not in {'paused', 'partial'}:
            raise MaintenanceError('invalid_state')
        steps = [row for row in self.store.steps(job_id) if row['id'] == step_id]
        if steps and steps[0]['kind'].startswith('advisor:'):
            return await self._retry_advisor(job_id, step_id)
        if not steps or steps[0]['kind'] not in {'extract', 'discover'}:
            raise MaintenanceError('invalid_argument')
        attempts = self.store.attempts(job_id, step_id)
        if not any(row['state'] in {'intent', 'unknown'} for row in attempts):
            raise MaintenanceError('invalid_state')
        if len([row for row in attempts if row['step'] == step_id]) >= 2:
            raise MaintenanceError('retry_exhausted')
        self._explicit_step = step_id
        try:
            return await self.run(job_id)
        finally:
            self._explicit_step = None

    async def _retry_advisor(self, job, step):
        if self.store._lock is not None:
            raise MaintenanceError('owner_busy')
        self.store.acquire()
        self._active, self._task = job, asyncio.current_task()
        self._cancel_event = asyncio.Event()
        self._model_stop = None
        dispatched = False
        try:
            self.store.validate_profiles(job)
            if self.store.model_stop(job) == 'budget_violation':
                raise MaintenanceError('budget_violation')
            prior = self.store.attempts(job, step)
            if len(prior) >= 2:
                raise MaintenanceError('retry_exhausted')
            if not prior or prior[-1]['state'] not in {'intent', 'unknown'}:
                raise MaintenanceError('invalid_state')
            goal = self.store.goal(job)
            if self.now() >= datetime.fromisoformat(goal['deadline']):
                raise MaintenanceError('deadline')
            if self.investigator is None:
                raise MaintenanceError('retry_mismatch')
            parent = next(row['kind'][len('advisor:'):] for row in self.store.steps(job) if row['id'] == step)
            finding_id = step[len('advisor:'):]
            finding = next((dict(value) for value in self.store._findings(job)
                            if value['finding_id'] == finding_id), None)
            if finding is None:
                raise MaintenanceError('invalid_state')
            finding.pop('advisory', None)
            evidence = [self.store.evidence(job, key) for key in finding['evidence_ids']]
            self.store.begin(job, now=self.now())
            finding, settlements, _ = await self._advise(job, parent, goal, finding, evidence, explicit=True)
            dispatched = bool(settlements)
            publications = self._publication(job, parent, finding, settlements)
            self.hook('advisor_before_publication', job_id=job, step_id=step)
            result = next(row['result'] for row in self.store.steps(job) if row['id'] == parent)
            self.store.checkpoint(job, parent, result, settlements=settlements, advisories=publications,
                violations=tuple(settlements) if publications[0]['payload'].get('status') == 'budget_violation' else ())
            self._complete(job)
            return self.store.report(job)
        except asyncio.CancelledError:
            self.store.request_cancel(job)
            self.store.finish(job, 'cancelled', 'cancelled')
            return self.store.report(job)
        except MaintenanceError as error:
            # Failed result publication must retain previous composed report and
            # the new uncertain charge; pre-dispatch refusal remains an error.
            self.store.finish(job, 'partial', error.code)
            if dispatched and error.code in {'report_budget', 'evidence_budget', 'cancelled'}:
                return self.store.report(job)
            raise
        finally:
            self.store.release()
            self._active, self._task, self._cancel_event = None, None, None

    async def cancel(self, job_id):
        state = self.store.request_cancel(job_id)
        if self._active == job_id and self._cancel_event:
            self._cancel_event.set()
            if self._task is not asyncio.current_task():
                self._task.cancel()
        end = time.monotonic() + self.tool_config.limits.cleanup_seconds
        while state['state'] == 'running' and time.monotonic() < end:
            await asyncio.sleep(.01)
            state = self.store.status(job_id)
        if state['state'] == 'running':
            raise MaintenanceError('cleanup_timeout')
        return state

    async def close(self):
        if self._active:
            await self.cancel(self._active)
        self._closed = True
        self.store.close()
