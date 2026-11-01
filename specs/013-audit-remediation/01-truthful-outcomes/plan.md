# Child implementation plan — G1 ready

## Constitution check

Preserve Product/Variant and ExtractionResult constructors, identity semantics,
default feed format and MIT/self-hostable runtime. Reuse tri-state coverage and
existing envelope schemas. Explain intentional corrected exits; supported source
facts never manufactured. Sequential bounded agents, no model calls.

## Architecture and decisions

Shared assessment derives failed/partial/complete from accepted product count,
catalog_complete/errors/reasons. ExtractionResult.outcome is additive read-only;
CLI and tool semantic projections reuse the rule or its precise shared inputs.
Native tool extraction is separate code: explicitly adapt its source/coverage
state, never infer pipeline parity. Discovery has different empty semantics and
no coverage proof; retain URLs with partial diagnostic. HTTP gate precedes parsing
for both browser modes. Shared generic product admission covers extractor and
normalization/tool seam; it preserves explicit free Product records. Woo adapter
records all404 transitions as incomplete, retaining prior records.

Detailed interfaces and component ownership are deliberately G2/G3 work, not
implemented here. No general runtime/budget refactor; tests use controlled external
transport/crawler boundaries while exercising real parser/normalizer/adapters.

## Required gates

G1 pending independent review of this design/tests/tasks/research/plan. G2 requires
skeleton and saved executable red acceptance failures. G3 requires reusable
components and revised skeleton review. None of these reviews imply user approval
requests; user has authorized implementation. Final review requires actual evidence.

## Verification and handoff

Follow test-design.md fixed budgets:41 synthetic cases maximum,seed0,one worker,
120s mechanism ceiling; full driver480s total/240s family; live max12 requests,
four sequential runs/120s aggregate after offline green. Save smoke before expansion.
Synthetic mechanism, actual browser/store observation and blocked live states are
separate. No prior parent diagnostic is counted as repaired acceptance evidence.
Next owner: independent reviewer at G1. Implementation and later child slices
remain pending. Child status.md is resume point; umbrella historical planning PASS
remains historical and does not certify this design or future code.
