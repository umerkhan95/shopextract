# Live workflow and skill interface candidate

Coordinator concrete runtime signatures: `live_profile.load_live_profile(path, *,
project_root=None)->dict` resolves trusted profile paths against explicit project
root (defaults to invocation directory, never the installed package path);
CLI --project-root selects it explicitly when invoked elsewhere.
`live.verify_google_live(profile_path,output_dir,*,live=False,site_id=None,
project_root=None,transport=None)->dict`. A supplied httpx transport is ONLY a
controlled boundary: result mode=controlled and live_verified=False even when
all mechanism assertions pass. CLI never accepts a transport override.
Without --live, fetch is not_run,requests0,status needs_review. Current-policy
denial yields blocked/skipped_network_policy with fresh policy digest/time and
requests0. At most2same-origin redirects per site count within the shared8request
budget. Cross-origin Location is blocked before requesting it.

Report keys include schema_version,run_id,started_at,finished_at,mode,status,
live_verified,profile_sha256,catalog_fingerprint,code_sha256,usage,sites. Each site
records fetch/parser/cli/mapping/export/artifacts; report data never substitutes
for a successful source capture. Actual CLI normalization and existing native
CSV/category-companion export run using bounded subprocesses, exact argv, output
digests and strict portable reload. Raw source bodies remain in the new runtime
directory under ignored build; public receipts reference their digests.
Existing output directory is rejected before any request. Twelve bounded risk
families in test-design remain required; initial9 genuine missing-API reds are
tests/test_google_live.py and evidence/live-red.log, before production code.

2026-10-31. Exact parent-proposed inputs; runtime harness remains coordinator-owned.

Root CLI configuration: examples/cli/google-live-cli.json, exactly
`{"schema_version":1,"output_format":"json","diagnostics":"quiet"}`.
No taxonomy/site fields belong in the existing root config.

Verification profile examples/cli/google-live-profile.json is a separate closed
object with exactly schema_version(1),catalog_root,catalog_fingerprint,cli_config,
sites and limits. sites are closed records id,url,platform,source_kind,shop_url,
mapping_rules. Active Pakistani cases are html and have exactly these six keys;
no css_schema is added to them. Optional html_css cases must add a trusted
css_schema with exact baseSelector and fields; each field has exact name,selector,
type, type=text, names drawn from title/price/product_type, unique names and
bounded literal selectors. This recipe feeds actual DOM capture, never invented
Google membership. Initial site rules are empty. limits exactly requests8,products4,
seconds120,response_bytes1048576, reducible only. Source kinds html, html_css and
shopify_products select existing parsing paths, never arbitrary code/imports.
Catalog must resolve to fingerprint
3b6a52f1d3512c813109844031e0b7e16574ca39c00a60eee02d0d992321323c.
Profile paths resolve against explicit project_root; its default is the invocation directory, so run the skill from repository root or pass --project-root. Installed package location is never used as a project base.

Preferred runtime entry:
`shopextract --config examples/cli/google-live-cli.json taxonomy google verify-live --profile examples/cli/google-live-profile.json --output-dir build/google-live/UNIQUE --live [--site SITE_ID]`.
Optional script adapter uses the same flags: `python scripts/verify_google_live.py`.
Shared package runtime is taxonomies/google/live_profile.py plus live.py; both are
coordinator-owned. html_css uses trusted crawl4ai JsonCssExtractionStrategy then
existing CSSExtractor capture/parsing over actual response HTML; no browser.
No URLs are accepted from website instructions. Named site ID must exist exactly
in profile and skill manifest. Existing output is rejected; no stale report reuse.

Harness report.json top status is pass/blocked/needs_review/fail. Per-site entries
retain exact source URL, fetch/parser/mapping outcomes, actual invoked CLI argv
and artifact references/hashes. Run/profile/catalog/reviewed-code identity and HTTP/product
usage accompany the report. Fresh request failure must create honest blocked/fail
evidence, never parsed products. A mapped positive assertion requires inspected
captured category support and an applicable scoped rule or direct declaration.
Empty mapping_rules never authorizes a category from title or store purpose.

The skill is `.agents/skills/shopextract-google-mapping/SKILL.md`; its
references/test-sites.json records exact intended URLs, authoritative profile path
and actual initial preflight status only. It does not embed fake captures or
expected positive classifications. Skill validates site/profile consistency,
checks CLI/catalog availability, executes the real harness once and reads that
new run's report plus cited evidence before answering.

Actual host verification uses existing signed-in Codex CLI0.163.0 with JSONL and
saved final response. No config/auth file reads/copies or global skill install.
The parent controls sandbox/runtime argv and timeout, observes actual skill/tool
events and compares final claims with the authoritative report. Login status is
eligibility only, not host execution or live verification. More specific event
schema detection must follow actual version output rather than fabricated events.

The user explicitly requested this focused live/skill slice after prior repository regressions passed. The historical spec013 exhaustive5595target gate is independent, not a reason to skip the newly authorized bounded live attempts. Its incomplete status remains visible in every broader coverage claim.

Selected reference IDs are priceoye-a16 and liberty-atomic-habits. Source kind is html/platform generic for both. Exact source/store URLs are frozen in references/test-sites.json. Root/site scope guards validate the initial URL and each redirect; redirected requests count toward8HTTP. A policy denial or source failure is skipped/blocked once. No further allowlist prompt or speculative replacement stores. Priceoye exact product has an actual403; Liberty canonical product has not been directly fetched, unlike the separately denied www-root. Parent evidence/pakistan-preflight.json preserves this distinction.

Fresh network-policy preflight reads current /etc/codex/network-policy.json, supported version1. Under restricted policy, a requested/redirect host absent from allowed rules yields fetch=skipped_network_policy with policy SHA256, observation time and zero additional requests before transport; then proceed to next configured site. Prior403 receipts remain historical references. Missing policy is unknown and uses normal proxied source guards, not an allow verdict. Controlled transport tests explicitly force controlled mode/live_verified=False; policy-skip cases assert no transport call.
