# Independent reviews — #24

## G1 — behavior, tests, tasks and research (2026-10-16)

Reviewer: feature_reviewer, separate from feature_author; sequential assignment. Verdict: **changes required**. No production implementation or test execution performed in this review. Actual session token counters unavailable. Review is bounded to these artifacts, issue #24 read once with `gh issue view 24 --json title,body`, workflow/constitution and material existing interfaces in `_discover`, `_storefront`, Shopify/WooCommerce, identity matching, evidence and reliable changes. No network sweep or dependency installation.

Reviewed SHA-256 revisions:

| Artifact | SHA-256 |
| --- | --- |
| spec.md | 5b5d2866c364d0f9c6ae3848af847fc909cd5e17651b80f1de08c3bb0cbf68ac |
| test-design.md | 2d24a939ca18c6477df67ccbe66e904af738682a554d5e0e24d3c1f6e815d201 |
| tasks.md | eee4d0fc89d4ff3fb7c3986ba154d6286601572cf2e351355010924f949b78a8 |
| research.md | 9e9d2d418f7476ab6e337bc6780cd0ca1f8bb712ce8c798fb972a0238c33c14f |
| plan.md | ca29233b1ee2045b8549d11a31847a554b00518e23913bd254122068c9e433ba |
| status.md | d8c97e3a01ff387aa7707f342add24c9fefb5a4278b71fb552b11755a0b48011 |

### Scope and accepted decisions

All issue #24 scope items have explicit FR/SC and slice mappings: the five domain capabilities, real reference MCP client, schemas/pagination/errors/jobs/cancel, source/tool permissions and no write tools, malicious-content defenses, runnable documentation, compatibility, MIT/self-hostability and child-slice breakdown. No required feature was identified as omitted. Stdio-only is a reasonable declared transport boundary for this issue. Official MCP v1 optional dependency bounded below v2 is consistent with the saved Python >=3.10 research; exact selected SDK installation/import/teardown remains a G2 executable obligation, not a demonstrated compatibility pass. Native API/structured parsing and explicit unsupported-mode errors are acceptable if supported modes and their limits remain documented. Shared origin checks plus vetted numeric TCP connection and original TLS hostname is the right egress boundary; implementation correctness remains unproven. Ownership checks, immutable pagination, deterministic cancellation winner and real SDK subprocess tests are substantive additions over existing coverage.

### Findings and required dispositions

**G1-01 — P1, blocking: bound DNS execution itself, not just the HTTP await.** FR-06/07 promise no unbounded work after timeout. Research gives synchronous domain work a killable process but leaves hostname resolution inside the async network backend unspecified. A common implementation using `getaddrinfo` through an async thread wrapper can leave a resolver thread blocked after cancellation; checking results before numeric connect does not solve its resource lifetime. Define the supported resolver execution/cancellation strategy and ownership, including a finite cleanup bound; do not claim asyncio cancellation terminates a blocking OS resolver. Add distinct deterministic cases for a stalled resolver, cancellation/deadline during resolution, and resolver completion after cancellation: no socket connection, no late publication, bounded cleanup and no accumulated unresolved workers. This can use a controlled resolver boundary while exercising actual scheduler/guard/cleanup. Update research, test design and task mapping before G2. Disposition: OPEN.

**G1-02 — P1, blocking: response decompression must be bounded before allocation.** Research requires a decompressed 2 MiB cap, but streaming `aiter_bytes()` and checking emitted length can already allocate an arbitrarily expanded compressed chunk. Existing `_storefront.request` uses that pattern; simply placing a counter around it cannot establish the new memory/response guarantee. Specify a safe server-mode compression policy: for example request identity encoding and reject unsupported content encodings before decoding, or use bounded incremental decoding with capped output allocation. Define raw/decoded budgets and error/completeness semantics, then add compressed expansion, misleading/missing Content-Length and multi-chunk boundary cases using a real controlled transport response. Never stub the decoder/cap being verified. Disposition: OPEN.

**G1-03 — P2, blocking clarification: retained evidence must share an explicit byte budget.** FR-07 limits serialized job results and single evidence responses, while FR-11 retains captured payloads separately; a 4 MiB result containing references does not bound its retained evidence graph. Declare whether 4 MiB covers the entire retained job graph, or give a separate total per-job/session retained-evidence cap, including deduplicated/shared payload accounting and release on eviction/cancel/expiry. Define how evidence truncation/unavailability is reported without dropping supported facts or claiming complete source payload. Add a many-small-references/large-shared-capture interaction and eviction release test; a single 1 MiB evidence-response test misses aggregate storage. Update scenario budget deliberately rather than silently exceeding 48 cases. Disposition: OPEN.

**G1-04 — P2, blocking clarification: discovery output and extraction authority must agree.** FR-03 says a discovered URL must be accepted by extraction, while test-design correctly says discovery does not grant an unallowed origin. Specify that output URLs are normalized, policy-screened extraction inputs (or explicitly classify rejected links separately as diagnostics), including cross-origin sitemap links and an allowed-origin URL whose DNS later becomes nonpublic. Acceptance means schema/source-mode eligibility, never permission to skip connection-time revalidation. Add exact expectations for cross-origin discovered links and later DNS change. Disposition: OPEN.

### Progression

Resolve G1-01–04 in design/research/tasks and resubmit changed artifact digests to this independent reviewer. No need for user permission to repair these engineering gaps. G2 must still prove SDK signatures, actual Host/SNI preservation, all fetch seams, worker/SQLite cancellation rollback and acceptance red failures. Child issues must be created before implementation as issue #24 and plan require. No future review verdict is implied by this review.

### Author response to G1-01–04 (2026-10-16; rereview pending)

- G1-01: Addressed in spec G1 clarification and research; R1/R2 test real resolver process cancellation/reaping/late replies; tasks B includes <=2s resolve, <=1s cleanup, fail-closed shutdown and no accumulated workers.
- G1-02: Addressed with identity-only encoding, predecode rejection and <=64KiB raw reads/2MiB actual-body cap; R3/R4 cover compressed expansion, Content-Length/framing and chunk boundaries.
- G1-03: Addressed by full reachable graph 4MiB/job and aggregate 32MiB/session, explicit shared-capture accounting, publication reservation and lifecycle release; R5/R6 cover distinct aggregate risks.
- G1-04: Addressed with normalized policy-screened discovery candidates, separate rejected_source diagnostics and mandatory connection-time DNS revalidation; R7/R8 cover cross-origin and DNS-change interaction.

## G1 rereview — revised design (2026-10-16)

Reviewer: feature_reviewer. Verdict: **PASS for G1; proceed to skeleton/red tests and G2**. This approves the revised behavior/research/test design, not implementation correctness or completed verification. No production code exists in this slice yet; no SDK compatibility, network security or resource result is represented as executed.

Reviewed SHA-256 revisions:

| Artifact | SHA-256 |
| --- | --- |
| spec.md | b62c9cb39a96474b03b92c44523c2550773124da8b1fca3fada00403cdc7e3b8 |
| test-design.md | 0b5d9d000f17642b0cfcf5c01db9ad1a43a95f65a3ce791a2de7c0e7081ac998 |
| tasks.md | cf6743d9891dda897de1294de7a0998edfbae48db1524a13d210bbadccafc422 |
| research.md | e9f0817ca4a4c2d4b9d7910aa9bd723cfefb1eee10c51271cc3d90dc08b5b81f |
| plan.md | e1fd05e06960a50207a0e19e9493b91ccf2a2b42d0482b90708fbe8832fcdbc5 |
| status.md | 6b817ac1c98e9075fa4ca8ea116d71cd42cbee55edd7e3f0f465c21d5d522521 |

Independent dispositions:

- G1-01 CLOSED at design stage: owned OS resolver process, <=2-second/remaining-deadline resolution, <=1-second cleanup grace, late-result exclusion and fail-closed admission on reap failure resolve the blocking-thread gap. Resolver/domain workers serialize under the existing one-auxiliary-process ceiling. R1/R2 and the reaper-failure boundary fault target deadline, explicit cancel, late completion and accumulation separately. Terminal reporting's cleanup grace is now explicit.
- G1-02 CLOSED at design stage: identity-only encoding rejected at headers before decoder consumption removes the expansion path. <=64 KiB raw reads and actual 2 MiB incremental cap specify the allocation boundary. R3/R4 include encoded response rejection, false/missing length, exact size and malformed framing. G2 must expose this before HTTPX automatic decoding or `_storefront` body iteration; rejecting an already decoded response would not meet this design.
- G1-03 CLOSED at design stage: 4 MiB covers the entire reachable serialized job graph and 32 MiB covers running/terminal/configured materializations, with conservative cross-job charging, atomic publication and owner invalidation/release. The single 1 MiB evidence-response cap remains independent. R5/R6 cover aliasing versus distinct payloads, aggregate exhaustion and lifecycle release rather than repeating single-payload assertions. These are serialized accounting limits, not measured resident-memory claims; the stress plan still separately measures its memory target.
- G1-04 CLOSED at design stage: discovery returns policy-screened source-mode eligible URLs and diagnostic-only denied links; extraction revalidates current DNS and permissions. R7 checks forbidden discovered destinations without connecting; R8 checks public-to-private change after valid discovery. Eligibility and durable authority are no longer conflated.

The eight additions have explicit fixture risks and expected outcomes and stay inside 48 planned cases by substitution. The pre-execution inventory is still required to preserve all original address/redirect/limit coverage; grouping parameterized boundaries cannot waive an invariant. Full epic capability mapping remains intact. Primary unresolved engineering obligations belong to G2/G3 and actual execution: selected MCP SDK signatures on Python 3.10, pinned IP plus correct Host/SNI, guarded injection across all parser/fallback seams, bounded worker IPC and SQLite rollback/publication races. Preserve original first-smoke, offline-before-live, real SDK process integration and independent final-review requirements. Coordinator must create mapped child issues before implementation. No new user approval is needed for the next engineering gate.

## G2 — skeleton and executable red review (2026-10-16)

Reviewer: feature_reviewer. Verdict: **CHANGES REQUIRED**. Inspected skeleton.md, verification.md, all four tools scaffold modules, four fixture/acceptance modules, pyproject.toml, acceptance-red.log and SDK probe source/log. No acceptance rerun or implementation. A bounded local signature inspection confirmed HTTPCore's public network_backend/connect_tcp seams; no stalled command or additional network research.

Reviewed SHA-256 digests (captured before this review edit):

