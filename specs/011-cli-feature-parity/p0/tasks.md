# P0 dependency-ordered tasks

Authored after spec/test design. Parent T01–T09 specialize to this slice.

- [x] D1 / author: design P0-FR01–07 / SC01–06, inspect native CLI, save one actual
  help smoke before complete bounded AST audit. Evidence: JSON schemas/contracts,
  baseline, manifest and evidence/audit-summary.json. This is design completion.
- [x] D2 / independent reviewer: G1 review actual artifacts/digests, check manifest
  classifications, schemas, compatibility and adverse cases. Author cannot approve.
- [x] D3 / skeleton author, after G1: define CLI loader/emitter/registration seams;
  create executable failing acceptance for SC01/03/04/05; record intended missing
  option/config behavior, never missing-import/dependency as acceptance red.
- [x] D4 / independent reviewer: G2 skeleton and actual red evidence.
- [x] D5 / component author: map reuse (Click/native serializers/config patterns),
  refine seams; independent reviewer G3 before business implementation (G3 pending;
  checked D5 denotes author deliverable only, not review passage).
- [x] D6 / implementer: bounded core config/I/O/error/help changes only, preserving
  nine legacy dispatches. Domain payload bindings cannot ship before affected
  schemas freeze; no P1–P5 placeholder commands pretending to support workflows.
- [x] D7 / fixture author + independent coverage reviewer: implement reviewed
  SC03–05 cases, check real loader/emitter execution and stress limits, then verifier
  runs bounded stress/regressions and independent final review. Live N/A to core
  parser/config; future actual network mechanisms remain phase requirements.

D2 passed design-only G1; D3 authored skeleton and tests with actual missing-feature
red evidence (28 failed, 4 legacy/boundary checks passed). D4 G2/D5 G3 PASS, D6 core implemented. D7 coverage PASS and actual bounded
mechanism/stress/fault/regression evidence saved; final independent review next.
Independent final P0 PASS recorded; F1 closed by actual4case reviewer probe.
D7 complete for reviewed P0 core scope. Domain payload phases stay open.
