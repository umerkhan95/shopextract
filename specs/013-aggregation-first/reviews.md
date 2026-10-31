# Independent planning review

Reviewer: `/root/aggregation_reviewer`. Date: 2026-10-31. Scope: planning G1
only; author/coordinator are separate agents. No source edits, runtime tests,
model calls or GitHub mutations performed by reviewer.

## G1 initial review — changes required

Reviewed actual spec, test design, tasks, research, plan, source audit, status and
verification. Read repository workflow/constitution and inspected main model
attribute declarations and matcher missing-attribute branches to challenge reuse.

The aggregation-first direction is sound: category-independent admission,
preserved source/Shopify classification, optional Google projection, native-record
companion compatibility, strong supported identity with conflict vetoes, distinct
offer versus cross-product views, finite matching work and no wholesale PR98
merge. Deferred wire/identity vocabulary and exact cursor accounting are explicit
child G1/G2 prerequisites, not current runtime claims. Saved-input Slice A may
honestly mark commerce live checks N/A; later acquisition retains live gates.

| Finding | Severity / disposition |
| --- | --- |
| G1-01: SC09 fixture counts a failed-source placeholder among six source records while requiring no phantom product. It does not fix exact record/group/source/offer denominators, allowing contradictory acceptance or inflated coverage. Define five real product records plus one separate failed-source diagnostic (or another explicit consistent fixture), exact counts and whether stale offer ownership remains visible; record and offer classifications are separate axes. | P2, blocks planning PASS until author clarifies test-design.md. |

Independent docs-only Python pathlib/re/hashlib check inspected every planning
Markdown file (excluding this review): **8 files, 11 FR definitions, 12 SC
definitions, 18 tasks; zero missing relative links, trailing whitespace,
final-newline errors or missing SC test rows**. No implementation tests run.
Command was an inline `python - <<'PY'` checker using `Path.glob('*.md')`, link
resolution, FR/SC/task regular expressions and SHA256; execution receipt is in
this session. Runtime red/green/mechanism/stress/live results remain not run.

Reviewed SHA256 before author repair:

| Artifact | SHA256 |
| --- | --- |
| spec.md | e6d5ded46f310d1c643edfef061afcff8708c0e587f9bd80e36de20fe66732fc |
| test-design.md | dc939ceff742dfe612931fdcd16e1a53b9b56529a9e92523747c332f340a098b |
| tasks.md | 1b34ac013699157c26d6d023f4732be305078ccfc8473e643a3d6114ad9773dd |
| research.md | 90ee931010e46ee4efe3e278778b76efca1e34cc205e5b696ac437054a5de1bf |
| plan.md | 3f204cc032660b5802bab8a7cf0fd90ea5a9ff093601853a374a95d6cd393f93 |
| source-audit.md | 94f059dd4aafd31f307d56f97e3c8fb5288d3de8518897f4624718e9949e0097 |
| status.md | 5227995b99958f747022776de7de42ccbc92029f99ab6c363b4bf6c88c7320ba |
| verification.md | 65df5f1bc847bbfcdea2b92ae0ca748b19f629d02bb3310091a52c9da5e1a4ec |

Re-review pending actual author repair. No G2/G3/runtime final verdict implied.

## G1 re-review — PASS

Reviewer: `/root/aggregation_reviewer`, 2026-10-31. Re-read the actual repaired
SC09 row after coordinator edit. It now defines five actual product records plus
one failed-source diagnostic; input_records5, grouped_records2, accepted_groups1,
unmatched_records2, review_records1, stale_offer_exclusions1 and failed_sources1.
The stale offer owner stays product-visible, and source/offer counts explicitly
do not form additional disjoint record buckets. **G1-01 resolved.**

Updated test-design.md SHA256:
`ebd5e792383202114c5033cb4a06ae2f30e82a564e3b71bf5c0764416674d345`.
Re-ran the independent inline Python docs-only link/whitespace/newline checker
against the eight planning artifacts: zero problems. Other design artifact
digests remain the initial reviewed set; coordinator may now update planning
status/task/verification bookkeeping to cite this verdict.

Planning G1 **PASS**, with no open blocking findings. This approves the bounded
roadmap and first implementation handoff only. G2/G3, executable acceptance reds,
implementation, full repository checks, mechanisms/stress and required live
verification remain future child-slice work. No runtime or PR completion claimed.

## Amended complete-Google G1 — changes required

Reviewer: `/root/aggregation_reviewer`, 2026-10-31. User expanded scope to ALL
Google targets and a complete implementation plan. Prior PASS applies only to
the earlier scope. Read all twelve Markdown artifacts, including three specialist
plans and retained review history. Inspected actual generic category adapter,
mapper and Shopify options helper to challenge source-version/mapping seams.

Complete target-set G proof, separate source-set S ledger, mandatory full catalog
provisioning, actual mapper/binder/public/export stages, bounded subsets, preserved
Shopify/native contracts, forward-only source audit, acquisition/work budgets and
category-independent aggregation are otherwise aligned with expanded scope.
No full corpus, runtime result or guaranteed universal merchant mapping is claimed.

