# Offline CLI examples

Configured Pakistani-site verification and the repository Codex mapping skill
are documented in [Codex Google mapping](../../docs/codex-google-mapping.md).
Use `google-live-cli.json` for root CLI options and the separate
`google-live-profile.json` for pinned taxonomy/site settings. `verify-live`
creates a fresh report and skips current policy-denied sites; a skip is not a
successful live mapping.

From the repository root with ShopExtract installed:

```sh
shopextract capabilities
shopextract schema show maintenance-goal
shopextract --config examples/cli/cli.json normalize examples/cli/raw-products.json > normalized.json
shopextract quality normalized.json
shopextract tools call --config examples/cli/operator.json --request examples/cli/session.json --timeout 10
shopextract maintenance --db ./example-jobs.db create examples/cli/goal.json
shopextract maintenance --db ./example-jobs.db list --limit 10
```

Use the returned job_id with `shopextract maintenance --db ./example-jobs.db run JOB_ID --timeout 10`.
This synthetic goal has a zero-product budget, so run intentionally exits3 with
partial/product_budget and performs no HTTP. IDs persist in the selected database;
bootstrap handles belong only to one tools call. A new positive-budget goal needs
a current future deadline and authorized public supplier origin. These files are
synthetic examples, not captured commercial data.

The configured Google live profile is version2 and uses native production
extraction with platform auto detection and browser eligibility. Limits count
pipeline starts/retained products/time/output; network request/byte counters are
unobserved. Version1 static profiles remain supported. See
[the native-core audit](../../docs/native-core-integration.md) for repaired CLI
browser/inference controls and intentional source-specific limits.
