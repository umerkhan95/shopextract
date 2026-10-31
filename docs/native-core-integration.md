# Native-core integration audit

Audit date: 2026-10-31. Scope: extraction-backed CLI adapters, category extraction,
Google live verification and the repository Codex mapping skill. This checks
whether adapters expose the existing core; it is not an assertion every optional
dependency/provider is installed or every merchant is accessible.

| Surface | Before | Repair / current contract |
|---|---|---|
| Google verification | Separate HTTP fetch and private static parsers | Configured v2 profile calls actual native extract in a supervised worker; platform detection, API, discovery, UnifiedCrawl and CSS remain core responsibilities. |
| Category extraction | Static generic HTML or platform API only | Explicit production mode uses native extract and the existing category binder; CLI defaults to production, library preserves native default. |
| compare, analyze, compare-catalogs | Hardcoded browser/inference off without controls | Existing shared execution controls now reach all nested extraction calls. |
| competitive position, competitive gaps | Hardcoded browser/inference off without controls | Same controls and one shared operation budget. |
| snapshot, watch | Hardcoded browser/inference off without controls | Same controls, including one shared state across watch iterations. |
| Source categories in fallback layers | Optional category capture not threaded through the core | Opt-in include_categories reaches native API, Unified HTTP/browser and CSS source parsing. Missing categories remain unsupported. |
| Short GTIN restoration | Flag reached API normalization only | Flag now reaches Unified/CSS/LLM normalization too; existing checksum and source rules still apply. |
| Browser proxy | Browser configuration did not explicitly use inherited HTTP proxies | Shared configuration supplies Crawl4AI ProxyConfig and fails closed on invalid configuration. |
| extract, extract-one, discover | Browser controls already available | Reused existing controls; no duplicate extraction engine. |
| Feed and category-tree readers | Source-specific API/feed extraction | Intentional: browser/LLM are not an alternative to their source contracts. |
| Bounded tools runtime | Explicit guarded HTTP-only source contract | Intentional: no browser/inference bypass of tool resource/security contracts. |
| LLM fallback | Requires explicit provider/model/key budget | Still explicit; inherited keys alone do not activate inference in bounded CLI operations. |
| Storefront authentication/enrichment | Optional explicit platform configuration | Preserved; no credentials invented or silently enabled. |

Examples (use real approved merchant URLs in place of STORE):

```sh
shopextract --output-format json analyze STORE --browser --timeout 60
shopextract --output-format json compare Book --stores STORE --browser --timeout 60
shopextract categories extract STORE --options category-options.json --browser --timeout 60
shopextract --output-format json snapshot STORE --db snapshots.db --browser --timeout 60
```

The eight repaired commands accept the existing `--allow-llm`, `--llm-model`,
`--llm-key-env` and bounded input/output/call settings. Browser and inference
remain off by default for bounded CLI operations. An early successful API/HTTP
result should not force later fallbacks. `categories extract --source-mode native`
retains source-specific API/feed behavior and rejects LLM activation.

All browser tiers use the first configured HTTPS_PROXY/https_proxy, then
ALL_PROXY/all_proxy, then HTTP_PROXY/http_proxy. The selected browser proxy can
carry both schemes; exact HTTPX per-scheme/NO_PROXY parity is not implemented.
Proxy variables, credentials and network allowlists are never changed. Invalid
proxy configuration never triggers direct-network fallback.

The configured v2 verifier enables browser eligibility, disables LLM, and records
actual native platform/tier. Unknown browser/tier attempts and network byte/request
counts remain unknown. Its bounds cover invocation count, retained products,
time/cleanup and child output; they do not claim v1's exact network/scope bounds.
See [configuration and verification](codex-google-mapping.md).

Controlled fixtures exercise the actual fallback/parsing/normalization/mapping
paths with external HTTP/browser/provider boundaries replaced. These tests do
not establish Chromium startup or live merchant access. In this environment
Crawl4AI0.9.5 is installed, the configured Playwright Chromium executable is
missing, and system Chromium's presence does not prove native compatibility.
Policy-denied sources are skipped before worker/browser execution.

Design, independent reviews, red/green tests and remaining live limitations:
[spec015](../specs/015-native-core-integration/status.md).
