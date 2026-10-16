import json,time
from pathlib import Path

def main():
 start=time.monotonic()
 import pytest
 from tests.tool_fixture_budget import FixtureBytesPlugin
 ledger=FixtureBytesPlugin()
 nodes=['tests/test_tool_discovery_lazy.py','tests/test_agent_tool_api.py::test_complete_domain_flow_uses_native_code_paths','tests/test_tool_mechanisms.py::test_discovered_denied_link_is_diagnostic_only','tests/test_tool_mechanisms.py::test_dns_change_after_discovery_denies_extraction','tests/test_mcp_reference_client.py::test_reference_mcp_client_complete_flow']
 code=int(pytest.main(nodes+['-q','--tb=short','-p','no:cacheprovider'],plugins=[ledger]))
 result={'exit':code,'nodes':nodes,'runner_seconds':time.monotonic()-start,'measured_fixture_bytes':sum(ledger.counts.values()),'fixture_categories':dict(ledger.counts),'byte_measurement_scope':'Actual HTTP response/graph representations in pytest process; existing SDK fixture server subprocess is outside this ledger, no aggregate byte-cap claim'}
 Path('artifacts/agent-tool-api-mcp/discovery-eligibility-green-caps.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return code
if __name__=='__main__':raise SystemExit(main())
