# Component ownership

- Existing top-level `_extract.extract`: sole fallback-chain owner (API, discovery, UnifiedCrawl, CSS, optional LLM). Worker is a transport/lifecycle adapter, not another extractor. `extract_one` is not a substitute.
- Existing `_execution`: explicit browser-on/LLM-off state; no production default changes or new model credential behavior.
- Existing extractors/parsers/capture/normalizer: own extraction facts, quality and evidence. Worker keeps capture unchanged; verifier does not recapture normalized rows or infer source categories.
- New small internal owned-process component: bounded process protocol and cleanup only; concrete consumers extraction worker and live verifier's normalization/export subprocesses. No taxonomy logic, browser logic, arbitrary tool framework, policy bypass or network counter fiction.
- Live profile loader: versioned operator input validation only. Separate v1 static and v2 pipeline resource contracts avoid weakening existing consumers.
- Existing live orchestrator: selects sources, policy preflight, budgets, artifacts, native CLI calls and truthful statuses; thin production worker adapter replaces private static parsing only for explicit production profiles.
- Existing category binder/Google options/portable CLI/export codecs: sole mapping/export authorities. Unsupported category capture produces review-needed instead of guessed success.
- Existing repository skill: describe and invoke production profile; distinguish configured eligibility from observed fallback attempts and controlled mechanism from real browser/merchant evidence.

G1, G2, G3 and final verdicts remain pending until independent reviewer records actual review. Authorship does not approve implementation.


SliceA ownership: categories.api gains an explicit production orchestration adapter and retains native compatibility, while `_extract` still solely owns tier selection. Existing category source adapters own facts. `_cli_extract.execution_options/policy_options` own public execution switches, reused by other extraction-backed CLI modules. `_execution` owns shared per-operation model state. Shared extractors/_browser owns environment proxy configuration for all browser tiers; no per-feature proxy hacks. tools.security HTTP-only runtime remains independent and unchanged.
