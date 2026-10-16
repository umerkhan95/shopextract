"""SC-02 genuine SDK subprocess flow; controlled outbound source, not public live."""
import asyncio
import json
import os
import sys
from pathlib import Path
import pytest
pytest.importorskip('mcp', reason='MCP feature verification requires the mcp extra')
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from tests.test_agent_tool_api import reference_flow


@pytest.mark.asyncio
async def test_reference_mcp_client_complete_flow():
    root = Path(__file__).resolve().parents[1]
    params = StdioServerParameters(command=sys.executable,
        args=['-m', 'tests.mcp_fixture_server'], cwd=str(root),
        env={**os.environ, 'PYTHONPATH': str(root / 'src') + os.pathsep + str(root)})
    async def exercise():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as client:
                initialized = await client.initialize()
                assert initialized.serverInfo.name == 'shopextract'
                async def call(name, arguments):
                    result = await client.call_tool(name, arguments)
                    assert not result.isError, result
                    if result.structuredContent:
                        return result.structuredContent
                    return json.loads(result.content[0].text)
                await reference_flow(call)
    await asyncio.wait_for(exercise(), timeout=10)
