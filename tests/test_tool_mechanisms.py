"""Seed24 finite adverse mechanisms. DO NOT run driver before fixture review."""
import asyncio
import copy
import json
import time
from datetime import datetime, timezone
from pathlib import Path
import httpcore
import httpx
import pytest
from shopextract.tools import Limits, ToolConfig, ToolRuntime
from shopextract.tools.context import OperationContext, OperationBudget
from shopextract.tools.contracts import ToolError, encoded, validate
from shopextract.tools.execution import OwnedProcess
from shopextract.tools.jobs import JobManager
from shopextract.tools.security import SourceGuard, GuardedTransport, PinnedBackend, normalized
from shopextract.tools.state import RetainedGraph, SessionStore
from tests.tool_api_fixtures import ORIGIN, HTML, resolver, runtime as sample_runtime
from tests.test_agent_tool_api import completed
from tests.tool_fixture_budget import charge


def context(limits=None, auxiliary=None, timeout=3):
    limits = limits or Limits()
    return OperationContext('case24', time.monotonic()+timeout, asyncio.Event(),
        OperationBudget(limits), auxiliary, datetime(2026,10,16,10,tzinfo=timezone.utc))


def guarded(response, *, limits=None, dns=resolver):
    config = ToolConfig(allowed_origins=(ORIGIN,), limits=limits or Limits())
    ctx = context(config.limits)
    return GuardedTransport(config, ctx, SourceGuard(config, resolver=dns), httpx.MockTransport(response))


def _stall_child(connection, kind, payload, maximum):
    # Controlled external OS-resolution/domain boundary, not algorithm substitute.
    time.sleep(10)


def _late_resolver_child(connection,kind,payload,maximum):
    import signal
    data=json.loads(payload);barrier=Path(data['barrier'])
    def late(signum,frame):
        barrier.with_suffix('.late').write_text('late-reply-attempt')
        try:connection.send_bytes(encoded({'ok':True,'value':['93.184.216.34']}))
        except (OSError,BrokenPipeError):pass
        raise SystemExit(0)
    signal.signal(signal.SIGTERM,late)
    barrier.write_text('resolver-started')
    time.sleep(10)


def _blocking_report_child(connection,kind,payload,maximum):
    from shopextract.monitor import reliable
    from shopextract.tools.execution import _execute
    data=json.loads(payload)
    barrier=data.pop('barrier')
    def before_commit(conn):
        Path(barrier).write_text('transaction-open')
        time.sleep(10)
    reliable._before_commit=before_commit
    connection.send_bytes(encoded({'ok':True,'value':_execute(kind,data)}))


def test_contract_missing_null_false_and_nonfinite():
    """Invalid schema distinctions reject before backend and serialize no nonfinite JSON."""
    deep=[]
    for _ in range(2000):deep=[deep]
    with pytest.raises(ToolError,match='invalid_argument'):
        validate('extract',{'schema_version':'1.0','url':deep},Limits())
    from jsonschema import validate as schema_validate
    from shopextract.tools.contracts import schema,envelope
    for name in ('discover','job_status','job_result','evidence'):
        schema_validate(envelope(error=ToolError('invalid_argument')),schema(name)['outputSchema'])
    from jsonschema import ValidationError
    with pytest.raises(ValidationError):
        schema_validate(envelope({'job_id':'j','state':'bogus'}),schema('discover')['outputSchema'])
    bad_error=envelope(error=ToolError('invalid_argument'));bad_error['error']['retryable']='yes'
    with pytest.raises(ValidationError):schema_validate(bad_error,schema('evidence')['outputSchema'])
    for config in (ToolConfig(limits=Limits(item_count=True)),ToolConfig(limits=Limits(item_count=1001)),ToolConfig(allowed_tools=('write',))):
        with pytest.raises(ValueError):ToolRuntime(config)
    for args in ({}, {'schema_version':'1.0','url':None}, {'schema_version':'1.0','url':''},
                 {'schema_version':'1.0','url':ORIGIN,'max_items':False},
                 {'schema_version':'1.0','url':ORIGIN,'timeout_seconds':float('nan')}):
        with pytest.raises(ToolError):validate('extract',args,Limits())


