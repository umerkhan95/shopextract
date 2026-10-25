# INT-03: Native n8n node and completed-job trigger

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#65](https://github.com/umerkhan95/shopextract/issues/65).
Related planned work: [INT-01 / #63](https://github.com/umerkhan95/shopextract/issues/63).

Status: planned; researched2026-10-24. Owner: n8n connector maintainer. Dependency:
INT-01; remote MCP optional, not required. Covers FR05/04/14, SC05/04/14. This is a
native deterministic HTTP integration: ordinary workflows require no LLM.

## Connector construction and packaging

Create a TypeScript package proposed as `n8n-nodes-shopextract`. The official
[node CLI](https://docs.n8n.io/connect/create-nodes/build-your-node/using-the-n8n-node-tool.md)
provides scaffolding; choose declarative HTTP actions where sufficient, with a
separate programmatic polling trigger in the same package. Do not implement custom
flow-control logic simply to wait; expose submit/status/result/cancel so standard
schedule/wait nodes can orchestrate work. Capture normalized API request/output
contracts in tests before writing execution code.

Define a service-base-URL and credential class using n8n's
[credential contract](https://docs.n8n.io/connect/create-nodes/build-your-node/reference/credentials-files.md).
Use scoped bearer auth for private self-hosted setup; optional OAuth only after
service flow is defined. Credentials stay within platform credential storage and
must never follow a user-controlled result URL to another origin. The node cannot
turn source URL into service URL or forward bearer auth to stores.

[Verification requirements](https://docs.n8n.io/connect/create-nodes/build-your-node/reference/verification-guidelines.md)
constrain package design: no external dependencies, filesystem/environment access;
English documentation/UI, MIT, provenance publication and valid public source.
Therefore use built-in HTTP helpers, not embedded Python or a new SDK dependency.
Package metadata lists nodes/credentials; [submission](https://docs.n8n.io/connect/create-nodes/deploy-your-node/submit-community-nodes.md)
is a separate release step after private testing. No verified/Cloud availability is
claimed from installing a private package.

## Operations and failure semantics

Initial actions map eight approved tools and capability preflight; result pages
emit stable product/variant/evidence fields, decimal strings and completeness.
Return job identity promptly, not a long synchronous crawl. Completed-job trigger
polls the owner's retained completion listing; event ID is completion identity,
not mutable product name or price. Checkpoint uses the service commit sequence, not terminal timestamps; late/backward-clock completions stay visible. First-start checkpoint, pause/resume, replay and
retention-gap behavior must be explicit. New commercial-change triggers/fresh snapshot
scheduling are future extensions; existing granted captures permit manual changes
review. Optional signed push requires #27, not a custom unaudited webhook implementation.

## Acceptance and future verification

- [ ] Private node credential test succeeds for correct service; malformed base URL, revoked token and cross-owner IDs fail safely.
- [ ] Submit returns durable identity; standard workflow later gets exact immutable result pages. Pending is not empty success.
- [ ] Two polls with same completed job emit one new completion within retained checkpoint contract; restart/response loss does not resubmit extraction.
- [ ] 429/backoff and deadline/cancel paths are bounded; decimal `0.10`, variants, unknown stock and evidence survive item conversion.
- [ ] Lint/package scan/native runner checks and focused fixture tests pass; one private action plus two trigger polls recorded live after offline success.

Framework/runtime versions, installation permission and plan-specific HTTP/execution
limits must be rechecked before implementation; use lower service/platform caps.
Save exact tested node/n8n/service versions. Developer account/npm ownership and
external verification approval are publication prerequisites. No connector package
was built, installed, submitted or tested by this planning task.

Journal sequence/checkpoints remain decimal text or opaque tokens across JavaScript
outputs; never cast to Number. SC04/14 test9007199254740993 losslessly.
