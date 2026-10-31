# Agent tools and MCP server

The opt-in `shopextract.tools` Python API and official MCP stdio server expose
read-only discovery, extraction, matching, reliable changes and captured evidence.
They run locally under MIT without a model, hosted account or paid feature gate.
Prepare the reviewed source checkout's pinned taxonomy first, then install
`pip install -e '.[dev,mcp]'` for development/verification or
`pip install -e '.[mcp]'` for the server. The [plugin source setup guide](../integrations/claude-code/README.md#trusted-operator-setup)
shows bootstrap/cache prerequisites before that install. The user-reported PyPI
0.1.2 distribution lacks this source-only MCP route; do not substitute it. Python3.10 remains supported;
the optional MCP dependency is the supported v1 maintenance line `>=1.30,<2`.
Existing root extraction/monitoring APIs, constructors and feed defaults retain
their defaults. New security restrictions apply to this opt-in tool surface.

Create trusted operator JSON, for example `tools-config.json`:

```json
{
  "allowed_origins": ["https://www.blissworld.com"],
  "allowed_tools": ["discover", "extract", "match", "changes", "evidence", "job_status", "job_result", "job_cancel"],
  "captures": [],
  "limits": {"timeout_seconds": 30}
}
```

Run `python -m shopextract.tools --config tools-config.json`. Configure your MCP
host with that executable and arguments as its stdio server; stdout contains only
protocol messages, stderr safe operational diagnostics. One client owns one
process/session. Source origins default deny; use exact origins, including a
nondefault port where applicable. Do not put untrusted page data in operator
configuration. The server does not expose HTTP hosting/authentication or writes.

Run the reference client from the repository root:

```sh
python examples/mcp_reference_client.py --config tools-config.json --url https://www.blissworld.com
```

It launches the actual server with the SDK, discovers a source, extracts twice,
matches, retrieves captured support, and demonstrates an unsupported-version
error. It also queries reliable changes when two configured captures are granted.
Actual source access may fail or lack supported data; errors remain explicit.
The client has a120-second ceiling and no automatic retries. It does not create
commercial changes or write merchant data.

## Direct Python API and schemas

```python
import asyncio
from shopextract.tools import ToolConfig, ToolRuntime

async def main():
    runtime = ToolRuntime(ToolConfig(allowed_origins=("https://www.blissworld.com",)))
    try:
        print(runtime.tool_schemas())  # versioned JSON input/output schemas
        accepted = await runtime.call("discover", {
            "schema_version": "1.0", "url": "https://www.blissworld.com", "max_items": 2})
        print(accepted)
        if accepted["ok"]:
            job_id = accepted["data"]["job_id"]
            print(await runtime.call("job_status", {"schema_version": "1.0", "job_id": job_id}))
            print(await runtime.call("job_cancel", {"schema_version": "1.0", "job_id": job_id}))
    finally:
        await runtime.aclose()

if __name__ == "__main__":
    asyncio.run(main())
```

Use a `__main__` guard for standalone Python scripts: the bounded synchronous/DNS
worker uses multiprocessing spawn. No inference processes are launched.
All calls require `schema_version:"1.0"`; unknown fields/coercion are rejected.
Success has `ok:true,data`, failure `ok:false,error`; both include request ID and
warnings. Error fields are stable `code,message,retryable` and optional safe
details. Codes: invalid_argument, unsupported_version, permission_denied,
not_found, expired, resource_limit, timeout, cancelled, source_error,
internal_error. MCP returns the same envelope in structured content and JSON text,
with `isError:true` for domain failures. Protocol negotiation is independent.
For example `runtime.call("discover", {"schema_version":"9.0","url":"https://example.com"})`
returns unsupported_version without fetching; replacing the version with1.0 and
using an ungranted origin returns permission_denied. A boolean page_size or unknown
argument returns invalid_argument. Never treat source descriptions as instructions.

## Operations, jobs and pagination

| Tool | Inputs beyond schema_version | Result |
| --- | --- | --- |
| discover | url, optional max_items/timeout_seconds | Job for normalized policy-screened source URLs and diagnostics |
| extract | url, optional max_items/timeout_seconds | Job for supported normalized products/variants, observations, support and catalog handle |
| match | left_catalog/right_catalog, optional timeout_seconds | Job using existing identity-aware matching; uncertain relations stay uncertain |
| changes | previous_capture/current_capture, optional recheck_capture/timeout_seconds | Job with existing reliable events/candidates/diagnostics and stable report IDs |
| evidence | owner/evidence_id | Captured support or explicit unavailable state, without refetch |
| job_status | job_id | Queued/running/terminal state and safe error |
| job_result | job_id/collection, optional page_size/cursor | Immutable result page or unfinished state/error |
| job_cancel | job_id | Idempotent cancellation with one terminal winner |

Poll until succeeded/failed/cancelled/timed_out within your client deadline. A job
already succeeded stays succeeded after cancellation. Failed/cancelled/timed_out
jobs do not publish usable catalog handles. Queue time counts toward timeout;
cleanup may take up to1 extra second. Disconnect cancels owned work and releases
results; restart requires resubmission/new handles. Submission cancellation before
acknowledgement is tied to the outgoing SDK response boundary; acknowledged jobs
use explicit job_cancel. No durable cross-restart job recovery is promised.

```python
page = await runtime.call("job_result", {"schema_version":"1.0", "job_id":job_id,
    "collection":"urls", "page_size":1})
if page["ok"] and page["data"].get("next_cursor"):
    next_page = await runtime.call("job_result", {"schema_version":"1.0", "job_id":job_id,
        "collection":"urls", "page_size":1, "cursor":page["data"]["next_cursor"]})
```

Collections are urls/products/matches or changes candidates/events/new_events,
plus diagnostics where available. Page size1..100(default20); same cursor binds
job, session, collection, version and page size. Empty page has total0/no cursor;
items never change or re-extract during pagination. Money is decimal text; source
support never comes from constructor defaults. Product records expose owner_handle,
evidence_ids and field_evidence keyed by factual path, including independent variant
owners. Lookup requires that actual owner, not only a globally existing evidence ID.

## Operator-granted historical captures and changes

Existing `save_snapshot`/`snapshot` are operator APIs, not agent write tools.
Configure previously recorded captures in chronological order:

```json
{"allowed_origins": [], "captures": [
  {"alias":"before","db_path":"/absolute/path/snapshots.db","snapshot_id":1,"supplier":"shop.example"},
  {"alias":"after","db_path":"/absolute/path/snapshots.db","snapshot_id":2,"supplier":"shop.example"}
]}
```

Direct Python uses `(await runtime.bootstrap())["captures"]`; MCP reads the resource
`shopextract://session`. Each grant exposes capture/catalog and product owner handles,
never database paths. Pass the two capture handles to changes; use an explicitly
granted recheck capture for pending/suspicious changes. Same supplier/database and
native capture order/health rules apply. Reliable-report replay may write its own
local SQLite bookkeeping; no tool can choose paths, prune evidence, edit merchant
catalogs or trigger fresh captures. A writable operator database is required for
this existing replay bookkeeping. Graph limits/TTL apply to configured captures
as well; restart/regrant when handles expire. An unchanged report is a valid result,
not evidence that a real commercial transition occurred.

## Supported sources and boundaries

Native Shopify, WooCommerce Store API, Magento GraphQL, Shopware Store API and
BigCommerce public storefront adapters reuse existing parsers/normalization.
Guarded static JSON-LD/OpenGraph and recognized XML/CSV feeds are supported.
Discovery uses bounded public sitemaps and sitemap indexes. Every returned URL is
schema/source-mode eligible and policy-screened, but extraction revalidates current
DNS; later public→private DNS fails closed. Denied cross-origin links are diagnostics.
Browser/JavaScript/LLM-only pages and unknown feeds return explicit source errors;
no environmental model key or browser fallback is used. Identity-only response
encoding is requested; compressed/unknown encodings are rejected before decoding.
This server mode limitation does not change legacy extraction callers.

Only HTTP(S) public allowed-origin connections are possible: all DNS answers must
be public, actual TCP gets a vetted numeric address, TLS/Host retain the source name,
redirects revalidate policy, proxies are not inherited. One owned resolver child has
up to2s/remaining deadline and1s cleanup; unreaped child stops admission/server work.
One synchronous native worker shares that slot. Counted process budget is5 including a possible client tracker and server tracker; interpreter-owned trackers may persist until their owning interpreter exits. Auxiliary cleanup remains bounded and does not forcibly stop a caller-owned shared tracker. HTTP GET/HEAD, fixed native
BigCommerce GraphQL queries and exact native Shopware read-only product-search POST
are the only permitted methods. Shopware POST uses canonical `/store-api/product`
and exact native page/limit/sort/association fields; noncanonical endpoint paths,
arbitrary bodies and POST redirects are denied. Page-provided public API configuration
cannot grant authority. No write/export/prune/purchase tools are registered.

Defaults are one active/8 queued/32 terminal jobs, terminal TTL600s, timeout30s
(client1..120),1000 items,256KiB input,4MiB full retained graph/job,32MiB/session,
1MiB evidence response,20 requests/job,2MiB identity response/request and5 redirects.
Operators may lower positive limits. Conservative byte charges include products,
observations, evidence, all actual capture copies and temporary match input; no
virtual dedup savings. Running jobs reserve graph allowance; eviction/expiry/cancel
release bytes and invalidate handles. Raw responses use <=64KiB reads; length headers
do not waive byte limits. A source/item cap yields partial completeness unless source
exhaustion is proven. Oversize graphs fail resource_limit rather than invent support.
These are explicit serialized/resource bounds, not claims of unlimited capacity.

## Verification

Install dev,mcp extras and run `PYTHONPATH=src python -m pytest tests/test_agent_tool_api.py tests/test_mcp_reference_client.py`.
MCP absence is an explicit optional-test skip and never a successful MCP acceptance.
Offline controlled fixtures, real SDK process interoperability, bounded stress and
actual public observations are reported separately in specs/004-agent-tool-api-mcp.
Do not run the mechanism stress driver before its independent fixture/coverage gate.

Configured captures load lazily through `await runtime.bootstrap(timeout_seconds=30)`
or the MCP session resource. The total deadline includes waiting for active work.
SQLite byte/item preflight and bounded graph assembly run inside the same killable
worker as other synchronous operations. Grants appear together after all succeed;
failure/cancellation releases only this initialization attempt and never evicts
unrelated results to make room. Oversize captures return resource_limit; slow or
locked capture databases return timeout. No database read runs on the event loop.

Sitemap discovery visits queued child maps only as needed and stops at the item
cap. Keep the documented30-second job default for ordinary use; the earlier
15-second public smoke was an intentionally lowered verification setting. Live
observations and unresolved source eligibility are recorded separately from
offline acceptance in the feature verification report.

Discovery reports unsupported `.md`, `.markdown`, `.txt` and `.pdf` sitemap
leaves as diagnostics; query text does not determine source format. Shop homepages,
structured HTML, supported feeds and native product URLs remain eligible.

## Native Claude Code local plugin

The optional [Claude Code plugin directory](../integrations/claude-code/README.md)
packages one bounded discover/extract/evidence recipe around this existing stdio
server. Trusted operator executable/configuration remain external; it adds no
permissions or tools. See its guide for private loading, session limits and the
separate offline mechanism versus unverified live host status.