def test_input_byte_limit_edges():
    """Byte admission counts UTF8 and rejects max+1 independently of field validity."""
    args={'schema_version':'1.0','url':ORIGIN}
    size=len(encoded(args))
    assert validate('extract',args,Limits(input_bytes=size))==args
    with pytest.raises(ToolError,match='resource_limit'):validate('extract',args,Limits(input_bytes=size-1))


def test_cursor_tamper_collection_and_session():
    """Authenticated cursor cannot move across sessions/collections or mutate offset."""
    store=SessionStore(Limits());store.publish('j',RetainedGraph({'urls':['a','b'],'products':[]},{},'complete'))
    cursor=store.page('j','urls',1,None)['next_cursor']
    for bad,collection in [(cursor+'x','urls'),(cursor,'products')]:
        with pytest.raises(ToolError,match='invalid_argument'):store.page('j',collection,1,bad)
    other=SessionStore(Limits());other.publish('j',RetainedGraph({'urls':['a','b']},{},'complete'))
    with pytest.raises(ToolError,match='invalid_argument'):other.page('j','urls',1,cursor)


def test_empty_page_and_zero_total():
    """Authoritative empty collection has one terminal empty page, no phantom cursor."""
    store=SessionStore(Limits());store.publish('j',RetainedGraph({'urls':[]},{},'complete'))
    page=store.page('j','urls',100,None)
    assert page['items']==[] and page['total']==0 and page['next_cursor'] is None


@pytest.mark.asyncio
async def test_queue_limit_and_waiting_deadline():
    """One active+one queued; third rejected, queued absolute deadline never resets."""
    limits=Limits(queued_jobs=1);store=SessionStore(limits);jobs=JobManager(store,limits)
    entered=asyncio.Event()
    async def wait(ctx):entered.set();await asyncio.Event().wait()
    a=jobs.submit(wait,1);await entered.wait();b=jobs.submit(wait,.02)
    with pytest.raises(ToolError,match='resource_limit'):jobs.submit(wait,1)
    await asyncio.sleep(.04)
    assert jobs.status(b['job_id'])['state']=='timed_out'
    await jobs.close();assert store.used_bytes==0


@pytest.mark.asyncio
async def test_resolver_process_stall_is_reaped():
    """Actual stalled child is killed/reaped at resolution budget; no later worker leaks."""
    limits=Limits(resolver_seconds=.05,cleanup_seconds=.2)
    owner=OwnedProcess(limits,child_target=_stall_child);ctx=context(limits,owner)
    before=time.monotonic()
    with pytest.raises(ToolError,match='timeout'):await owner.run('resolve',encoded({'host':'store.example'}),ctx)
    assert owner.process is None and time.monotonic()-before<1


@pytest.mark.asyncio
async def test_repeated_process_cancel_no_accumulation(tmp_path):
    """Three explicit cancellation lifetimes share one slot and leave zero child handles."""
    limits=Limits(cleanup_seconds=.3);owner=OwnedProcess(limits,child_target=_late_resolver_child)
    for index in range(3):
        ctx=context(limits,owner)
        barrier=tmp_path/f'resolver-{index}.ready'
        task=asyncio.create_task(owner.run('resolve',encoded({'host':'store.example','barrier':str(barrier)}),ctx))
        for _ in range(300):
            if barrier.exists():break
            await asyncio.sleep(.005)
        assert barrier.exists(), 'Controlled resolver did not start'
        ctx.cancelled.set();task.cancel()
        with pytest.raises(asyncio.CancelledError):await task
        assert barrier.with_suffix('.late').exists()
        assert owner.process is None



@pytest.mark.asyncio
async def test_domain_process_deadline_no_success():
    """Noncooperative synchronous work cannot outlive its bounded process deadline."""
    limits=Limits(cleanup_seconds=.2);owner=OwnedProcess(limits,child_target=_stall_child)
    with pytest.raises(ToolError,match='timeout'):await owner.run('domain',b'{}',context(limits,owner,.05))
    assert owner.process is None


@pytest.mark.asyncio
async def test_reaper_failure_stops_replacement():
    """Injected unreapable OS boundary makes owner broken, never launches replacement."""
    class Unreapable:
        def is_alive(self):return True
        def terminate(self):pass
        def kill(self):pass
    owner=OwnedProcess(Limits(cleanup_seconds=.01));owner.process=Unreapable()
    with pytest.raises(ToolError,match='internal_error'):await owner.cancel_and_reap()
    assert owner.broken
    with pytest.raises(ToolError,match='resource_limit'):await owner.run('resolve',b'{}',context(auxiliary=owner))


