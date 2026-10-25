# Dependency-ordered tasks — complete with recorded live limits, 2026-10-17

Behavior/test drafts existed before this breakdown. User authorized implementation and
parallel platform agents; default implementation/test execution remains sequential.
Root coordinates; author cannot approve own gates. No unchecked epic implementation.

| Task/status | Dependencies | Owner | FR/SC coverage | Deliverable / completion evidence |
| --- | --- | --- | --- | --- |
| T01 [x] Behavior/test design and distinct-risk inventory | none | root + temporary shared synthesis author | FR01–14 / SC01–12 | spec.md/test-design.md, exact C01–24, platform fixture designs saved before code |
| T02 [x] Six platform discovery + bounded schema resolution + direct consultation | T01 initial drafts | dedicated platform authors/root | FR01,02,07,08,14 / SC02–05,07,08,12 | six platforms/*.md and findings/*.json; minimal BigCommerce/Magento schema proofs; research.md |
| T03 [x] Task-breaker/independent G1 review | T01,T02 | independent reviewer | all | reviews.md actual artifact digest/findings/verdict; resolve blockers before skeleton |
| T04 [x] Shared skeleton and executable red acceptance | T03 pass | shared author + fixture author | FR03,05,09–14 / SC01,08–12 | skeleton.md, explicit stubs/interfaces, C01/C03/C14/C17/C19/C20 failing for intended missing behavior; red.log |
| T05 [x] G2 independent skeleton review | T04 | independent reviewer | all interfaces/error paths | reviews.md digest, findings/disposition/verdict |
| T06 [x] Reusable component model/refined skeleton | T05 pass | shared author with platform consultation | FR05,08,09–14 / SC09–12 | components.md shared consumers/ownership/lifecycle; no duplicated mappers or security bodies |
| T07 [x] G3 independent component review | T06 | independent reviewer | all | reviews.md revised artifact digest/verdict; meaningful contract change reopens affected gates |
| T08 [x] Predesigned sanitized synthetic fixtures + remaining red cases | T03 pass; implementation waits T07 | fixture author; independent coverage reviewer | C01–24 / all | exact native schema/provenance, fixed params/seed26, expected values reviewed; no fake mechanism |
| T09 [x] Shared source observations/mapping/wrappers/companion codec | T07 pass + relevant red evidence | one shared owner | FR03–05,09–12 / SC01,03,05–07,09,11,12 | common code only; focused C10–18,C22; both encode/decode binding checks |
| T10 [x] Six native/generic adapter implementations | T07,T08,T09 interfaces stable | dedicated per-platform authors, sequential by default | FR01,02,07,08,14 / SC02–05,07,08,11,12 | each acknowledges research shared contract; own extractor/adapter only; BigCommerce/Magento actual opt-in bounded queries; source/parser retention generic |
| T11 [x] Common extraction/tool/security/domain plumbing | T07,T09,T10 minimal query contracts | shared owner only | FR07,09,12,14 / SC08,11,12 | exact producer constant guard, no changed defaults, captured payload reaches wrapper before compatibility loss; C03,C04,C21 |
| T12 [x] Maintenance/cache/checkpoint integration | T07,T09,T11 | shared owner only | FR05,06,12,13 / SC09–11 | explicit runtime opt-in/digest/replay/cache validation, codec child-process boundary; C19,C20,C24 |
| T13 [x] Bounded mechanism/adversarial stress | T08–12 | sequential verifier; independent coverage reviewer | C01–24 | smoke saved then <=100 fixed invocations/120s, real code, seed/limits/log/minimal failure; one diagnosed repair/blocker |
| T14 [x] Affected offline regressions + required repo checks | T13 pass | shared author/verifier | FR07 / SC11 | verification.md commands/results; reuse baseline44 smoke, no unnecessary repeated sweep |
| T15 [x] Bounded live verification | T14 pass | root/sequential verifier | per-source FR01,07,14 / SC08,12 | explicit endpoints/access caps before dispatch; <=12HTTP total,2/source,2products; observe or honestly blocked/inconclusive; synthetic separate |
| T16 [x] Final independent review/docs/handoff | T13–15 evidence | independent reviewer/root | all | reviews.md final digest/verdict, verification.md separate offline/live/limitations, status.md; no unsupported completion |

No production/test implementation before G1/G2/G3 and relevant red evidence. Fixture
author may prepare test/generator sources after G1 for red stage; acceptance expectations
remain design-derived. Root controls common-file ownership and stage progression.

T13 evidence:75 unique planned checks passing across reviewed split runs;77 cumulative starts, mechanism-status.json/verification.md. T14:1054pass377.35s, SDK check passed. T15:7 actual requests, Shopify/Woo category observed; Magento cap-limited, Shopware/generic inconclusive, BigCommerce blocked. T16 independent final evidence review PASS in reviews.md.
