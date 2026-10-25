"""Bounded opt-in report projection over retained snapshots and committed facts."""
import hashlib
import json
from .contracts import MaintenanceError


def encode_coverage_response(envelope) -> bytes:
    data = (json.dumps(envelope, ensure_ascii=False, allow_nan=False, separators=(',', ':')) + '\n').encode('utf-8')
    if len(data) > 1048576:
        raise MaintenanceError('resource_limit')
    return data


def page_coverage(goal, definitions, findings, offset, limit):
    groups = {}
    for finding in findings:
        groups.setdefault(finding['product_key'], []).append(finding)
    products = []
    for key, values in sorted(groups.items()):
        selected = goal['profiles'].get(key)
        definition = definitions.get(selected, {})
        rules = definition.get('fields', {})
        configured = sorted(rules)
        requested = sorted(goal['fields'])
        fields = {value['field']: value for value in values}
        classified = {name: [] for name in ('checked', 'unavailable', 'invalid', 'unsupported', 'not_recorded')}
        diagnostics = []
        for field, finding in sorted(fields.items()):
            states = finding.get('input_states', {'before': 'unknown', 'after': 'unknown'})
            reasons = finding.get('input_reasons', {'before': None, 'after': None})
            supplier = finding.get('supplier_support', {})
            baseline = finding.get('baseline_support', {})
            comparison = finding.get('comparison')
            if field not in rules:
                outcome = 'unsupported'
            elif (any(state in {'missing', 'null', 'empty'} for state in states.values())
                  or supplier.get('state') in {'unsupported', 'unknown', 'expired', 'conflicting'}
                  or baseline.get('state') in {'unsupported', 'unknown', 'expired', 'conflicting'}
                  or finding.get('before') is None or finding.get('after') is None):
                outcome = 'unavailable'
            elif (supplier.get('state') != 'observed' or not supplier.get('evidence_ids')
                  or goal.get('baseline_mode') == 'captured' and (baseline.get('state') != 'observed' or not baseline.get('evidence_ids'))
                  or comparison not in {'equal', 'different', 'unknown'}):
                outcome = 'not_recorded'
            elif comparison == 'unknown':
                outcome = 'invalid'
            else:
                outcome = 'checked'
            classified[outcome].append(field)
            blockers = sorted(set(finding.get('category_review_reasons', [])) |
                              ({finding['reason']} if finding.get('reason') else set()))
            diagnostics.append(dict(field=field, outcome=outcome,
                reason=next((reason for reason in reasons.values() if reason), None) or
                    (finding.get('reason') if outcome != 'checked' else None),
                input_states=states, input_reasons=reasons, blockers=blockers,
                baseline_basis=goal.get('baseline_mode', 'supplied')))
        fingerprint = hashlib.sha256(json.dumps(definition, ensure_ascii=False, sort_keys=True,
            separators=(',', ':'), allow_nan=False).encode()).hexdigest() if definition else None
        row = dict(product_key=key, selected_profile=selected, profile_definition_digest=fingerprint,
            configured_fields=configured, requested_fields=requested, page_fields=sorted(fields),
            unrequested_fields=sorted(set(configured) - set(requested)), field_diagnostics=diagnostics)
        row.update({name + '_fields': value for name, value in classified.items()})
        products.append(row)
    return dict(schema_version=1, scope='finding_page', offset=offset, limit=limit,
                finding_count=len(findings), products=products)
