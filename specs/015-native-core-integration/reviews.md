# Independent integration reviews

Reviewer: `/root/native_integration_reviewer`; date: 2026-10-31. Author: `/root/fallback_integration_design`; corrections: parent `/root`. No production implementation was reviewed or approved by these design gates.

## G1: behavior, acceptance design, tasks and research — PASS

Reviewed behavior/tests/research/tasks first, then checked current core/category/CLI/browser seams. Requirements distinguish legacy native category behavior, explicit production mode, shared execution controls, and versioned verifier resource contracts. Cases cover policy denial before child launch, successful API short circuit, HTTP-to-browser and CSS mechanisms through real orchestration, unknown attempt/network counts, missing evidence, lifecycle cleanup, and shared budgets. Source-specific HTTP-only feed/tree/tools contracts are intentional exceptions; enabling those blindly is outside this repair. Real merchant/browser observation remains separately blocked if access/dependencies are absent.

Resolved finding R1: original FP-FR7 globally prohibited pass when a browser was absent, contradicting successful API short circuit. Parent revised it to required browser-path failure, while sufficient API evidence can pass without a browser. No unresolved design blocker.

Reviewed identities:
- `spec.md`: `41989166c9b71bd27baaf45998a7a8805ed2182b584e1d6bec8a42e324609ac9`
- `test-design.md`: `b136f9b84ca948e386f30ba8dca740daf5f28f4a3c8dc298666a2c7bdd871b93`
- `research.md`: `44e19c458b8f234ad86c8a45074a4b8d8db26044ea06c924a4b98f5c31a9b563`
- `tasks.md`: `1ed16835644520252bd901020445b1030e72f24550b3cabe0ead565b702a7c69`

## G2: documented skeleton — PASS

Reviewed signatures and dependency direction after G1. Native fallback selection remains in `_extract.extract`; source-mode adapter preserves raw rows and existing category binder. Version2 worker invokes full extract rather than extract_one; bounded child protocol, unknown network counts, exact invocation counters and cleanup-before-next-consumer are explicit. Existing version1 limits remain unchanged. Execution switches must enter one context around the complete operation, not per URL/event.

Resolved finding R2: original worker interface omitted opt-in category capture. Parent amended the worker call to `extract(..., max_urls=1, include_categories=True)`, so source categories can survive the same production path. No unresolved skeleton blocker. Executable intended-red evidence remains a prerequisite to production code; this gate does not assert tests already exist or pass.

Reviewed identity:
- `skeleton.md`: `f1fc19ae03046b59ef54b4b969cd91397a38bf075d63271d188a544f06c15931`

## G3: reusable components — PASS

Reviewed components after G2. Existing extraction, policy, category mapping/binding and codecs retain single ownership. New process lifecycle adapter has two concrete consumers (worker and verifier CLI stages) and no taxonomy/fallback logic. Shared browser configuration owns proxy parsing across all browser tiers; feature-specific proxy workarounds and direct routing on decode errors are prohibited. Different configured HTTP/HTTPS proxy or NO_PROXY behavior is not misrepresented as HTTPX parity. Credentials must stay out of diagnostics. No unresolved component blocker.

Reviewed identities:
- `components.md`: `12b241620eeaba108e02b91b6f033df66c2a4c43d805e1c55f2aae90fa59e6a0`
- `plan.md`: `6d99d5b16903e052e8803aaff4f7bdb6bd40d2193840426294ed6159aa94917e`

## Implementation and final review — PENDING

Actual code, intended-red/green evidence, configured full repository tests, real-path controlled mechanisms and bounded live reports must be reviewed before completion. A fake final extraction report cannot substitute for the designed fallback tests. Exact network request and browser attempt counters must remain unknown where not observed. No live/full5595/native-host gate is waived by these design approvals.

## Narrow NC-FR6 / NC-SC9 amendment — G1/G2/G3 PASS

Reviewer `/root/native_integration_reviewer`, 2026-10-31. Author `/root/fallback_integration_design` supplied the requirement and exact expected fixture before implementation. Reviewed the added spec/test-design paragraphs and current API-only forwarding defect in `_extract.py`. The existing boolean option must reach each existing `_normalize_batch` call; the existing Shopify normalizer, capture checks and checksum rules remain sole authorities. Expected fallback results: valid29877030712 restores0029877030712 only when explicitly enabled; false/default and invalid29877030713 remainNone. Controlled HTTP/seeder/browser boundaries leave real fallback and normalization code under test. G1 behavior/tests PASS; G2 interface PASS (no new signature or state); G3 components PASS (argument propagation only, no duplicate normalizer). Save intended-red before repair and green/regressions afterward. This approves design, not unexecuted implementation.

