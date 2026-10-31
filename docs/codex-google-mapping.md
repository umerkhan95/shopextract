# Configured Pakistani-site mapping and Codex skill

The repo-scoped skill is
[shopextract-google-mapping](../.agents/skills/shopextract-google-mapping/SKILL.md).
It uses the installed CLI and a separate trusted site profile, then reads the
new run's actual evidence before answering. It does not classify from titles or
turn missing source categories into observed Google assignments.

Run from the repository root:

```sh
shopextract --config examples/cli/google-live-cli.json taxonomy google verify-live \
  --profile examples/cli/google-live-profile.json \
  --output-dir build/google-live/my-new-run --live
```

Use `--site priceoye-a16` or `--site liberty-atomic-habits` to select one case.
Use `--project-root PATH` when profile resource paths belong to another working
root. Omit `--live` for configuration-only preflight. Output directory must be
new; existing reports are never reused as fresh scans. Root CLI config retains
its existing three-key contract; taxonomy/site settings belong in the profile.

The configured Pakistani candidates are Priceoye's Samsung A16 product page and
Liberty Books' Atomic Habits product page. Active merchant rules are initially
empty. Add a reviewed native mapping rule only after inspecting captured
category labels/IDs; no title/store-name guess can authorize a mapping. Native
Google declarations can resolve directly when supported by source capture.

The live workflow checks a supported managed network policy before requesting.
An explicitly denied host is skipped with a fresh policy digest/time and zero
requests, following the user's request to leave blocked sites. Unknown policy
format is not an authorization grant; the normal inherited proxy still applies.
Policy-denied sites are not retried through another route.

The configured version2 profile invokes the native `extract()` pipeline with
platform detection, API extraction, discovery, UnifiedCrawl/Crawl4AI and CSS
fallbacks. Browser is explicitly enabled; inference is disabled without a budget.
The pipeline stops after sufficient data; enabling fallbacks does not mean every
tier must run. Browser availability is required only if the selected path needs
it. No dependencies or models are automatically installed.

Production supervision currently requires Linux and a sequential call from the
main thread; unsupported supervision fails before launching a worker. It owns
the launched process group, not descendants that deliberately escape that group.

Version2 limits2pipeline invocations, max_urls1 each,4retained products,120s
including child cleanup, and1MiB per child stream/JSON artifact. Native discovery
and browser subrequests/response bytes are not counted by this integration; the
report records their counts as null. Initial approved URLs are validated; v2
does not claim the static verifier's same-origin redirect/response-byte bounds.
Version1 static profiles retain their original8request/1MiB response/scope limits.

Original raw captures go through the same Google normalization CLI, portable
reload and CSV/category-companion export as static verification. Worker results
report actual platform/tier, source completeness and owned-process cleanup.
Per-tier attempts and actual browser execution remain unknown unless separately
observed. Artifact hashes identify saved worker/CLI data, not a fabricated HTML
response. Controlled runs always disable live_verified.

In a Codex surface that supports local repo skills, invoke:

```text
$shopextract-google-mapping Verify the configured Pakistani sites; skip blocked sites.
```

Local `.agents/skills` discovery follows the
[official skill guidance](https://learn.chatgpt.com/docs/build-skills).
No global Codex configuration, credentials, plugins or user skill files are
changed. Skill file presence/static checks are separate from actual native-host
activation and response verification.

## Actual verification disposition

Current managed environment allows package/GitHub destinations, so selected
merchant origins are policy-skipped. No product was fetched or mapped live.
Native Codex CLI0.163.0 reported a signed-in account, but its ChatGPT backend
connection was proxy-denied before any command/skill execution; no native skill
activation or answer is claimed. That failed attempt was stopped and cleaned.

An actual agent in the existing Codex app runtime separately read the skill,
ran one fresh CLI workflow and saved its actual model answer. The answer matched
the blocked report: zero HTTP requests/products, extraction/mapping not run and
live_verified=false. This is an explicit file-based agent exercise, not proof of
native CLI discovery. An unrelated-task agent answered2+2 without requesting the
workflow; it does not prove native implicit-discovery behavior.

See [host verification](../specs/014-codex-google-live/evidence/host-verification.json),
[the actual agent answer](../specs/014-codex-google-live/evidence/orchestrated-positive.answer.json)
and [its report](../specs/014-codex-google-live/evidence/orchestrated-positive.report.json).
The earlier complete5595target mapping/export sweep remains independently blocked
in spec013; neither these small controlled tests nor a policy skip completes it.

## Native-core audit and controls

[The integration audit](native-core-integration.md) distinguishes repaired adapter
gaps from intentional source-specific limits. Eight extraction-backed commands
now expose shared `--browser` and `--allow-llm` controls; their bounded defaults
remain browser off and inference off. Category CLI defaults to production; use
`--source-mode native` for the compatible source-specific API/feed route. Library
`extract_with_categories` keeps native as its default. Auto-platform profiles
require unscoped reviewed rules; explicitly scoped rules require a declared platform.

Historical spec014 skill answers used the previous static profile. A new version2
report is necessary to assess the current pipeline; old zero-request results do
not prove the repaired fallback integration ran live.
