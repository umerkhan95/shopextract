# Verification records included with this change

The checked-in review summaries, JSON results, bounded stress driver and test logs
record the provenance and storefront authentication work. Full fetched storefront
pages, large catalogs, database files, complete evidence exports and unrelated
experiments remain local and are not included in this pull request. Some review
summaries refer to those local files for reproducibility and diagnosis.

- `live-provenance-35/all-domains/review.md`: extraction-family provenance checks.
- `api-integration/review.md`: initial native adapter integration checks.
- `live-stress/review.md` and `summary.json`: live pagination, budgets and repeat audit.
- `bigcommerce-auth/review.md`: documentation-based authentication mock coverage.

These are successive checkpoints. The final full-suite result is 535 passing tests
in `bigcommerce-auth/tests.log`; earlier reports retain their historical counts.

Field-resolution follow-up (#36): `field-resolution-live/review.md` and `review.json`
record the live platform matrix. The included drivers can reproduce the run; large
compressed captures remain local. Latest full suite: 590 passed in
`field-resolution-live/full-tests.log`. Compact Magento/Shopware captures used by
automated tests are included under `tests/fixtures/field-resolution/`.

Reliable change detection (#23): `reliable-change-23/review.md` and
`live/summary.json` record 95 focused and 726 full-suite tests, independent review,
and a two-request live pipeline smoke. Live source values did not change, so
commercial-change validation remains inconclusive. The driver and compact stage
logs are included; full storefront responses and the live SQLite database remain
local and are not included.

Tool API and MCP server (#24): `agent-tool-api-mcp/delivery-summary.json` records
48 passing current-code mechanism cases with bounded resource usage.
`agent-tool-api-mcp/live-data-verification/summary.json` and `data-audit.json`
record the real MCP client flow and source comparisons for two live products.
Only compact API responses, currency-cookie projections, portable records and
verification summaries are included. Full storefront HTML, local SQLite databases
and unrelated experiments remain local. Historical failures remain documented;
the current delivery run supersedes their coverage gaps without rewriting them.
