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