| Artifact | SHA-256 |
| --- | --- |
| skeleton.md | 6d463d68c299394eb322f115e35b7c508e9fb518f7f2f1b2f8cde01004954df2 |
| verification.md | 4139ae1e43f72efb608064aa573301c0f54c7b21b1f444db70d3bc28e50657e2 |
| tools/__init__.py | 96a1d67c55da5d7bf565c2a0f89f5ad2bdc3e115ffd25224e2d31222cb6ddea8 |
| tools/mcp_server.py | 7b5c3460d7229478c1197d564eaf8cac683b26da8338c1a952a0e546ade0f89f |
| tools/runtime.py | e2950990c782ecebc83613c7740d047005edecf3c2f4f50ae2c8c31ef3d6a954 |
| tools/security.py | b7097361d910c76fab25e2c8e4e9df8bc3943d7f3338c68c68159fe2bbc5e1e1 |
| test_agent_tool_api.py | 29d5bd7b6155f36652c0b01105d5f49c923121bfc8580c1c91b79f2393e4c703 |
| test_mcp_reference_client.py | e0d50afaae8a11df4e5055d0d9a49c9b4e9dcdd6c2aa2f0733c642f58d89d4e3 |
| tool_api_fixtures.py | 243fb4beeb590718cf65738d3cab568169faeafb2206a41f08053926915d2e5b |
| mcp_fixture_server.py | bdf0890817b917fd2ff71428e85276e48d02cac8a4daba485a47557e2561d0ca |
| pyproject.toml | 7a4c594a191224344255eedccc3896d1fc4cab3933de3c2816d06a950aa7053a |
| acceptance-red.log | 0829aa818bbd14a16c279aa8a00a50fd09d9567c89a9d9fea99e93632415dad0 |
| sdk-probe.log | 30a4137218da9b182dc8a54776a961786b9b4882a5ba326c41260cffcb47eb4d |
| sdk-probe.py | 09285c7fb8591cd900daa7a30e7c728a94ecf9e688b46b4b36f9435e5cc32ebf |

Accepted evidence: eight tests collected and failed on deliberate missing dispatch, guard or authoritative schemas, rather than missing dependency/import/environment errors. The real MCP test initialized SDK stdio before the missing-schema failure. Separate SDK probe demonstrates initialize/list/call/disconnect on mcp1.30.0/Python3.10.11; it does not demonstrate domain success. Stub teardown failure is disclosed and no existing job/resource cleanup is claimed. Dependency direction and reuse intentions remain consistent with G1. The full SC/R matrix remains a later implementation/verification obligation; G2 does not require every future assertion executable now.

- **G2-01 — P1, OPEN:** Deadline/resource ownership is prose-only at the critical boundary. `SourceGuard.authorize(url)` has no job deadline, cancellation owner or shared request/resolver budget; pinned backend resolution similarly lacks a declared binding to that job. Define an explicit typed operation context (or equally explicit constructor-bound per-job ownership) passed through sources, guard, backend and OwnedProcess. Show the same absolute deadline/cancel signal and one auxiliary-process slot reaching both candidate screening and connection-time resolution, and how budgets survive redirects/fallbacks without resets. Add declarations only; no business logic is requested. Update the representative cancellation fixture to exercise the declared context seam.
- **G2-02 — P2, OPEN:** The ownership red currently supplies an invented owner and evidence ID that exists nowhere. Even a globally unscoped lookup returning not_found would satisfy it. Add a representative preimplementation red that obtains actual retained evidence from one authorized owner/session and requests that existing ID through a different valid owner/session; expected not_found, with the authorized lookup still available. Define valid opaque handle syntax or mint handles through the API so malformed-ID validation cannot substitute for ownership. Strengthen the existing complete-flow evidence assertion to compare its captured value/pointer and deterministic capture metadata with predeclared fixture expectations; truthy retained_data/source_url alone would accept an unrelated payload. This is a focused representative ownership/evidence repair, not a demand to implement the entire future coverage matrix.
- **G2-03 — P2, OPEN:** `test_mcp_reference_client.py` imports optional mcp unconditionally while the dev extra does not require it. Existing test collection without the optional server extra will fail at import. Use an explicit optional-test skip/import guard, or a declared test dependency strategy that preserves ordinary installation compatibility; document and retain the extra-enabled command as mandatory for MCP feature verification. An absent-extra skip must never be reported as MCP acceptance passing.

Repair these artifacts and save updated meaningful red evidence, then request independent rereview. G2/G3 are not passed. Future G3/implementation obligations include actual strict schemas, CallToolResult error flag/structured parity, try/finally disconnect cleanup, exact Host/SNI pinning, real resolver reaping, IPC caps and SQLite rollback/publication races. No user permission is required for these routine engineering repairs.

These are author dispositions, not reviewer approval. Original findings/verdict remain historical and independent G1 rereview is required. Eight named stress cases substitute within the existing 48-case ceiling; no budget expansion or feature omission.

### Author response to G2-01–03 (2026-10-16; independent rereview pending)

- G2-01 addressed by typed OperationContext/OperationBudget/AuxiliaryOwner/Resolver declarations and constructor/authorize signatures; skeleton binds the same context through candidate, redirect, fallback, TCP and owned process; cancellation fixture checks actual passed context cancellation signal.
- G2-02 addressed by real persisted two-owner graphs, existing foreign evidence availability proof, API-minted valid owner handles and authorized→foreign-denied→authorized checks. Full flow selects exact price evidence and checks pointer/value/source pointer/method/fixed UTC timestamp/truncation.
- G2-03 addressed by pytest.importorskip before optional MCP imports; absent-extra skip is documented as incomplete MCP verification, mandatory extra-enabled command retained.

Updated representative red saved: eight intended failures in2.72s; real ownership fixture persistence/lookup succeeds before missing bootstrap red. Added components.md at coordinator request, awaiting corrected G2 then separate G3 review. These are author dispositions only; no reviewer pass claimed.

## Corrected G2 rereview (2026-10-16)

Reviewer: feature_reviewer. Verdict: **PASS for G2**. Bounded inspection of changed declarations, tests, revised skeleton, author dispositions and saved acceptance-red-g2-revision.log only; no tests/probes rerun, dependency installs or new research. Existing SDK probe remains reused evidence.

Reviewed revisions, also serving as the immediately following G3 artifact manifest:

| Artifact | SHA-256 |
| --- | --- |
| skeleton.md | f436146152a0a9989e2ab06e459e1509661dce6943e75d6353c1a91b2d0deb0f |
| components.md | bdeaf9ccebc82ea5dcc910a6ccf635e7aceb2fe9af55dbeaaf2d155346cad7bd |
| verification.md | d899212068a174bb05c922953ef223ffa3ffe69c278705fee3761c5fe5908bf9 |
| tools/context.py | 323b6d2023cf83411ac6277b410b6db636a0a51957d4be6df50870824c099086 |
| tools/runtime.py | 3b49859725161ae92f7146b9314a0fa90931678c48439e6dd6886d36a28a7ded |
| tools/security.py | b6f6fe22ec0d3a3dce2f58a25100f5739a8e667b8287281f94d69ee88650a5a2 |
| test_agent_tool_api.py | bb3a62caa8f203d24438893085541a158137e083ea27ea512f7c22b7e06e7b3d |
| test_mcp_reference_client.py | 37d55aa53d72c13836a98a9e0a9c0036a047ae22bc5b8cd0967943aff5571ee5 |
| tool_api_fixtures.py | 4d488c1997753e4b630abf310af51df31e6b226867012d6cb2ae9a79ed20e4c6 |
| acceptance-red-g2-revision.log | fde44462ede8fd04c5233869c439079c4a70f5e0991b75b8e5353bbbd576d788 |

- G2-01 CLOSED at skeleton stage: explicit OperationContext/OperationBudget/AuxiliaryOwner/Resolver declarations carry absolute deadline, cancellation signal, cumulative budget and the shared auxiliary slot. SourceGuard now receives context; revised mandatory declarations bind the same context through sources, candidate screening, per-job transport/backend and process execution. Constructor-bound context is appropriate for the fixed HTTPCore connect_tcp signature. Later mandatory signatures explicitly supersede earlier sketch signatures. The representative cancel test checks the passed context signal; actual process reaping remains an implementation obligation.
- G2-02 CLOSED at red-design stage: two real persisted owner graphs establish existing evidence before bootstrap; valid owner handles are API-minted. Authorized → wrong-owner denied → authorized unchanged assertions exercise the intended ownership invariant once implemented. Price evidence selection now checks exact value, source pointer, pointer, method, fixed UTC time and truncation. The revised log still reports eight intentional failures, including missing bootstrap/guard/runtime/schema, with no optional-import skip or environment failure. No green ownership assertion is claimed yet.
- G2-03 CLOSED: importorskip precedes SDK imports. Optional absence is an explicit skip; the documented extra-enabled run is still mandatory for feature verification and currently produces the intended red, not a skipped MCP result.

No blocking G2 findings remain. This approves interfaces and representative meaningful reds, not completed functionality or full acceptance coverage.

## G3 — reusable components and revised skeleton (2026-10-16)

Reviewer: feature_reviewer, reviewed sequentially after corrected G2 pass. Verdict: **PASS for G3**. Artifact revisions are the manifest immediately above, primarily components.md and skeleton.md; unchanged G1 contracts and existing-interface inspection are reused. No implementation or tests run in this review.

Existing parsers, normalization/capture/field resolution, portable serialization, identity-aware matching and reliable-change/evidence persistence have named consumers and preserve their algorithm ownership. Narrow source injection and supported static modes avoid duplicating extraction engines or inheriting unguarded fallbacks. The new contracts, store, jobs, execution owner and transport layers each have a concrete shared responsibility; there is no proposed generic orchestration framework. Per-job network pools/context and session auxiliary ownership make authority and cleanup explicit. RetainedGraph owns evidence/catalog handles and byte charging, preventing a second unaccounted evidence cache. Active dependency lifetime is checked again before publication, and temporary copies are charged rather than silently extending expired handles. Python/MCP adapters share one domain contract; optional SDK stays outside legacy imports.

No blocking cohesion/reuse/ownership finding remains. Implementation must preserve the spec's terminal-winner rule: cancellation of an already succeeded job keeps its graph/results; cancellation release language applies to cancelled/unpublished work. The component wording is read under that explicit spec invariant. Existing planned checks for real DNS/process cleanup, raw encoding bounds, exact Host/SNI, SQLite rollback, publication races, all source seams and R1–R8 remain mandatory. The prepared component model does not establish any of those runtime properties by itself. Proceed sequentially through mapped child slices, saving focused red-to-green evidence, then offline/stress/live and independent final review. No completion or final-review pass is implied.

## Affected G1/G2/G3 review — native Shopware read-only search (2026-10-16)

Reviewer: feature_reviewer. **Affected G1 PASS; affected G2 PASS; affected G3 PASS.** Narrow sequential design review of the appended Shopware amendment, NS-01–03 and NativeReadPolicy declaration only. Existing native Shopware request-body shape was checked locally; no implementation audit, test execution, external research or other gate is claimed. Guard allowance remains to be implemented and verified.

Reviewed SHA-256 revisions:

