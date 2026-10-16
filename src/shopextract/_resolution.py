"""Deterministic field authority over already-aligned captured observations."""
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
import json
import re
import unicodedata

from ._evidence import (FieldResolution, SupportState, TrustContract, _utc,
                        encode_value)

# These paths describe an offer, not manufacturer specifications or list prices.
_OFFER = re.compile(r'^/(?:variants/(?:0|[1-9][0-9]*)/)?(?:price|compare_at_price|currency|in_stock|condition|sku|external_id|variant_id|product_url)$')
_CASELESS = {'/title', '/vendor', '/condition'}


@dataclass(frozen=True)
class ResolutionPolicy:
    """Version-one rules; source role labels must be established by the caller."""
    offer_max_age: timedelta = timedelta(days=1)
    specification_max_age: timedelta = timedelta(days=30)
    name: str = field(default='field-source-authority', init=False)
    version: str = field(default='1', init=False)

    def __post_init__(self):
        for age in (self.offer_max_age, self.specification_max_age):
            if not isinstance(age, timedelta) or age <= timedelta(0):
                raise ValueError('Freshness windows must be positive timedeltas')

    def max_age(self, path):
        return self.offer_max_age if _OFFER.fullmatch(path) else self.specification_max_age

    def authority(self, path, role):
        if _OFFER.fullmatch(path):
            return {'supplier': 2, 'unverified': 1}.get(role, 0)
        return {'verified_manufacturer': 3, 'supplier': 2,
                'manufacturer': 1, 'unverified': 1}.get(role, 1)


def _equivalent_key(value, path):
    """Typed equivalence for normalized data; preserve original values verbatim."""
    if isinstance(value, bool):
        return ('bool', value)
    if isinstance(value, (int, float, Decimal)):
        return ('number', Decimal(str(value)))
    if isinstance(value, str):
        text = unicodedata.normalize('NFC', value).strip()
        variant_leaf = re.sub(r'^/variants/[0-9]+', '', path)
        if variant_leaf in _CASELESS:
            text = ' '.join(text.casefold().split())
        return ('text', text)
    if isinstance(value, dict):
        return ('dict', tuple((k, _equivalent_key(v, path)) for k, v in sorted(value.items())))
    if isinstance(value, list):
        return ('list', tuple(_equivalent_key(v, path) for v in value))
    return ('typed', json.dumps(encode_value(value), sort_keys=True, ensure_ascii=False))


def resolve_fields(contract: TrustContract, *, as_of: datetime,
                   policy: ResolutionPolicy | None = None) -> TrustContract:
    """Resolve one aligned record without changing scalars or input observations.

    Every input observation/evidence record is retained. Evaluation time is required;
    the resolver never reads the system clock or infers roles from source URLs.
    Callers must align product/variant identities, offer scope and currency first.
    """
    _utc(as_of)
    policy = ResolutionPolicy() if policy is None else policy
    if not isinstance(policy, ResolutionPolicy):
        raise ValueError('policy must be a ResolutionPolicy')
    policy.__post_init__()
    contract.validate()
    result = deepcopy(contract)
    result.evidence.sort(key=lambda e: e.evidence_id)
    result.observations.sort(key=lambda o: o.observation_id)
    evidence = {e.evidence_id: e for e in result.evidence}
    grouped = {}
    for observation in result.observations:
        grouped.setdefault(observation.field_path, []).append(observation)
    result.resolutions = []
    for path, observations in sorted(grouped.items()):
        eligible, explanations, stale = [], [], False
        for observation in observations:
            identifier = observation.observation_id
            if observation.state != SupportState.OBSERVED:
                explanations.append(f'{identifier}: {observation.state.value}: {observation.reason}')
                continue
            sources = [evidence[i] for i in observation.evidence_ids]
            if any(e.observed_at > as_of for e in sources):
                explanations.append(f'{identifier}: excluded future-dated evidence')
                continue
            if any(as_of - e.observed_at > policy.max_age(path) for e in sources):
                stale = True
                explanations.append(f'{identifier}: excluded stale evidence')
                continue
            rank = min(policy.authority(path, e.source_role) for e in sources)
            if not rank:
                explanations.append(f'{identifier}: excluded role not authoritative for this offer field')
                continue
            eligible.append((rank, observation))
            roles = ','.join(sorted({e.source_role for e in sources}))
            explanations.append(f'{identifier}: eligible roles={roles}, authority={rank}')
        selected = None
        if eligible:
            rank = max(rank for rank, _ in eligible)
            top = [o for r, o in eligible if r == rank]
            if len({_equivalent_key(o.normalized_value, path) for o in top}) == 1:
                selected = min(o.observation_id for o in top)
                state = SupportState.OBSERVED
                outcome = f'Selected {selected}: highest authority={rank}; equivalent peers use stable observation ID'
            else:
                state = SupportState.CONFLICTING
                outcome = f'Unresolved disagreement among highest-authority={rank} observations'
        else:
            if stale or all(o.state == SupportState.EXPIRED for o in observations):
                state = SupportState.EXPIRED
            elif all(o.state == SupportState.UNSUPPORTED for o in observations):
                state = SupportState.UNSUPPORTED
            else:
                state = SupportState.UNKNOWN
            outcome = 'No eligible supported candidate'
        config = (f'as_of={as_of.isoformat()}; offer_max_age={policy.offer_max_age}; '
                  f'specification_max_age={policy.specification_max_age}')
        result.resolutions.append(FieldResolution(path, state,
            [o.observation_id for o in observations],
            '; '.join([outcome, config, *explanations]), selected, policy.name, policy.version))
    result.validate()
    return result


def resolution_references(contract: TrustContract) -> dict:
    """Lightweight report links; evidence payloads remain in the originating contract."""
    contract.validate()
    resolutions = {r.field_path: r for r in contract.resolutions}
    grouped = {}
    for observation in contract.observations:
        grouped.setdefault(observation.field_path, []).append(observation)
    report = {}
    for path, observations in sorted(grouped.items()):
        resolution = resolutions.get(path)
        single = observations[0] if len(observations) == 1 else None
        state = (resolution.state if resolution else observations[0].state
                 if len(observations) == 1 else SupportState.CONFLICTING)
        report[path] = {
            'state': state.value,
            'observation_ids': sorted(o.observation_id for o in observations),
            'evidence_ids': sorted({i for o in observations for i in o.evidence_ids}),
            'selected_observation_id': (resolution.selected_observation_id if resolution else
                                        single.observation_id if single and single.state == SupportState.OBSERVED else None),
            'policy': resolution.policy if resolution else None,
            'policy_version': resolution.policy_version if resolution else None,
            'reason': resolution.reason if resolution else 'No field policy has been applied',
        }
    return report
