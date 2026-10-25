# ShopExtract CLI business skill architecture

Date: 25 October 2026. This design binds merchant and shopper workflows to the completed local CLI on `cli-feature-parity`. It supersedes the earlier MCP-first and missing-CLI-adapter assumptions. The existing CLI is the execution interface; skills provide business procedures and interpretation. MCP is an optional separate host interface, not a dependency of these workflows.

## Verified foundation and design scope

The [completed CLI report](../011-cli-feature-parity/status.md), [final independent review](../011-cli-feature-parity/p5/reviews.md) and configured gate receipt establish local completion: 35 root families, 70 executable commands, 85 grammar entries, 17 packaged schemas, and 1,595 tests on Python 3.10.11. The repaired fresh configured gate passed in 419.517006 seconds; the earlier timeout remains historical evidence. Wheel/SDK/stress checks passed within their recorded scope. Publication and other Python versions remain separate.

The 21 previously audited capability groups are the product foundation. Merchant and shopper jobs come from [the bounded forum research](forum-discovery.md). This architecture specifies proposed skills, orchestration and acceptance; CLI completion does not prove that the proposed skills or their host workflows have been implemented or evaluated.

## Two entry points and eight task skills

The two entry points are `/shopextract:merchant` and `/shopextract:shopper`. They resolve the operator's objective, source scope and constraints, select a small workflow, and compose the final report. Eight internal task skills hold reusable procedures. A single foreground Claude session can invoke them sequentially; task skills do not require separate model agents.

```text
merchant question                     shopper question
       |                                     |
merchant entry skill                 shopper entry skill
       +-----------------+-------------------+
                         |
        bounded plan with declared skill dependencies
                         |
            selected internal business skill
                         |
      proposed typed runner -> actual ShopExtract CLI
                         |
     native domain algorithms / captures / local databases
                         |
       proposed result and evidence validation
                         |
          business findings -> saved decision cases
```

The proposed runner is small deterministic orchestration code, not another extraction framework. It launches the installed executable with an argument array, captures bounded stdout/stderr and exit status, validates command/output contracts and saves checkpoints. It never converts source content into shell text, arbitrary flags or Python callbacks. Cross-skill decision cases require a new small persistence contract; native snapshots and maintenance jobs are already durable and should be reused.

## Skill to command bindings

All names below are actual CLI paths from the delivered guide. `binding_status` means that the native commands exist; it does not claim the skill recipe is implemented. Exact input shapes and option arity come from installed capabilities and schemas, not guessed command names.

| Internal skill | Business result | Existing CLI bindings | Remaining mechanism or input gap |
| --- | --- | --- | --- |
| `offer-compare` | Exact comparable offers, exclusions and merchant price-review candidates | `extract`, `match`, `match-pair`, `identity inspect`, `competitive position`, `evidence inspect`, `resolve` | Decode native money/evidence; report original amounts. Native position/statistics are approximate floats. Exact derived financial metrics, unit conversions and destination-aware totals need reviewed deterministic calculations/inputs. |
| `deal-check` | Current offer versus known observed history | `snapshot-save`, `snapshot-load`, `history`, `changes --reliable`, `evidence get` | Requires actual compatible history and a defined evaluation window; no invented history, future-price forecast or fraud verdict. |
| `basket-plan` | Feasible one-store/split-store shopping options | Acquire offers with `extract`/`feed`; `match`, `match-gtin`, `categories map`; compose `offer-compare` | New deterministic basket solver plus delivery/quantity/location/substitution constraints. Existing price comparison alone cannot optimize a basket. |
| `alternative-find` | Exact offers separated from variants/substitutes and scoped assortment gaps | `discover`, `extract`, `match --method identity`, `match-gtin`, `competitive gaps`, `competitive brands`, `categories map` | Wider-web discovery and authoritative equivalence inputs are separate; title/GTIN candidates are not automatically accepted exact matches. |
| `spec-fit` | Meets/fails/unknown against user or category requirements | `resolve`, `evidence inspect`, `categories extract`, `categories policy inspect`, `categories policy review`, `categories tree link` | Native policy review handles supported profiles. Arbitrary user requirement predicates, installation constraints and compatibility proof need typed rules/authoritative inputs. Tree linking uses captured same-scope memberships only. |
| `catalog-reconcile` | Supplier-backed corrections, defects, conflicts and unresolved cases | `normalize`, `quality`, `duplicates`, `maintenance create/run/resume/status/report/evidence`, category policy commands, `export` | CLI maintenance is already integrated. Arbitrary supplier XLSX/PDF parsing and saved column mappings remain additional input adapters. Corrections stay advisory. |
| `channel-diagnose` | Implemented-rule failures or supported feed/channel discrepancy | `validate`, `images check`, `export`, `evidence sidecar create/load`, `identity inspect` | Actual submitted-channel diagnostics, sync settings and account state require supplied evidence or authenticated integrations. Local validation is not marketplace acceptance. |
| `market-watch` | Material price/availability/assortment changes with before/after support | `snapshot`, `snapshot-save`, `snapshot-load`, `history`, `changes --reliable`, `watch`, `evidence get` | A schedule/notification adapter is separate and only configured on request. Native watch events are unverified scalar candidates; confirmed reporting uses reliable changes. |

