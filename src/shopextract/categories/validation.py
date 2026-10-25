"""Category-only facet/evidence alignment; primitive evidence checks remain shared."""
from .._capture import _same_source
from .._evidence import Evidence, SupportState
from ._codec import wire, typed
from .contracts import CategoryError, CategoryObservation


def validate_observations(observations, limits=None):
    for observation in observations:
        typed(CategoryObservation, wire(observation))
        refs = {t.ref for t in observation.terms}
        edges = set(observation.parent_edges)
        for fact in observation.facts + tuple(f for t in observation.terms for f in t.facts):
            binding, outcome = fact.binding, fact.outcome
            if not fact.pointer.startswith('/') or outcome.source_paths != (fact.pointer,):
                raise CategoryError('Invalid category source binding')
            if binding.term is not None and binding.term not in refs:
                raise CategoryError('Category fact references unknown term')
            if binding.edge is not None and binding.edge not in edges:
                raise CategoryError('Category fact references unknown edge')
            if binding.facet in ('native_id','label','code_context','raw_path') and binding.term is None:
                raise CategoryError('Category term facet requires a term binding')
            if binding.facet in ('parent_id','child_id') and binding.edge is None:
                raise CategoryError('Category edge facet requires an edge binding')
            if not outcome.source_values or not _same_source(fact.raw_value, outcome.source_values[0]):
                raise CategoryError('Category conversion source changed')
            if fact.support == SupportState.OBSERVED:
                if not outcome.accepted or not fact.evidence:
                    raise CategoryError('Observed category requires accepted source evidence')
                for evidence in fact.evidence:
                    typed(Evidence, wire(evidence))
                    if not _same_source(evidence.resolve_pointer(), fact.raw_value):
                        raise CategoryError('Category evidence differs from source facet')
                if binding.facet == 'native_id' and (isinstance(fact.raw_value,bool) or
                        str(fact.raw_value) != outcome.normalized_value or binding.term.native_id != outcome.normalized_value):
                    raise CategoryError('Category native ID conversion mismatch')
                if binding.facet in ('parent_id', 'child_id'):
                    endpoint = binding.edge[0 if binding.facet == 'parent_id' else 1]
                    if (isinstance(fact.raw_value, bool) or endpoint.native_id is None or
                            str(fact.raw_value) != outcome.normalized_value or
                            endpoint.native_id != outcome.normalized_value):
                        raise CategoryError('Category edge endpoint conversion mismatch')
                if binding.facet == 'label' and fact.raw_value != outcome.normalized_value:
                    raise CategoryError('Category label conversion mismatch')
        if limits and (len(observation.terms) > limits.terms or len(observation.parent_edges)*2 > limits.relation_refs):
            raise CategoryError('Category relation exceeds configured bounds')