- `spec.md`: `d8255f915bfc957b06ed45efb691b235d6ee171e769bc25c0f0eb7b023b01b03`
- `test-design.md`: `87176c4addbc561f05d51d96196fd87dfe073aeda251697223da361630eb6947`

## Initial implementation review — CHANGES REQUIRED / final evidence pending

Reviewer `/root/native_integration_reviewer`, 2026-10-31. Inspected actual SliceA core/category/browser changes, eight CLI execution-policy adapters, worker, process supervisor and production verifier. Core fallback selection remains native; controlled external HTTP/seeder/browser fixtures exercise real parsers/binding. Existing CLI defaults/legacy routing and one shared context per multi-source operation are preserved in inspected code. Lifecycle supervision declares Linux/main-thread/sequential/owned-group limits rather than claiming arbitrary escaped descendants.

- R3, medium: production verifier catches downstream mapping/export exceptions and overwrites successful extraction with extraction.status failed. Preserve native extraction success, identify the actual failing stage, and keep overall failure. Parent notified; awaiting repair/regression.
- R4, low: worker result validator compares browser/LLM objects by Python equality, admitting numeric1/0 for booleans. Enforce exact field types at the bounded protocol boundary; parent notified.
- R5, verification: designed cancellation/signal restoration, stderr overflow and two-site shared-budget cases are not present in the initial9 production tests inspected. Parent is adding adversarial coverage. Existing proxy tests exercise all tiers with HTTPS proxy but precedence/NO_PROXY non-parity should receive a small distinct configuration case before claiming that behavior verified.
- R6, design question: production category library validates shop_url/options scope but not input URL against scope; CLI and verifier guard this. Asked core author/parent to decide narrow production-only URL origin/base-path validation while preserving native hosted-feed compatibility. No author self-approved expansion.

Configured full driver, final amended code identities and actual live observations have not yet been reviewed. Design passes above are not final feature verification.

## FP-FR8 / FP-SC13 platform detection amendment — G1/G2/G3 PASS

Reviewer `/root/native_integration_reviewer`, 2026-10-31. Reviewed parent-authored saved requirement, scenario and skeleton plus explicit returned-platform invariant. G1 PASS: v2 auto delegates actual native detection instead of guessing platform from domain; v1 compatibility remains, scoped mappings require explicit platform and denied sites never assert a detection. Predesigned controlled HTTP detection→Shopify API fixture must retain actual platform and capture. Unknown/mismatched explicit platform must reject before mapping. G2 PASS: only auto becomes None at extract boundary, worker returns Platform value, verifier passes returned platform through a site copy without mutating input profile. G3 PASS: existing detector/extractor remain owners, generic preflight is target/rule validation only, not a copied classifier. Intended-red tests precede implementation. No native browser/live observation is inferred from this amendment.

- `spec.md`: `ee31888359ed385cb94a5c42d01aab741fed3f40f121b7d3ff9cb5d8a022fc86`
- `test-design.md`: `87176c4addbc561f05d51d96196fd87dfe073aeda251697223da361630eb6947`
- `skeleton.md`: `a9266ab9402c36e80ddef6bcf39a5ebb4e77ac36194bcb60608e498f9d2c5840`

## Compatibility-test input amendment and watch grammar — APPROVED

Reviewer `/root/native_integration_reviewer`, 2026-10-31. First configured main family failed10 tests with1728 passing in81.09s; later families did not run. Inspected actual failure names/traces in build/native-core-ci/main.log. Failures are source-specific/native category CLI expectations (complete source API status0, bounded direct-source request count) now receiving the previously reviewed production default (core reports unverified catalog status3/discovery requests).

Approved exact input adaptation: add explicit `--source-mode native` to invocation definitions in p4 family extract, extraction controls, six real wire parsers, and valid nested source-scope tests. Preserve all existing assertions, expected exit statuses, evidence/portable checks and request bounds. Do not inject mode globally, change0→3 expectations or increase request caps. New default-production CLI policy/fallback tests remain unchanged and required. This exercises declared compatibility mode rather than weakening assertions to match output. Save failed run as historical evidence, then rerun affected/native+production checks and complete configured driver on the final revision.