def test_graph_default_byte_cap_and_shared_copies():
    """Actual full graph charge, not virtual dedup, enforces default4MiB exact boundary."""
    graph=RetainedGraph({'urls':['']},{},'complete')
    overhead=graph.size;graph.collections['urls'][0]='x'*(Limits().graph_bytes-overhead)
    assert graph.size==Limits().graph_bytes
    store=SessionStore(Limits());store.publish('a',graph)
    larger=copy.deepcopy(graph);larger.collections['urls'][0]+='x'
    with pytest.raises(ToolError,match='resource_limit'):store.publish('b',larger)
    assert store.used_bytes==Limits().graph_bytes


@pytest.mark.asyncio
async def test_identity_encoding_rejected_before_stream_read():
    """Unsupported compression is denied on headers; decoder/body is never consumed."""
    class Bomb(httpx.AsyncByteStream):
        async def __aiter__(self):pytest.fail('Compressed body consumed');yield b''
    transport=guarded(lambda req:httpx.Response(200,headers={'content-encoding':'gzip'},stream=Bomb()))
    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(ToolError,match='source_error'):await client.get(ORIGIN)


@pytest.mark.asyncio
async def test_raw_body_multichunk_cap_and_false_length():
    """Actual streamed bytes enforce below/at/above cap with missing or false lengths."""
    class Chunks(httpx.AsyncByteStream):
        def __init__(self,size):self.size=size
        async def __aiter__(self):
            charge('stream_fixture_input',self.size)
            for _ in range(self.size):yield b'x'
    for size in (31,32,33):
        transport=guarded(lambda req:httpx.Response(200,headers={'content-length':'1'},stream=Chunks(size)),limits=Limits(response_bytes=32))
        async with httpx.AsyncClient(transport=transport) as client:
            if size<=32:assert len((await client.get(ORIGIN)).content)==size
            else:
                with pytest.raises(ToolError,match='resource_limit'):await client.get(ORIGIN)


@pytest.mark.asyncio
async def test_shared_request_and_redirect_budget():
    """Redirects consume same cumulative request cap, never allocate a fresh budget."""
    sent=[]
    def response(req):sent.append(str(req.url));return httpx.Response(302,headers={'location':ORIGIN+'/next'})
    transport=guarded(response,limits=Limits(requests=2,redirects=5))
    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(ToolError,match='resource_limit'):await client.get(ORIGIN)
    assert len(sent)==2


@pytest.mark.asyncio
async def test_redirect_count_cap():
    """Redirect exact+1 is denied before target send, with finite cycle handling."""
    sent=[]
    def response(req):sent.append(str(req.url));return httpx.Response(307,headers={'location':ORIGIN+'/next'})
    async with httpx.AsyncClient(transport=guarded(response,limits=Limits(redirects=1))) as client:
        with pytest.raises(ToolError,match='resource_limit'):await client.get(ORIGIN)
    assert len(sent)==2


@pytest.mark.asyncio
async def test_nonpublic_address_family_vectors():
    """Private/mapped/linklocal/metadata/multicast answers never authorize a socket."""
    guard=SourceGuard(ToolConfig(allowed_origins=(ORIGIN,)))
    for address in ('127.0.0.1','10.0.0.1','169.254.169.254','0.0.0.0','224.0.0.1','::1','fc00::1','fe80::1','::ffff:127.0.0.1'):
        async def dns(host,ctx):return [address]
        guard.resolver=dns
        with pytest.raises(ToolError,match='permission_denied'):await guard.authorize(ORIGIN,context())



@pytest.mark.asyncio
async def test_mixed_public_private_dns_denied():
    """One public answer never launders another nonpublic address."""
    async def dns(host,ctx):return ['93.184.216.34','127.0.0.1']
    guard=SourceGuard(ToolConfig(allowed_origins=(ORIGIN,)),resolver=dns)
    with pytest.raises(ToolError,match='permission_denied'):await guard.authorize(ORIGIN,context())


