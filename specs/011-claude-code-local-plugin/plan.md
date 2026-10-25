# Implementation plan

## Constitution check
Reuse existing read-only tool API with unchanged constructors/identity/source/evidence/defaults. Package is MIT, local/self-hosted, no hosted or paid feature gate. Evidence must separate deterministic mechanisms from actual Claude behavior. No new runtime functionality is required.

## Architecture and decisions
See research.md for official refreshed facts and alternatives. Native package at integrations/claude-code uses default manifest/skill/MCP roots, one instructions-only skill and direct trusted Python argv. Operator supplies executable/config outside distributable files. A narrow test-side inventory check handles project policy beyond native validation; it is not an installer or claimed host protection. No custom runtime wrapper. Detailed signatures and component ownership belong to later skeleton.md/components.md after G1/G2.

## Required gates
G1, G2, G3 and final engineering/offline reviews passed independently; see reviews.md. Native/live checks remain blocked. Record reviewer/digest/findings/disposition in reviews.md; never assume passage. Implementation depends on G3 and saved intended missing-behavior red evidence.

## Verification and handoff
Predesigned SC01..08 cover real parser, literal argv/config, SDK/runtime fixtures, canonical/evidence fidelity, privilege denial, bounded pending/partial states, ephemeral restart and actual host activation. Save actual red/green evidence, commands and sanitized environment in verification.md. Native CLI access alone is not signed-in model proof. Only #82 local slice is completed by eventual delivery; #73/#74 broader routes remain planned. Preserve primary checkout/planning branch; no config overwrite, public publishing, labels or branded Git metadata.

## Implementation handoff (2026-10-24)

G1/G2/G3 passed independently (reviews.md); direct native package and test-only fixtures/harness are implemented. No new production Python abstraction or core mutation. A standalone MIT LICENSE accompanies directory copies. Available offline affected regressions and supplemental identity/evidence checks pass; see verification.md for exact commands, historical failures/repairs and limits. Native parser was attempted twice within one diagnosed repair and remains blocked by installed CLI flags/auth; normal host activation is also blocked. No native compatibility success is inferred. Final independent engineering/offline review passed; native/live compatibility remains blocked.

## Revision 1 plan (2026-10-25): user findings on PR #89

Behavior/test design revision precedes revised tasks. FR08..14/SC09..15 supersede conflicting old accounting/report assumptions; the prior final review is historical. Fresh independent G1/G2/G3/final gates are required for the revised slice. Historical design-entry stage: revised G1 was pending, before code edits.

Decisions: six domain MCP calls exclude schema-only ToolSearch but all activity shares120s; explicit tool/schema preflight; deterministic returned product-path choice with exact no-product stop; finite-delay unsynchronized pending is valid (no new host wait capability). Source installation requires actual taxonomy bootstrap before source MCP install. Native report parser uses nested manifest.errors and separates ancillary listing warnings. Preserve user-reported2.1.310 success versus locally blocked1.0.35 observations. Reported inherited skip flag is diagnosis, not an automatic configuration override.

Architecture remains instructions-only production plugin around existing CLI/runtime/MCP. Test-only recipe/selection/trace logic and external source fixture own their boundaries. Opt-in real native subprocess harness uses per-session copied plugin with explicitly recorded fixture MCP override, stream-json and independent time/call limits; default suite cannot initiate inference. It must record blocked normal access/unsupported limits honestly. No Product/dict/entity/USD library fixes, new service, public marketplace or other ecosystem tickets.

Verification is revised intended reds after G1, skeleton/G2, component/G3, focused green smoke, deterministic adverse cases/affected regressions, then actual native run only if existing normal access and supported bounded options are available. No scope expansion/model sweeps. See test-design.md revision for exact fixture sizes/counts, selected case outcomes and provenance. Source and native-report/schema facts are in research.md; user observations are attributed separately from local evidence. Coordinator handles eventual PR89 evidence/update after final review, not this design-only assignment.

Revision G2 correction: concrete native run bounds are max-turns10, wall120s, cleanup2s total (TERM1s/KILL-reap1s) on an owned process group. Runnable preflight/host-case/supervisor acceptance, including zero ineligible launches and actual controlled-process termination, is mandatory; reducer-only tests do not satisfy host harness delivery. Actual native execution still requires opt-in, normal access and known support for the exact bounded flags before inference.

Historical component handoff: G2 had passed; revised components/refined skeleton awaited G3. No production abstraction is added: existing CLI/runtime/schemas/source/MCP are reused, fixture controls external payload/timing only, and one test-only smoke module owns literal bounded process+trace classification. Record copied MCP override/hash and every evidence tier separately. Operator setup uses real bootstrap/Hatch seam, with no claim docs inspection proves fresh installation. No implementation before G3.

Current revision delivery state2026-10-25: approved G1/G2/G3 and SC15b changes implemented; plugin version0.1.1. Source/core unchanged; final affected run191passed/1native skip69.03s and final independent review passed; later focused corrections have their own passing re-review. Actual local eligibility blocked before inference/0model calls. Current evidence/status supersede earlier pending-stage planning notes; original gate prose remains historical. No author commit/push.

Final-review correction state: focused affected G1/G2/G3 passed; FR15..18/SC16..19 implemented against saved20red/8green reproduction. Required expected-case binding separates complete success, pending incomplete, unrelated zero-activation and executed grant denial. Clean supervision gates every probe before output interpretation; original encoded separators reject before decoding. Four genuine subprocess boundary checks are retained. Focused repairs28passed4.52s; latest bounded affected evidence and current final-review handoff are in verification.md/status.md. Earlier pending gate notes are historical. No author commit/push or native inference.
