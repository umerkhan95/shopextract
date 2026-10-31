# Bounded live/skill task breakdown

Author checked FR01–08/SC01–08 before breakdown. Each scenario has a distinct
fixture, expected result and offline/live disposition in test-design.md.

- [x] LV01 Author behavior/test design first; inspect existing CLI/mapping and
  actual Codex availability/source policy. Evidence: spec/test and parent probe.
- [x] LV02 Coordinator/reviewer G1 actual behavior/test/task/source plan; resolve
  blockers. No live PASS assumed from installed/login-status host.
- [x] LV03 Coordinator runtime skeleton+intended red tests; reviewer G2, reusable
  component model then reviewer G3. Author's concrete skill/report contract below
  is candidate only, not independent approval. Depends LV02.
- [x] LV04 Coordinator implements strict separate profile/CLI config, live
  harness/artifacts and fixture/control tests, reusing existing source capture,
  Google mapping, CLI and portable paths. Depends LV03 actual reds/gates.
- [x] LV05 Author supplies repository skill and exact site-reference manifest;
  reviewer checks activation, commands, evidence claims and adverse cases.
  Depends LV02/03; actual host invocation waits LV04/05 verification.
- [ ] LV06 Fixture author and independent coverage reviewer validate controlled
  mechanisms, then bounded focused/full driver and sequential live sample.
  Depends LV04/05. Record failed/blocked request actual evidence separately.
- [ ] LV07 Coordinator invokes actual Codex host at most2 sequential runs, saves
  sanitized JSONL/final responses and checks trace/artifact/report consistency.
  Positive mapping, blocked response and nonactivation are distinct outcomes.
  Depends passing offline mechanism checks and inspected skill draft.
- [x] LV08 Independent final reviewer checks actual source/CLI/host evidence and
  open limits; coordinator updates status/verification. Missing live access,
  missing mapped assertion or host evidence remains blocked, no overall PASS.

Owners: /root coordinator runtime/profile/source/host; /root/live_skill_author
behavior/test/tasks/interfaces/components/skill draft; independent reviewer is
separate. User explicitly requested agent collaboration. No publication/GitHub
changes/global auth changes or parallel Codex inference implied.

User steering amendment: current selected live sites are Pakistani Priceoye and Liberty Books; blocked sites are skipped once and no further allowlist question is pending. Native html is selected for both, no invented CSS recipe. Earlier international-site attempts remain historical evidence only. Independent review must inspect this actual revised scope and profile/manifest equality.

Actual current evidence: LV06 controlled23cases and full1800repository tests PASS; focused live cases are policy-skipped, not mapped. LV07 nativeCLI attempted once but backend403 prevented skill/command execution and final model answer; negative nativecase not run. Separate actual app-agent file-based skill exercise and unrelated response are recorded in evidence/host-verification.json, never substituted for native discovery proof. LV06/LV07 overall live requirements remain blocked; LV08 records an honest blocked final disposition after independent review.

Final independent audit recorded in reviews.md: no open blocking code findings;1800full-repository checks pass. LV08 is audit completion only, not all-live success. LV06/07 merchant/native-host required outcomes remain blocked/unmet. No further network/model attempts were made after known policy/backend denial.