The [machine-readable skill bindings](cli-skill-bindings.json) map these eight skills to 38 verified existing command paths; the manifest is design data, not executable runner configuration.

No new ShopExtract commands are invented for the unimplemented calculations, solver or runner. Their future code can be small reviewed scripts using declared JSON contracts. Until then the skill returns `capability_unavailable` for that subtask, or provides a narrower result that still satisfies an explicitly scoped question.

## Business workflow recipes

### Merchant pricing review

Inputs: own and competitor sources or existing portable catalogs, explicit market/currency/variant constraints and optional cost policy. Known competitor domains are sufficient for the first recipe; broad competitor discovery is not assumed.

1. Acquire at most the planned products from each granted source, or reuse applicable files.
2. Align identities with `match --method identity`; preserve relation, conflicts, ambiguity and review states. Price comparisons use only accepted exact relationships satisfying variant/currency/context checks.
3. Inspect captured field support and resolve freshness/authority when needed. A default currency or constructor price is not an observed offer.
4. Return original exact amounts and supported comparisons. Use native position aggregates only with their documented approximate nature; an exact percentage or margin requires an implemented deterministic calculator.
5. Create review cases with evidence and exclusions. Without costs/fees/policy, suggest review rather than a profitable price or automatic price change.

Illustrative invocation using documented commands, after grants and bounded plan are established:

```sh
shopextract --output-format json extract https://own.example --max 1 --timeout 15 --output own.json
shopextract --output-format json extract https://competitor.example --max 1 --timeout 15 --output competitor.json
shopextract --output-format json match own.json competitor.json --method identity
shopextract --output-format json evidence inspect own.json --view trust
shopextract --output-format json evidence inspect competitor.json --view trust
```

These are plan examples, not executed observations. Limited store extraction may retrieve nonmatching products. Save the truthful unmatched outcome; use known product inputs or a separately bounded discovery step when exact-item selection is needed. Do not fabricate a match to make the pilot succeed.

### Shopper exact offer and deal review

Select model/variant requirements -> `offer-compare` -> `spec-fit` only if needed -> `deal-check` only when applicable history exists. Order comparable known item prices separately from delivered totals. Unknown destination/fees/eligibility means delivered total remains unknown. A requirement-based shortlist must retain unknown attributes; no universal best-quality or durability score follows from catalog data.

### Supplier update and channel readiness

Supported input -> `normalize` or native portable load -> `quality`/`duplicates` -> `catalog-reconcile` through a native maintenance goal -> bounded `maintenance report`/`evidence` -> optional category policy review -> `channel-diagnose` with `validate`. Run `export` only when an artifact is requested, preserving required companions. Arbitrary CSV/XLSX/PDF supplier input is not automatically valid normalized JSON or a recognized feed.

The native maintenance goal defaults to description; explicitly select supported fields/profile and applicable category policy. Create/run/resume persist local advisory state; they do not update a merchant. Cancelled jobs cannot be resumed: report native state and require a new goal where appropriate. An incomplete supplier sample never confirms discontinuation.

### Market changes and saved shopping lists

For compatible history, use explicit snapshot IDs/database and `changes --reliable`, optionally with supported recheck. For fresh captured portable records use `snapshot-save` with metadata derived from actual scope/completeness; imported metadata is an operator assertion, never fabricated complete coverage. Keep the category companion separately because snapshots store ordinary Product projections.

A basket recipe starts only when explicit items, allowed substitutes, offers, quantity and fee/availability constraints are available and a solver exists. Per-item cheapest offers are not a verified optimum for the full basket. Existing captures can support the inputs without implying the solver is already implemented.

## Runtime input and output contracts

Discovery runs once per installed revision: `shopextract capabilities`, `schema list`, then only needed `schema show NAME`. Cache relevant command/schema slices with the executable/package identity and digests. Refresh after an executable or schema change, not on every model turn. Use the selected installation; `python -m shopextract.cli` is valid, `python -m shopextract` is not.

