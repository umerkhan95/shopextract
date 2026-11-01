"""P5 acceptance contracts: production CLI operations/discovery, no fake mechanisms."""
import json
from pathlib import Path
import pytest
from click.testing import CliRunner
from shopextract.cli import main


def invoke(*args, **kwargs):
    return CliRunner().invoke(main, ['--output-format','json',*args], **kwargs)


def payload(result, exit_code=0):
    assert result.exit_code == exit_code, result.output
    value=json.loads(result.stdout)
    assert value['schema_version']=='1.0'
    return value['data']


def goal():
    return {'schema_version':'1.0','baseline':[{'external_id':'S1','title':'Synthetic widget','description':'old'}],
            'supplier_origin':'https://store.example','product_urls':['https://store.example/p/1'],
            'deadline':'2030-01-01T00:00:00+00:00','budgets':{'products':0}}


def write(tmp_path,name,value):
    p=tmp_path/name;p.write_text(json.dumps(value));return str(p)


def test_maintenance_durable_native_engine(tmp_path):
    db=str(tmp_path/'jobs.db'); f=write(tmp_path,'goal.json',goal())
    key=payload(invoke('maintenance','--db',db,'create',f))['job_id']
    assert payload(invoke('maintenance','--db',db,'show',key))['state']=='queued'
    rows=payload(invoke('maintenance','--db',db,'list'))['jobs'];assert rows[0]['id']==key
    report=payload(invoke('maintenance','--db',db,'run',key),3)
    assert report['state']=='partial' and report['stop_reason']=='product_budget'
    assert payload(invoke('maintenance','--db',db,'report',key))['job_id']==key


def test_tools_schema_inventory_lazy():
    data=payload(invoke('tools','schemas'))
    assert data['native_schema_version']=='1.0'
    assert {s['name'] for s in data['tools']}=={'discover','extract','match','changes','evidence','job_status','job_result','job_cancel'}


def test_tools_call_real_empty_bootstrap(tmp_path):
    config=write(tmp_path,'operator.json',{})
    request=write(tmp_path,'session.json',{'schema_version':'1.0','steps':[{'id':'boot','tool':'bootstrap','arguments':{}}]})
    data=payload(invoke('tools','call','--config',config,'--request',request))
    assert data['session_only'] is True and data['steps'][0]['result']['captures']==[]


def test_tools_serve_protocol_errors_never_enveloped(tmp_path):
    result=invoke('tools','serve','--config',str(tmp_path/'missing'),env={'SHOPEXTRACT_OUTPUT_FORMAT':'json'})
    assert result.exit_code==2 and not result.stdout and 'config' in result.stderr.lower()


def test_capabilities_actual_grammar():
    data=payload(invoke('capabilities'))
    paths={tuple(v['path']) for v in data['commands']}
    assert {('maintenance','create'),('tools','serve'),('categories','tree','link'),('schema','show')}<=paths
    assert data['schema_version']=='1.0'
    assert data['limits']=={'input_bytes':33554432,'depth':64,'records':1000,'json_nodes':1000000}


def test_packaged_schema_discovery():
    inventory=payload(invoke('schema','list'))
    assert {'response','config','maintenance-goal','tool-session','tool-operator'} <= {v['name'] for v in inventory['schemas']}
    schema=payload(invoke('schema','show','maintenance-goal'))['schema']
    assert schema['type']=='object' and schema['additionalProperties'] is False


def test_tools_static_and_help_never_construct_runtime(monkeypatch):
    from shopextract.tools import ToolRuntime
    def forbidden(*a,**k):raise AssertionError('runtime initialized')
    monkeypatch.setattr(ToolRuntime,'__init__',forbidden)
    for args in [('tools','schemas'),('schema','show','tool:match'),('capabilities',),('tools','serve','--help'),('maintenance','run','--help')]:
        result=invoke(*args)
        assert result.exit_code==0,result.output


