# Implementation plan — G1 ready

Constitution: constructors/identity preserved,source support and explicit absence,
MIT/self-hostable,one sequential delegate,no inference. Designs in spec.md precede
architecture. Reuse existing components identified in research; skeleton/components
remain next gated stages.

Delivery: lazy imports first (small independent repair); Woo bound/retry; checkpoints; process-isolated seeder/robots/stdout; stable ordering. Do not bundle all runtime work into one unchecked implementation task.
Dependencies: child01 semantics; child02 money/roundtrip before downstream; HTML
and adapter coverage may each follow their own gates; runtime lazy imports can
precede later native verification. Child07 uses child05 rules. No parallel work.

Checks: test-design.md named SC contracts,bounded fixtures and live plan; required
full-driver gate remains unchanged. Each substantial implementation substep gets
red tests plus independent gate review,not a whole unreviewed epic.

G1 pending;G2/G3/implementation/green/stress/live/final pending. Existing full-suite
timeout and child01 pending live remain visible,not waived by design acceptance.