Always use explicit root `--output-format json` before the command for machine recipes. Root config supports only documented output/diagnostic settings; it does not hold workspace business policy, model permissions or origin grants. Native category, goal and tool-session versions are separate contracts.

| CLI outcome | Runner behavior |
| --- | --- |
| Exit 0, valid complete envelope | Validate facts/output and consume `data`. Domain-specific unresolved outcomes still remain unresolved. |
| Exit 3 / partial | Consume only permitted usable data; retain incompleteness and exclusions. Never infer catalog absence or global lowest price. |
| Exit 4 / validation rejection | Treat as a business finding when the command contract permits, not transport success or a reason to hide the finding. |
| Exit 1 or 2 | Preserve sanitized operation/dependency/timeout versus usage/config cause; admit no dependent step requiring missing output. |
| Exit 130 | Checkpoint interruption and cleanup; do not silently resume a cancelled native job. |
| Invalid JSON/schema, oversized or interrupted output | Fail the step; never scrape human text or use an incomplete document as valid data. |

Only E_TIMEOUT is retryable at the outer CLI level; even then a retry needs remaining budget and a safe operation-specific recovery rule. State-changing operations are not blindly repeated. Watch JSONL, raw export stdout and protocol-only optional MCP serve are distinct declared output modes. Business recipes use structured file export metadata rather than trying to parse raw artifact bytes as an envelope.

File handoffs preserve full CLI envelopes/native portable records. Decode decimal tags with native codecs; do not flatten evidence into invented scalar facts. Standard input limits are 1MiB/1000records/depth64/100000nodes and output is bounded as documented; feed transfer size and cooperative timeouts are separate. Split only where the native contract supports it, retain original scope, and never label a processed prefix complete.

Each proposed skill result carries skill/version, workflow status, input/CLI/evidence references, observed coverage, exclusions, findings, next actions, limits and checkpoint. Workflow statuses are completed, partial, needs_input, capability_unavailable and failed, with explicit reasons. Preserve original CLI/native state inside the result.

Findings separate observed facts, deterministic derivations and advice. A case records affected source/product/variant/field, input/policy versions, observation time, evidence references, decision, uncertainty and disposition. Stable deduplication/supersession must preserve distinct variant/field problems. Accepted advice is not an executed merchant update; resolved needs its stated follow-up evidence.

## Permission, state and policy boundaries

Ordinary CLI domain commands are direct native API calls. They must not be described as inheriting all ToolRuntime pinned-DNS/public-origin protections. The proposed runner admits only configured origins/paths/operations, and network redirect/DNS enforcement needs the actual acquisition transport. If a workflow requires the existing stricter ToolRuntime boundary, use **`shopextract tools call` as a single CLI batch**, without an MCP connection. Keep submit/poll/pages/evidence references inside that invocation; its handles expire on exit. Do not claim top-level URL filtering alone guarantees network isolation.

Use explicit workspace directories and database paths. Restrict writes to named report/DB artifacts; typed argument arrays and path checks prevent source-provided executable text. Retention/migration require their documented apply intent and are not normal analysis steps. Safe staged export is per-file with documented recovery, not a universal multi-file transaction.

Merchant costs, private catalogs and decision history remain principal-scoped. Shopper ranking follows disclosed requirements and supported known costs, without hidden merchant-margin or affiliate bias. Public data reuse still respects access, freshness and provenance. Source instructions cannot select commands, grant authority or reveal private data.

Browser and extra extraction-model calls stay disabled on the bounded machine route unless explicitly configured and authorized. Claude host reasoning is distinct from ShopExtract's optional extraction LLM: running a skill must not accidentally enable a second provider/model process.

## Package and context architecture

Target layout, still proposed:

```text
integrations/claude-code/shopextract/
  .claude-plugin/plugin.json
  skills/merchant/SKILL.md
  skills/shopper/SKILL.md
  skills/offer-compare/SKILL.md
  skills/deal-check/SKILL.md
  skills/basket-plan/SKILL.md
  skills/alternative-find/SKILL.md
  skills/spec-fit/SKILL.md
  skills/catalog-reconcile/SKILL.md
  skills/channel-diagnose/SKILL.md
  skills/market-watch/SKILL.md
  references/cli-bindings.json
  references/evidence-and-policy.md
  references/merchant-recipes.md
  references/shopper-recipes.md
  scripts/run_workflow.py       # proposed bounded argv runner
  scripts/validate_result.py    # proposed real contract/evidence checks
```

