# Isolated main integration independent review

Reviewer `/root/audit_plan_review`,2026-11-01. Bounded staged-source inspection
only; no tests/full/network/new features or cherry-pick continuation/push.
Scope:492f89e onto319ee9b, fix/audit-remediation-main.

Disposition: one concrete integration blocker. In `_discover_via_sitemap`,
`if native.urls:return list(native.urls)` precedes `native.stop_fallback` handling.
The retained main traversal returns positive URLs AND stop_reason=native_sitemap_budget
on request/byte cap. With positive retained URLs the wrapper drops that reason,
contradicting integration-main.md's forwarded-stop-reason contract and remediation
budget diagnostics. Record the native stop reason before returning retained URLs;
retain no-fallback behavior. Verify one actual positive-then-budget traversal,
not a mocked result, before marking this source integration passed. No new
architecture is needed.

Otherwise inspected preservation is sound: main native traversal is retained with
12request/20MiB/robots/scoped/category-map handling; adapter stream is one physical
send and reuses cached robots, main longest-match behavior preserved. Static
image/brand/SKU helper remains single-product, explicit brand conflicts suppress
refill, ImageObject source pointers target actual leaf. Main Magento HTML analysis
and listing categories remain. No QuantityValue/MISSING_QUANTITY/refrigerator
attribute dependencies found in integrated src; portable and maintenance changes
against main are remediation-only. No unmerged index entries.

Saved89critical+115remediation selected passes are scoped evidence only; no
integrated-source full pass. Historical2229 pass predates compression and is not
a final gate. Latest full/resource, browserlive and Khaadi observations remain
pending/blocked/inconclusive as documented. Draft PR may describe this exact
state; this review grants no merge/complete approval. Original workspace untouched.

```json
{
  "src/shopextract/_discover.py": "200218f51dbf5fc25c50425096eb7d6ca6519ea92e529258456374341da50a32",
  "src/shopextract/_discovery_runtime.py": "6ef652e554252b7f2a4b6af5cc96af3c05e4a3163bccbb731860dcebbc406d2d",
  "src/shopextract/_discovery_sitemaps.py": "62136a81628f3e428e7305705c6391039b915173dc22d500088f2cdd53ad0bac",
  "src/shopextract/_structured_html.py": "3e842dcf374bf984082bb7b8a1e0b1628373099e885f0d0544c79503d8046103",
  "src/shopextract/extractors/_product_html.py": "f0366834f265dacadf11bc9ab63de3fc207ce5c3e130413dc922bcb93c1c5826",
  "src/shopextract/_portable.py": "a7188d082cdb0dd21c4871ecd5d3f8887921a7ed8a20aa01a911a1a4a29b1af0",
  "src/shopextract/maintenance/engine.py": "2183c982ba997c7cb160e166d51ffcf9dd6431f3f73eb78140331c7b0d83430f",
  "specs/013-audit-remediation/integration-main.md": "ce340904d6196c020687f54d0fe0fb9ae0876988ff4b874592b47c4d0fd68f3d"
}
```

## Exact blocker repair re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01. Only exact source reorder and new
regression inspected, no probes/tests/network/commit/push. Native stop reason is
now noted before returning positive URLs; stop_fallback still suppresses legacy
restart when no URLs. Actual parser/MockTransport regression uses3requests:
robots,index,firstleaf; retains exact URL and budget reason, fails any extra
request. Saved missing-diagnostic red then59relatedPASS6.15s accepted as scoped
evidence. Prior concrete blocker resolved; bounded source integration PASS.
This permits primary's draft publication workflow, not merge/complete approval.
Integrated latest-source full/resource and browser/Khaadi qualifications remain
pending as above; no historical test pass is relabelled currentfull.

```json
{
  "src/shopextract/_discover.py": "9fedf3c3829eb9b7344684f36a972aacef92f654a8bc45353601082c95e10ac5",
  "tests/test_discovery_sitemap_bounds.py": "b03ab044ddbf2de633cc9cfb82e66e630126b8e9e4e1c707ae2ca71bc736ec47",
  "specs/013-audit-remediation/integration-main.md": "f11aa2a3f2fea8dbca3ee5f91d5204a47b0ac92ae404473f6274321b81031623"
}
```