| Artifact | SHA-256 |
| --- | --- |
| spec.md | 414d337cd11b77a94412ac0f07592627979fb13e39b50a2d6787e66b19ba8a8d |
| test-design.md | 05b024d7dba5a386376c53aedbd0f89ad0f1e58303e17ded64903d1386beaf1c |
| research.md | 6da13e9c7a9dfaad4add78d4550694bfd05dc76a72e16118280b85932cc03c71 |
| skeleton.md | db63788eb0e4b58184eff3936b26d3b1d7632a2b26da17222a5db1cc5cc00f05 |
| plan.md | 746f97a4d8b5aa3f30ff70b05ea2dc3cb561f7c6ab5f8a4971a3704ccce35955 |
| tasks.md | 45ab034ef821aaf55768568c89feae4d2597ff38d12b53d85686d513c45fa02f |
| status.md | 9f792e9e3704b226acafd182d71247e0a2af1fbfbab597b41165e75527f1e0d1 |

G1: The amendment explicitly supersedes GraphQL-only POST wording in FR-08 for one existing read-only Store API operation. It preserves all five native platform modes without granting a user write tool. Exact allowed origin plus canonical `/store-api/product` path, no query/userinfo/fragment, strict bounded page/limit, integer total-count mode and fixed nested sort/associations prevent arbitrary request-body authority. Current source/IP/connection/budget/error constraints still apply. NS-01 covers meaningful zero/false/variant/context-evidence behavior through existing parsing; NS-02 independently tests route/policy/method/redirect authority; NS-03 tests strict nested body authority. They refine existing slots within 48 cases, retaining the mandatory pre-execution coverage inventory.

G2: A frozen per-job NativeReadPolicy constructed only by trusted native adapter is an appropriate explicit seam; default absence denies non-GraphQL POST. Exact normalized URL binding and pre-transport strict body validation are required, not suffix checks or a generic POST flag. Public configuration may supply data after origin/DNS screening but cannot register arbitrary routes or policy. GET context and product search use the existing OperationContext and shared transport budgets; no extra resolver/job framework is introduced. For NS-02 redirect assertions, zero destination bytes means zero bytes to the redirected target: the initial authorized search request necessarily occurs before its redirect response can be known. That initial request still counts toward the shared budget.

G3: The adapter continues using the existing ShopwareExtractor request body and parser. Policy is a narrow parameter to the existing guarded transport, not a duplicated platform implementation or extensible mutation mechanism. Canonical-path mode limits are explicit and legacy defaults remain unchanged. No blocking finding remains for this amendment. Before enabling/accepting the feature, save intended red evidence for NS-01–03, implement the exact allowance, and run their real-path checks plus affected regressions. This review grants no runtime-security, full native-platform, stress/live or final-verification pass.

## Mechanism fixture/coverage gate (2026-10-16)

Reviewer: feature_reviewer. Verdict: **CHANGES REQUIRED before driver/stress execution**. Bounded source inspection only: concrete manifest/driver, new adverse tests, relevant existing lifecycle/owner fixtures and actual job/process seams. No stress, full suite or live execution; previous focused green logs are not rerun or broadened into coverage claims.

| Reviewed artifact | SHA-256 |
| --- | --- |
| mechanism-inventory.md | b2a14d2b06a975a1b4786ff03027b91cf99a310a24c906e0336b288dca8cbe5c |
| test-design.md | 67243b96c3176f607fa93ba16fb922b5e9dc9fa66c94694d0308ccf1e60be0e5 |
| spec.md | 414d337cd11b77a94412ac0f07592627979fb13e39b50a2d6787e66b19ba8a8d |
| mechanism-inventory.json | 7d5de0343d5633fe88bf867ce3a3bd6bd1f269b48a23f9e40b78076704c3d47a |
| run-mechanisms.py | cfcc52f4cd5d2ffe5adf78319d91d4e14b4a570ba2fcaee6d09b680cf525587d |
| test_tool_mechanisms.py | fc8ad3e9e5603902cbe57dc2e9bfad0a51d18f598fc096897f23de908b75c57b |
| test_tool_lifecycle.py | 70bd35add40afc5eb7caa49ccef53b7c5bd9c3fdb81522096cdb7c07eeaa9725 |
| test_agent_tool_api.py | 464e74df6145ecd83058df95761bbd793ec4186a96c492544f627ea5c9eb5617 |

Accepted design/mechanism strengths: real two-owner SQLite captures, deterministic source fixture values, native parser/normalizer flow, exact-body Shopware cases, actual killable spawned resolver/domain children, late resolver reply attempt, real reliable_changes transaction interruption and SQLite integrity/report-count rollback assertion. Host/SNI arguments are inspected through real HTTPCore and a controlled network stream; separate actual local TCP servers prove denied redirect target receives no connection. This is controlled connection/hostname wiring evidence, not a live TLS certificate validation demonstration. Queue-wait timeout, compressed-header rejection, byte caps and graph charging have distinct real-path assertions. None is marked executed by this review.

- **MC-01 — P1, OPEN: negative control does not break the mechanism.** The owner test replaces `engine.call` with a function returning the previously authorized payload, then proves an assertion rejects that canned payload. This demonstrates assertion tautology, not sensitivity to a missing owner check. Keep real dispatch/evidence lookup active; temporarily remove only the actual owner-scope constraint or remap the lookup scope at its precise seam, then run the same denied-owner assertion and demonstrate it fails, restoring with try/finally/monkeypatch. Add similarly narrow redirect guard and terminal-publication cancellation controls as promised in the design. Do not replace algorithms/dispatcher with expected answers. Define the control recipes and required observations before running them; a test-scoped guard/owner bypass must never ship as production configuration.
- **MC-02 — P1, OPEN: missing declared interactions.** Queue deadline is genuinely covered. Resolver late IPC and cancelling a forever-waiting operation do not cover a domain operation that catches cancellation and returns a graph at the publication boundary; add a deterministic barrier case proving no successful graph/handles survive that loser. Normal reliable-change replay does not cover partial/incomplete capture plus replay: use real persisted incomplete capture metadata and verify no unsupported removal/promotion, stable report/event identity and truthful diagnostics on replay. The current TTL case uses an empty known owner and direct lookup; add page-of-real-extraction → clock expiry → tool evidence lookup, and dependency expiry before delayed match/change publication, with explicit expired/no-published-handle outcomes. Group related assertions or replace weaker cases to remain within 48; preserve distinct earlier risks.
- **MC-03 — P2, OPEN: inventory overclaims traceability.** Every M20–M48 row currently claims FR02–11, SC01/03–09/11/12 and R1–R8, even where the node only checks one body or address invariant. Several existing rows similarly list broad ranges. Replace these with the exact FR/SC/R/NS links each node asserts and a short expected outcome; explicitly identify which original required invariants remain outside this stress run with separate saved/planned tests. Fix misleading descriptions such as copy isolation where the node only checks oversized-response metadata. Counts and blanket ranges cannot establish full coverage.
- **MC-04 — P2, OPEN: resumability/resource receipt needs complete identity and accounting.** Driver revision hashes manifest/tools/test globs but omits itself and existing parser/normalizer/matching/reliable-change/evidence production dependencies. A changed existing algorithm could therefore reuse stale passed cases. Include the driver and actual production dependency sources (or a conservative complete source-tree content digest), plus fixture inputs outside the existing glob. `fixture_bytes_limit` is declared but never checked/accounted: record a deterministic fixture-byte bound/inventory and validate the aggregate against 16 MiB, distinguishing retained artifacts from temporary allocation. Preserve default-cap probes without claiming unmeasured memory. The existing RSS measurement and stop-first-failure behavior are useful; they do not enforce the separate fixture-byte promise.

Affected contract clarification: explicit output schema shapes, strict deep/cyclic JSON failure and conservative charging of actual payload copies refine existing FR02/07 and R5/R6 without dropping scope; accepted at design level. Full output-schema correctness is still a final implementation-review obligation. Repair MC-01–04 and request bounded rereview before invoking `--reviewed`; this verdict does not authorize treating planned 48 cases as passing. No user approval is required for these engineering repairs.

## Corrected mechanism-gate rereview (2026-10-16)

Reviewer: feature_reviewer. Verdict: **CHANGES REQUIRED — one remaining driver resource-receipt defect**. No stress/full-suite/live execution. Only repaired controls/interactions, mapping, resource ledger/driver and process-count clarification inspected.

| Artifact | SHA-256 |
| --- | --- |
| mechanism-inventory.md | 76bbe33cf36ffd97377b0d9c6827e013633d1199f4fffa11ef2e7ce37b80fc5a |
| spec.md | 401ef04ee3ffc394472a7e57ed1d7fe3619240906c5d0c1a29989b8e06ddcb56 |
| test-design.md | 454ba26c893f7a85f922adade9aef9bd1dd01918865da317d463b07f48205c16 |
| mechanism-inventory.json | 8df2f4894eef4d932620fd74cb71d4a872156393539b8e2e14ac433d80a8feab |
| run-mechanisms.py | 6915487aa0f29ab093bfadd1207abcf0df22e65e309e109b2aac7127e4bf0036 |
| process-inventory-probe.log (identity) | fdebbbd44c9949f08e6eba002d5eae233ecb3e9cea9fcc722a4b6e29854fc531 |
| tool_faults.py | 8b9c8232551b5cba217ca3dd9c495bd744015761ea0a6f803c914fd28c552c43 |
| tool_fixture_budget.py | 150b93649d3de2e88ab67d55f72b1c1abcfe0a1b959499cbc524da2b245f03ae |
| test_tool_mechanisms.py | e138a9ce5520c756a53bee2e23e1bc4b35c22aca49fa85230b833a518540e984 |
| test_agent_tool_api.py | e8da2e55f1bd5598e12f191ac10febd03b56cb8d21fa130e3c3fb022408145d5 |

MC-01 CLOSED at fixture-design stage: owner control remaps only actual store lookup scope, redirect control changes only guard origin membership, and AST control removes exactly the actual post-operation cancellation branch. Real dispatch, lookup, guard and job publication stay active; normal and broken paths assert the same invariant, with finally restoration. These now establish meaningful planned sensitivity controls rather than a canned payload assertion.

MC-02 CLOSED at fixture-design stage: cancellation-catching graph return tests late publication and reservation/handle exclusion; real complete→incomplete persisted capture replay checks no removal promotion plus stable report/candidates/diagnostics; real extracted evidence crosses TTL through tool lookup and a fresh runtime; real matching result is held before publication while its catalog dependency expires. These fill the identified interaction gaps without duplicating random input variations. Actual execution remains pending.

MC-03 CLOSED: individual rows now name exact asserted links/outcomes and separate outside-run obligations; removed weak cases are disclosed. The manifest no longer presents every node as proving all R/SC requirements. Remaining final traceability obligations are explicitly pending rather than waived.

