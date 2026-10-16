"""Real stdio MCP fixture, controlled outbound boundary, never public-live evidence."""
import asyncio
from shopextract.tools.mcp_server import serve
from tests.tool_api_fixtures import runtime

if __name__ == '__main__':
    asyncio.run(serve(runtime()))
