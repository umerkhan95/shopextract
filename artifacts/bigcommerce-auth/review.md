# BigCommerce authentication implementation review — 2026-10-04

The adapter now supports explicit storefront, private and impersonation bearer
token modes. Python integrations can use private tokens without Origin or public
HTML token discovery. Customer access tokens carry the documented strict-error
header; invalid sessions cannot silently become guest pricing via the extractor's
HTML continuation. Customer context is separated from guest observation scopes.
Credentials do not enter query strings, query bodies, captured evidence or errors.

Documentation: [Authentication](https://docs.bigcommerce.com/developer/docs/storefront/guides/graphql-storefront-api/authentication),
[Customer context](https://docs.bigcommerce.com/developer/docs/storefront/guides/graphql-storefront-api/customer-context).
BigCommerce recommends private tokens for server-to-server use. Published storefront
token discovery remains a compatibility path, not the recommended Python deployment.

The mock validates actual request headers and executes the adapter's actual query
against a frozen documented catalog schema subset. All 32 selected field types and
nullability agree with retained official definitions. Negative query tests reject
unknown fields and arguments. A new dev dependency, graphql-core, provides parsing,
validation and execution; production dependencies are unchanged.

Other diagnosed repairs: a nullable product `prices` value no longer routes native
BigCommerce data through the generic normalizer and loses stock/image/URL mappings.
The repeated-cursor fixture now uses distinct product IDs so the cursor guard is
actually exercised. The original duplicate-ID fixture masked that code path.

Coverage: bearer/Accept/Content-Type/Origin headers; private and impersonation modes;
customer context validation; strict session errors; public token rotation; invalid
configuration before network; synthetic expired/revoked/channel/origin rejections;
HTTP-200 GraphQL errors, HTTP 401/403/429/500, partial data, mid-page failures and
timeout; pagination; optional prices/inventory; credential redaction; cross-origin
redirect blocking; actual public extraction dispatch and guest/customer fallback rules.

Focused suite: **91 passed**, 2.92 seconds. Full suite: **535 passed**, 27.62 seconds.
`git diff --check` passed. Logs are retained as `focused.log` and `tests.log`.
All test traffic uses HTTPX MockTransport; no real credentials or authenticated
live catalog calls were used. Provider JWT signature validation, token permissions,
actual expiry/revocation and exact rejection messages/statuses are not simulated.
Issuance, login and account/cart mutations remain outside read-only extraction.
