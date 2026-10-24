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
