# R1b/R2 component ownership — G3 proposal

The lightweight `_http_defaults` module owns the existing header dictionary,
HTTP user-agent string and function. Native Shopify/Woo/legacy Magento import
those exact objects; `_browser` reexports them. Browser configuration/class access
retains its existing loading behavior. No wrappers, environment probes or caches.

Woo owns product/page accounting. Optional max_products validates before I/O;
None retains legacy pagination. A bounded request uses page=1, explicit offset
from accepted catalog rows, shrinking per_page and ascending ID order. Local page
counter owns max_pages and pages_completed. Exact full response at budget means
partial unless a valid total confirms exhaustion; clipping never implies complete.
Pipeline and guarded native provider pass the limit before the first request.
Variant-detail limits remain separate and cannot enlarge the parent product cap.

The existing execution state owns the monotonic deadline. `_retry.wait_for_retry`
parses seconds/HTTP-date, treats invalid/negative as fallback2, compares remaining
budget before sleeping and returns False if insufficient. Both Woo and Shopify
retain accepted base records with an incomplete diagnostic; retry at most once.
No global clock mutation or detached task. Existing caller cancellation propagates.

Twenty-four new cases cover module identity, actual HTTP loops, source continuity,
retry deadline, invalid limits and public API/native tool forwarding. R3 progress,
R4 worker/robots and R5 ordering remain future stages, not approved by this file.
