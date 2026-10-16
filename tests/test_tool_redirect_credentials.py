"""F01 predeclared real-wire credential isolation on allowed-origin redirects."""
import asyncio
import httpcore
import httpx
import pytest
from shopextract.tools.runtime import ToolConfig
from shopextract.tools.security import GuardedTransport,SourceGuard
from tests.test_tool_mechanisms import context
from tests.tool_api_fixtures import resolver

@pytest.mark.asyncio
@pytest.mark.parametrize('cross_origin',[True,False])
async def test_native_context_redirect_credentials(monkeypatch,cross_origin):
    received=[];connections=[];target_url=[None]
    async def serve(reader,writer):
        raw=await reader.readuntil(b'\r\n\r\n')
        lines=raw.decode().split('\r\n');headers={k.lower():v.strip() for k,v in (line.split(':',1) for line in lines[1:] if ':' in line)}
        received.append((lines[0],headers))
        if lines[0].split()[1]=='/store-api/context':
            response=f'HTTP/1.1 302 Found\r\nLocation: {target_url[0]}\r\nContent-Length: 0\r\n\r\n'.encode()
        else:response=b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nok'
        writer.write(response);await writer.drain();writer.close();await writer.wait_closed()
    first=await asyncio.start_server(serve,'127.0.0.1',0)
    second=await asyncio.start_server(serve,'127.0.0.1',0)
    a=f'http://first.example:{first.sockets[0].getsockname()[1]}'
    b=f'http://second.example:{second.sockets[0].getsockname()[1]}' if cross_origin else a
    target_url[0]=b+'/finish'
    original=httpcore.AnyIOBackend
    class LocalBoundary:
        async def connect_tcp(self,host,port,**kwargs):
            connections.append(host)
            return await original().connect_tcp('127.0.0.1',port,**kwargs)
    monkeypatch.setattr(httpcore,'AnyIOBackend',LocalBoundary)
    cfg=ToolConfig(allowed_origins=(a,b));ctx=context(timeout=4)
    transport=GuardedTransport(cfg,ctx,SourceGuard(cfg,resolver=resolver))
    credentials={'sW-aCcEsS-kEy':'key_canary','SW-Context-Token':'context_canary',
        'X-BC-Customer-Access-Token':'bc_canary','x-bc-customer-id':'id_canary',
        'Authorization':'Bearer auth_canary','Cookie':'cookie_canary','X-Secret':'unknown_canary'}
    try:
        async with httpx.AsyncClient(transport=transport) as client:
            reply=await client.get(a+'/store-api/context',headers={**credentials,'Accept-Language':'en'})
            assert reply.text=='ok'
        assert len(received)==2 and set(connections)=={'93.184.216.34'}
        assert all(received[0][1][k.lower()]==v for k,v in credentials.items())
        target=received[1][1]
        assert target['host']==httpx.URL(b).netloc.decode() and target['accept-language']=='en'
        assert 'authorization' not in target and 'cookie' not in target
        for k,v in credentials.items():
            if k.lower() in {'authorization','cookie'}:continue
            if cross_origin:assert k.lower() not in target
            else:assert target[k.lower()]==v
    finally:
        first.close();second.close();await first.wait_closed();await second.wait_closed()
