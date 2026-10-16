# Proposed sequential CI partition — awaiting reviewer approval

No CI configuration edit or suffix execution performed.
The one local whole-suite run hit the existing 240-second outer deadline.
Strict quiet progress confirms 783/923 completed passes; 140 remain
unconfirmed. The next collected node is `tests/test_reliable_changes_stress.py::test_sm09_seeded_event_oracle[2909-7]`; quiet output cannot establish
whether it had begun. No inference from the displayed percentage is used.

Proposed change: keep the current Python 3.10/3.11/3.12 matrix and existing job;
replace its single pytest step with two sequential steps, each `timeout 240s`.
First run the existing suite with explicit `--ignore` for every collected
`test_maintenance_*.py` file (817 nodes). Second run those exact maintenance
files (106 nodes). Save exit status/log for both; fail the job on either
failure/timeout. No extra matrix jobs or parallel execution. Explicit file
lists avoid shell pattern filtering that accidentally includes helper drivers.

The diagnosis does not establish that each partition fits 240 seconds; execution
requires reviewer approval. Source identity is preserved. Desired remaining
nodes are saved verbatim in full-suite-unconfirmed-nodes.txt, collection order
in full-suite-ordered-nodes.txt and strict mapping in full-suite-progress-map.json.
No rerun of completed nodes proposed for the immediate local suffix diagnosis.

Packaging remains blocked because build and hatchling are absent; no install.
Actual live verification remains unexecuted behind the offline barrier.
