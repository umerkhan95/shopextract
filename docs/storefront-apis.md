# Storefront API routing

`extract(store_url)` chooses a platform's customer-facing API when it is accessible.
REST and GraphQL are protocols, not a required sequence. API access or an unsupported
schema can fail; extraction then continues through structured HTML, CSS and the
configured optional LLM path. Failed API attempts remain inspectable in `result.errors`.
Every normalized field still uses the evidence contract; an unavailable source or
compatibility default does not become an observed fact.

| Platform | Default API path | Access requirements |
| --- | --- | --- |
| Shopify | Public storefront product JSON | Accessible Shopify-hosted storefront; custom headless stores can differ |
| WooCommerce | `/wp-json/wc/store/v1/products` | Public Store API enabled |
| Magento Open Source / Adobe Commerce PaaS | `/graphql`, `products` query | Public storefront catalog query supported; legacy REST can be selected explicitly |
| Shopware | Store API product search and context | Endpoint and sales-channel key explicitly published in inline storefront config, or supplied by the caller |
| BigCommerce | Storefront GraphQL `/graphql` | Storefront token explicitly published in inline page context, or supplied by the caller |
| Other stores / unavailable API access | Structured HTML, CSS, optional LLM | Accessible product pages; model configuration only for the optional LLM tier |

Magento's REST `/V1/products` endpoint is restricted for anonymous callers by default.
The default adapter therefore uses the documented storefront GraphQL product query;
it does not blindly attempt a REST-to-GraphQL sequence. Adobe Commerce SaaS uses a
different Catalog Service schema and is not supported by this Magento GraphQL adapter.
A store with a customized or unsupported schema continues to the HTML path.

Shopware runtime discovery reads an explicit `shopware: { endpoint, accessToken }`
object. It works with the official Nuxt demo's public runtime configuration. BigCommerce
runtime discovery reads explicit `storefrontApiToken`, `storefrontAPIToken` or
`storefront_api_token` string properties, including escaped page-context JSON. Scripts
are never executed. Bundled or dynamically computed keys are not inferred, and admin
credentials are never guessed. Missing configuration is an ordinary reason to use HTML.
A discovered token is not reused for an unrelated caller-supplied endpoint.

## Optional explicit configuration

Simple extraction needs no API options. For a headless storefront or a key not
published inline, callers can provide the endpoint and appropriate storefront token:

```python
result = await shopextract.extract(
    "https://my-shop.example",
    platform=shopextract.Platform.SHOPWARE,
    max_urls=20,
    api_options={
        "endpoint": "https://backend.example/store-api",
        "access_token": "sales-channel-access-key",
    },
)
```

BigCommerce accepts the same `endpoint` and `access_token` options with
`Platform.BIGCOMMERCE`. The adapter sends a storefront Origin header for the supplied
shop URL. Storefront tokens and channel/origin permissions must match the actual
endpoint. For Python/server-to-server integrations use a caller-supplied private token with
`token_type="private"`; this mode sends no Origin header and makes no public HTML
configuration request. Private/impersonation tokens are never discovered from pages.
The default `storefront` mode preserves published-token compatibility, but BigCommerce
now deprecates server-to-server use of storefront tokens. Token issuance, permissions,
rotation and revocation remain caller/BigCommerce responsibilities.

Magento defaults to GraphQL. A legacy integration can explicitly select REST:

```python
result = await shopextract.extract(
    "https://magento.example",
    platform=shopextract.Platform.MAGENTO,
    api_options={"protocol": "rest", "access_token": "integration-token"},
)
```

An optional REST `endpoint` override means the full products endpoint. GraphQL endpoint
overrides likewise mean the full GraphQL URL. Shopware endpoint overrides mean the
Store API base URL. Tokens are request headers, not source URL query parameters.

## Bounds, pagination and evidence

New adapters bound product retention with `max_urls`, page counts and a 10 MiB response
limit, and use per-request timeouts. Magento uses fixed-size offset pagination;
BigCommerce uses advancing cursors. Repeated IDs/cursors and GraphQL partial-data
errors are rejected as incomplete observations. GraphQL configurable variants and
BigCommerce variant nodes use their own nested source paths. BigCommerce/Shopware
child association budgets are explicit, and known truncated child collections cannot
report a complete adapter catalog. Main extraction still reports non-Shopify catalog
coverage as unverified; successful API extraction does not certify catalog completeness.

Shopware currency retains the actual Store API context response URL/time and original
currency value. Product API fields retain the product response URL/time. Monetary zero
and explicit false stock remain observed values. HTML fallback uses the HTML source's
normalizer even when the store platform has already been detected.

