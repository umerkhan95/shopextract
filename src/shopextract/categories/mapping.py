"""One exact deterministic category mapper, independent of native adapters."""
from .._evidence import SupportState
from .config import validate_options
from .contracts import CategoryObservation, CategoryOptions, MappingDecision


def _supported(term, facet, expected):
    return tuple(f for f in term.facts if f.binding.facet == facet and f.binding.term == term.ref
                 and f.support == SupportState.OBSERVED and f.outcome.accepted
                 and f.outcome.normalized_value == expected and f.evidence)


def map_categories(observations: tuple[CategoryObservation, ...], *,
                   options: CategoryOptions) -> tuple[MappingDecision, ...]:
    validate_options(options)
    from .validation import validate_observations
    validate_observations(observations, options.limits)
    decisions = []
    for observation in observations:
        if observation.relation in ('index','parent_edges'):
            continue
        groups = {}
        for term in observation.terms:
            key = (term.ref, None if term.ref.native_id is not None else term.label)
            groups.setdefault(key, []).append(term)
        if not groups:
            decisions.append(MappingDecision(observation.observation_id, None, 'unavailable', (),
                options.registry.namespace, options.registry.version, (), observation.completeness != 'complete', reason=observation.reason or observation.source_state))
        for terms in groups.values():
            matches, pointers, unsupported = [], set(), False
            for rule in options.rules:
                selector = rule.selector
                if selector.scope is not None and selector.scope != observation.scope:
                    continue
                for term in terms:
                    if selector.namespace != term.ref.namespace or selector.taxonomy_version != term.ref.taxonomy_version:
                        continue
                    if term.ref.taxonomy_version is None and not selector.allow_unknown_version:
                        continue
                    if selector.native_id is not None:
                        facet, expected, candidate = 'native_id', selector.native_id, term.ref.native_id
                    elif selector.raw_label is not None:
                        facet, expected, candidate = 'label', selector.raw_label, term.label
                    else:
                        facet, expected = 'raw_path', selector.raw_path
                        candidate = next((f.raw_value for f in term.facts if f.binding.facet == facet and f.raw_value == expected), None)
                    if candidate != expected:
                        continue
                    facts = _supported(term, facet, expected)
                    if observation.taxonomy_kind == 'structured_code' and not any(
                        f.binding.facet == 'code_context' and f.binding.term == term.ref and
                        f.support == SupportState.OBSERVED and f.outcome.accepted for f in term.facts):
                        facts = ()
                    if facts:
                        matches.append(rule)
                        pointers.update(f.pointer for f in facts)
                    else:
                        unsupported = True
            matches = {r.rule_id: r for r in matches}
            targets = {tuple(sorted(r.target_ids)) for r in matches.values()}
            candidates = tuple(sorted({target for group in targets for target in group}))
            usable = any(f.support == SupportState.OBSERVED and f.outcome.accepted for t in terms for f in t.facts)
            status = ('mapped' if len(targets) == 1 else 'ambiguous') if targets else ('unavailable' if unsupported or not usable else 'unmapped')
            decisions.append(MappingDecision(observation.observation_id, terms[0].ref, status, candidates,
                options.registry.namespace, options.registry.version,
                tuple(sorted((r.rule_id, r.version) for r in matches.values())),
                observation.completeness != 'complete', tuple(sorted(pointers))))
    return tuple(sorted(decisions, key=lambda d: (d.observation_id, repr(d.term), d.status, d.target_ids)))