MC-04 PARTIALLY RESOLVED: conservative source/test/driver/helper/static-input/config/environment identity prevents stale reuse, consumed time/bytes survive revision changes, and runtime fixture categories plus per-case maxima make the 16 MiB promise auditable. Serialized fixture accounting remains distinct from RSS. **P2 remaining blocker:** RSS/process overflow is checked only after recording the current case `passed`, and merely breaks the loop. On the final case the driver still returns success because all case statuses are passed; on a resumed run the resource-violating passed case is skipped and prior resource peaks are not a failure barrier. Before saving progress, mark such an overflow as failed/resource_limit with explicit reason and persist a resource-failure receipt. Final success and resume must not accept a saved violating pass; preserve consumed budget and require a diagnosed repair/rerun or report blocker. A small helper/unit check of final-case and resume handling can verify this without executing stress.

Affected G1/G2/G3 numerical clarification: **PASS at design level** for a maximum five-process tree including client/server interpreter resource trackers, while retaining exactly one active job and one auxiliary worker. Trackers are interpreter-owned support, not additional resolver/domain workers; killing a caller's shared tracker during library close would be incorrect. The revised declaration explicitly supersedes the earlier three-process estimate, preserves <=1-second auxiliary cleanup and prohibits per-job tracker accumulation. Actual tree/RSS limits still require measurement during execution; this clarification does not excuse a driver success after overflow.

Only the MC-04 resource-failure accounting/return defect blocks the corrected gate. Do not run `--reviewed` until its bounded rereview passes. No new investigation or broader scope is required.

## MC-04 driver-state rereview and mechanism-gate disposition (2026-10-16)

Reviewer: feature_reviewer. **MC-04 CLOSED; corrected fixture/coverage gate PASS for the bounded 48-case run.** Inspected only changed driver state transitions, four pure regression cases and their saved result. No mechanisms, full suite, SDK probe or live request executed during rereview.

| Artifact | SHA-256 |
| --- | --- |
| run-mechanisms.py | 9d44f4f32cf03f102d27ccc1eee33a3b39a9e7e0c78169387f19e6ad9e880f26 |
| test_mechanism_driver_state.py | af05f426f5733efc2032c7ba0a7df3a27fe1fd58ac8f46998dfd68cf777e1a7c |
| driver-state-regression.log | 020312481c03f9e92ba5820c1caeeb7919027c5a2849fbbcb3a4192c77bf403c |

Resource observations now change a violating case to failed_resource before saving, preserving reasons and failure history. Final monitor observations are applied again before successful() checks every exact manifest node and requires zero current/historical resource failures. Resume checks saved peaks/history before any revision replacement; legacy overflowing passes acquire an explicit blocking resource receipt. Revision change preserves consumed elapsed time and fixture bytes, so source identity changes cannot reset the experiment budget. Pure regressions exercise RSS and process overflow on the final case, legacy receipt resume and exact-node/history success requirements; saved outcome is four passed in 0.06s, not stress evidence.

MC-01–03 and the five-process numerical clarification retain the immediately preceding rereview dispositions. The planned deterministic real-path cases and narrow negative controls are approved to execute under existing 120-second/48-case/16-MiB fixture/256-MiB additional RSS/five-total-process limits and stop-first-failure rules. An unavailable RSS measurement must remain explicitly unavailable. A later failure requires the declared bounded diagnosis/repair process, not receipt deletion or budget reset. Outside-run obligations listed in mechanism-inventory.md, full regression/actual MCP request lifecycle, public live observations and independent final implementation review remain pending. This is execution-readiness approval, not a mechanism/stress pass or feature completion.

## Bounded timing/carry-forward audit after M11 (2026-10-16)

Reviewer: feature_reviewer. **PASS for semantic carry-forward of M01–M10 and independent M12–M48 continuation; M11 remains a failed/blocked timing case.** No tests, full suite, stress or live requests run in this audit. Inspected saved before/after source diff, exact cache helper, original receipt, one repaired affected-check receipt and audit accounting. No second M11 repair or retry is requested or authorized by this disposition.

| Artifact | SHA-256 |
| --- | --- |
| original mechanism-progress.json, unchanged | 59163f1839c85f22cdf12ff558fca0a3a9fa2acab2304f42027392eb9c943453 |
| validator-cache-repair.json | e5674dc84254d546dd0089e7cc357e7f04b294d47dcfa0a1cfac45bf643d586d |
| validator-cache-before.source | e8da2e55f1bd5598e12f191ac10febd03b56cb8d21fa130e3c3fb022408145d5 |
| tests/test_agent_tool_api.py after repair | 466c79afcdfa8d6993f6eace639c3332c8e3267d50cdb7ebb0c36ef7d61013c5 |
| tests/tool_schema_validation.py | 211ffc69d7d6d43fe6f88a6321f213b335889c0e0b83b48b6139f09bffbcd48a |
| m11-cache-affected.json | ed7a95aeb0f5aac37839a80712f28110ec8aa035f284b70b42c7f1c0550abf00 |

The only existing test-file changes are four imports switching schema_validate to a bounded LRU helper. That helper keys a fresh immutable schema snapshot by exact canonical JSON, uses the same draft selection and check_schema, then validates each actual/corrupted instance. Assertions, schemas, fixture values and acceptance/rejection semantics are unchanged; error-selection ordering is not asserted by these tests. The ten saved passes may therefore carry forward with their original revision/provenance; M09's schema-validation import change is semantically equivalent. The repair inventory identifies fourteen affected manifest consumers and the separate MCP consumer; none is claimed newly passed by this audit.

Accounting independently matches: 10.747519020005711 original-driver seconds + 8.008281950998935 affected-check setup/case seconds + 0.452095695 audit-creation seconds = **19.207896666004647 seconds charged**, leaving **100.79210333399536 seconds** of the original 120-second experiment. Fixture accounting is 194,362 + 77,600 = **271,962 bytes**, leaving **16,505,254 bytes** of 16 MiB. Original receipt SHA remains unchanged. Isolated repaired M11 still exceeded its five-second case ceiling (5.662139695996302 case seconds); setup must not be hidden by charging only the case. This is a recorded bounded timing limitation, not a successful M11 mechanism result.

Safe continuation instructions: preserve the original receipt and repair evidence read-only. Create a separately named derived continuation receipt with current complete identity, original pass entries/provenance, this review reference, and the additive consumed time/bytes above. Carry M11 as explicit blocked_timing_after_one_repair, retaining both failed observations and reason; do not mark it passed, delete it, reset budgets, raise its five-second limit or retry it in the stress driver. Skip only this explicitly reviewed blocked ID while executing M12–M48 sequentially within the remaining aggregate budget and existing per-case/resource bounds. Preserve resource-failure resume barriers. A new failure still stops for its own bounded diagnosis; this is not permission to skip arbitrary future failures. If continuation handling needs a narrow runner change, bind it to this specific review/receipt/blocked-ID provenance rather than a generic ignore-failures switch.

Final driver success must still require all 48 passed and zero resource violations: continuation may finish useful independent checks, but must return/report incomplete or nonzero while M11 is blocked. A separately bounded full-suite run may execute the unchanged M11 assertions under the declared 180-second suite ceiling; save its result as distinct regression evidence. It cannot erase the five-second stress failure or retrospectively make the 48-case stress run pass. No further M11 optimization cycle is part of this assignment. Report final mechanism correctness and the remaining stress timing limitation separately.

## Canonical-guard/offline-repair carry audit (2026-10-16)

Reviewer: feature_reviewer. **PASS for the narrow repairs and evidence preservation; further stress expansion is BLOCKED by unbounded accounting uncertainty.** No tests, suite or live execution in this audit. Original receipts remain unchanged; full implementation review remains pending.

| Artifact | SHA-256 |
| --- | --- |
| guard-normalization.diff | 5c554737da7644b1d69311baab9ed3ffea1240e17f78e856df1cbfe7d3be0649 |
| guard-normalization-repair.json | 51618349d21215055fa260fc4811d45fb07fd359e4ab312158a882b5ae758363 |
| three-offline-repair.diff | ce61506c4b0eb936b6e61be40e17dfcfeebb0edfa537879a6832cfdf49526df0 |
| three-offline-repair.json | ac6f4c44a18c713dca75c3150c2df758e08de8ee3017abf37c2ee8cae71756c0 |
| mechanism-continuation.json | 61338ea0110e91076e80da0983a03c8949a8b3bde678d7033e333367edc466ce |
| full-repository-suite.json | 4697b22ba20cb8fda40d569ba93d2fdbc827c50d8e415a28aa1b682ad8bdaabb |
| tools/security.py | 7222d74661a3238384f48a4142c250ee8035ac197ad27376f169473b37cb85e2 |
| tools/domain.py | 395a97df76f8d4f76233e5bd2a902db712b27b7873c23caed9c8cc19e85d44de |
| test_tool_mechanisms.py | 2256197b7b00de581e042abc15d9dc2f5f217adfafc8914ecfc9c6f875e1eecd |

The canonical repair uses the URL actually returned by authorization and derives Host from that exact URL before method/body/send processing; it does not relax origin/IP policy. Its twenty manifest consumers are identified. Saved standalone M39 passes its unchanged real-guard/negative-control assertion, separately from the original failed driver record. Preserve that bounded affected evidence with its own revision, timings and resource measurements.

The three subsequent repairs match concrete diagnoses: existing lossless json_value adapts reliable report Decimals to worker JSON; feed execution calls the actual existing GoogleFeedExtractor pure parser; failed-source test waits boundedly for terminal state rather than treating valid ok/running as completed success. Its error expectation is strengthened to source_error. Event/identity/rollback and price/evidence assertions stay intact. Three affected-only greens are acceptable offline evidence, not five-second stress results. The earlier suite's 800 passed/3 failed remains the truthful pre-repair outcome.

The 37 existing stress passes remain reusable evidence of their recorded invariants under their original identities; do not relabel them newly executed on the changed revision. Domain changes touch the changes/feed branches not used by those passes; the narrow canonical adapter change is separately identified, with preserved assertions and existing offline regression evidence. Carry provenance/affected dependency mapping rather than clearing the receipt or presenting a fresh 48-pass run. M39 standalone green and M43/M44/M47 focused greens must remain separate evidence categories; M40–M48 remain unexecuted under the stress driver. M11 remains blocked after its one repair, regardless of any full-suite pass.

Accounting: 44.34914476702397 prior measured seconds + 1.5163689469918609 diagnostic body seconds + 11.54725256600068 affected outer seconds = **57.41276628001651 seconds measured lower bound**. Fixture charge 9,104,041 + 94,344 + 194,780 = **9,393,165 bytes**, leaving **7,384,051 bytes**. Diagnostic interpreter/import startup is explicitly unmeasured; no saved bracketing upper bound is established by these artifacts. Therefore 120 minus the measured lower bound is only an upper bound on possible remaining time, not an authorized verified remaining budget. Do not invent a reserve, treat typical startup as a bound, or run further stress nodes on that subtraction. Preserve the uncertainty and stop expanding this experiment. No more timing probes are needed to chase a retroactive bound.

