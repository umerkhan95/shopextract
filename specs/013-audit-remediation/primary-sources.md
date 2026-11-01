# Primary source register — fetched2026-11-01

Six primary pages opened; no merchant/network sweep. OpenAI documentation skill
used for the official OpenAI feed page; community mirrors excluded. These are
retrieval-date pins, not immutable versions; implementation stores rule version/hash.

- G1 https://support.google.com/merchants/answer/7052112?hl=en — required core
  catalog fields plus destination/category/country conditions. Missing GTIN does
  not alone prove identifiers do not exist; do not invent manufacturer identifiers.
- G2 https://support.google.com/merchants/answer/6324371?hl=en — amount plus ISO4217
  currency, matching landing/checkout prices. Explicit zero has conditional uses;
  do not universally reject supported zero as a parsing defect.
- S1 https://schema.org/Product — vocabulary defines properties, not a universal
  mandatory-field/compliance checklist; page identifies itself as development view.
- S2 https://schema.org/ProductGroup — grouped variants vary in stated ways; group
  itself is not directly offered. Preserve group/variant identity and ownership.
- O1 https://developers.openai.com/commerce/specs/file-upload/products?fields=required&version=currently-stable&view=table
  — stable OpenAI discovery feed requires item_id,title,description,url,brand,
  seller_name,image_url,availability,price. Unknown availability is explicitly
  allowed; arbitrary unknown placeholder strings are not universal substitutes.
  Ads/checkout have additional separate requirements. Feed is not checkout proof.
- A1 https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/blob/main/rfcs/rfc.product_feeds.md
  — ACP product-feed RFC is Proposal/unreleased, not a supported certification
  target. Distinguish it from O1 stable upload format and checkout protocol.

No paid API, feed upload or checkout access used. Remaining country/category rule
branches must be explicitly unsupported/needs-context rather than blanket-valid.
