"""Bounded genuine SDK handshake/call/disconnect, not feature integration proof."""
import asyncio,inspect,json,sys
from pathlib import Path
from importlib.metadata import version
from mcp import ClientSession,StdioServerParameters,types
from mcp.client.stdio import stdio_client
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

async def serve():
    server=Server('sdk-probe',version='1')
    @server.list_tools()
    async def tools():
        return [types.Tool(name='ping',inputSchema={'type':'object','properties':{}})]
    @server.call_tool()
    async def call(name,args):
        return {'probe':'ok'}
    async with stdio_server() as (read,write):
        await server.run(read,write,server.create_initialization_options())

async def probe():
    p=StdioServerParameters(command=sys.executable,args=[str(Path(__file__).resolve()),'serve'])
    async with stdio_client(p) as (read,write):
        async with ClientSession(read,write) as session:
            initialized=await session.initialize()
            listed=await session.list_tools()
            result=await session.call_tool('ping',{})
            assert initialized.serverInfo.name=='sdk-probe'
            assert listed.tools[0].name=='ping'
            assert result.structuredContent=={'probe':'ok'}
    print(json.dumps({'mcp':version('mcp'),'python':sys.version.split()[0],
        'initialize_list_call_disconnect':'pass','Server.run':str(inspect.signature(Server.run)),
        'ClientSession.call_tool':str(inspect.signature(ClientSession.call_tool))}))

if __name__=='__main__':
    asyncio.run(serve() if sys.argv[-1]=='serve' else asyncio.wait_for(probe(),timeout=8))
