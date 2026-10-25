# P0 bounded production research

2026-10-25; native dirty working-tree source digests in command-baseline.json and
capability-manifest.json. Saved parent six-file AST inventory reused, reconciled
with a single AST scan over local Python source (92 classified module records).
No source imports for the inventory, models, installs, network or broad sweeps.

Decisions: retain Click root registration and existing lazy command-body imports;
root options require placement before command, avoiding ambiguous two-pass domain
parsing. Reuse native serializers where available; never universal default=str.
Parent envelope and precedence remain authoritative; completeness is the explicit
additive field required by parent's partial-data contract. Root config accepts
only CLI settings, so cannot enlarge trusted tool-origin scope or enable LLMs.
Error serialization depends on resolved machine mode; explicit json still works
when config is malformed. Invalid overridden settings remain errors.

Native baseline: cli.py registers exactly nine commands. extract prints ten-record
preview; analyze truncates brands; validate reports issue text without failure
exit. These quirks are historical legacy behavior; new machine mode must carry
full domain data after phase-specific schema freeze. Config flags do not exist
currently. Existing package startup produced a bounded warning on stderr during
help; this is not optional-runtime activation proof. Smoke checks availability
only. Unrelated preexisting working-tree edits are preserved.

Inventory: every nonprivate top-level definition/method is classified conservatively,
including internal modules; this is deliberately broader than documented public
API. Export aliases and root imports are retained in module/saved inventory maps.
Classes used as schemas are not constructor commands. Helpers use their module's
parent target. Alert when/callback registration is Python-only; portable watch
results do not claim callback equivalence. Native context callback parameters,
maintenance Investigator/fault hooks, tools resolver/transport seams and DataFrame
objects stay Python-only. Portable category config helpers belong to categories
config/record workflows. Exact per-domain flags/config still require phase G1.

Remaining: runtime lifecycle, payload shapes, native partial mapping, codec specifics,
streaming, browser/LLM budgets, file staging and P1–P5 input grammar are reserved
rather than implied by core freeze. No external factual research needed for this
local design. Actual session token counters unavailable; no quota estimate.

Focused independent review repair: workflow recognition now uses an explicit
class+method allowlist and top-level domain entries; no bare method name collision.
Per-workflow phase/target/rationale links and grouped helper rationale distinguish
operator actions from adapters, injected clock/hooks, storage and owned cleanup.
Help/version/error routing is frozen in contracts.json B01–B15; future runtime
implementation may need a small bootstrap scan to honor these exact contracts.
