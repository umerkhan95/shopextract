# INT-08: Make custom app connections and modules

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#70](https://github.com/umerkhan95/shopextract/issues/70).
Related planned work: [INT-01 / #63](https://github.com/umerkhan95/shopextract/issues/63).

Status: planned; researched2026-10-24. Owner: Make integration maintainer.
Dependency: INT-01; optional later push reuses #27. Covers FR10/04/14, SC10/04/14.
No app is installed or published in this planning task.

## Construction and authentication

Define a custom app with common base request/response handling, one connection,
actions for submit/status/cancel and search for result pages, plus new-completed-job
polling trigger. Keep definitions exported/version-controlled, with clear app/module
names and typed output interfaces. [Connections](https://developers.make.com/custom-apps-documentation/app-components/connections)
provide common auth patterns and protected common data. Use scoped bearer credentials
or service OAuth; module inputs cannot override destination/auth headers or select
operator paths. Only service-allowed merchant origins can be extracted.

Use request/response declarations and IML mappings over INT-01; no embedded Python
or ad hoc browser scraping in modules. Every output bundle includes canonical record
identity, decimal text/currency, variants and evidence/completeness fields. Job metadata
is distinct from product output. Pending job returns explicit pending state, not an
empty successful search. Do not use an unbounded wait inside the module.

## Paging, polling and failures

Map service `next_cursor` using Make's [pagination block](https://developers.make.com/custom-apps-documentation/component-blocks/api/pagination);
keep original owner/job/collection/page size bindings. Add a strict return limit;
do not request unlimited full catalogs or infer numeric offsets from opaque cursors.
Set bounded requests/timeouts based on actual Make runtime and account limits verified
before implementation, with service caps as upper bound.429 retries respect Retry-After
and remaining budget;400/401/403 do not repeatedly submit jobs.

[Polling triggers](https://developers.make.com/custom-apps-documentation/best-practices/trigger-modules)
need compatible identity/order/start-point semantics. Use sorted completed records
and per-principal monotonic commit-sequence ordering with service checkpoint filtering; test
late same-timestamp/lower-ID, backward-clock and multi-page cases. No bundles on unchanged successful poll is valid;
it does not prove products were removed. Completion journal gap surfaces explicit
recovery guidance. Fresh-capture monitoring and signed instant triggers remain separate
extensions; implement no alternate outbound delivery engine in this ticket.

## Acceptance and future verification

- [ ] Private connection test works without leaking credentials, operator paths or cross-owner metadata.
- [ ] Submit/status/result/search modules emit correctly typed bundles; two-page results preserve exact decimal/evidence/variant identities.
- [ ] Pending then completed-empty is distinguished; unchanged polling yields no new completion, never invented deletion.
- [ ] Late equal-timestamp and backward-clock completions, response loss, paused schedule and retention gap follow explicit checkpoint semantics; cancelled/failed job cannot appear successful.
- [ ] Package export/source review and real module request/response harness pass; one private scenario action/search/two polls is recorded live after offline success.

## Distribution and blockers

[Visibility](https://developers.make.com/custom-apps-documentation/create-your-first-app/app-visibility)
distinguishes private app, published invite link and approved catalog app. Invite
publishing is not fully reversible in UI; no auto-publication during private smoke.
Approved distribution and updates require Make's review process; record exact account,
region, app version and status. Developer/custom-app rights, scenario credits, public
API endpoint and current quotas remain prerequisites. Future live limit ≤12service
requests/two products/120seconds with one transient retry and ≤6source requests.

Journal sequence/checkpoints remain decimal text or opaque tokens across JavaScript
outputs; never cast to Number. SC04/14 test9007199254740993 losslessly.
