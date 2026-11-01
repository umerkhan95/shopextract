# Dependency-ordered tasks

- [x] Behavior/test author /root/audit_research: spec/test-design before breakdown;
  scenario inventory covers stated FR/SC and boundary/interactions.
- [x] Bounded saved-source research; source dates/limits recorded.
- [ ] Independent /root/audit_plan_review G1: resolve blocking findings.
- [ ] AfterG1 skeleton + executable intended-red acceptance; save smoke/logs;G2.
- [ ] Component reuse/ownership/error contract; separate G3.
- [ ] Implement sequential bounded substeps: lazy imports first (small independent repair); Woo bound/retry; checkpoints; process-isolated seeder/robots/stdout; stable ordering. Do not bundle all runtime work into one unchecked implementation task.
- [ ] Fixture author/executor: designed mechanisms + bounded stress; independent
  coverage review; exact counts/seed/limits and first minimal failure saved.
- [ ] Focused/affected/full-driver checks; predeclared bounded live or justifiedN/A.
- [ ] Independent final diff/evidence review; update status/verification.

No implementation gate or completed verification is implied by this design.

R1 stage: documentary skeleton + six real fresh-process tests authored; first red
smoke and full bounded red saved in verification.md. Independent G2 pending for
R1 only. R2–R5 interfaces described as future seams, each requires its own concrete
red/skeleton/component review; no runtime-wide implementation gate assumed.
