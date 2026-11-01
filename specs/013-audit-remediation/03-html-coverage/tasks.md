# Dependency-ordered tasks

- [x] Behavior/test author /root/audit_research: spec/test-design before breakdown;
  scenario inventory covers stated FR/SC and boundary/interactions.
- [x] Bounded saved-source research; source dates/limits recorded.
- [ ] Independent /root/audit_plan_review G1: resolve blocking findings.
- [ ] AfterG1 skeleton + executable intended-red acceptance; save smoke/logs;G2.
- [ ] Component reuse/ownership/error contract; separate G3.
- [ ] Implement sequential bounded substeps: JSON-LD walker; image candidate reuse; scoped DOM enrichments as separate bounded steps. No adapter schema expansion.
- [ ] Fixture author/executor: designed mechanisms + bounded stress; independent
  coverage review; exact counts/seed/limits and first minimal failure saved.
- [ ] Focused/affected/full-driver checks; predeclared bounded live or justifiedN/A.
- [ ] Independent final diff/evidence review; update status/verification.

No implementation gate or completed verification is implied by this design.

Skeleton/executable-red author portion complete:skeleton.md,tests/test_html_coverage.py,
28 cases/logs/verification. Independent G2 (including shared-parser refinement)
pending; components/G3 and production remain gated.
