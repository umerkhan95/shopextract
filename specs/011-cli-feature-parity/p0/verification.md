# P0 actual evidence

- Passed: `.venv/bin/python -m shopextract.cli --help` with PYTHONPATH=src,
  BLAS/OMP/MKL workers 1 and tokenizer parallelism disabled. Timeout 20s; exit 0,
  727 stdout bytes / 247 stderr bytes, 1.508s. Saved before inventory expansion
  in evidence/smoke.json, root-help.txt and root-help.stderr.txt. Legacy availability
  smoke only; no red acceptance or help activation/correctness claim.
- Executed: bounded AST-only inventory; 92 module records, nine registered root
  commands, 70 named reserved workflow targets. Audit metadata and exact source
  hashes saved; no imports/network/models. Reproduce inventory with
  `python specs/011-cli-feature-parity/p0/evidence/audit-design.py`.
- Passed: all JSON artifacts decode with stdlib; installed jsonschema
  Draft202012Validator.check_schema accepts both config/response schemas (0.24s
  combined local syntax check). Saved evidence/design-checks.json. No runtime
  mechanism is exercised by this structural check.
- Runtime acceptance red/green, production mechanism/stress, G2/G3/final review:
  not run. Design tooling/schema syntax checks are not runtime coverage.
- Live: not applicable to docs-only contract freeze; future phase live acceptance
  remains pending. Actual session token counters unavailable.

## Focused design repair evidence

Ran `.venv/bin/python specs/011-cli-feature-parity/p0/evidence/author-repair-checks.py`
locally, exit 0 in <1s. 22 schema examples passed (10 valid success/error examples,
9 invalid retryability inverses, 3 original reviewer negatives); every one of 69
local workflow labels resolves; 15 named lifecycle/extension/classification checks
passed. Inventory regenerated once per focused generator edit; current module and
source digests saved. B01–B15 are designed bootstrap cases, zero runtime executions.
Independent G1 re-review pending. No runtime mechanism/stress pass implied.

## Final narrow classification correction

Coordinator corrected the exact `tools/contracts.py::validate` collision to a
composed P5 tools schema-validation helper, added a named regression assertion,
and aligned parent coverage's example with root-option placement. Ran the two
saved audit/design-check scripts sequentially, exit 0: 92 modules, nine legacy
commands, 68 linked workflows, 16 named classification checks, 22 schema examples.
The check script now saves `evidence/author-repair-checks.json`; the older file
at the P0 root remains historical pre-correction evidence. Runtime bootstrap
cases executed: zero. Independent final narrow recheck pending.

## Independent gate disposition

Final independent G1 PASS (design only) recorded by /root/cli_p0_review in
reviews.md, with evidence/reviewer-final-check.json. R1–R3 closed. Independent
108 schema combinations had zero mismatches. Administrative status/plan/task
markers were updated after the recorded final digests; behavior/schema/manifest
contracts were not changed after final review. Runtime acceptance and later gates
remain pending.

## D3 actual acceptance red before production implementation

Command: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_cli_core.py -q
--tb=line --disable-warnings`, run through a sequential subprocess driver with
30s timeout, BLAS/OMP/MKL workers 1 and tokenizer parallelism false. Exit 1,
3.172s driver / 0.64s pytest: **28 failed, 4 passed**. Log and metadata:
evidence/acceptance-red-g2.log and evidence/acceptance-red-g2.json.

Failures are intended absent root --output-format/--config, config/env policy and
bootstrap precedence/unknown-command behavior. Assertions fail on wrong exit or
missing envelope/option recognition; no import, dependency or collection failures.
Legacy registration/defaults, legacy detect JSON and option-looking URL operand
checks pass; passing eager-help case is existing behavior, not implementation.
Native detect boundary uses deterministic async fixture/failure only; Click main,
parsing, future config/emitter flow remain real. No actual network/models/DB work.
No production code edited. G2/G3 pending; these are genuine red acceptance results,
not production mechanism/stress verification. Signature declarations in skeleton.md
are documents only, so absent private production modules are never imported by tests.

## D5 component stage

Reused G2-reviewed 28-red/4-pass evidence without rerun. components.md records
reuse/ownership/error/lifecycle seams; test-design.md adds G01–G10 cases for
single-read success/failure, quiet/streams, remaining B cases and invocation
isolation before tests are added. No tests, production edits or runtime checks
added at this stage. Independent G3 pending.

## Actual P0 implementation and controlled verification

G3 PASS and independent G01–G10/C1 coverage PASS are in reviews.md. Author
implemented the private core plus detect machine binding; native legacy defaults
and declarations/dispatches remain unchanged for all nine commands. Other commands
return explicit machine E_OPERATION until their domain payload phase binds them;
no expanded domain parity is claimed. Existing discover/extract diagnostics reuse
the quiet-aware helper. User documentation: docs/cli.md.

Saved checks, all sequential, BLAS/OMP/MKL1 and tokenizer parallelism false:

- core-first-smoke: original 32 checks pass, pytest0.24s, saved before expansion.
- core-expanded: all48 designed public/core checks pass, pytest0.45s.
- core-stress: 12 fixed synthetic cases, seed11025, <=65,537bytes, 1worker,
  <=30s/case/120s total; all12 pass through real CLI/config/bootstrap/emitter.
  Native detect alone is controlled. Actual driver0.023s.
- core-fault-proof: actual duplicate rejection hook temporarily replaced with
  dict in scoped process patch. Baseline E_CONFIG/2, mutant0 triggered critical
  expected-exit assertion, restored E_CONFIG/2. Three real CLI invocations; patch
  restored before exit, no source mutation.
- core-regressions: 181 tests pass (core + detect/discover/export/analyze/validate/
  monitor), pytest0.84s, one30s process cap per saved command.
- core-compatibility: all nine AST command declarations and native dispatch calls
  identical to frozen baseline; new private core symbols classified as shared
  P0 helpers/data; baseline artifacts preserved. git diff --check passes.

Exact commands/timings/logs are in evidence/core-*.json/log and reproducible
core-mechanism-driver.py. No installs/network/models or live capture. Core live
not applicable: it performs parser/config/I/O policy, with native external boundary
controlled; later domain live obligations persist. Actual token counters unavailable.
Independent final review pending; green tests alone do not approve final closure.

## Independent final review F1 focused repair

Reviewer found the deferred-machine guard ran before actual Click domain argument
validation. Designed missing-URL/bad-integer/missing-file plus valid-deferred cases
first, then ran focused genuine red: **3 failed,1 passed** in0.21s (core-f1-red).
Moved the guard to shared CoreCommand.invoke after Click context parsing; no
domain payload implemented. All **52 core tests passed in0.33s**, one30s capped
process (core-f1-green). Previous181 affected regressions/12 stress/fault evidence
remain valid and are preserved; focused fix changes ordering only.

core-f1-compatibility.json records the new private helper and current source
digests; cli.py/legacy declarations unchanged in repair; diff check passed.
Independent final re-review pending; original blocking finding remains historical.

## Final independent disposition

Independent reviewer `/root/cli_p0_review` recorded **FINAL P0 PASS**, F1 CLOSED,
with13artifact digests in reviews.md. Reviewer executed4real public-CLI cases
with native failure sentinels; all expected usage/deferred outcomes passed, no
native calls (evidence/reviewer-f1-final.json). P0 D7 administratively complete
after that verdict; P1–P5 payload/domain work remains open and separately gated.
