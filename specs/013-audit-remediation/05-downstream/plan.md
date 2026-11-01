# Implementation plan — G1 ready

Constitution: constructors/identity preserved,source support and explicit absence,
MIT/self-hostable,one sequential delegate,no inference. Designs in spec.md precede
architecture. Reuse existing components identified in research; skeleton/components
remain next gated stages.

Delivery: canonical projection+destination rules first; quality report labels; match/duplicates distinct step; statistics distinct step. No opaque single quality score advertised as readiness.
Dependencies: child01 semantics; child02 money/roundtrip before downstream; HTML
and adapter coverage may each follow their own gates; runtime lazy imports can
precede later native verification. Child07 uses child05 rules. No parallel work.

Checks: test-design.md named SC contracts,bounded fixtures and live plan; required
full-driver gate remains unchanged. Each substantial implementation substep gets
red tests plus independent gate review,not a whole unreviewed epic.

G1 pending;G2/G3/implementation/green/stress/live/final pending. Existing full-suite
timeout and child01 pending live remain visible,not waived by design acceptance.

G1 blocking-design repair authored; revised spec/test-design authoritative.
Independent re-review pending; no implementation or approval inferred.
