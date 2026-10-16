# Evidence & Data Trust

## Outcomes and shared requirements
Consumers distinguish observed facts, missing values, unsupported legacy/default
values and competing values without guessing from Product scalar defaults.

- FR-01: Field evidence includes source URL, aware UTC observation time, captured
  excerpt or pointer into retained data, method and evidence ID; cover nested facts.
- FR-02: Explicit unknown/default/unsupported states distinguish literal zero/false;
  preserve raw values, normalized values and transformation explanations.
- FR-03: Versioned field-specific authority retains alternatives and rationale.
- FR-04: Atomic persistence/retrieval and conservative migration preserve history.
- FR-05: Lossless portable evidence bundles; compatible restricted-format sidecars.
- FR-06: Rule/model scores remain separate from validated confidence metadata.
- FR-07: Bounded capture and retention explicitly expose expired/unavailable support.

#34 delivers interfaces and fixtures for FR-01, FR-02, FR-06. Capture (#35), policy
(#36), SQLite (#37), export (#38) and the end-to-end example (#39) remain pending.

## Acceptance scenarios for #34
1. Given absent price/currency/stock normalized through the existing API, when the
   trust view is inspected, then defaults are unsupported with null trusted values.
   Given explicit evidence for zero/false, then those values are observed.
2. Given nested variants, attributes, lists or empty collections, when enumerated,
   then every factual leaf/container has evidence or an explicit unsupported reason.
3. Given an uncalibrated model score, when serialized, then validated confidence is
   unavailable. Given validated confidence, method/dataset/version are required.
4. Given legacy constructors/records, when inspecting support or assigning identity,
   then compatibility and canonical identity remain stable. Malformed IDs, timestamps,
   states and dangling references are rejected.
5. Given competing observations, when inspected without a resolution, then no fact
   is selected; an explicit resolution retains all candidates and its rationale.

Named fixtures and requirement coverage are in tasks.md. Epic SC-01–SC-04 require
completion of all child tickets, not only these contracts.

## Boundaries
Evidence-backed reporting only. No catalog mutation, model launch, hosted gate,
MCP, webhooks, broad crawl or fabricated historical observations.