@pytest.mark.parametrize('change',[
    {'schema_version':1}, {'extra':True}, {'budgets':{'products':True}},
    {'budgets':{'products':-1}}, {'fields':[]}, {'deadline':'not-a-date'},
    {'product_urls':'https://store.example/p'}, {'baseline':{}},
])
def test_goal_rejects_before_database(tmp_path,change):
    value=goal();value.update(change)
    db=tmp_path/'absent.db'
    result=invoke('maintenance','--db',str(db),'create',write(tmp_path,'bad.json',value))
    assert result.exit_code==2 and not db.exists(),result.output


def test_maintenance_unknown_scope_and_job(tmp_path):
    db=str(tmp_path/'jobs.db')
    assert invoke('maintenance','--db',db,'status','missing').exit_code==2
    assert not Path(db).exists()
    key=payload(invoke('maintenance','--db',db,'create',write(tmp_path,'g.json',goal())))['job_id']
    assert invoke('maintenance','--db',db,'retry',key,'unknown').exit_code==1
    assert payload(invoke('maintenance','--db',db,'status',key))['state']=='queued'
    assert invoke('maintenance','--db',db,'report',key,'--limit','0').exit_code==2


@pytest.mark.parametrize('value',[
    {'schema_version':'1.0'}, {'allowed_origins':'https://store.example'},
    {'allowed_origins':['https://store.example/path']}, {'limits':{'active_jobs':True}},
    {'limits':{'timeout_seconds':0}}, {'limits':{'item_count':1001}},
    {'allowed_tools':['fake']}, {'captures':[{'alias':'x','db_path':'missing','snapshot_id':True,'supplier':'store.example'}]},
])
def test_operator_closed_bounds(tmp_path,value):
    request=write(tmp_path,'r.json',{'schema_version':'1.0','steps':[{'id':'b','tool':'bootstrap','arguments':{}}]})
    result=invoke('tools','call','--config',write(tmp_path,'op.json',value),'--request',request)
    assert result.exit_code==2,result.output


@pytest.mark.parametrize('steps',[
    [],[{'id':'a','tool':'bootstrap','arguments':{},'extra':True}],
    [{'id':'a','tool':'bootstrap','arguments':{}},{'id':'a','tool':'bootstrap','arguments':{}}],
    [{'id':'a','tool':'evidence','arguments':{'owner':{'$ref':'later#/owner'}}}],
    [{'id':'a','tool':'shell','arguments':{}}],
    [{'id':'a','tool':'bootstrap','arguments':{}}]*33,
])
def test_session_preflight(tmp_path,steps,monkeypatch):
    from shopextract.tools import ToolRuntime
    def forbidden(*a,**kw):raise AssertionError('invalid input started runtime')
    monkeypatch.setattr(ToolRuntime,'__init__',forbidden)
    result=invoke('tools','call','--config',write(tmp_path,'op.json',{}),'--request',write(tmp_path,'r.json',{'schema_version':'1.0','steps':steps}))
    assert result.exit_code==2,result.output


def session_fixture(tmp_path,count=2):
    from tests.test_reliable_changes import product,save,DOMAIN
    db=tmp_path/'captures.db';sid=save(str(db),[product(key=str(i)) for i in range(count)],0)
    config={'captures':[{'alias':'synthetic','db_path':str(db),'snapshot_id':sid,'supplier':DOMAIN}]}
    steps=[{'id':'boot','tool':'bootstrap','arguments':{}},
        {'id':'m','tool':'match','arguments':{'schema_version':'1.0','left_catalog':{'$ref':'boot#/captures/0/catalog_handle'},'right_catalog':{'$ref':'boot#/captures/0/catalog_handle'}}},
        {'id':'p','tool':'poll','arguments':{'job_id':{'$ref':'m#/data/job_id'}}},
        {'id':'rows','tool':'pages','arguments':{'job_id':{'$ref':'m#/data/job_id'},'collection':'matches','page_size':1,'max_pages':10}}]
    return config,{'schema_version':'1.0','steps':steps}


