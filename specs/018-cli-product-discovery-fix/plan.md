# Implementation plan

## Constitution check

Preserve public extraction APIs, Product/Variant identity and evidence, output
formats and honest coverage semantics. Use bounded, reproducible verification;
keep the implementation self-hostable with existing dependencies. Scope is the
existing native CLI route for a 50-product sample.

## Architecture and decisions

Research identifies the gap in `src/shopextract/_discover.py`: generic sitemap
indexes are discarded and `AsyncUrlSeeder` can enumerate 5,000 host URLs before
the browser fallback. The existing extract call chain passes `max_urls` to
discovery but drops the caller's remaining deadline. The repair will add native
robots/sitemap/index traversal ahead of that legacy path and propagate the
requested URL cap and active deadline through discovery. Keep platform API and
product-sitemap precedence/fallback compatibility; successful native results
must avoid broad seeder/browser work.

The native walker owns URL eligibility, canonical duplicate/cycle suppression,
origin and store-path checks, robots decisions, source request/byte/time caps,
and cancellation propagation. It returns at most the requested number of
eligible product URLs. Category/collection-only sitemap leaves are excluded.
Use existing HTTP/XML/filter infrastructure where possible; add no parallel
operational crawler. Existing extractors continue to parse real product pages
and build existing records. A capped sample remains partial/unverified.

Bound proposal: 12 source requests, 20 MiB aggregate, 10 MiB per response,
30-second native traversal maximum, each request at most 15 seconds and capped
by the enclosing remaining deadline. These limits derive from `test-design.md`;
G1 must approve them before they become implementation contracts. Timeout or
cancellation must stop work without publishing a successful empty result or
starting a fallback after the operation deadline.

Detailed interface decisions belong in `skeleton.md`; reusable ownership and
lifecycle belong in `components.md`. Do not treat this plan as approval of
unreviewed interfaces.

## Required gates

G1 reviews behavior, tests, tasks, research and this plan. G2 reviews the
interface skeleton and executable red. G3 reviews reusable component ownership.
All verdicts and revisions belong in `reviews.md`; implementation waits for G3
and saved red evidence. A changed behavior contract returns to design and
invalidates affected reviews.

## Verification and handoff

First save a failing 3-page acceptance red, then implement one bounded task at a
time. Exercise the actual production sitemap parser, URL filters, product
extractors, normalization and CLI output using deterministic controlled HTTP
fixtures. Run the saved 3-page smoke before the fixed-seed adversarial/stress
matrix; stop on first failure and permit one diagnosed repair per blocker.
Record commands, fixture seed/configuration, counts, result and environment in
`verification.md`.

Run focused regressions and the full `python scripts/run_tests.py` driver. The
reported macOS failures in existing native-Linux-only tests must be classified
with exact evidence; do not substitute a partial suite for the required full
gate. If the current host cannot support a gate, request/obtain a supported
environment result or leave the gate incomplete.

After affected offline success and the required full-driver result is recorded
and classified under the host disposition below, run the live `naheed.pk` CLI max-3
smoke with timeout 60 and save it before max-50 with timeout 300. Use the
existing command, inspect the real output and sources, and report actual valid
product count and partial/catalog coverage metadata. Live output cannot be
fabricated from fixtures, and no run establishes full-catalog completeness.

## Host verification disposition
The required full driver will be executed, not bypassed or replaced by focused tests. Current-host baseline already records17macOS/nativeLinux-supervision failures plus one existing resource-dependent skip; Docker Linux probe itself failed, so no supported-container proof is available. Keep whole-repository gate explicitly incomplete if these unchanged failures recur. For this explicitly requested read-only live diagnosis, run the reviewed smoke/50 CLI only after new acceptance, adversarial and affected offline checks pass and the full driver result is recorded/classified. A blocked unrelated baseline is not promoted to PASS, and no overall full-repository verification is claimed. Final review must separately assess the fix, actual live result, and unresolved full gate.
