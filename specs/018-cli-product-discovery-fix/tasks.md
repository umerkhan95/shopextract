# Dependency-ordered tasks

Behavior and expected outcomes are defined in `spec.md` and `test-design.md`.
Do not expand scope into a new crawler/driver. Use one author/reviewer at a
time; each review gate is independent and recorded in `reviews.md` by the
coordinator.

- [x] T01 — Author: complete bounded research in `research.md` and initial
  decisions in `plan.md` (FR01–FR04, SC01–SC05). Evidence: code/test/evidence
  references and limits recorded; no implementation or live requests.
- [x] T02 — Task-breaker self-check: map every FR/SC and distinct risk to an
  expected test and task. Coordinator assigns a separate reviewer for G1.
- [x] T03 — G1 independent review of spec, test design, tasks, research and
  plan. Resolve findings before skeleton work; record verdict in `reviews.md`.
- [x] T04 — Author: define native-discovery interface and integration seams in
  `skeleton.md`; add executable CLI acceptance test(s) and save an initial
  failing red result before business logic (FR01, FR03–FR04; SC01, SC04).
  Red must demonstrate the missing native index path / category-vs-product
  behavior without relying on broad browser crawling.
- [x] T05 — G2 independent skeleton review: signatures, cancellation/deadline
  path, compatibility, and ability of the red acceptance test to reach real
  parsing and normalization. Record verdict in `reviews.md`.
- [x] T06 — Author: document reused components, owners, boundaries and error
  lifecycle in `components.md`; refine the skeleton only if needed (FR01–FR03;
  SC01–SC04).
- [x] T07 — G3 independent component review. Record verdict in `reviews.md`;
  implementation is blocked until G3 passes and saved red evidence exists.
- [x] T08 — Author: implement native robots/sitemap/index traversal and wire
  the existing CLI/extract call chain to pass requested max and remaining
  deadline/cancellation (FR01–FR04; SC01–SC04). Add no merchant hardcoding or
  new operational crawler. Preserve safe legacy fallbacks.
- [x] T09 — Fixture author: create deterministic synthetic robots/index,
  category-leaf and 50 valid product-page fixtures plus adverse cases from
  `test-design.md`; expected outcomes are fixed before execution. Independent
  coverage reviewer checks distinct risks and fixture realism (SC01–SC03).
- [x] T10 — Run real-path mechanism checks and bounded stress sequentially
  against production parsing, normalization and CLI paths: first the 3-page
  smoke, then the predeclared fixed-seed cases and limits in `test-design.md`.
  Save seed/configuration, counts, commands and results in
  `verification.md`; stop on first failure, minimize it, make one diagnosed
  repair, and rerun affected checks only (FR01–FR04; SC01–SC04).
- [ ] T11 — Run focused affected regressions, then required full
  `python scripts/run_tests.py` in a supported configured environment. Save
  full evidence in `verification.md`. On macOS, distinguish native-Linux-only
  unsupported-host failures from feature correctness; do not mark the full gate
  passed without a passing full-driver result (FR01–FR04; SC01–SC04).
- [x] T12 — After affected offline success and classified required full-driver result (per reviewed host disposition), run the required live existing
  CLI sequence against `https://www.naheed.pk`: max 3 / browser / timeout 60,
  save result, then max 50 / browser / timeout 300. Inspect actual products,
  source URLs, retained capture, runtime, and partial/completeness metadata.
  Record live facts separately from synthetic results; no whole-catalog claim
  (FR01, FR04; SC05).
- [x] T13 — Final independent review of diff, task traceability, offline/full
  gate evidence, live evidence and remaining limitations. Update status, docs
  and issue mapping; report incomplete gates honestly (FR01–FR04; SC01–SC05).

T11 executed with saved full-driver evidence; acceptance remains incomplete because this macOS host fails16existing Linux-only supervisor cases. T12 performed under reviewed host disposition.
