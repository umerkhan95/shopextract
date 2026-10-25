# Final integration handoff

P0–P3 final evidence is complete and reusable; do not restart these phases.
P4 owns categories and its affected cross-phase integrations. P5 follows only
after P4 author/reviewer stop, and owns operations plus the final integrated audit.

- Use installed `shopextract` and supported `python -m shopextract.cli` entrypoints.
  `python -m shopextract` currently has no `__main__`; examples must be accurate.
- Existing hatchling/pip can build a genuine wheel via
  `python -m pip wheel --no-deps --no-build-isolation`; build frontend is absent.
  Install the resulting wheel into a disposable system-site-packages venv,
  outside the checkout with PYTHONPATH cleared. Verify import origins.
- CI requires the main suite and seven maintenance files in separate sequential
  240-second groups, plus optional MCP import compatibility. MCP and pyarrow are
  installed; exercise real SDK stdio and native durable maintenance processes.
- Package schemas and capability discovery. Audit actual leaves, native public
  APIs, complete help/examples, machine output, protocol-only server stdout,
  config precedence and optional runtime activation. No actual registered leaf
  may retain a deferred-phase machine guard.
- Reconcile parent task checkboxes/coverage/status/verification/reviews and all
  six phase tickets plus epic only against actual final evidence. Distinguish
  local completion from publication; no push/PR has been performed.
- Retain the initial dirty-source baseline and unrelated work. No broad staging,
  author identity changes, branding, labels or history rewrite.
- Reuse reviewed phase stress evidence where applicable and explicitly map the
  final 24-case parent requirements. Run only remaining uncovered cases.
- Shared live budget includes category nodes as retained items: consult current
  `live-budget.json`, preserve actual receipts and distinguish controlled tests
  from public live observations. No model/server download or paid inference.
- Complete an independent final whole-feature review with exact evidence and
  honest remaining limitations. Actual session token counters are unavailable.