Next independent work: one mandatory full repository rerun under the existing explicit 180-second total subprocess ceiling is justified by the two production fixes and changed asynchronous terminal fixture. Save it as separate offline validation; stop on failure and record the exact blocker under the one-repair policy. This does not reset or borrow time for the stress experiment. Public live remains held until required offline validation/review prerequisites are satisfied. Missing bounded stress observations and timing uncertainty remain explicit limitations and cannot be silently waived by that suite rerun. Final completion still requires the independent implementation/evidence review; no feature-complete verdict is given here.

## Final implementation/evidence review (2026-10-16)

Reviewer: feature_reviewer. **Implementation verdict: CHANGES REQUIRED. Verification readiness: INCOMPLETE; epic must remain open.** Bounded static review of final critical runtime/egress/domain/store/protocol/source/schema paths, integration file manifest and saved evidence; no new tests, network research, probes, suite or live execution. This is an actual review with findings, not approval inferred from 803 green tests.

Critical reviewed revision identities:

| Artifact | SHA-256 |
| --- | --- |
| tools/runtime.py | 0d317b9f8fe22124854fea1fd5bfab701e536c52ef006daec8585fadbc026af7 |
| tools/security.py | 7222d74661a3238384f48a4142c250ee8035ac197ad27376f169473b37cb85e2 |
| tools/domain.py | 395a97df76f8d4f76233e5bd2a902db712b27b7873c23caed9c8cc19e85d44de |
| tools/execution.py | afc36d895e128d26707c5150cf5e9bf92108bd51c9a714cda9609c94e188fe51 |
| tools/jobs.py | 2d41456d84939957f499dd1513deff678694a6440b156d2e50b9a25cd53c0502 |
| tools/state.py | 837b2f0607c8a0ce838717964899078f791a3d64d5762474c76025ce61c69c2b |
| tools/mcp_server.py | 122b5db77abee480fff744e3eb66cc5f10449e38052aadd4211d399dc60a9a50 |
| tools/sources.py | 06c6621938da885fb4affa8e2b768abec63dd812887e9806102aaf0c4b533b67 |
| tools/contracts.py | 0bd9814b31d635fa645938b7ba7de9c9b6fe6d8dec3699bd26c1dfb7cd278cd5 |
| tools/schemas.py | 9bb44bd403dbe547d139d085d9ac5abff7f873811fe904450ca4a2c5f51edeb0 |
| tools/__main__.py | 244e047f6a964a39db76a36b7d60d5fb055604376751569a6bbe82c04a70ea1e |
| extractors/_storefront.py | dbe3e09f20dac8ee9a36e5e45b60a7389baaf78668a4f52958ea92e7449fc2c0 |
| extractors/shopify.py | 9eb2081e148f693b18d4ff0c3856cb12f8d867b892a1439fb6be0f8df3d41dff |
| extractors/woocommerce.py | 66f72e317fff6757d4c7ad1bdcc4414261f3033d2b6779aa77a152a271a338cf |
| docs/agent-tools.md | 2aafda271bb97cc35e2e1d7820ae5b38895035d205dd38501f7e1de06afb1b4b |
| examples/mcp_reference_client.py | 863c18e009e2f1488f8f6ceb99fc92e95fe3c39a919916daba25daca0ba72e7f |
| pyproject.toml | f73c6fc7c93f9b61a44f72420d38b60c9ef3bc56426f9859d60890e124aa99dc |
| .github/workflows/test.yml | 8bda17193162cef2bf4ae907c6474d404ab00ba1da0845a2c89e1488b315796c |
| final-full-repository-suite.json | c3f8847a87006aa2e21f9b9b0e85e43de91385398632d9962a4df5bd47551ac3 |

**F-01 — P1, OPEN: native credential headers cross allowed-origin redirects.** security.py:201–204 removes only authorization/cookie/host when following redirects. Shopware context GET carries sw-access-key (and supported native clients may carry sw-context-token/x-bc-customer-access-token/x-bc-customer-id). If an allowed source redirects to another separately allowed origin, those headers survive and are sent there. The guarded transport consumes the redirect internally, so `_storefront.request` never gets its opportunity to reject keyed cross-origin redirection. This violates FR08/09 and the Shopware amendment's explicit no-cross-origin-key promise. Enforce an origin-bound native-header policy at the shared transport boundary: reject keyed origin changes or remove every supported credential header before the redirected request; do not rely on the upstream helper. Design a controlled two-allowed-origin context redirect with secret canaries, exact initial request and zero forwarded credentials/target bytes as appropriate, including mixed header casing. Existing denied-origin tests cannot detect this because they stop before any allowed second origin is considered.

**F-02 — P2, OPEN: configured-capture bootstrap performs unbounded synchronous loading before admission.** runtime.py:132–147 calls load_snapshot, converts all products and builds the complete evidence graph synchronously before SessionStore.publish checks graph/session bytes. MCP read_resource calls this directly on the server event loop with no operation deadline/killable worker. A large or slow operator-granted snapshot can therefore exceed memory/time limits or block MCP cancellation/disconnect before the later 4 MiB rejection. Trusted path authority does not imply small stored data. Apply bounded preflight/streaming capture loading and a finite owned execution deadline before full materialization; charge temporary graph data under the existing session cap and preserve cleanup/error behavior. Design a real oversized persisted capture and an injected slow SQLite boundary, checking bounded resource_limit/timeout, responsive cancellation/close and no handles/reservations. Keep operator paths out of tool input/errors. This is an existing FR07/11 configured-materialization guarantee, not additional product scope.

F-02 interface obstruction: `bootstrap()->dict` is currently synchronous and directly consumed by async MCP `read_resource`; it cannot await the existing OwnedProcess lifecycle/context without blocking the event loop. Before implementing, review an explicit async/lazy bootstrap contract (including direct API/example callers), shared auxiliary-slot ownership, operation deadline and atomic partial-grant failure/cleanup. A raw SQLite byte/count preflight in the same killable worker can reject excessive captures before decoding their graph; moving the same unlimited load to a thread would not satisfy the reviewed cancellation/resource contract. This focused interface change needs affected G1/G2/G3 review, not a user approval flow.

Positive implementation findings: direct/MCP share schema/envelope dispatch, actual SDK framing and CallToolResult error flags; session handles authorize exact owner graphs; pages deep-copy immutable retained results; numeric TCP pinning retains origin Host/SNI; identity-only responses are rejected before decoding; actual resolver/domain work is killable with one shared auxiliary slot; job cancellation checks before terminal publication and dependency expiry revalidation; native algorithms/legacy defaults are reused. These strengths do not resolve the two uncovered paths above.

Evidence verdict: saved final repository run reports **803 passed in 169.29 seconds**, outer171.859 seconds within180. Five-native controlled integrations and genuine SDK subprocess flow are substantial offline evidence. Required bounded stress is still incomplete:37 historical driver passes, M39 standalone repair green, three focused offline greens; M11 timing-blocked after one repair; M40–M48 not executed by the stress driver. Unknown diagnostic-startup overhead prevents verified remaining experiment time, so no further stress expansion is requested. Ordinary suite success does not retrospectively satisfy those individual five-second stress cases.

The one actual public MCP discovery smoke timed out after three guarded raw attempts in18.12 seconds, peak4 processes. It proves a real attempted SDK/public path and structured timeout, not successful discovery/extraction/matching/evidence or actual-capture changes. Full public reference flow and inspectable captured live value/pointer assertions remain unobserved; do not call them passed or waive them because controlled fixtures pass. Original live receipt/time/request accounting must remain intact; no retry/site expansion is requested by this review.

Required remaining work: repair F-01/F-02 through predeclared focused cases and affected review; run justified affected regressions under explicit bounds; obtain independent verification disposition for missing stress/live evidence without resetting exhausted/uncertain budgets; complete actual mandatory public flow only under a valid reviewed bounded plan/receipt; then return for independent final rereview. Keep issue/child completion status honest and do not close the epic. If constraints prevent required verification, report that exact incomplete work. No commits/push/issue closure authorized or performed by this reviewer.

## F01 repair / F02 affected design review (2026-10-16)

Reviewer: feature_reviewer. **F-01 CLOSED after focused code/evidence review. F-02 affected G1 PASS, G2 PASS, G3 PASS for design; implementation finding remains OPEN until implemented and verified.** No tests, probes, new research or broad code reread in this bounded review.

| Artifact | SHA-256 |
| --- | --- |
| tools/security.py | 26f1862d98b211dced1e5be90925fda6ebb91075799e3474c7636cdb9cb788b3 |
| test_tool_redirect_credentials.py | 9d2239b619a8cbc058c2bad32256c369634176f2aa33b94d7f53a96c0c66b747 |
| f01-repair.json | 98488a40ff0e6a473a35fcd4370e50af786cf55069b87bb69b84e625b13f9260 |
| f01-green.log | 01c081b93c168d11ea4abe004be37ae842973308e592b42e7c5999e6b2d91da0 |
| spec.md | bd02929c67bd804e48922ad2ab73e6d3a7da633d83050ff4d828da222948fe0e |
| test-design.md | ea0af270d162bf66619e112c20c757a230a3216fed57fcd4aa6fd255e415db92 |
| skeleton.md | 94a613180f0a97267aa20658ab1e4742cdf80ea93346af94f93fcb7b8eb75590 |
| components.md | 43ac586c6eb28f56f166e60153116903deadb35646901dd95718fc7656e1a1c5 |
| plan.md | cee8dd05302458fee107d9bb4c6db19bedd9ca0b1fee03ddb8ec0ade475c0f9d |

F01: Exact three-line repair uses a safe read-header allowlist only when normalized origins differ, retaining DNS/pinning and same-origin native context behavior. Controlled actual TCP/HTTPCore cases exercise separately granted origins, initial credential presence, mixed casing, native/context/unknown credential removal and correctly rebuilt target Host; same-origin compatibility is independently checked. Saved red exposes the native-key leak; saved green is two passed in0.15s, bounded outer2.503s/15s. This directly closes the reported path; it is not a general live/security certification.

F02 G1: Public async bootstrap and safe error migration resolve the sync-interface obstruction while preserving granted catalog/capture/product/variant/evidence capabilities. Deadline starts before lock/admission; shared job/process ownership, conservative graph/session reservation, atomic exposure and attempt-only rollback specify failure behavior. B01–B08 cover real persisted normal/oversized/item/aggregate/locked/cancel/concurrent/legacy consistency boundaries with declared expected outcomes. These are focused repair checks, not reopening the closed stress experiment.

