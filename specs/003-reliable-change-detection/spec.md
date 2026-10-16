# Reliable Change Detection — issue #23

Stage: behavior design, 2026-10-16. This opt-in feature supplements existing monitoring. Reviewable child
issues must be linked before implementation.

## Outcomes and requirements

- **FR-01 Identity.** Compare explicit persisted previous/current snapshot IDs for one supplier. Match
  products by canonical_product_id and variants by (canonical_product_id, canonical_variant_id). Titles and
  array positions are display metadata, never matching keys. Reject duplicate/conflicting identities; do not
  arbitrarily select a record. Reuse persisted identities without running historical migrations in this API; selected rows without canonical identities are rejected and need an explicit separate legacy migration.

- **FR-02 Comparable fields.** Emit individual field-change candidates for product /price, /currency,
  /in_stock, /pack_quantity and each /attributes/<escaped-key>, including warranty and pack_size attribute
  keys. Variants support /price, /in_stock and attribute leaves; inherited product currency qualifies
  variant prices, without inventing a variant currency observation. Product/variant title renames do not
  emit membership events. Warranty/pack_size do not introduce new scalar model fields or heuristic aliases;
  only explicit captured attributes count.

- **FR-03 Supported facts.** Both sides must have selected, observed, retained evidence under existing
  field-resolution policy. Resolve at each snapshot's recorded capture timestamp, so historical comparisons
  do not age out merely because queried later. Preserve candidate observations and rejection reasons.
  Missing, unknown, unsupported, conflicting, expired, future-dated or malformed values cannot become zero,
  false, USD, empty text or field removal. Return diagnostic entries for unequal/unevaluable tracked fields
  without publishing an alert. Legacy scalars alone remain unsupported.

- **FR-04 Typed comparison.** Compare finite nonnegative numeric prices using Decimal; booleans never
  qualify as prices. Stock must be bool, pack_quantity a positive non-bool integer, currency uppercase
  three-letter text. Other attribute values use existing conservative typed equivalence (NFC/trim, mapping
  key order insignificant, list order significant, no unit conversion or arbitrary casefold). Both price
  endpoints need supported identical currency. Currency differences produce a currency candidate and
  suppress price candidates with currency_mismatch; unknown currency suppresses prices with
  currency_unverified.

- **FR-05 Scope and membership.** Known equal observation_scope is mandatory for this reliable comparison,
  including field differences. Unknown/different scopes produce an explicit suppressed report, no events or
  removal candidates. A newly present product is confirmed only when the previous catalog is complete and
  the current record has at least one supported tracked field. Current partiality does not prevent a
  supported addition. A catalog is healthy-complete only when catalog_complete is True and incompleteness_reasons is empty; contradictory failure reasons prevent membership confirmation. Missing products are unobserved, never immediately removed. Removal requires old
  presence, current complete absence, and an explicitly supplied later, same-scope complete recheck with
  absence. Failed/partial/unknown catalogs cannot confirm absence. An incomplete previous catalog cannot
  prove an addition. Catalog completeness does not prove variant coverage: variant membership changes remain
  diagnostic/unverified in v1.

- **FR-06 Suspicious changes and recheck.** In policy reliable-change-v1, a price decrease >=50%, increase
  >=100%, any transition from/to zero, and every currency change are suspicious. Exact thresholds qualify;
  equivalent zero-to-zero does not. Emit pending candidates, no confirmed event, until explicit third
  snapshot recheck. Ordinary supported fields confirm immediately. Recheck performs no network. It must be
  later than current by snapshot ordering, same supplier and known scope; reject invalid IDs, wrong supplier
  or scope, and reversed ordering without writes. Price rechecks require supported currency equal to
  the candidate currency, including parent currency for variants. Missing/mismatched recheck currency
  leaves the candidate pending with currency_unverified/currency_mismatch. Supported recheck value equal to candidate new value
  confirms; equal to old value rejects; a third value rejects with superseded_value (caller may compare
  current/recheck as a new comparison). Unsupported/missing recheck leaves pending with unverified_recheck.
  Reappearing product rejects removal; partial absence leaves it pending. Store recheck snapshot/evidence
  references.

- **FR-07 Durable replay.** Add explicit opt-in report API; freeze one persisted comparison per (supplier,
  previous ID, current ID, policy version). First call creates it atomically; replays reuse IDs and stored
  evaluation. Optional recheck transitions pending -> confirmed/rejected; terminal candidates cannot be
  rewritten. Repeat same recheck is idempotent. Different recheck after a terminal result does not rewrite
  history. Reports expose all confirmed events plus new_events, the confirmed events first durably published
  by that invocation. Reopen/retry has empty new_events. Concurrent calls have one publisher; crash rollback
  leaves no partial report/outbox. This is durable publication, not guaranteed external callback delivery.
  Arbitrary overlapping historical pairs are distinct comparisons; callers should compare successive
  snapshots and use stable event IDs to deduplicate downstream delivery. Reversals A->B->A are real separate
  events. No event for B->B even with new evidence IDs/timestamps.

- **FR-08 Evidence and explanations.** Each event/candidate includes stable ID, type/state/reason, supplier
  and canonical product/optional variant ID, normalized field path, exact typed old/new values,
  previous/current snapshot IDs and qualified observation/evidence references (snapshot ID, owner
  record_key, ID). Each reference resolves to captured source URL, actual observation time and selected
  support; no fabricated confidence. Removal's new value is explicit absence, with current/recheck catalog
  metadata as coverage evidence, never a fabricated field observation. Addition old value is explicit
  absence supported by previous catalog metadata. Expiry after publication changes lookup availability to
  expired, not stored event identity/value or historical publication state.

- **FR-09 Compatibility and bounds.** Preserve changes(), price_history(), watch(), Change dataclasses,
  Product/Variant constructors and default CLI/feed formats. Existing watchers do not silently opt in.
  Reliable reports are explicit Python API with no implicit fetch, callbacks or background process. Use
  existing evidence loading/storage, scoped identity and field-resolution components. Invalid/missing
  snapshots or corrupt evidence fail explicitly and atomically; fewer than two snapshots is not silently a
  successful comparison. Initialize only bounded additive DDL without legacy backfill; never parse or mutate unrelated history. SQLite waits bounded to existing five-second policy; honor existing 16 MiB snapshot
  cap and reject oversized direct storage inputs. Limit generated candidates + diagnostics to 10,000 entries and serialized stored report to 16 MiB; overflow raises ValueError with no partial writes, never silent truncation. No implicit retry or new dependency/service requirement.

## State and boundaries

Report status: compared or suppressed with reason. Candidate states: confirmed, pending, rejected. Diagnostics
are not events. Only pending may transition and only with a valid explicit recheck. Empty/new values
distinguish absence from unknown using tagged states rather than None/default scalar ambiguity. Stable
ordering is canonical product ID, variant ID (product first), field path/type. Identity conflicts and
malformed graphs are errors; valid but unsupported values are diagnostics. Rechecks cannot publish a candidate
twice.

Non-goals: UI/dashboard, automatic scheduling/retries or network rechecks, manufacturer discovery, semantic
warranty/unit parsing, variant removal claims, probability calibration, global dedup of manually overlapping
historical pairs, or exactly-once external callback delivery. Do not infer observed commercial changes from
controlled local mutations or a repeat live capture alone.

## Acceptance and workflow

SC-01 through SC-18 in test-design.md are authoritative acceptance cases. Design review must resolve material
ambiguity before task breakdown/research gates. Follow docs/development-workflow.md with independent
G1/G2/G3/final reviews, executable failing tests before production logic, offline checks then live smoke.