def test_origin_idna_trailing_dot_port_and_bypass_syntax():
    """Canonical allowlist identity is stable; ambiguous schemes/auth/numeric hosts deny."""
    assert normalized('https://BÜCHER.example.:443/a')[1]=='https://xn--bcher-kva.example'
    for url in ('file:///etc/passwd','http://0177.0.0.1','http://2130706433','http://0x7f000001',
                'https://name:secret@store.example/','https://%31%32%37.0.0.1/','https://store.example/#secret'):
        with pytest.raises(ToolError,match='permission_denied'):normalized(url)


@pytest.mark.asyncio
async def test_discovered_denied_link_is_diagnostic_only():
    """Cross-origin sitemap link never becomes authority or a fetch destination."""
    def response(req):
        assert req.url.host=='store.example'
        return httpx.Response(200,text='<urlset><url><loc>'+ORIGIN+'/products/a</loc></url><url><loc>http://169.254.169.254/</loc></url></urlset>')
    engine=ToolRuntime(ToolConfig(allowed_origins=(ORIGIN,)),resolver=resolver,wire_transport=httpx.MockTransport(response))
    try:
        jid=await completed(engine.call,'discover',{'url':ORIGIN,'max_items':3})
        page=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'urls'})
        assert page['data']['items']==[ORIGIN+'/products/a'] and page['data']['completeness']=='partial'
        diagnostics=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'diagnostics'})
        assert {d['code'] for d in diagnostics['data']['items']}=={'discovery_coverage_unverified','rejected_source'}
    finally:await engine.aclose()


@pytest.mark.asyncio
async def test_dns_change_after_discovery_denies_extraction():
    """Previously eligible URL is revalidated after public-to-private DNS change."""
    engine=sample_runtime();jid=await completed(engine.call,'discover',{'url':ORIGIN})
    async def private(host,ctx):return ['127.0.0.1']
    engine.guard.resolver=private
    accepted=await engine.call('extract',{'schema_version':'1.0','url':ORIGIN+'/products/widget'})
    for _ in range(20):
        status=await engine.call('job_status',{'schema_version':'1.0','job_id':accepted['data']['job_id']})
        if status['data']['state']=='failed':break
        await asyncio.sleep(.01)
    assert status['data']['error']['code']=='permission_denied'
    await engine.aclose()


@pytest.mark.asyncio
async def test_cross_origin_redirect_no_target_bytes():
    """Denied public-origin redirect sends no target bytes; removing only origin check is detected."""
    sent=[]
    def response(req):
        sent.append(str(req.url))
        return httpx.Response(302,headers={'location':'https://other.example/result'}) if req.url.host=='store.example' else httpx.Response(200,text='controlled public target')
    transport=guarded(response)
    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(ToolError,match='permission_denied'):await client.get(ORIGIN,headers={'authorization':'canary'})
    assert sent==[ORIGIN+'/']
    # Leave guard, resolver, redirect processing and raw sends active; alter only origin authority.
    transport=guarded(response);original=set(transport.guard.origins);sent.clear()
    try:
        transport.guard.origins.add('https://other.example')
        async with httpx.AsyncClient(transport=transport) as client:await client.get(ORIGIN)
        with pytest.raises(AssertionError):assert sent==[ORIGIN+'/']
        assert sent[-1]=='https://other.example/result'
    finally:transport.guard.origins=original