F02 G2: `async bootstrap(*, timeout_seconds=None)` is concrete and all direct/example/MCP consumers must await it. The worker preflight must cover every fetched selected text/blob, including legacy products_json, normalized product records, owner graph/reason, all evidence-record metadata/status/text and each referenced payload representation; an SQL numeric length/count result is permitted before decoded loading. The evidence_references table is not traversed by the existing loader; any new reader traversal must likewise be length/count bounded. Snapshot metadata newly read by the helper is also subject to the stated every-selected-value rule. Consistent transaction, incremental rows, finite busy handling and graph/item checks before decoding/materialization preserve the resource boundary. Oversize proof must instrument the real decoder/materializer boundary while leaving real SQLite/preflight logic active; a fake preflight returning resource_limit would not meet B02/B03. Shared slot and cancellation must use the existing owned worker, no second process pool/thread.

F02 G3: Narrow monitor.evidence bounded loading retains existing decode/trust semantics and legacy default loader behavior. Private materialization and per-attempt bookkeeping reuse existing jobs/process/store responsibilities. Mandatory consequence of the no-unrelated-loss invariant: private staging must not invoke normal store eviction on unrelated graphs; use non-evicting reserved staging/atomic admission and reject capacity before any unrelated handle is revoked. Each failed attempt removes only its own graphs/handles/reservations; close/cancel cannot publish a late cache. This is required by the reviewed atomic contract and B04, not an optional implementation shortcut. Worker IPC stays bounded per grant, handle collisions checked before admission, and no raw DB path enters results.

No design blocker remains; implement after saving normal/oversize meaningful reds, then the bounded <=45-second focused acceptance run and affected independent rereview. F-02 is not closed merely by these design passes. Existing stress/public-flow limitations and final feature verdict remain unchanged.

Future full-suite planning: the saved169.29-second base leaves little room under180 seconds for eight new process/SQLite cases. Before the next justified whole-suite run, an explicit **240-second total subprocess ceiling** with unchanged thread/process/log/cleanup limits is a reasonable finite amended plan; record it prospectively in plan/verification first. This review neither runs a suite nor changes the currently saved180-second evidence, and grants no stress-budget reset or automatic retries after timeout.

## Final F02 checkpoint — unresolved private-work cleanup (2026-10-16)

Reviewer: feature_reviewer. **CHANGES REQUIRED; F-02 remains OPEN.** One bounded read-only ownership-path check; no execution, repair, new finding expansion, commit/push or issue closure.

Reviewed runtime.py SHA256 `0757234d05406a66c7c83564b00743e41d04b4781e59ffd548d45b003dc0bf54`; jobs.py `759a182f309263ec924ae47d4d6a5078b0933f9bb78d8f51a371dfed0781e78a`; execution.py `ba460813e9e9fda2535629333b00488b915081e2b9504a8bc64faca0d65d42d1`.

Actual checkpoint: frozen B01–B08 produced seven passes and B05 failure, then the single diagnosed serialized/idempotent reap repair removed the closed-process race but B05 still fails. Cumulative focused outer time46.509374293 seconds of60. No second repair/retry is performed or requested within that exhausted-per-blocker repair allowance. Preserve both outcomes; seven passes do not make the focused suite green.

Precise resume path: runtime.bootstrap initialize awaits `shield(job['task'])` (runtime.py:171), outer `wait_for(initialize(), seconds)` enforces total deadline (192), and initialize finally calls `jobs.discard_private` (190). discard_private invokes cancel for a nonterminal private job (jobs.py:134–141). JobManager.run independently awaits `wait_for(work(), remaining)` and then marks terminal/releases reservation in its exception/finally path. JobManager.cancel can cancel that outer job task while the nested work task is already unwinding its timeout and OwnedProcess cleanup; shielding only the outer task does not establish ownership/join of the nested work cleanup. Serialized process reaping prevents double-close but does not itself prove that private work has finished before bootstrap returns. B05's observed worker still present at return is the remaining concrete contract failure.

Next single implementation target, if work is explicitly resumed with an appropriate bounded allowance: make JobManager retain and join its actual work task through cancellation/deadline cleanup, so private discard/terminal publication cannot finish before OwnedProcess reap and reservation cleanup. Keep the original enqueue deadline and <=1-second cleanup grace; do not weaken B05, add sleeps, drop the worker assertion, or start another worker. No additional investigation/gate is needed to identify the target. This checkpoint does not authorize another automatic repair/test cycle now.

Required checks after that correction: first B05/B06 focused deadline/cancel ownership assertions, then all frozen eight B cases under a prospectively recorded finite focused budget; only after green, the justified full repository run under the reviewed240-second total ceiling and independent final rereview. Preserve exact source/evidence ownership and atomic grant rollback expectations. The803-pass/169.29-second repository result predates F02 and is historical regression evidence, not a current-revision pass. No final full suite has run on this unfinished revision.

F-01 remains closed as previously reviewed. Stress remains incomplete (M11 timing block and missing bounded-driver cases, uncertain remaining time); public discovery smoke timed out and required public full flow remains unobserved. Neither a later eight-test green nor a full-suite green silently waives those verification limitations. Epic completion/final approval is withheld.

Checkpoint clarification requested by coordinator: the remaining JobManager task-ownership/join defect is a **distinct diagnosed root** from the already repaired OwnedProcess concurrent-reap/closed-handle race. The former can return while nested work cleanup is alive even when each process reap is perfectly serialized; the latter corrupts concurrent calls on the same process object. Do not repeat or broaden the process-reap repair. Exactly one narrow correction to the owning JobManager component may therefore be treated as an independent blocker within the existing remaining focused allowance, not a second attempt at the same reap fix. This distinction supersedes the checkpoint's general prohibition only for that specified independent root; it adds no user permission requirement.

Minimal correction target: retain the concrete work task created for each job, cancel that owned task once, and shield/join its cleanup before terminal state/private discard completion; bootstrap outer cancellation must not detach that join. Preserve the never-started-task handling without treating every CancelledError as proof that no work began. Required first test pair is the unchanged B05 real locked-SQLite deadline and B06 explicit bootstrap cancellation/disconnect. They target natural timeout and external cancellation independently. Use one sequential runner with an outer ceiling no greater than the remaining **13.490625707 seconds** (60 minus46.509374293); stop and record if the pair cannot finish. No test is run by this review, no fit is promised, and no focused-budget reset is granted. The full eight/current-revision regression requirements remain; if they cannot be completed within available reviewed bounds, report their exact pending status rather than silently extending the phase.

## Final narrow code rereview — F02 closure (2026-10-16)

Reviewer: feature_reviewer. **Final CODE verdict: PASS for the reviewed implementation with F-01/F-02 closed. Verification readiness: INCOMPLETE; epic not complete or merge-ready under required verification contracts.** No tests, new research, probes or expanded coverage executed in this rereview. Scope is the previously identified F02 blocker and its reviewed amendment, not a new whole-project audit.

| Current artifact | SHA-256 |
| --- | --- |
| tools/captures.py | d19a89547aacebf0b0e4021d28d2e5def8b196e98da685f4a862881255e16fd6 |
| tools/runtime.py | 0757234d05406a66c7c83564b00743e41d04b4781e59ffd548d45b003dc0bf54 |
| tools/jobs.py | a4b6e3931037d7a5bd0ccf9817ed202c2929879208080e66f659da1625186423 |
| tools/execution.py | ba460813e9e9fda2535629333b00488b915081e2b9504a8bc64faca0d65d42d1 |
| tools/state.py | 9c0aa94727cddbe6932887684464fffd45d25c1aa4bce6a1fbff818dc1510a4b |
| f02-repair.json (complete thirteen-file manifest/diff references) | 8c26c6627785bac853eb00e044ddacc194831fdf6eada3e9354d14b4fba94326 |
| f02-final-full-suite.json | c8d11f5695f61b75e246480f1745ff6074eb17cf56237b0ca63116f56c06af2e |

F02 resource path now runs read-only SQLite in the existing owned worker. Numeric length/count preflight precedes product/trust decoding and traverses all selected snapshot/product/owner/evidence/reference tables, charging referenced payloads conservatively. Read transaction consistency, item checks, incremental graph construction and graph/IPC/session bounds replace unrestricted event-loop materialization. Default legacy loader behavior is retained through the narrow existing iterator seam. Public bootstrap is async; finite lock/admission waits and await migrations preserve configured capture/catalog/evidence capabilities.

Private jobs reserve staged graph bytes through the existing job slot and expose no handles before batch commit. publish_batch validates count/graph/collisions before its non-awaiting commit and never evicts unrelated graphs; attempt failure discards private reservations rather than clearing unrelated catalogs. Constructor performs no capture loading. Cached grants return copies after lifetime validation.

The distinct JobManager correction retains the concrete nested work_task, waits on its shield, cancels owned work on deadline/cancellation and joins it before terminal publication/reservation cleanup/private discard. Repeated outer cancellation cannot detach that join. Combined with serialized/idempotent owned process reaping, this addresses the B05 worker-presence-at-return defect rather than weakening the test. Saved unchanged B05/B06 outcomes are two passed in1.18s, outer3.724s; cumulative focused50.233 seconds remains below60. No further code blocker remains from this review.

Current-revision ordinary full repository evidence is **813 passed in201.61 seconds**, outer204.253 seconds within the prospectively recorded240-second ceiling, with all eight F02 cases, F01, real MCP and legacy regressions included. Saved log/resource/cleanup limits remain explicit. Earlier803-pass evidence stays historical; current813 result is not attributed to the old revision. Root diff-check is separately reported saved/pass; no commit/push/issue closure is implied.

Open verification items remain exactly the recorded ones: bounded stress incomplete (37 historical driver passes, separate M39 green/focused evidence, M11 timing-blocked after one repair, M40–M48 not driver-run), unknown startup overhead preventing verified remaining stress time, and actual public live limited to a three-request discovery timeout without successful full discovery→extraction→matching→captured-evidence/changes observation. Ordinary813-test success does not waive or retrospectively pass those requirements. Preserve receipts and do not restart/expand closed experiments under this verdict. Required missing proof needs an explicitly bounded valid continuation disposition; absent that, hand off the feature as implemented/offline-verified but verification-incomplete, keeping the epic open. No additional code investigation or new engineering gate is requested.

## Discovery timeout D01/D02 affected review (2026-10-16)

Reviewer: feature_reviewer. **Affected G1 PASS; G2 PASS; G3 PASS**, reviewed in that order. Narrow behavior/test/interface/reuse inspection only; no new tests, research, full-code review or live requests. Production repair/green verification remains next.

| Artifact | SHA-256 |
| --- | --- |
| test_tool_discovery_lazy.py | 35aaf6eb148623ab2bcb075208f0ac5b2d01f51727c9af61908b0c30434bd759 |
| spec.md | 160e102b986149b71f632686cc79fc0e5039245ab5940721878fea160f526053 |
| test-design.md | cf4fedb12b1342ebcb6649358f172249551c81601320b5db3216c7b4d64ac080 |
| skeleton.md | 81baab8f9d5f3b029cc827f33bdc11e49b52891ae014aa3340438f56e7ba29a5 |
| components.md | 1652dc9f17a153d36aefa4ebae506052bcd2028f17d974e1a971a2299bbea61a |
| plan.md | 04bf88c309090f85ed2d323c3a4ac450cf725f79a68d412488008034b3bad585 |