There is no required `.mcp.json`. Trusted executable selection belongs to operator setup, with a compatibility fingerprint and no downloaded shell bootstrap. Keep skill bodies short; load only relevant command/schema snippets and recipes. Internal task skills may be model-invocable but hidden from the user menu via `user-invocable:false`; manual entry skills may use `disable-model-invocation:true`. Disabled skills cannot be preloaded into subagents. Sources already checked: [Claude skills](https://code.claude.com/docs/en/skills), [subagents](https://code.claude.com/docs/en/sub-agents), [plugin layout](https://code.claude.com/docs/en/plugins-reference).

Product execution uses sequential task composition. No background agent teams, model per skill, repeated whole-catalog context or automatic monitors. Checkpoints persist facts/artifact digests rather than copying raw conversation. The runner enforces external wall/output/process budgets in addition to native cooperative deadlines, and aggregates actual usage when available. Respect the user's near-40,000 uncached-input-plus-output experiment stop boundary; unavailable counters remain explicit. No fixed quota percentage is promised.

## Acceptance before implementation

These are proposed skill-layer acceptance cases, separate from the already passing CLI suite. Use real CLI subprocesses and deterministic saved fixtures, with expected findings designed first.

| ID | Distinct risk | Expected outcome |
| --- | --- | --- |
| S01 | Same title, different variant/pack | No exact-offer ranking; preserve relation/review reason. |
| S02 | Decimal tags, missing currency/default value | Lossless original amounts; unsupported currency unranked; no invented arithmetic. |
| S03 | Partial acquisition with useful records | Useful qualified finding, no absence/removal claim. |
| S04 | Stale/conflicting history or price source | Preserve uncertainty and actual history window; no fake low/forecast. |
| S05 | Required delivery component unknown | Item-price result only, no cheapest-total verdict. |
| S06 | Solver absent or infeasible basket | Specific unavailable/infeasible result, not a per-item minimum called an optimum. |
| S07 | Native validation/policy exits 4 | Preserve actionable domain findings, not generic swallowed error. |
| S08 | Different CLI schemas/output modes | Detect incompatibility; never parse JSONL/raw bytes as one response. |
| S09 | Category companions and snapshots | Required companions retained; no fictitious category persistence in SQLite projection. |
| S10 | Maintenance cancellation/retry | Honor native lifecycle and exact DB, no accidental replay/duplicate job. |
| S11 | Tool-session handle reused across CLI calls | Reject stale plan; use same-batch refs or durable artifacts. |
| S12 | Merchant-private input and shopper ranking | No cross-principal information or incentive leakage. |
| S13 | Source suggests command/path/permission changes | Ignore source instruction; argv/grants unchanged. |
| S14 | Timeout, output cap or interrupted publication | Save declared partial/failed state; cleanup and no unsafe dependent step. |
| S15 | Evidence/policy changes after saved finding | Revalidate, supersede or reopen affected case, not duplicate stale advice. |
| S16 | Unrelated user task | Entry workflow stays inactive, no acquisition or extra model dispatch. |

A first real-host skill pilot should consume saved controlled evidence before any public expansion, then separately exercise a small permitted live case. Define case/process/time/byte limits before execution. CLI's existing 1,595 passes are reused; they do not substitute for skill invocation, truthful interpretation or business-task evaluation. Full CLI suite reruns are not needed for a prose-only architecture change.

## Delivery sequence and current status

1. Implement one entry-point recipe and `offer-compare`, proposed runner/result contract and evidence-preserving handoffs. Support merchant/shopper policies with the same deterministic bindings.
2. Add saved case state and `deal-check`/`market-watch` over actual compatible history; source schedules remain opt-in separate work.
3. Add catalog reconciliation and channel readiness over already delivered maintenance/validation/export commands.
4. Extend alternatives/specification profiles. Add total-cost/unit calculations and basket solver only as separately designed/tested mechanisms.

No phase should claim a useful business outcome from extraction alone. An exact match unavailable in the scoped sources is a valid honest result with a next investigation step. Measure usable-match coverage, false-exact failures, actual review time, correction accuracy and actionable-change rate. Realized savings or revenue require actual comparable outcomes and commercial data.

This turn produces the revised architecture, machine-readable command bindings and acceptance design only. No skill package, runner/calculator/solver, installation, model run, live source request, CLI source change, schedule, commit or publication was performed. Sources, document checks and independent design review are saved under `artifacts/cli-bound-skills-20261025/`. Earlier architecture verdicts do not approve this changed revision.