@pytest.mark.asyncio
async def test_pinned_numeric_tcp_preserves_host_and_tls(monkeypatch):
    """Real HTTPCore connection gets vetted IP while HTTP Host/TLS keep source hostname."""
    calls=[];writes=[]
    class Stream(httpcore.AsyncNetworkStream):
        wrong_length=False
        def __init__(self):
            self.body=('HTTP/1.1 200 OK\r\nContent-Length: '+('3' if self.wrong_length else '2')+'\r\n\r\nok').encode()
            charge('controlled_core_wire_input',len(self.body))
        async def read(self,max_bytes,timeout=None):
            value,self.body=self.body[:max_bytes],self.body[max_bytes:];return value
        async def write(self,buffer,timeout=None):writes.append(buffer)
        async def aclose(self):pass
        async def start_tls(self,ssl_context,server_hostname=None,timeout=None):calls.append(('tls',server_hostname));return self
        def get_extra_info(self,info):return None
    class Backend:
        async def connect_tcp(self,host,port,**kwargs):calls.append(('tcp',host));return Stream()
    original_backend=httpcore.AnyIOBackend
    monkeypatch.setattr(httpcore,'AnyIOBackend',Backend)
    config=ToolConfig(allowed_origins=(ORIGIN,));ctx=context()
    transport=GuardedTransport(config,ctx,SourceGuard(config,resolver=resolver))
    async with httpx.AsyncClient(transport=transport) as client:assert (await client.get(ORIGIN)).text=='ok'
    assert ('tcp','93.184.216.34') in calls and ('tls','store.example') in calls
    assert b'Host: store.example' in b''.join(writes)
    Stream.wrong_length=True
    transport=GuardedTransport(config,context(),SourceGuard(config,resolver=resolver))
    async with httpx.AsyncClient(transport=transport) as client:
        with pytest.raises(ToolError,match='source_error'):await client.get(ORIGIN)
    Stream.wrong_length=False
    # Controlled actual TCP proves denied redirects cannot touch a second server.
    denied=[];connections=[]
    async def denied_receiver(reader,writer):
        denied.append(True);writer.close();await writer.wait_closed()
    blocked=await asyncio.start_server(denied_receiver,'127.0.0.1',0)
    blocked_port=blocked.sockets[0].getsockname()[1]
    async def first_receiver(reader,writer):
        await reader.readuntil(b'\r\n\r\n')
        fixture=('HTTP/1.1 302 Found\r\nContent-Length: 0\r\nLocation: http://127.0.0.1:'+str(blocked_port)+'/\r\n\r\n').encode()
        charge('controlled_tcp_wire_input',len(fixture))
        writer.write(fixture)
        await writer.drain();writer.close();await writer.wait_closed()
    first=await asyncio.start_server(first_receiver,'127.0.0.1',0)
    first_port=first.sockets[0].getsockname()[1]
    class ControlledBackend:
        async def connect_tcp(self,host,port,**kwargs):
            connections.append(host)
            return await original_backend().connect_tcp('127.0.0.1',first_port,**kwargs)
    monkeypatch.setattr(httpcore,'AnyIOBackend',ControlledBackend)
    config=ToolConfig(allowed_origins=('http://store.example',));ctx=context()
    try:
        transport=GuardedTransport(config,ctx,SourceGuard(config,resolver=resolver))
        async with httpx.AsyncClient(transport=transport) as client:
            with pytest.raises(ToolError,match='permission_denied'):await client.get('http://store.example/')
        await asyncio.sleep(.01)
        assert connections==['93.184.216.34'] and denied==[]
    finally:
        first.close();blocked.close();await first.wait_closed();await blocked.wait_closed()


@pytest.mark.asyncio
async def test_evidence_response_cap_metadata():
    """Payload response limit is independent of graph size and returns metadata without oversized payload."""
    engine=ToolRuntime(ToolConfig(limits=Limits(evidence_bytes=50)))
    graph=RetainedGraph({}, {}, 'complete', owners={'owner':{'evidence':{'e':{'retained_data':{'value':'x'*60},'source_url':ORIGIN}},'availability':[]}})
    engine.store.publish('j',graph)
    reply=await engine.call('evidence',{'schema_version':'1.0','owner':'owner','evidence_id':'e'})
    assert reply['error']['code']=='resource_limit' and 'retained_data' not in reply['error']['details']['metadata']
    await engine.aclose()


@pytest.mark.asyncio
async def test_incomplete_capture_replay_never_confirms_removal(tmp_path):
    """Real incomplete-capture replay has no removal promotion and stable truthful diagnostics."""
    from tests.test_reliable_changes import product,save,DOMAIN
    from shopextract.tools.runtime import CaptureGrant
    db=str(tmp_path/'partial.db')
    previous=save(db,[product()],0);partial=save(db,[],1,complete=False)
    engine=ToolRuntime(ToolConfig(captures=(CaptureGrant('before',db,previous,DOMAIN),CaptureGrant('partial',db,partial,DOMAIN))))
    grants=(await engine.bootstrap())['captures'];reports=[]
    try:
        for _ in range(2):
            jid=await completed(engine.call,'changes',{'previous_capture':grants[0]['capture_handle'],'current_capture':grants[1]['capture_handle']})
            events=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'events'})
            candidates=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'candidates'})
            diagnostics=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'diagnostics'})
            assert events['data']['items']==[]
            assert not any(v['state']=='confirmed' and v['kind']=='product_removed' for v in candidates['data']['items'])
            assert diagnostics['data']['items']
            reports.append((events['data']['metadata']['report_id'],candidates['data']['items'],diagnostics['data']['items']))
        assert reports[0]==reports[1]
    finally:await engine.aclose()


