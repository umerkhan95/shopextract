"""D01/D02 predeclared lazy sitemap requests; actual source/parser/guard paths."""
import httpx
import pytest
from shopextract.tools.runtime import ToolConfig,Limits
from shopextract.tools.security import SourceGuard
from shopextract.tools.sources import GuardedSources
from tests.test_tool_mechanisms import context
from tests.tool_api_fixtures import ORIGIN,resolver


def index(*urls):
    return '<sitemapindex>'+''.join('<sitemap><loc>'+url+'</loc></sitemap>' for url in urls)+'</sitemapindex>'


def products(*urls):
    return '<urlset>'+''.join('<url><loc>'+url+'</loc></url>' for url in urls)+'</urlset>'


@pytest.mark.asyncio
async def test_D01_cap_avoids_later_failing_sibling():
    seen=[]
    bodies={'/sitemap.xml':index(ORIGIN+'/first.xml',ORIGIN+'/slow-or-failing.xml'),
        '/first.xml':products(ORIGIN+'/products/a')}
    def wire(request):
        seen.append(str(request.url))
        return httpx.Response(200,text=bodies[request.url.path]) if request.url.path in bodies else httpx.Response(500)
    config=ToolConfig(allowed_origins=(ORIGIN,))
    source=GuardedSources(config,SourceGuard(config,resolver=resolver),httpx.MockTransport(wire))
    result=await source.execute('discover',ORIGIN,1,context(timeout=2))
    assert result=={'urls':[ORIGIN+'/products/a'],'complete':False,'diagnostics':[]}
    assert seen==[ORIGIN+'/sitemap.xml',ORIGIN+'/first.xml']


@pytest.mark.asyncio
async def test_D02_empty_denied_duplicate_and_cycle_stay_bounded():
    seen=[];denied='https://denied.example/map.xml'
    bodies={'/sitemap.xml':index(ORIGIN+'/empty.xml',denied,ORIGIN+'/empty.xml',ORIGIN+'/sitemap.xml',ORIGIN+'/valid.xml'),
        '/empty.xml':products(),'/valid.xml':products(ORIGIN+'/products/a',ORIGIN+'/products/a',ORIGIN+'/products/b')}
    def wire(request):
        seen.append(str(request.url))
        assert request.url.host=='store.example'
        return httpx.Response(200,text=bodies[request.url.path])
    limits=Limits(requests=3);config=ToolConfig(allowed_origins=(ORIGIN,),limits=limits)
    source=GuardedSources(config,SourceGuard(config,resolver=resolver),httpx.MockTransport(wire))
    result=await source.execute('discover',ORIGIN,2,context(limits,timeout=2))
    assert result['urls']==[ORIGIN+'/products/a',ORIGIN+'/products/b']
    assert result['complete'] is False and result['diagnostics']==[{'code':'rejected_source','message':'Discovered source denied'}]
    assert seen==[ORIGIN+'/sitemap.xml',ORIGIN+'/empty.xml',ORIGIN+'/valid.xml']


@pytest.mark.asyncio
async def test_E01_agent_files_skipped_before_product_map():
    seen=[]
    bodies={'/sitemap.xml':index(ORIGIN+'/agentmap.xml',ORIGIN+'/productmap.xml'),
        '/agentmap.xml':products(ORIGIN+'/agents.md',ORIGIN+'/info.MARKDOWN?lang=en'),
        '/productmap.xml':products(ORIGIN+'/products/a')}
    def wire(request):
        seen.append(str(request.url));return httpx.Response(200,text=bodies[request.url.path])
    config=ToolConfig(allowed_origins=(ORIGIN,));source=GuardedSources(config,SourceGuard(config,resolver=resolver),httpx.MockTransport(wire))
    result=await source.execute('discover',ORIGIN,1,context(timeout=2))
    assert result['urls']==[ORIGIN+'/products/a'] and result['complete'] is False
    assert [item['code'] for item in result['diagnostics']]==['unsupported_source','unsupported_source']
    assert seen==[ORIGIN+'/sitemap.xml',ORIGIN+'/agentmap.xml',ORIGIN+'/productmap.xml']


@pytest.mark.asyncio
async def test_E02_case_query_and_supported_source_modes_preserved():
    valid=[ORIGIN+'/products/a.html',ORIGIN+'/feed.csv',ORIGIN+'/feed.xml',ORIGIN+'/products/edition.v2',ORIGIN+'/products/a?download=.md']
    seen=[]
    body=products(ORIGIN+'/products/a.MD?x=1',ORIGIN+'/docs.txt',ORIGIN+'/file.pdf',*valid)
    def wire(request):seen.append(str(request.url));return httpx.Response(200,text=body)
    config=ToolConfig(allowed_origins=(ORIGIN,));source=GuardedSources(config,SourceGuard(config,resolver=resolver),httpx.MockTransport(wire))
    result=await source.execute('discover',ORIGIN,10,context(timeout=2))
    assert result['urls']==valid and result['complete'] is False
    assert [item['code'] for item in result['diagnostics']]==['unsupported_source']*3
    assert seen==[ORIGIN+'/sitemap.xml']