API requests handle compressed responses without decoding twice. Keyed requests do
not replay access headers across origin-changing redirects. Adapter error strings do
not echo tokens, response bodies or GraphQL server error payloads.

## Validation

Offline tests cover public configuration discovery, native API dispatch through
`extract()`, pagination/budgets, configurable variants, zero/false evidence, context
currency, missing-access HTML fallback, HTML normalizer selection, compressed transport,
keyed redirects, empty catalogs and explicit legacy REST selection.

Live results are saved in `artifacts/api-integration/`. Magento Magebit and the official
Shopware demo pass the actual public `extract()` API path. The official BigCommerce
Cornerstone demo does not expose a storefront token; its live HTML product extraction
passes through the actual public pipeline. Native Stencil product-card discovery
returns the requested homepage sample without a broad browser discovery walk; this
does not certify full catalog coverage. The token-based BigCommerce adapter is validated against deterministic fixtures
and the official GraphQL type reference, not a live authenticated catalog.

## Official references

- [Magento anonymous REST restrictions](https://developer.adobe.com/commerce/webapi/rest/use-rest/anonymous-api-security)
- [Magento storefront products query](https://developer.adobe.com/commerce/webapi/graphql/schema/products/queries/products)
- [Shopware Store API](https://developer.shopware.com/docs/concepts/api/store-api.html)
- [Shopware public demo configuration](https://github.com/shopware/frontends/blob/main/templates/vue-demo-store/nuxt.config.ts)
- [BigCommerce storefront authentication](https://docs.bigcommerce.com/developer/docs/storefront/guides/graphql-storefront-api/authentication)
- [BigCommerce GraphQL reference](https://docs.bigcommerce.com/developer/api-reference/graphql/storefront/queries/site)
- [WooCommerce Store API](https://developer.woocommerce.com/docs/apis/store-api/)
- [Shopify Ajax API](https://shopify.dev/docs/api/ajax)

## BigCommerce authentication modes

The three documented bearer token families are explicit; JWT content is never decoded
to guess permissions or validate expiry locally:

| `token_type` | Required options | Additional request headers |
| --- | --- | --- |
| `storefront` (compatibility default) | Published or supplied storefront `access_token` | Storefront `Origin` |
| `private` (recommended for Python) | Caller-supplied `access_token` | No Origin required |
| `private` with customer context | `access_token`, `customer_access_token` | `X-Bc-Customer-Access-Token` and `X-BC-Error-On-Invalid-Customer-Access-Token: true` |
| `impersonation` | `access_token`, positive decimal-string `customer_id` | `X-Bc-Customer-Id` |

```python
result = await shopextract.extract(
    "https://my-shop.example",
    platform=shopextract.Platform.BIGCOMMERCE,
    api_options={
        "token_type": "private",
        "access_token": private_token,
        "endpoint": "https://my-shop.example/graphql",
    },
)
```

For customer pricing, add `customer_access_token` to private mode. The strict error
header prevents BigCommerce from silently returning anonymous prices for an invalidated
customer session. Impersonation and customer access tokens are mutually exclusive.
Customer requests never continue into anonymous HTML, even if the API result has low
quality or an error. Their observation scope includes a digest of the context identifier,
keeping it separate from guest observations without exposing the credential. Customer
access-token rotation conservatively produces a different scope; it is not a stable
customer identity. B2B/customer permissions must already be present in the caller's token.
This extractor only reads catalog data; it does not perform login, token creation,
refresh, revocation, cart or account mutations.

Configuration errors fail before requests. HTTP rejection status is retained without
server messages or credentials; GraphQL errors (including partial data) produce an
incomplete result. Successful earlier pages can remain captured after a later error.
Anonymous catalog requests may continue into HTML with the API failure retained.
No automatic retry, token refresh or guessed authentication fallback is performed.

Authentication regression tests use HTTPX MockTransport and execute the adapter query
with graphql-core against a frozen documented catalog schema subset. They check headers,
request variables, cursor progression, nullable fields and negative query validation.
Synthetic error responses cover expired/revoked credentials, channel/origin rejection,
HTTP and GraphQL failures, partial data, mid-page failure and timeout. These fixtures
exercise response handling; they do not emulate BigCommerce JWT signature validation,
permission policy, or promise identical rejection messages/statuses across stores.

See `tests/test_bigcommerce_auth.py`, `tests/fixtures/bigcommerce/README.md` and
`artifacts/bigcommerce-auth/review.md`. The customer-context rules come from
[BigCommerce customer context](https://docs.bigcommerce.com/developer/docs/storefront/guides/graphql-storefront-api/customer-context).