@pytest.mark.asyncio
async def test_real_changes_replay_and_capture_grants(tmp_path):
    """Real persisted captures, native reliable report and replay preserve event IDs."""
    from tests.test_reliable_changes import product,save,DOMAIN
    from shopextract.tools.runtime import CaptureGrant
    db=str(tmp_path/'changes.db');a=save(db,[product()],0);b=save(db,[product('11',tick=1)],1)
    engine=ToolRuntime(ToolConfig(captures=(CaptureGrant('a',db,a,DOMAIN),CaptureGrant('b',db,b,DOMAIN))))
    grants=(await engine.bootstrap())['captures'];args={'previous_capture':grants[0]['capture_handle'],'current_capture':grants[1]['capture_handle']}
    reports=[]
    try:
        for _ in range(2):
            jid=await completed(engine.call,'changes',args)
            report=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'events'})
            from jsonschema import validate as schema_validate
            from shopextract.tools.contracts import schema
            schema_validate(report,schema('job_result')['outputSchema'])
            assert report['ok'];reports.append(report['data'])
        assert len(reports[0]['items'])==1
        assert reports[0]['items'][0]['state']=='confirmed'
        assert reports[0]['items'][0]['event_id']==reports[1]['items'][0]['event_id']
        # Fault only the existing commit boundary, never reliable comparison itself.
        import sqlite3
        c=save(db,[product('12',tick=2)],2)
        barrier=tmp_path/'report-ready'
        owner=OwnedProcess(Limits(),child_target=_blocking_report_child)
        ctx=context(auxiliary=owner,timeout=3)
        payload={'operation':'changes','arguments':{'domain':DOMAIN,'db_path':db,
            'previous_snapshot_id':b,'current_snapshot_id':c},'barrier':str(barrier)}
        task=asyncio.create_task(owner.run('domain',encoded(payload),ctx))
        for _ in range(300):
            if barrier.exists():break
            await asyncio.sleep(.005)
        assert barrier.exists(), 'Real report never reached commit boundary'
        ctx.cancelled.set();task.cancel()
        with pytest.raises(asyncio.CancelledError):await task
        assert owner.process is None
        with sqlite3.connect(db) as connection:
            assert connection.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
            assert connection.execute('SELECT COUNT(*) FROM reliable_reports').fetchone()[0]==1
    finally:await engine.aclose()


@pytest.mark.asyncio
async def test_empty_extraction_and_backend_failure_are_errors():
    """Both authoritative-empty extraction and failed native source are errors."""
    for status in (200,500):
        def response(req):
            if req.url.path=='/':return httpx.Response(200,text='<meta name="generator" content="wordpress">')
            return httpx.Response(status,json=[] if status==200 else {'error':'secret_canary'})
        engine=ToolRuntime(ToolConfig(allowed_origins=(ORIGIN,)),resolver=resolver,wire_transport=httpx.MockTransport(response))
        accepted=await engine.call('extract',{'schema_version':'1.0','url':ORIGIN})
        for _ in range(150):
            reply=await engine.call('job_result',{'schema_version':'1.0','job_id':accepted['data']['job_id'],'collection':'products'})
            if not reply['ok'] or reply['data']['state']=='succeeded':break
            await asyncio.sleep(.02)
        assert not reply['ok'] and reply['error']['code']=='source_error' and 'secret_canary' not in str(reply)
        await engine.aclose()


