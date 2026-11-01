# G2 red evidence
2026-11-01. Existing .venv, PYTHONPATH=src, one worker, BLAS/OMP threads2, tokenizer parallelism false.
Command: timeout120 pytest tests/test_rendered_money.py -q --tb=short (via bounded Python subprocess runner).
Actual16 cases:10failed,6passed in2.81s; red.log retained. The initial16-case run was the small smoke; no prior single-case run is claimed. No production repair yet.
Failures expose precision/grouping/zero, ambiguous symbols, malformed/negative acceptance, actual browser context conflict and metadata0. Controls explicitEUR/USD/GBP,nonfinite rejection,contextCAD and policy admission pass.
Full-driver/live gates pending; session counters unavailable.

G2 repair evidence: first2case smoke2intendedred in4.65s (04/repair-smoke.log). Combined bounded run `pytest tests/test_rendered_money.py tests/test_adapter_coverage.py -q --tb=short`, timeout120, same capped environment:44collected,33failed11passed in6.37s (04/repair-red.log). Rendered17=11red6control;adapter27=22red5control (invalidcapability API existingguard alreadypasses). No timeout/harness error. No implementation yet.

Functional evidence: first17run16pass1fixtureURL/excerptassertion failure3.34s (green-attempt.log), explicitly corrected existing crawlerhelper URL and established retained_data.source_excerpt slot afterdesign note. Bounded actual `pytest tests/test_rendered_money.py tests/test_html_coverage.py tests/test_capture_provenance.py -q --tb=short` =>108PASS15.39s (green.log),timeout120. Shareddecimal/registry parsing,caller metadata0 presence,contextconflict and precision/source support nowgreen. Full-driver/live/exporttimeout remain pending.

Functional repair: seven newly designed cases7red/17controls5.01s functional-red.log. Minimalfix removes£/₩code assumptions,whole-spacegroup token parsing (explicitlocale sharedconversion,otherwise rejection),existingstructuredcurrency cleared when competingauthorityconflicts whileoriginalcapture stays. Actual `pytest tests/test_rendered_money.py tests/test_html_coverage.py tests/test_capture_provenance.py tests/test_money_roundtrip.py -q --tb=short` timeout120 =>179PASS30.63s functional-green.log. No broader/full/live pass.

OG/case refinement:2new cases2red3.20s og-red.log;minimalcanonicalization+OGunresolvedprojection repair. Focused26rendered+52HTML=78PASS7.05s og-green.log,timeout120. Earlier179pass retained as priorrun,not inflated to new181allgreen. Independent re-review pending.
