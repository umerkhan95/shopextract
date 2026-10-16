# Live field-resolution regressions

Captured 2026-10-16 by `artifacts/field-resolution-live/worker.py` using actual HTTP
responses. These fixtures retain only the price observations and referenced evidence
from same-product, same-currency API/HTML comparisons. Source URLs and original UTC
capture timestamps are retained in each contract. No source authority was relabeled.

- Magento Magebit: both API and HTML provide supported equivalent prices.
- Shopware official frontend demo: Store API supplies supported 22 EUR; the HTML
  price observation has no retained source mapping and is explicitly unsupported.
  Its compatibility default must neither create a conflict nor replace the API price.

`test_saved_live_api_html_observations_preserve_support_distinctions` replays each
contract with evaluation time fixed just after the latest source timestamp. The
fixture's unavailable HTML observation is not evidence of an actual zero price.
Controlled fault probes (altered prices/roles/times) live in the separate live harness
and are explicitly labeled synthetic; they are not included as captured store facts.