@pytest.mark.asyncio
async def test_publication_fault_releases_reservation(monkeypatch):
    """Failed result publication leaks neither handle nor running byte reservation."""
    limits=Limits();store=SessionStore(limits);jobs=JobManager(store,limits)
    def fail(*args):raise ToolError('source_error')
    monkeypatch.setattr(store,'publish',fail)
    async def result(ctx):return RetainedGraph({'urls':['a']},{},'complete')
    accepted=jobs.submit(result,1)
    for _ in range(20):
        if jobs.status(accepted['job_id'])['state']=='failed':break
        await asyncio.sleep(.01)
    assert store.used_bytes==0 and not store.handles
    await jobs.close()
    engine=sample_runtime();now=[time.monotonic()];engine.store.clock=lambda:now[0]
    source=await completed(engine.call,'extract',{'url':ORIGIN+'/products/widget','max_items':1})
    page=await engine.call('job_result',{'schema_version':'1.0','job_id':source,'collection':'products'})
    catalog=page['data']['metadata']['catalog_handle'];ready=asyncio.Event();release=asyncio.Event()
    original=engine.domain.execute
    async def held(name,args,ctx):
        graph=await original(name,args,ctx)
        if name=='match':ready.set();await release.wait()
        return graph
    engine.domain.execute=held
    accepted=await engine.call('match',{'schema_version':'1.0','left_catalog':catalog,'right_catalog':catalog})
    try:
        await asyncio.wait_for(ready.wait(),timeout=2)
        now[0]+=601;release.set()
        for _ in range(20):
            status=await engine.call('job_status',{'schema_version':'1.0','job_id':accepted['data']['job_id']})
            if status['data']['state']=='failed':break
            await asyncio.sleep(.01)
        assert status['data']['error']['code']=='expired'
        assert accepted['data']['job_id'] not in engine.store.graphs
        assert not engine.store.handles
    finally:engine.domain.execute=original;release.set();await engine.aclose()


@pytest.mark.asyncio
async def test_real_evidence_expiry_and_disconnect():
    """Actual extracted page/evidence expires through tools; restart cannot reuse owner authority."""
    engine=sample_runtime();now=[time.monotonic()];engine.store.clock=lambda:now[0]
    jid=await completed(engine.call,'extract',{'url':ORIGIN+'/products/widget','max_items':1})
    page=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'products'})
    product=page['data']['items'][0];args={'schema_version':'1.0','owner':product['owner_handle'],'evidence_id':product['field_evidence']['/price'][0]}
    before=await engine.call('evidence',args);assert before['data']['evidence']['retained_data']['value']=='10.25'
    now[0]+=601
    expired=await engine.call('evidence',args);assert expired['error']['code']=='expired'
    expired_page=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'products'})
    assert expired_page['error']['code']=='expired'
    await engine.aclose();assert engine.store.used_bytes==0
    other=ToolRuntime(ToolConfig())
    absent=await other.call('evidence',args);assert absent['error']['code']=='not_found'
    await other.aclose()


@pytest.mark.asyncio
async def test_feed_static_real_parser_and_evidence():
    """Supported XML feed is parsed/captured/normalized via real existing engine, no browser."""
    xml='<rss xmlns:g="http://base.google.com/ns/1.0"><channel><item><g:id>p</g:id><g:title>Widget</g:title><g:price>10.25 EUR</g:price><g:link>'+ORIGIN+'/p</g:link></item></channel></rss>'
    engine=ToolRuntime(ToolConfig(allowed_origins=(ORIGIN,)),resolver=resolver,
        wire_transport=httpx.MockTransport(lambda req:httpx.Response(200,text=xml)))
    try:
        jid=await completed(engine.call,'extract',{'url':ORIGIN+'/feed.xml','max_items':2})
        reply=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'products'})
        assert reply['data']['items'][0]['price']=='10.25'
        assert reply['data']['items'][0]['field_evidence']['/price']
    finally:await engine.aclose()


@pytest.mark.asyncio
async def test_late_cancelled_domain_cannot_publish():
    """Cancellation-catching domain loser never publishes; surgical real guard mutation is detected."""
    from tests.tool_faults import without_post_operation_cancel_check
    async def scenario():
        limits=Limits();store=SessionStore(limits);jobs=JobManager(store,limits)
        ready=asyncio.Event()
        async def operation(ctx):
            ready.set()
            try:await asyncio.Event().wait()
            except asyncio.CancelledError:
                return RetainedGraph({'products':[]},{'catalog_handle':'late_catalog'},'complete')
        accepted=jobs.submit(operation,1);await ready.wait()
        try:
            await jobs.cancel(accepted['job_id'])
            assert jobs.status(accepted['job_id'])['state']=='cancelled'
            assert accepted['job_id'] not in store.graphs and not store.handles and store.used_bytes==0
        finally:await jobs.close()
    await scenario()
    original=JobManager.run
    try:
        JobManager.run=without_post_operation_cancel_check(original)
        with pytest.raises(AssertionError):await scenario()
    finally:JobManager.run=original
