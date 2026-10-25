# P0 resume point — complete reviewed core slice

2026-10-25. Author /root/cli_p0_author; independent reviewer /root/cli_p0_review.
G1/G2/G3/coverage/final PASS recorded in reviews.md; final F1 ordering finding
closed by independent4case real-CLI probe, no native execution. D1–D7 complete
for the P0 core scope. Exact reviewed digests remain in reviews.md.

Implemented root config/output-format/diagnostics controls, strict single-read
configuration, deterministic help/version/error routing, machine envelopes/error
codes/quiet diagnostics. Actual detect machine branch supported; all nine legacy
command declarations/default/native dispatch preserved. Other machine domain
commands explicitly return deferred E_OPERATION until their payload phase binds.
This completion does not claim P1–P5 domain parity.

Evidence: initial32green smoke, expanded48green, focused final52green after F1;
181 affected regressions;12 bounded synthetic cases; duplicate-key fault proof
baseline2/mutant0(detected)/restored2; independent F1probe4pass. Old evidence is
preserved and reused where applicable; actual commands/timings in verification.md.
No installs/network/models/push; counters unavailable. Live N/A for core policy,
while later extraction/monitor/tools phase live obligations persist.

Reuse handoff: cli.main remains shared CoreGroup. _cli_core.settings() gives
immutable per-invocation settings; emit_success(data) emits one validated-shape
success envelope, emit_diagnostic() gates nonessential stderr, CliFailure carries
sanitized code/message for centralized exit/error emission. Native payloads must
be JSON-safe using existing reviewed codecs, never default=str. Root config is
closed to three CLI keys; do not put native/LLM/trust settings there.

CoreCommand.invoke validates availability after Click argument validation and
before callback/native execution. Extend _MACHINE_COMMANDS canonical command-path
tuples only when implementing the affected reviewed payload binding; current set
is {("detect",)}. New groups/nested grammar require their phase scanner review;
P0 scanner deliberately freezes the existing flat-nine grammar. Help parameters
are actual Click options expose_value=False, available to introspection.
Next: parent coordinator assigns P1 design/implementation slice; P0 author stops.