G1: Lazy FIFO URL dequeue fixes the diagnosed unnecessary sibling fetch while preserving observable result order, authority and truthful capped completeness. D01's real later500 sentinel proves that an irrelevant failed sibling cannot erase an earlier sufficient result; exact two-request assertion detects eager work. D02 independently preserves empty-child handling, denied-link diagnostics, duplicate/cycle suppression, unique product order and the shared three-request cap. They exercise actual GuardedSources/parser/guard with only external resolver/wire fixtures injected. The saved representative red is reported one failure/one pass in0.28s, outer2.659s; no successful repair is inferred yet.

G2: Existing discover signature and operation context remain unchanged. Queue entries represent normalized child URLs plus optional root text; fetch only a dequeued URL, and return immediately on requested unique-item cap. Keep candidate authorization and transport-time current DNS/redirect pinning active; queued identity is not durable address authority. Unvisited siblings are not errors or claimed exhausted coverage: completeness remains false at cap. No timeout inflation, broad exception swallowing or API migration is introduced.

G3: Only the existing GuardedSources traversal owns this change; existing sitemap parsing, normalization, guard/client and cumulative budgets remain authoritative. No new queue framework, dependencies, model/worker engine or native-extraction scope is added. Proceed with smallest implementation and focused affected checks within the prospectively recorded45-second budget, charging the existing red/setup evidence. No prior stress/live receipt or historical813-pass result is reset/relabelled.

A later explicitly authorized retry has a distinct90-second/eight-request ceiling on the same reviewed public target after offline green/review, using the existing default30-second job deadline. This design review does not execute that retry or assert the timeout is resolved live. Required verification gaps remain until actual saved observations satisfy them.

## Discovery timeout fix — final narrow review (2026-10-16)

Reviewer: feature_reviewer. **PASS; close the requested discovery timeout/unsupported-leaf fix.** No additional execution, research, full suite or live request during review. Scope is the minimal source/test diffs and compact saved outcomes; original epic verification limitations remain separate.

| Artifact | SHA-256 |
| --- | --- |
| tools/sources.py | 55c12019dd0dfc29fd3d2d7b70604bb323d80930a4b098274f72efa3232aab4c |
| test_tool_discovery_lazy.py | 57ab15d20ccf1d061d62f41c33038ff14c155091a14daddb91ba8fcff4351635 |
| discovery-lazy.diff | 50425c4ac1fd412e8c9fe853f67b2066d132e7c0f25dd8ad4bd20125fa329c6d |
| discovery-eligibility.diff | 36c0b420ceee339dd5f9d93c888fe73c012e201bc45909c2a477462a8c73d1c6 |
| discovery-eligibility-green.json | a8087404aa06d9becbbadfe6b2e56f0358acc682ff9ceb39b3321c3647e70bc8 |
| postrepair live smoke-result.json | c285414945f91cca4558e9e38b2c36c22dd327b25353d2abf09285a9b2ce9aa4 |

Actual change is confined to GuardedSources.discover: pending maps are FIFO URL/text entries, nested fetch occurs only on visit, and maximum unique eligible results returns immediately without DNS/HTTP for irrelevant queued siblings. Duplicate/cycle identity remains normalized; actual dequeued requests still cross original current-DNS/redirect/pinned transport authority. Permission denials produce diagnostics, while genuine backend/parse/resource/time failures are not silently swallowed. Unsupported known .md/.markdown/.txt/.pdf leaf suffixes are checked on the decoded case-folded path, excluding query strings; supported HTML/XML/CSV/native and unknown dotted slug inputs remain eligible. No new dependency, timeout ceiling inflation or unguarded transport was introduced.

D01/D02 and E01/E02 have genuine pre-repair failures and concrete expected request/result/diagnostic assertions. E01 distinguishes an agents file from a supported source; E02 checks case/query boundaries and supported modes. Saved affected result is eight passed in11.67 seconds, including real SDK subprocess/domain/guard consumers; cumulative focused33.523 seconds stays within45. This is the current affected verification, not a new current full-repository run. The813-pass suite predates this discover change and remains labelled historical.

Public outcome after the one eligibility repair: genuine SDK stdio discovery with original GuardedTransport/PinnedBackend/default resolver succeeds in14.219 seconds with three raw attempts, default30-second job deadline and peak4 processes. Returned URL is `https://www.blissworld.com/`, a valid allowed shop/catalog extraction input under FR03; it is not represented as a product-detail page or proven extracted catalog. Known agents.md is skipped, not fetched. Earlier new-window smoke returned agents.md in11.755 seconds/two attempts; aggregate new authorized requests are five of eight. The initial old15-second discovery timeout and all prior receipts remain preserved. The saved separate retry phases are explicit rather than relabelled continuous elapsed time or unlimited retries.

The reported discovery timeout now has a concrete minimal mechanism repair, focused greens and actual public discovery success; no further probing is needed for this user fix. It does not guarantee arbitrary sites/network latency or complete the epic's public extraction→matching→evidence/changes flow. Historical bounded-stress gaps, M11 block and uncertain old experiment remainder are unchanged. No new tests, suite, gate, public request, commit/push or issue closure is requested by this review. Hand off the timeout fix as reviewed while keeping epic completion/merge readiness dependent on its separately recorded missing proof.

## Independent actual live-data audit (2026-10-16)

Reviewer: feature_reviewer. **PASS for the bounded real-data/full MCP flow observed: two products from one supplier.** Read-only inspection of saved actual response bodies, MCP extraction records, exact driver/audit assertions and budget/cookie/capture receipts. No new network, tests, models, key access or full suite in this review. This supersedes the earlier public-flow-unobserved limitation only for the specifically observed sample below; it does not complete the epic's outstanding stress proof.

| Artifact under live-data-verification/ | SHA-256 |
| --- | --- |
| summary.json | fd6fd55a9e5f123104fdc996ec12285a06e543888a0b047eb655e43a60c73fbd |
| data-audit.json | 219623ab5b7b3aba9f84815d18fe10b82375612ded072be505ae23a595464b61 |
| receipt.json | 728e713249b586c3a05c66e870e63213502f203be4eedb6c93a21d0388a8cb66 |
| currency-cookie-proof.json | f4fc8e60f5fc8371eab08f2aa6d628401f90a95badfcc55164107f057ee849e0 |
| run.py | 6dc903b334e0df629aefa1ebbd0e3ef3d18b894af1ccbc384c8b66c1d5a9ac01 |
| http-05.body | 06e56c83039c441787c0f4ec6e0b26f53b28e4efda80c3f5b14051219befbbc5 |
| http-07.body | 8c81603d239cc9846b7a5f9fec1e85f37b4e8e32876ebf5fe018f4d334d946bd |
| actual-captures.db | 867c0babdb71a2a57fff1c27224d716d1e84eb81a286fb4dd682c13f7b32aab0 |

Saved raw Shopify data agrees with the two MCP product records: Bliss Halloween Costume price65.00, SKU0585-0057003, variant67743111872797; Salmon DNA Duo price55.00, missing SKU, variant67705008455965. Both raw variants explicitly available=true and normalized stock remains observed true. Titles, source handles/product URLs, variant IDs/prices/SKUs and counts are checked against actual raw records by external ID, not invented expected product output. Both absent barcodes remain GTIN null/unsupported, and second SKU remains null/unknown. These distinctions are materially verified rather than hidden behind scalar defaults.

USD support comes from the actual products response cart_currency cookie projection. Driver observation calls original guarded HTTP handling before saving response bytes and reading only that cookie value; the proof binds it to the same URL/body hashes and `/cart_currency`. Normalized currency is observed USD, not an inferred USD default. Other cookie/session/header contents are not retained as evidence. No GLM/key/model was needed.

Actual supplier-scoped catalog matching returns exactly pairs(0,0) and(1,1), relation exact. Reasons are agreeing canonical/external IDs, plus SKU for the first product; no GTIN match or cross-supplier identity claim is made. The inspected price lookup retains value65.00, pointer `/value`, source pointer `/variants/0/price`, and the actual products.json source URL. The driver asserts that evidence through a different actual product owner returns not_found; unsupported-version returns unsupported_version. Dispatch/retrieval remain real.

The SDK launches actual stdio server processes with original GuardedTransport/PinnedBackend/default owned resolver. Observer wrappers count/capture original I/O and record original domain graph output; they do not supply fake responses or algorithm answers. First two-product extraction was saved before expansion at22.626 seconds. Whole flow41.441 seconds, outer41.807 below120, seven of16 raw requests, peak4 below5. Both extraction samples and portable graphs are retained. An operator save of those actual portable records creates two real partial snapshots; a second actual MCP server bootstrap/changes call compares them and returns zero events. That is honest actual-capture integration evidence, not proof of full-catalog unchanged state or a commercial transition.

Bounded actual discover→extract→match→evidence and configured-capture changes observation now passes for this sample. No additional site/item/variant coverage, adversarial live behavior, cancellation replay or production scale is implied. No code changed during this live verification; prior813-test suite remains historical to the discovery change and its eight affected greens remain separate current focused evidence. Historical stress is still incomplete:37 driver passes, separate repaired/focused evidence, M11 timing block, nine M40–M48 not driver-run and unknown old timing remainder. Do not reset those receipts, claim48 stress passes, close the epic or infer overall merge readiness solely from this successful live sample. No further execution or investigation is requested by this audit.

## Current-revision delivery verification/packaging readiness (2026-10-16)

Reviewer: feature_reviewer. **PASS to execute the separately planned current-revision delivery verification once under declared bounds.** No execution, new research or whole-code rereview in this review. User's explicit PR/merge/ticket delivery request justifies obtaining missing current-revision evidence; this is not a reset/resume or reinterpretation of historical failed experiments.

| Artifact | SHA-256 |
| --- | --- |
| delivery-plan.md | 108d9c85e796e28a30663e9125d6fbc514b1939c8df28d923061b845da30983f |
| delivery-driver.diff | ab047e3bc3157ae01578879dc5aaeb3632f09e07fd5c724f3a137b7fc213ad04 |
| run-delivery-mechanisms.py | c72986075633562417d1ed057db6a106644ce54f134573b9e5d569ed7af8bb33 |
| delivery-inventory.json | a8d9e43ab5d7e54a49d67de06e2c237f0246bdf96543a1a8d5464c2925ea751a |
| delivery-files.json, proposed allowlist | b366c3de6de957e7c9096795df84f33a06c538c78ce0441349535cdd6ef41769 |
| delivery-preflight.json | 9c5abbbdf56c9eb8e4b6ec378b209a731852a48833c294f3573981c73733d0c2 |

