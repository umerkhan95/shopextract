# Repository working instructions

## Required feature workflow

Follow [the development workflow](docs/development-workflow.md) and
`.specify/memory/constitution.md` for feature work. Use `.specify/templates/`.
Design behavior and acceptance tests before task breakdown or implementation.
Use separate author and reviewer agents at the recorded gates. Run agents
sequentially by default; explicit authorization is required for parallel work.
User authorization to use agents for this workflow was given on 2026-10-16.
Review gates are engineering checks; routine passage does not require another
user permission request. Keep feature status and evidence in `specs/<feature>/`.

## Bounded usage and local model experiments

Start with a small concrete test and save results before broad research or sweeps.
Reuse saved sources and summaries; avoid large repeated cards, files and logs.
Batch independent reads and keep output compact. Run at most one local inference
process at a time, CPU-only, at most two intra-op threads and one inter-op thread;
cap BLAS, tokenizer and download workers. Use a sequential bounded driver and
saved status. Set explicit per-model timeouts. Make one diagnosed repair per
blocker, then record the limitation and continue independent work. No parallel
model launches or agents without explicit user authorization.

Check actual session token counters at meaningful experiment milestones when
available. If incremental uncached input plus output approaches 40,000 tokens,
stop expanding the experiment and report saved results and remaining work.
If counters are unavailable, record that limitation; do not infer a quota
percentage. Do not restart completed work after compaction.

## Git and pull requests

Use ordinary feature/fix branch names without `codex/`, AI, agent, assistant or
tool-brand prefixes unless explicitly requested. Preserve configured author
identity. Keep commits and PR titles/descriptions focused on the work; omit
branding, generated-by statements, badges and assistant co-author trailers.
Do not apply PR labels without explicit authorization. Before pushing or opening
a PR, check names, messages, author trailers, title/body and requested labels.
Do not rewrite unrelated history without authorization.