def test_session_real_bootstrap_match_poll_pages_stale_and_cleanup(tmp_path):
    import multiprocessing
    config,request=session_fixture(tmp_path)
    data=payload(invoke('tools','call','--config',write(tmp_path,'op.json',config),'--request',write(tmp_path,'r.json',request),'--timeout','20'))
    rows=data['steps'][-1]['result']
    assert rows['complete'] and rows['next_cursor'] is None
    assert sum(len(page['data']['items']) for page in rows['pages'])==2
    assert all(page['data']['items'][0]['relation']=='exact' for page in rows['pages'])
    stale=data['steps'][1]['result']['data']['job_id']
    r={'schema_version':'1.0','steps':[{'id':'s','tool':'job_status','arguments':{'schema_version':'1.0','job_id':stale}}]}
    result=invoke('tools','call','--config',write(tmp_path,'empty.json',{}),'--request',write(tmp_path,'stale.json',r))
    assert result.exit_code==1 and 'not_found' in result.output
    assert not multiprocessing.active_children()


def test_session_page_cap_partial_and_evidence(tmp_path):
    config,request=session_fixture(tmp_path)
    request['steps'][-1]['arguments']['max_pages']=1
    result=invoke('tools','call','--config',write(tmp_path,'op.json',config),'--request',write(tmp_path,'r.json',request),'--timeout','20')
    data=payload(result,3)
    assert data['completeness']=='partial'
    assert data['steps'][-1]['result']['next_cursor'] and not data['steps'][-1]['result']['complete']
    # Native ownership/evidence through the captured owner rather than matching projection.
    from tests.test_reliable_changes import product
    from shopextract._evidence import trust_view
    record=product();eid=record.evidence_contract.evidence[0].evidence_id
    request={'schema_version':'1.0','steps':[{'id':'b','tool':'bootstrap','arguments':{}},
        {'id':'e','tool':'evidence','arguments':{'schema_version':'1.0','owner':{'$ref':'b#/captures/0/owners/0/owner_handle'},'evidence_id':eid}}]}
    result=invoke('tools','call','--config',write(tmp_path,'op.json',config),'--request',write(tmp_path,'ev.json',request),'--timeout','20')
    evidence=payload(result)['steps'][-1]['result']['data']
    assert evidence['status']=='available' and evidence['evidence']['retained_data']


def test_session_denied_origin_error_closes_runtime(tmp_path,monkeypatch):
    from shopextract.tools import ToolRuntime
    closed=[];original=ToolRuntime.aclose
    async def observed(self):
        await original(self);closed.append((self.closed,self.auxiliary.process))
    monkeypatch.setattr(ToolRuntime,'aclose',observed)
    request={'schema_version':'1.0','steps':[{'id':'e','tool':'extract','arguments':{'schema_version':'1.0','url':'https://denied.example/product'}}]}
    result=invoke('tools','call','--config',write(tmp_path,'op.json',{}),'--request',write(tmp_path,'r.json',request))
    assert result.exit_code==1 and 'permission_denied' in result.output and closed==[(True,None)]


def test_reference_escape_and_wrong_pointer():
    from shopextract._cli_operations import references
    from shopextract._cli_core import CliFailure
    assert references({'$ref':'a#/x~1y/~0'}, {'a':{'x/y':{'~':'preserved'}}},resolve=True)=='preserved'
    with pytest.raises(CliFailure):references({'$ref':'a#/01'},{'a':['x','y']},resolve=True)


def run_process(args,*,fixture=False,env=None,timeout=20):
    import subprocess,sys,os
    root=Path(__file__).resolve().parents[1]
    process=subprocess.run([sys.executable,'-m','tests.cli_operation_fixture' if fixture else 'shopextract.cli','--output-format','json',*args],cwd=root,
        env={**os.environ,'PYTHONPATH':str(root/'src')+__import__('os').pathsep+str(root),**(env or {})},capture_output=True,text=True,timeout=timeout)
    return process


