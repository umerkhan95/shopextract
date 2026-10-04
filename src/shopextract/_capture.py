"""Bounded source capture and conservative normalization provenance."""
from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import asdict, is_dataclass, replace
import json
from uuid import uuid4

from ._evidence import Evidence, FieldObservation, SupportState, TrustContract, factual_paths

FRAGMENT_BYTES = 4096
PRODUCT_BYTES = 65536


def _size(value):
    return len(json.dumps(value, ensure_ascii=False, default=str, allow_nan=False).encode('utf-8'))


def capture(raw, source_url, method, *, observed_at=None, source=None, excerpt=None):
    """Retain bounded source projections before adapters enrich/mutate values."""
    context = {"url": source_url, "method": method,
               "at": (observed_at or datetime.now(timezone.utc)).isoformat() if not isinstance(observed_at, str) else observed_at, "values": {},
               "truncated": False}
    used = 0

    def visit(value, path, containers=False):
        nonlocal used
        try:
            size = _size(value)
        except (ValueError, TypeError):
            context["truncated"] = True
            return
        is_container = isinstance(value, (dict, list))
        if is_container == containers and size <= FRAGMENT_BYTES and used + size <= PRODUCT_BYTES:
            # JSON copy prevents subsequent adapter mutations altering evidence.
            context['values'][path] = json.loads(json.dumps(value, default=str))
            used += size
        elif is_container == containers:
            context['truncated'] = True
        if isinstance(value, dict):
            for key, item in value.items():
                if not key.startswith('_'):
                    visit(item, path + '/' + key.replace('~', '~0').replace('/', '~1'), containers)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                visit(item, path + '/' + str(index), containers)

    # Reserve leaf support first; repeated ancestor objects must not starve later fields.
    for containers in (False, True):
        for key, value in (source if source is not None else raw).items():
            if not key.startswith('_'):
                visit(value, '/' + key.replace('~', '~0').replace('/', '~1'), containers)
    if excerpt and len(excerpt.encode('utf-8')) <= FRAGMENT_BYTES and used + len(excerpt.encode('utf-8')) <= PRODUCT_BYTES:
        context['excerpt'] = excerpt
    elif excerpt:
        context['truncated'] = True
    raw['_capture'] = context
    return raw


def attach_contract(product, raw, outcomes):
    """Consume normalizer outcomes; never select sources or repeat conversions."""
    context = raw.get('_capture')
    contract = TrustContract()
    used = 0
    for path, value in factual_paths(product).items():
        outcome = outcomes.get(path)
        sources = outcome.source_paths if outcome else ()
        state = SupportState.UNSUPPORTED
        reason = outcome.reason if outcome and outcome.reason else 'No retained source mapping; compatibility/default value'
        evidence_ids, raw_values = [], []
        transformations = list(outcome.transformations) if outcome else []
        supported = bool(outcome and outcome.accepted and _plain(value) == _plain(outcome.normalized_value))
        for source_index, source_path in enumerate(sources):
            source_context = context
            # An ID-checked adapter capture replaces only the enriched input's support.
            for enrichment in raw.get('_identifier_sources', []):
                if enrichment.get('source_path') == source_path and enrichment.get('_capture'):
                    source_context = enrichment['_capture']
                    source_path = '/barcode'
                    transformations.append('Identifier enriched by matching product and variant IDs; original barcode absent')
                    break
            field_source = raw.get('_field_sources', {}).get(source_path)
            if field_source and field_source.get('_capture'):
                source_context = field_source['_capture']
                source_path = field_source['capture_path']
            values = source_context.get('values', {}) if source_context else {}
            original = values.get(source_path)
            raw_values.append(original)
            if context and context.get('method') == 'llm':
                reason = 'LLM output has no verified supporting source span or pointer'
            elif source_path not in values:
                reason = 'Selected source has no retained capture; support unavailable'
                if source_context and source_context.get('truncated'):
                    reason += ' or truncated by capture byte limits'
            elif not _same_source(original, outcome.source_values[source_index]):
                reason = 'Selected input differs from retained capture; changed or enriched value has no matching support'
            elif original is None or original == '':
                state, reason = SupportState.UNKNOWN, 'Source explicitly contains no value'
            elif supported and value is not None:
                payload = {'source_pointer': source_path, 'value': original}
                if source_context.get('excerpt'):
                    payload['source_excerpt'] = source_context['excerpt']
                if _size(payload) > FRAGMENT_BYTES:
                    payload.pop('source_excerpt', None)
                size = _size(payload)
                if size <= FRAGMENT_BYTES and used + size <= PRODUCT_BYTES:
                    evidence = Evidence('e_'+str(uuid4()), source_context['url'], datetime.fromisoformat(source_context['at']),
                                        source_context['method'], retained_data=payload, pointer='/value',
                                        truncated=source_context.get('truncated', False))
                    contract.evidence.append(evidence)
                    evidence_ids.append(evidence.evidence_id)
                    used += size
                    state, reason = SupportState.OBSERVED, ''
                else:
                    reason = 'Retained evidence byte budget exhausted; support truncated'
            elif not reason:
                reason = 'Normalization rejected source value or emitted a compatibility default'
        if context and context.get('method') == 'llm':
            state = SupportState.UNSUPPORTED
            reason = 'LLM output has no verified supporting source span or pointer'
        if len(evidence_ids) != len(sources) and state == SupportState.OBSERVED:
            state, reason = SupportState.UNSUPPORTED, 'Some selected inputs have no retained support'
        contract.observations.append(FieldObservation('o_'+str(uuid4()), path, state,
            raw_value=raw_values[0] if len(raw_values) == 1 else raw_values or None,
            normalized_value=_plain(value) if state == SupportState.OBSERVED else None,
            evidence_ids=evidence_ids, reason=reason, transformations=transformations))
    contract.validate()
    product.evidence_contract = contract
    for index, variant in enumerate(product.variants):
        prefix = f'/variants/{index}'
        observations = [replace(o, field_path=o.field_path[len(prefix):])
                        for o in contract.observations if o.field_path.startswith(prefix + '/')]
        referenced = {e for o in observations for e in o.evidence_ids}
        variant.evidence_contract = TrustContract(
            evidence=[e for e in contract.evidence if e.evidence_id in referenced],
            observations=observations)
    return contract


def _plain(value):
    if is_dataclass(value):
        return {k: _plain(v) for k, v in asdict(value).items()}
    if isinstance(value, list):
        return [_plain(v) for v in value]
    if isinstance(value, dict):
        return {k: _plain(v) for k, v in value.items()}
    return value




def _same_source(retained, selected):
    # Match the capture codec, preserving distinctions such as literal zero/false.
    try:
        options = dict(sort_keys=True, ensure_ascii=False, default=str, allow_nan=False)
        return json.dumps(retained, **options) == json.dumps(selected, **options)
    except (TypeError, ValueError):
        return False