Delivery manifest contains the same48 reviewed concrete nodes in the same order/seed24; no old pass carry or M11 skip remains. Prospective15-second individual ceiling is finite and justified by measured roughly6-second existing process/schema flow, while whole180-second bound prevents a multiplied720-second sweep. Assertions and production timeout/SLA remain unchanged. Module-start timing now charges imports/setup; final timing overflow records a failure before successful completion. Resource-failure-before-save, exact source/test/helper/self/environment identity, actual fixture ledger, blocked violating resume and all-exact-nodes success checks remain inherited from the reviewed driver. Fresh delivery paths isolate old receipts and preserve their failure history.

Preflight fixture bound14,490,163 bytes is below16MiB; actual ledger still decides the executed result. AdditionalRSS256MiB, five total processes, one active worker, numerical threads2 and <=1MiB log remain declared. Execution must use the plan's external180-second total subprocess watchdog with owned-process-group cleanup, including interpreter startup/final accounting, and record its actual outer result; driver-only elapsed measurement is insufficient to replace that outer bound. No models/public requests are part of this run. Stop on first failure and do not reset cumulative consumption to repair/rerun automatically.

Proposed88-file delivery allowlist is scoped to feature code, affected legacy seams, tests, docs/specs, CI and small reproducibility/native evidence. The small actual JSON bodies, portable records and cookie projection preserve inspectable live proof; large HTML/raw session headers/SQLite databases and unrelated workspace material are excluded. This is packaging scope approval, not a claim that every unseen local file is safe to stage. Use the explicit allowlist, refresh changed review/status/evidence hashes before staging, and add only the resulting bounded delivery receipts/logs deliberately. Do not stage directory-wide unrelated artifacts or credentials. Existing author identity, neutral branch/commit/PR naming and no unsolicited labels remain required before push/PR.

Actual48-case success is still pending and must be inspected before changing completion/merge-readiness claims. A fully passing current run may satisfy the previously missing bounded mechanism proof while leaving the old five-second experiment accurately historical. Previously audited two-product/one-supplier real live flow remains bounded evidence, with no commercial-transition/full-catalog claim. No additional user approval is required for the explicitly requested PR/CI/merge/ticket actions once required checks and final receipt disposition support them; this review neither executes nor pre-approves an unobserved failing result.

## Final delivery-result audit and merge readiness (2026-10-16)

Reviewer: feature_reviewer. **PASS: current implementation and required bounded mechanism/live evidence are ready for PR delivery, with merge subject to required GitHub CI on the exact clean PR tree.** No tests, publication, commits, research or additional scope executed by reviewer.

| Executed delivery artifact | SHA-256 |
| --- | --- |
| delivery-summary.json | 64fbdf64028f097d6af36bf967ac80525cb80272b4943c506373296c456e12ae |
| delivery-progress.json | 42d23424472d4babfa4e94a4d6142a1e9e8c77394fd75bb894933798b2bbfd41 |
| delivery-outer.json | 9d523b6face5da0d1f881a78c65be2499548bcd0e2c633a7c752e678b5fc8777 |
| delivery-run.log | 5b7a746a8e94bd6e1fc2e27d1b056ce711ffbb4e2c1642c6dfd98b4df75adcc1 |
| delivery-files.json, before this review append | 93cb14ef78d781c61bd797b0908af050be13d7e6ee5cfd261a548f189b805caa |

Inspected actual progress: all48 exact manifest node IDs match, every status is passed, seed24, revision `8ce4633ae8aec574cd71f53cb21f344523a7ea8da08ca5a7b0f45bc7685d6504`, no prior revision or carry-forward review, no resource failure. Saved131-file source/test/helper identity has no content mismatches with inspected current files. Driver53.415 seconds and external whole53.752 seconds are below180; fixture9,408,848 bytes below16,777,216; measured additionalRSS252,899,328 bytes below268,435,456; measured peak3 processes below5. Outer exit0/no stop reason and owned-group cleanup are recorded. This is a fresh current48-case pass, not skipping M11 or treating old passes as new evidence.

The CURRENT bounded mechanism gap is therefore closed, including newly executed M11 and M40–M48 under prospectively reviewed15-second cases. Historical five-second M11 failures, earlier incomplete receipts and diagnostic timing uncertainty remain truthful historical records; they need not be erased or claimed retroactively passing. Existing independently audited actual live SDK flow verifies two products/one supplier in41.44 seconds/seven requests, raw-source field and cookie-currency support, matching/owner evidence and actual partial-capture changes. Commercial transition/full-catalog completeness and unlimited scale are not claimed; these sample limits do not negate the specified bounded acceptance proof.

Packaging manifest contains92 listed files plus the manifest itself (93 delivered files), consistent with excluding unrelated/large HTML/SQLite/session material. Refresh review/status/evidence manifest hashes before selective staging. The reported two pre-existing local workflow/reliable-stress commits must not be accidentally included or rewritten: coordinator's plan to cherry-pick only the new feature commit onto a clean origin/main delivery worktree preserves unrelated history. Reviewed MCP source/test bytes must remain unchanged through that transfer; required GitHub CI must validate the actual clean PR tree/dependencies. A local pass on a different base cannot substitute for that CI.

No unresolved code finding or CURRENT required mechanism/public-flow evidence blocker remains from these reviews. Proceed with the user's authorized selective commit/push/PR, required CI, merge and truthful ticket updates once CI passes. Do not mark merged/close delivery tickets before those operations actually succeed. Neutral Git/PR naming, configured author identity and no unsolicited labels remain in force. No additional user approval or new engineering gate is requested. This audit is merge readiness conditional on required CI, not a statement that a PR is already merged.

### Author response MC-01–04, CI and process count (2026-10-16; rereview pending)

MC-01: Canned dispatcher and destructive-cancel replacements removed. Owner control remaps only actual SessionStore.lookup owner scope while real dispatch/evidence retrieval execute. Redirect control changes only guard.origins for one otherwise-public target while real DNS/redirect/send execute. Terminal control AST removes exactly one post-operation cancelled-event guard from an in-memory JobManager.run copy; same cancellation-loser/no-graph invariant must fail. All scope/branch mutations restore in finally. Recipes/outcomes were saved in test-design before fixture edits; controls not executed during this repair.

MC-02: Replaced/merged weak cases without exceeding48: cancellation-catching late domain result + surgical publication control; real incomplete persisted capture replay with no removal promotion and stable diagnostics/report identity; real extraction page→actual /price evidence→TTL expiry→tool expired→restart not_found; actual matching held after real worker computation until dependency TTL expires, then failed/expired/no publication. Existing exact earlier risks retained or explicitly listed outside-run in corrected inventory; no planned result marked passed.

MC-03: Every concrete row now has a manually enumerated exact mapping and expected outcome, no blanket FR/SC/R ranges. Renamed oversize metadata case to avoid claiming copy-isolation coverage. Inventory explicitly separates saved genuine MCP/regression evidence and still-required protocol cancellation/error/CLI/fullsuite/live/final obligations.

MC-04: Driver identity includes itself/build script/all local helper scripts, complete production/test Python source trees, selected static JSON inputs, manifest/config and complete installed-distribution versions. A changed revision invalidates passed-case reuse while preserving consumed time/fixture bytes. Runtime ledger records actual HTTP/stream/wire fixture bytes, full graph construction/publication representations and generated tmp fixture files; static inputs separate. Conservative preflight bound14,490,163 bytes <=16MiB; per-case and cumulative measured bytes enforced and saved, not merely declared. RSS/log artifacts tracked separately. No stress run executed. Collection-only:29 functions in0.19s; manifest48 cases.

CI plumbing: Python3.10–3.12 jobs install dev,mcp, require SDK import and separately block optional SDK import for direct API compatibility; jsonschema remains explicit dev dependency. CI not executed locally.

Counted process clarification requires affected review: a single12-second-ceiling controlled observation measured actual peak5 (client+caller tracker+server+server tracker+one auxiliary worker). Post runtime/server close snapshot retained only client+its interpreter-owned tracker, zero auxiliary workers. Exact PID/role receipt saved process-inventory-probe.log; no inference/public requests. Current declared process budget is5, including support trackers; auxiliary worker cleanup remains <=1s and shared caller tracker is not force-killed by library runtime.close. Trackers count in actual driver process/RSS receipt. This supersedes historical3-process estimates; no new parallel job/model launch.

Original changes-required verdict remains until separate rereview. No broad green tests rerun, stress/fullsuite/live/commit/push/issue close during this repair. Current branch tool-api-mcp-server.

### MC-04 final driver repair — author disposition (2026-10-16)

Resource observations now finalize a row as failed_resource/exit resource_limit with explicit RSS/process reasons BEFORE receipt persistence. Failure history survives final checks and resume; a legacy all-passed receipt with violating global peaks persists an unattributed saved-resource barrier and exits, preserving consumed seconds/bytes. Final success checks every exact manifest node and zero current/historical resource failures, including final monitor observations after shutdown. Digests/budgets remain intact.

Predesigned pure driver-state regression uses synthetic48-row runner results and injected observations, never mechanism execution. driver-state-regression.log:4 passed in0.06s (RSS-final-case overflow, process-final-case overflow, legacy violating resume with unchanged budget, exact all-node/zero-history success predicate). No source behavior changes, stress/fullsuite/live/research or broader green rerun. Independent MC-04 rereview remains pending; prior MC01–03 and numerical process-budget gate verdicts stand.

### M11 bounded timing blocker — carry-forward review requested

Reviewed driver first10 cases passed, M11 timed out; one diagnosed schema-validator cache repair retains exact draft/schema checking and all response/mutation assertions. Isolated affected retry still exceeded5s. Exact helper old/new digests/14 consumer nodes and before-source in validator-cache-repair.json; old receipt SHA verified unchanged. No second repair. Additive charge19.207896666004647s/271962 fixture bytes (including retry setup/actualfixture counts and measured audit diagnostic), preserving original failed attempt/history. Review semantic-equivalent cache and which M01–M10 results may carry before any resumed driver or full suite. No pass/permission inferred for the timing blocker.

### Author response F01/F02 — affected review requested, no verdict claimed

F01: reproduced real allowed-origin wire leak with mixed-case native and unknown credentials, then cross-origin safe read-header allowlist repair; same-origin policy explicit. Targeted red/green artifacts f01-repair.json and tests/test_tool_redirect_credentials.py; original Host/DNS/real HTTP framing exercised.

F02: no production change. Canonical async bootstrap and worker-first preflight/admission/atomic-grant cleanup contract in spec.md, affected interfaces/components/plan and B01–B08 in test-design.md. Preserves all owner/evidence grants, proposes finite private materialization operations through existing job/worker slot and narrow bounded SQLite reader. Request affected G1/G2/G3 review before implementation; no author assertion of pass.
