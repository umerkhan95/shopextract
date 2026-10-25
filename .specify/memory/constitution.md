# ShopExtract project principles

1. Preserve existing Product/Variant constructors, canonical identity semantics,
   extraction APIs and default feed formats. Add explicit opt-in contracts.
2. Report supported facts only with inspectable captured source support. Missing
   and legacy/default values never become observed facts through scalar defaults.
3. Preserve competing observations and transformation history. Never invent source
   URLs, observation times, manufacturer authority or calibrated probabilities.
4. Design observable behavior and acceptance tests before task breakdown and code.
   Follow `docs/development-workflow.md`: research/review, skeleton/review,
   reusable components/review, implementation, offline checks, then bounded live
   checks. Record live not-applicable or blocked honestly; never substitute mocks
   for required live proof. When live behavior is unobservable, agents must design
   reproducible synthetic/adversarial cases first and run bounded mechanism and
   stress checks against real code, with independent review and separately
   labelled evidence. Include relevant edge cases and distinct tests for uncovered
   failure risks/interactions; duplicated assertions do not establish coverage.
   An inconclusive live result cannot replace those checks.
   Save results before expanding scope.
5. Apply the user's bounded-usage instructions: sequential work, no parallel agents
   or inference without authorization, bounded processes, and saved progress.
6. Keep core code and contracts MIT, self-hostable and free of paid service gates.

Integration: use `.specify/templates/` as local planning templates. No CLI install,
user configuration replacement, or generated agent commands are required. Feature
work lives in `specs/<number>-<feature>/`; linked tickets update the relevant spec
in place. Completed evidence/data-trust work remains in
`specs/002-evidence-data-trust/`. `AGENTS.md` defines persistent agent, usage and
Git instructions; independent review gates do not require routine user approval.