def test_maintenance_real_separate_processes(tmp_path):
    db=str(tmp_path/'jobs.db');f=write(tmp_path,'g.json',goal())
    made=run_process(['maintenance','--db',db,'create',f]);assert made.returncode==0,made.stderr
    key=json.loads(made.stdout)['data']['job_id']
    report=run_process(['maintenance','--db',db,'run',key]);assert report.returncode==3,report.stdout+report.stderr
    status=run_process(['maintenance','--db',db,'status',key]);assert json.loads(status.stdout)['data']['state']=='partial'
    cancelled=run_process(['maintenance','--db',db,'cancel',key]);assert cancelled.returncode==0,cancelled.stdout
    resumed=run_process(['maintenance','--db',db,'resume',key]);assert resumed.returncode==1 and 'invalid_state' in resumed.stdout


@pytest.mark.parametrize('interrupt',[False,True])
def test_maintenance_deadline_interrupt_durable_cleanup(tmp_path,interrupt):
    import os,sys,subprocess,time,signal
    value=goal();value['budgets']={'products':1,'attempt_seconds':10}
    db=str(tmp_path/'jobs.db');f=write(tmp_path,'g.json',value)
    key=json.loads(run_process(['maintenance','--db',db,'create',f]).stdout)['data']['job_id']
    entered=tmp_path/'entered';env={'CLI_WIRE_ENTERED':str(entered)}
    args=['maintenance','--db',db,'--allow-origin','https://store.example','run',key,'--timeout','10' if interrupt else '1']
    if interrupt:
        root=Path(__file__).resolve().parents[1]
        process=subprocess.Popen([sys.executable,'-m','tests.cli_operation_fixture','--output-format','json',*args],cwd=root,env={**os.environ,**env,'PYTHONPATH':str(root/'src')+os.pathsep+str(root)},stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        try:
            deadline=time.monotonic()+10
            while not entered.exists() and process.poll() is None and time.monotonic()<deadline:time.sleep(.02)
            assert entered.exists()
            process.send_signal(signal.SIGINT);stdout,stderr=process.communicate(timeout=5)
            assert process.returncode==130 and json.loads(stdout)['error']['code']=='E_CANCELLED',stdout+stderr
        finally:
            if process.poll() is None:process.kill();process.wait()
    else:
        result=run_process(args,fixture=True,env=env)
        assert entered.exists() and result.returncode==1 and json.loads(result.stdout)['error']['code']=='E_TIMEOUT',result.stdout+result.stderr
    status=run_process(['maintenance','--db',db,'status',key])
    assert json.loads(status.stdout)['data']['state']=='cancelled'
    from shopextract.maintenance import MaintenanceStore
    store=MaintenanceStore(db)
    try:store.acquire();store.release()
    finally:store.close()


@pytest.mark.asyncio
async def test_real_sdk_root_stdio_protocol_and_bootstrap(tmp_path):
    import os,sys,asyncio
    from mcp import ClientSession,StdioServerParameters
    from mcp.client.stdio import stdio_client
    root=Path(__file__).resolve().parents[1]
    config=write(tmp_path,'op.json',{})
    params=StdioServerParameters(command=sys.executable,args=['-m','shopextract.cli','tools','serve','--config',config],cwd=str(root),
        env={**os.environ,'PYTHONPATH':str(root/'src'),'SHOPEXTRACT_OUTPUT_FORMAT':'json','SHOPEXTRACT_DIAGNOSTICS':'bad','SHOPEXTRACT_CONFIG':str(tmp_path/'absent-root-config')})
    async def exercise():
        with open(tmp_path/'sdk-stderr.log','w') as errlog:
            async with stdio_client(params,errlog=errlog) as (read,write_stream):
                async with ClientSession(read,write_stream) as client:
                    initialized=await client.initialize();assert initialized.serverInfo.name=='shopextract'
                    assert len((await client.list_tools()).tools)==8
                    resource=await client.read_resource('shopextract://session')
                    assert json.loads(resource.contents[0].text)['captures']==[]
                    denied=await client.call_tool('extract',{'schema_version':'1.0','url':'https://denied.example/p'})
                    assert denied.isError
    await asyncio.wait_for(exercise(),10)


@pytest.mark.parametrize('tool,args',[
    ('bootstrap',{'unexpected':1}),('poll',{'job_id':'j','interval_seconds':0}),
    ('poll',{'job_id':'j','interval_seconds':True}),('pages',{'job_id':'j','collection':'matches','max_pages':11}),
    ('pages',{'job_id':'j','collection':'matches','max_pages':True}),('pages',{'job_id':'j','collection':'matches','page_size':101}),
    ('job_status',{'schema_version':'1.0','job_id':'j','unexpected':1}),
])
def test_all_literal_session_steps_preflight_before_runtime(tmp_path,monkeypatch,tool,args):
    from shopextract.tools import ToolRuntime
    def forbidden(*a,**kw):raise AssertionError('literal validation too late')
    monkeypatch.setattr(ToolRuntime,'__init__',forbidden)
    request={'schema_version':'1.0','steps':[{'id':'b','tool':'bootstrap','arguments':{}},{'id':'x','tool':tool,'arguments':args}]}
    result=invoke('tools','call','--config',write(tmp_path,'op.json',{}),'--request',write(tmp_path,'r.json',request))
    assert result.exit_code==2,result.output


@pytest.mark.parametrize('terminal',[False,True])
def test_session_deadline_and_native_terminal_cleanup(tmp_path,monkeypatch,terminal):
    import asyncio,httpx,multiprocessing
    from shopextract.tools import ToolRuntime
    original=ToolRuntime.__init__;closed=[];closing=ToolRuntime.aclose
    async def resolver(host,ctx):return ['93.184.216.34']
    async def slow(request):await asyncio.sleep(10);return httpx.Response(200,text='<html/>')
    def configured(self,*args,**kwargs):
        original(self,*args,resolver=resolver,wire_transport=httpx.MockTransport(slow),**kwargs)
    async def observed(self):
        await closing(self);closed.append((self.closed,self.auxiliary.process))
    monkeypatch.setattr(ToolRuntime,'__init__',configured);monkeypatch.setattr(ToolRuntime,'aclose',observed)
    config={'allowed_origins':['https://store.example']}
    request={'schema_version':'1.0','steps':[{'id':'e','tool':'extract','arguments':{'schema_version':'1.0','url':'https://store.example/product','timeout_seconds':1 if terminal else 10}},
        {'id':'p','tool':'poll','arguments':{'job_id':{'$ref':'e#/data/job_id'}}}]}
    result=invoke('tools','call','--config',write(tmp_path,'op.json',config),'--request',write(tmp_path,'r.json',request),'--timeout','3' if terminal else '1')
    assert result.exit_code==1,result.output
    assert json.loads(result.stdout)['error']['code']==('E_OPERATION' if terminal else 'E_TIMEOUT')
    if terminal:assert 'timed_out' in result.output
    assert closed==[(True,None)] and not multiprocessing.active_children()


def test_exact_output_bytes_and_no_silent_truncation(monkeypatch):
    import io
    from contextlib import redirect_stdout
    from shopextract import _cli_operations as ops
    from shopextract._cli_core import make_response,CliFailure
    data={'text':'€retained'}
    amount=len(json.dumps(make_response(data),ensure_ascii=False,allow_nan=False).encode())+1
    for cap in (amount+1,amount):
        monkeypatch.setattr(ops,'MAX_BYTES',cap)
        with redirect_stdout(io.StringIO()) as stream:ops.bounded_output(data)
        assert json.loads(stream.getvalue())['data']==data
    monkeypatch.setattr(ops,'MAX_BYTES',amount-1)
    with redirect_stdout(io.StringIO()) as stream:
        with pytest.raises(CliFailure):ops.bounded_output(data)
    assert not stream.getvalue()


def test_missing_sdk_actionable_protocol_stderr(tmp_path,monkeypatch):
    import builtins
    original=builtins.__import__
    def blocked(name,*args,**kwargs):
        if name=='mcp':raise ImportError('SECRET dependency detail')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',blocked)
    result=invoke('tools','serve','--config',write(tmp_path,'op.json',{}))
    assert result.exit_code==1 and not result.stdout and 'shopextract[mcp]' in result.stderr and 'SECRET' not in result.output


def test_maintenance_category_policy_and_custom_profiles(tmp_path):
    from tests.test_cli_categories import options
    from shopextract.categories.contracts import CategoryRuntimeConfig
    from shopextract.categories.config import runtime_record
    from shopextract.categories.maintenance import category_policy_digest
    from shopextract.maintenance import MaintenanceStore
    config=CategoryRuntimeConfig(options(),(('boots','footwear-v1'),))
    policy=write(tmp_path,'policy.json',runtime_record(config))
    value=goal();db=str(tmp_path/'jobs.db')
    key=payload(invoke('maintenance','--db',db,'--category-config',policy,'create',write(tmp_path,'g.json',value)))['job_id']
    store=MaintenanceStore(db)
    try:assert store.category_policy(key).config_digest==category_policy_digest(config)
    finally:store.close()
    result=invoke('maintenance','--db',db,'--category-config',policy,'run',key)
    assert payload(result,3)['stop_reason']=='product_budget'
    bad={'schema_version':1,'profiles':{'generic-v1':{'description':{'kind':'text','role':'comparable'}}}}
    absent=tmp_path/'absent.db'
    result=invoke('maintenance','--db',str(absent),'--profiles',write(tmp_path,'profiles.json',bad),'create',write(tmp_path,'g.json',value))
    assert result.exit_code==2 and not absent.exists()


def test_packaged_schemas_validate_examples_and_native_versions():
    import jsonschema
    from shopextract._cli_discovery import packaged_schema
    root=Path(__file__).resolve().parents[1]
    for name,file in [('config','cli.json'),('maintenance-goal','goal.json'),('tool-session','session.json'),('tool-operator','operator.json')]:
        schema=packaged_schema(name);jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.validate(json.loads((root/'examples'/'cli'/file).read_text()),schema)
    from tests.test_cli_categories import options
    from shopextract.categories._codec import wire
    from shopextract.categories.contracts import CategoryRuntimeConfig
    jsonschema.validate(wire(options()),packaged_schema('category-options'))
    jsonschema.validate(wire(CategoryRuntimeConfig(options())),packaged_schema('category-runtime'))


@pytest.mark.parametrize('tool,args',[
    ('poll',{'job_id':'j','interval_seconds':{'invalid':1}}),
    ('pages',{'job_id':'j','collection':'matches','max_pages':{'invalid':1}}),
    ('pages',{'job_id':'j','collection':'matches','page_size':{'invalid':1}}),
    ('extract',{'schema_version':'1.0','url':'https://store.example/p','max_items':{'invalid':1}}),
])
def test_malformed_numeric_objects_reject_before_prior_steps(tmp_path,monkeypatch,tool,args):
    from shopextract.tools import ToolRuntime
    monkeypatch.setattr(ToolRuntime,'__init__',lambda *a,**k:pytest.fail('invalid later literal started runtime'))
    request={'schema_version':'1.0','steps':[{'id':'b','tool':'bootstrap','arguments':{}},{'id':'bad','tool':tool,'arguments':args}]}
    result=invoke('tools','call','--config',write(tmp_path,'op.json',{}),'--request',write(tmp_path,'r.json',request))
    assert result.exit_code==2,result.output


@pytest.mark.parametrize('limits,args',[
    ({'item_count':1},{'schema_version':'1.0','url':'https://store.example/p','max_items':2}),
    ({'input_bytes':64},{'schema_version':'1.0','url':'https://store.example/'+100*'x'}),
])
def test_reduced_operator_limits_apply_before_prior_steps(tmp_path,monkeypatch,limits,args):
    from shopextract.tools import ToolRuntime
    monkeypatch.setattr(ToolRuntime,'__init__',lambda *a,**k:pytest.fail('operator limits validated too late'))
    request={'schema_version':'1.0','steps':[{'id':'b','tool':'bootstrap','arguments':{}},{'id':'bad','tool':'extract','arguments':args}]}
    result=invoke('tools','call','--config',write(tmp_path,'op.json',{'limits':limits}),'--request',write(tmp_path,'r.json',request))
    assert result.exit_code==2,result.output


def test_actual_export_output_contract():
    data=payload(invoke('capabilities'))
    row=next(v for v in data['commands'] if v['path']==['export'])
    assert row['output_contract']=='json-envelope-or-artifact-stdout'
    assert row['output_modes'][0]['when']=={'--output':'-'}
    assert row['output_modes'][0]['contract']=='artifact-stdout'


def test_native_list_pagination_and_custom_profile(tmp_path):
    db=str(tmp_path/'jobs.db');keys=[]
    profiles={'schema_version':1,'profiles':{'custom-v1':{'description':{'kind':'text','role':'comparable'}}}}
    pf=write(tmp_path,'profiles.json',profiles)
    for i in range(3):
        value=goal();value['profiles']={'S1':'custom-v1'}
        keys.append(payload(invoke('maintenance','--db',db,'--profiles',pf,'create',write(tmp_path,f'g{i}.json',value)))['job_id'])
    rows=payload(invoke('maintenance','--db',db,'list','--offset','1','--limit','1'))['jobs']
    assert [r['id'] for r in rows]==keys[1:2]
    assert rows[0]['profile_definitions']['custom-v1']['fields']['description']['kind']=='text'
    assert payload(invoke('maintenance','--db',db,'list','--offset','3'))['jobs']==[]


def test_foreign_maintenance_category_policy_keeps_state(tmp_path):
    from tests.test_cli_categories import options
    from dataclasses import replace
    from shopextract.categories.contracts import CategoryRuntimeConfig
    from shopextract.categories.config import runtime_record
    opts=options();original=CategoryRuntimeConfig(opts)
    foreign=CategoryRuntimeConfig(replace(opts,scope=replace(opts.scope,store_url='https://foreign.example')))
    db=str(tmp_path/'jobs.db')
    key=payload(invoke('maintenance','--db',db,'--category-config',write(tmp_path,'policy.json',runtime_record(original)),'create',write(tmp_path,'g.json',goal())))['job_id']
    result=invoke('maintenance','--db',db,'--category-config',write(tmp_path,'foreign.json',runtime_record(foreign)),'run',key)
    assert result.exit_code==1 and 'category_policy_mismatch' in result.output
    assert payload(invoke('maintenance','--db',db,'status',key))['state']=='queued'


def test_capabilities_full_recursive_grammar_equality():
    import click
    actual={tuple(row['path']):row for row in payload(invoke('capabilities'))['commands']}
    expected={}
    def walk(command,path=()):
        expected[path]=command
        if isinstance(command,click.Group):
            for name,child in command.commands.items():walk(child,(*path,name))
    walk(main)
    assert actual.keys()==expected.keys()
    for path,command in expected.items():
        row=actual[path];assert row['group']==isinstance(command,click.Group)
        parameters={p['name']:p for p in row['parameters']}
        assert parameters.keys()=={p.name for p in command.params}
        for param in command.params:
            value=parameters[param.name]
            assert value['nargs']==param.nargs and value['required']==param.required
            assert value['multiple']==getattr(param,'multiple',False)
            assert value['type']==param.type.name
            safe_default=param.default if isinstance(param.default,(str,int,float,bool,list,tuple,dict,type(None))) else None
            assert value['default']==json.loads(json.dumps(safe_default))
            if isinstance(param.type,(click.IntRange,click.FloatRange)):
                assert value['min']==param.type.min and value['max']==param.type.max
            if isinstance(param,click.Option):
                assert value['options']==param.opts and value['secondary_options']==param.secondary_opts
                assert value['is_flag']==param.is_flag
            if isinstance(param.type,click.Choice):assert value['choices']==list(param.type.choices)


def test_valid_numeric_references_native_page_dispatch(tmp_path):
    config,request=session_fixture(tmp_path)
    config['limits']={'item_count':2}
    request['steps'][-1]['arguments'].update(page_size={'$ref':'boot#/limits/item_count'},max_pages={'$ref':'boot#/limits/active_jobs'})
    data=payload(invoke('tools','call','--config',write(tmp_path,'op.json',config),'--request',write(tmp_path,'r.json',request),'--timeout','20'))
    rows=data['steps'][-1]['result']
    assert rows['complete'] and len(rows['pages'])==1 and len(rows['pages'][0]['data']['items'])==2
