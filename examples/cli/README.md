# Offline CLI examples

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
