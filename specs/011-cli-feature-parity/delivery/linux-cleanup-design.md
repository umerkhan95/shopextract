# Linux cleanup repair — design before implementation

Observed external CI, heads18a0120/3579b5c: test_descendant_group_cleanup fails on Linux Python3.10/3.11/3.12; local Darwin passes. The same requested timeout returns failed because killpg(0) still sees a killed orphan zombie. Existing test additionally requires the owned descendant PID to disappear; do not weaken that assertion or treat zombies as a clean group.

Required behavior: a bounded driver owns, terminates AND reaps descendants in its launched process group. Timeouts remain timeout, failed cleanup remains failed, later groups never launch after either. Existing240/480 ceilings unchanged. Unrelated children/signals/subreaper state remain untouched after driver completion.

Proposed seam: on Linux, temporarily enable PR_SET_CHILD_SUBREAPER around run_plan (retain/restore PR_GET_CHILD_SUBREAPER state), allowing orphaned group descendants to reparent to the driver instead of depending on runner PID1. Use standard-library ctypes/libc only; fail before launching work if Linux cannot establish this contract. During cleanup, poll the Popen leader first, then repeatedly waitpid(-owned_pgid,WNOHANG) for owned adopted descendants, bounded by existing cleanup deadline. Never waitpid(-1) or reap another group's child. Other POSIX platforms retain system reparenting and may use the same owned-group reap helper.

Reusable components: existing _cleanup/deadlines/signals and Popen.poll. New helpers only child-subreaper state and group-scoped nonblocking reap. No test assertion change. Existing real descendant test is the decisive Linux regression; add independent POSIX real-zombie scoped-reaping case plus subreaper state restoration/platform case. Run focused driver tests locally, then fresh remote matrix/full configured gate. Linux live mechanism cannot execute on this Darwin host; remote Linux matrix remains mandatory. No models/network probes.

Diagnostics step also switches from read-all-then-slice to seek/read16000 to bound memory. CI dev environment must install optional parquet engine pyarrow so its designed test is exercised rather than skipped; no production dependency change.