Watch's prior Click required timeout grammar should remain required in help/capability metadata, even though the runtime already rejects missing timeout. Narrow shared decorator interface `execution_options(timeout_required=False)` with watch requestingTrue is approved; all other commands retain existing defaults. Test required metadata and missing-timeout usage before source I/O. No extraction algorithm/default changes are approved by this amendment.

## Final independent code and offline verification — PASS

Reviewer `/root/native_integration_reviewer`, 2026-10-31. Final source/test/skill/profile/doc identities are saved in evidence/reviewed-revision.json. Runtime fingerprint: `26506d815157ab127e8aac3aad7ad1711cb4acefe7b2bc3718d61225e2f72b0f`; independently matched against the fresh skill report and configured suite summary. No source/test identity changed between reviewed snapshot and final verification.

Resolved R3: successful extraction is retained when subsequent mapping/export raises, with separate failure stage; actual owned-worker→mapping-fault regression verifies it. Resolved R4: strict browser/LLM boolean metadata validation. Resolved R5: actual stdout/stderr exact boundaries, noisy/invalid worker replies, SIGINT/SIGTERM cleanup and caller-state restoration, normal-exit/timeout grandchild cleanup and two-site invocation/product budgets are covered. Resolved R6: production library validates selected origin/decoded base path before I/O; cross-origin, sibling and encoded traversal cases reject, valid descendant reaches native parser/binder, native hosted-feed compatibility retained. Proxy precedence/NO_PROXY non-parity is explicitly tested/documented, not claimed equivalent to HTTPX. Short-GTIN forwarding honors the existing opt-in without changing checksum/normalization algorithms. Native auto detection and explicit-platform mismatch rejection are verified through controlled real detector/API paths. Eight CLI adapters share existing policy controls; one state/budget covers complete multi-store/watch operation, and watch required-timeout grammar remains intact.

Independently read configured final report and all three final log summaries: **1869 passed,0 failures,0 skipped**, main1739 + reliable-oracle24 + maintenance106,130.594584s. Original240s/family and480s total ceilings retained; every owned test group gone after cleanup. First failed compatibility run remains recorded, with approved exact mode-input edits and unchanged assertions. git diff --check passed. Source-specific feed/tree/guarded-tools restrictions remain intentional and documented. No remaining blocking code finding in this reviewed integration slice.

Non-raising mapping CLI failures retain the existing v1-style mapping.failed/top needs_review semantics; per-stage CLI result is authoritative and these outcomes cannot become pass/live_verified. A broader top-status redesign was not required by this slice. Production supervision is explicitly Linux/main-thread/sequential and owns its launched process group; no claim covers descendants deliberately escaping that group.

## Actual skill execution and live disposition — BLOCKED / UNMET

After final offlinePASS, this reviewer read the updated repo skill/profile/reference/config, inspected actual taxonomy help/catalog info, and ran exactly one configured CLI verification for both Pakistani sites into build/google-live/native-core-review-skill-1. CLI exit3; new report run f4251e2ad9c84b34a493c49997ef27aa, SHA256 a914e5dac2fffebff72560d88a37085b24413800d6756d587dfa3c7b6a591582. Independently checked fresh profile/runtime/catalog/policy hashes and exact site URLs. Both sites are skipped_network_policy/host_not_allowed; pipeline starts0, products0, network countersnull, extraction/mapping not_run, no detected platform or source artifacts, live_verifiedfalse. No denied-site retry, alternate route or native Codex backend attempt occurred.

Actual reviewer model answer, copied report and command/identity summary are saved as evidence/updated-skill-{answer,report,summary}.json. This is explicit file-based execution by an existing Codex app agent, not proof of native CLI skill discovery/activation. Historical spec014 answers remain historical static-profile evidence.

Also inspected evidence/browser-startup.json: parent observed real Crawl4AI local raw-HTML startup failure because its configured executable is missing; process cleanup completed in0.740961s, no merchant request or dependency install. System Chromium presence is not a working native browser result. Merchant live mapping, successful Crawl4AI browser operation, native Codex backend skill activation and prior full5595 mapping/export gate remain blocked/unmet. Offline implementation PASS does not waive these required live observations or authorize a fully-live-verified claim.
