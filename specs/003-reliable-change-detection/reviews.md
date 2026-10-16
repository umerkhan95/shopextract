# Independent review gates

## G1 initial — changes required
Reviewer: /root/workflow_review; 2026-10-16.
Blocking findings: price recheck lacked currency verification; proposed schema/migration
path scanned/backfilled unrelated legacy history despite bounded-read requirement.
Disposition: spec/test design/research/plan corrected before skeleton. Added explicit
recheck-currency and unrelated-history isolation regressions. Re-review pending.

## G1 corrected — PASS
Reviewer: /root/workflow_review; 2026-10-16. Both blockers resolved.
Proceed to skeleton/red tests only; G2/G3 remain pending.

- `spec.md` SHA-256: `4d5d53e6ad912e45045f21c851398112c122bc352a03a2c5c81a1279634ce3d9`
- `test-design.md` SHA-256: `c0256bcebe89737e3b06842d687707d8a3e6b26aa39ab33b56ae262f52aeb161`
- `tasks.md` SHA-256: `313cd1b851811584b59b9c36e21abdced25297cd5eff4bcedd139cfd0cd6f030`
- `research.md` SHA-256: `e03509e33d64e6013d5315599db18729d383ee5bd7b4ae705be235b3a6ebbd01`
- `plan.md` SHA-256: `2b1d597287a3ca6c3196546135bf52ac76c4a23809903c44312a8b85f2ac4a90`

## G2 initial — changes required
Reviewer: /root/workflow_review; 2026-10-16.
No business implementation; 76 intended missing-behavior failures, 39 regressions green.
Blocking findings: inconsistent currency recheck reasons; missing executable currency/
unsupported rechecks, same-supplier history isolation and missing IDs, unsupported
addition, synchronized publisher/recheck races; loose schema/evidence/order assertions;
missing nonfinite stored-graph corruption coverage. Verification file was being saved
during review and is now present. Author is correcting skeleton/tests before G2 rerun.

## G2 corrected — PASS
Reviewer: /root/workflow_review; 2026-10-16. All listed blockers resolved.
87 red cases fail only for missing declared behavior; 39 legacy tests green.
Next: component model and independent G3.

- `specs/003-reliable-change-detection/skeleton.md` SHA-256: `f39334f582b8bc19bf219dc40a7332cfc8cf30b614aabb8516a32e1033c4e90c`
- `specs/003-reliable-change-detection/verification.md` SHA-256: `cbed7476de87bb6beeec616102db267d52cf7670312f5f6143dd42b39d261393`
- `tests/test_reliable_changes.py` SHA-256: `e1130e6bdcc67302befe9d0f0d49126bfa390149eccc6fbd6fab0dcaa1ba8e3b`
- `src/shopextract/monitor/reliable.py` SHA-256: `59869ad09f0bd889db8462fa74bc3361ca6e66fea6785f66a564cfa06c7a2193`

## G3 — PASS
Reviewer: /root/workflow_review; 2026-10-16.
Reviewed components.md SHA-256: 49aac170f2f7a61b345044e16117d80d450880d5958a008c4d0096127f8c9df8
Reuse, dependency ownership, bounded loader/DDL separation and atomic ledger pass.
G1/G2 contracts unchanged. Implementation now started by /root/implement.

## Targeted health delta — G1/G2/G3 PASS
Reviewer: /root/workflow_review; 2026-10-16.
Healthy-complete now explicitly requires empty failure reasons; three red cases
cover previous/current/recheck. Implementation hold lifted after independent pass.
- `spec.md`: `8c468aa599b1f31264f20008b8f884d4e5d6bb3147fedeea4cc6726091fa3c9c`
- `test-design.md`: `7a1bf955e5aab2d4de5d3d174edd535b14a1eeeea7a2594eec9eb999e9032ed8`
- `tests/test_reliable_changes.py`: `8d745d4cf1dae7cd0f924f6b0c3ca056601bd04d4b6cdc91b5227240891854f6`

## Final initial — changes required
Reviewer: /root/workflow_review; 2026-10-16.
Two P2 findings: non-string domain raised AttributeError instead of ValueError;
stored ledger payload was fetched before its byte limit check. No other blockers.
Disposition: five supplemental cases designed first; red result 3 failed, 2 passed
with 90 deselected. Domain validation and pre-fetch SQLite byte-length check fixed
in one targeted repair batch; focused/full rechecks and independent re-review pending.
Membership presence unknown/value None with captured references accepted as designed.
Live smoke and inconclusive commercial-change status accepted as honest.

## Final corrected — PASS
Reviewer: /root/workflow_review; 2026-10-16. Both P2 fixes independently accepted;
no remaining code blockers. Supplemental regressions written before repairs.
Coordinator subsequently confirmed 726 full-suite tests, synthetic demo and saved
live-capture replay passed with final code; no additional network requests.

- `src/shopextract/monitor/reliable.py` SHA-256: `0e7294faf303ee4052de77ec385b0be8fb0cf7a4014df9885a7c1deab2d63139`
- `src/shopextract/monitor/evidence.py` SHA-256: `2418dd0124c455bf628ec057ef85d3daa2106646c3508f01bb852e9681be16b4`
- `src/shopextract/monitor/__init__.py` SHA-256: `d6468963316bec1d3c48ad182525bbaf816311d0c65bd950fb054ff8583a5f92`
- `tests/test_reliable_changes.py` SHA-256: `f3436fbdcbc2706d298aca4c4a2fed7851f2207dd87bf825d4bbd697fcda99b8`
- `docs/reliable-changes.md` SHA-256: `71ba0610334c2bf8e3e1a9f6946217314ea1e87ec4752a1fe05022f0779569c5`
- `examples/reliable_changes.py` SHA-256: `dadb8e2272876660cc9b1adfdb35b471c06cf9298015cd8a305ee39e8bfe550e`
- `artifacts/reliable-change-23/live_check.py` SHA-256: `c58cb36b5b468341a2d77cc299bb3973d2fc6db31b0981473d2f578dd74098c9`
- `artifacts/reliable-change-23/live/summary.json` SHA-256: `08f3b679f1705c2168012fab060aabf52d68ee68720b57de8751483c276603f3`