| Finding | Severity / required repair |
| --- | --- |
| G1-A01: google-verification-plan says exhaustive feed fixtures use a declared synthetic source version. Actual generic adapter always emits taxonomy_version=None; other requirements forbid replacing unknown observed version with target version. A sweep that stamps a version after adapter observation would bypass the real seam it claims to verify. | P2 blocking: use actual feed source_version=None with explicit allow_unknown_source_version=True, assert source None and pinned target identity survive; test denied permission separately. Any known-source-version fixture must be separately labelled and must not masquerade as actual feed-adapter behavior. |
| G1-A02: source-mapping-plan MAP02 names a different primary source-ledger status set than spec/research. In particular ambiguous versus mapped-multiple and unsupported/unavailable versus version-unavailable have different possible meanings. Exact disjoint set/count reconciliation cannot use two unstated enum translations. | P2 blocking: define one canonical primary per-source partition consistently; keep row conflicts, precision, support and route outcomes secondary. Invalid references/contradictory exclusions block publication with diagnostic disposition rather than double-counting the same source. Freeze exact payload schema later at child G2. |

Independent inline Python pathlib/re/hashlib checker: **12 Markdown files
including review, 11 reviewed artifact hashes, 13 FR, 15 SC, 25 GAG tasks;
zero missing relative links, whitespace/final-newline problems or absent SC
test-design rows**. This docs-only check does not establish runtime correctness.

Initial amended artifact SHA256:

| Artifact | SHA256 |
| --- | --- |
| google-catalog-plan.md | 800e74a2ac1c8064ebb8f29310ea5018ef7eb0de0eb7190726896c0289967ce1 |
| google-verification-plan.md | 4f0c9ef500ea437f2f0d46f90d71169b857690deb4dfe6ded6578e621d83563e |
| plan.md | 75701abd31f6f64522f6e4f9879f4794bdf20625c29765ddf6950eb35fcff404 |
| research.md | c0a777e335b267b5af92b1ba9a78a1e8b99eeeed074103e8165e360217e1f7a4 |
| source-audit.md | b4136d69542a07c4cfd382379c553706f32e0ba5511cd85501052b2a61b88ee0 |
| source-mapping-plan.md | 7c32b6df8d90187f37c88b3b132711d642096fca539a5f23f8cc5dd38014b395 |
| spec.md | 65f5ad983beabab572bd5f210ace01cae30622f3e0dafddfbadb7f9178ff6a39 |
| status.md | 33f3fd0687713f1fd10501ee46ade3ced8dde0c47964e8b9a34ef538232fe31b |
| tasks.md | 8e463d170d1d35f8a48885733caf7d24afba8814201d4909b661fb4349f616f2 |
| test-design.md | c54e0579a8ea168dd23a9aaa54cf96b87841dce302e9bfe0b184d0a7545bcc25 |
| verification.md | e53528cbc31e86a539480ef800031e41da0287fa26b234b57984dadcbbee4b3e |

Amended G1 re-review pending actual author/coordinator corrections. No production
or historical source files edited by reviewer; no G2/G3/runtime gates passed.

## Amended complete-Google G1 re-review — PASS

Reviewer: `/root/aggregation_reviewer`, 2026-10-31. Independently re-read actual
coordinator corrections in google-verification-plan.md, source-mapping-plan.md
and test-design.md; reviewer did not author those repairs.

- **G1-A01 resolved:** exhaustive actual generic-feed path preserves observed
  source version None, explicitly permits unknown source versions and checks
  pinned version/digest only on target projection. Separate false-permission
  case must not map; synthetic provenance cannot stamp source version.
- **G1-A02 resolved:** MAP02 and SC14 use the canonical six primary statuses.
  Ordered precedence is version-unavailable, invalid-reference, validated
  mapped-single/multiple, explicit-upstream-unmapped, then missing-rule.
  Duplicate rows retain diagnostics without double-counting; contradictory
  exclusions and outside-S source rows prevent publication. Precision, support,
  effective-route conflicts and outside-S diagnostics remain secondary axes.
  Primary counts reconcile to |S| without authorizing an invalid index.

Updated reviewed SHA256:

| Artifact | SHA256 |
| --- | --- |
| google-verification-plan.md | c8851c99a745471448dc42e34643744a5c2ba427e5747e16728a0b8d0bce7477 |
| source-mapping-plan.md | 322f2f574b2df12501b10d2e9423afd61816085e12d003d17778d16f062a4358 |
| test-design.md | b1416e8d00807e54073e68159957ca7d0e33cac356db831ed92df0136e1ebdb6 |

Other design digests remain the initial amended reviewed set. Independent
pathlib/re/hashlib docs check repeated over eleven non-review artifacts:
zero missing relative links, whitespace or final-newline problems.

**AMENDED planning G1 PASS**, no open blocking findings. The complete mandatory
Google target integration and directional source ledger are now planned with
consistent acceptance design; this is not a lookup-only or partial-catalog
approval. Coordinator may finalize GAG03/status/verification bookkeeping against
this verdict. All child G1/G2/G3, actual source acquisition, implementation,
full-ID/source ledgers, installed/full-driver/mechanism/stress/live and final
runtime gates remain NOT STARTED. No runtime completion or external PR mutation
is claimed.
