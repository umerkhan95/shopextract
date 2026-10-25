"""Operator CLI composition of native durable maintenance and restricted tool sessions."""
from __future__ import annotations

import asyncio
import copy
import json
import math
import re
import sqlite3
from dataclasses import fields
from pathlib import Path

import click

from ._cli_core import CliFailure, CoreCommand, emit_response, make_response
from ._cli_data import MAX_BYTES, read_json_file


def object_value(value, allowed, required=()):
    if not isinstance(value, dict) or value.keys() - set(allowed) or not set(required) <= value.keys():
        raise CliFailure('E_USAGE', 'Invalid closed JSON object; consult schema discovery.')
    return value


def numeric(value, low, high, *, integer=False):
    if (type(value) not in ((int,) if integer else (int,float)) or not math.isfinite(value)
            or not low <= value <= high):
        raise CliFailure('E_USAGE','Numeric value is outside the supported finite range.')
    return value


def strings(value):
    if not isinstance(value,list) or any(not isinstance(v,str) or not v for v in value):
        raise CliFailure('E_USAGE','Expected an array of nonempty strings.')
    return tuple(value)


def load_operator(path):
    from .tools import ToolConfig
    from .tools.runtime import Limits, CaptureGrant, TOOL_NAMES
    value=object_value(read_json_file(path), ('allowed_origins','allowed_tools','captures','limits'))
    limits=object_value(value.get('limits',{}), (f.name for f in fields(Limits)))
    defaults=Limits()
    for name,actual in limits.items():
        maximum=getattr(defaults,name)
        numeric(actual, 1e-12, maximum, integer=type(maximum) is int)
    if limits.get('active_jobs',1)!=1:
        raise CliFailure('E_USAGE','Only one tool worker is supported.')
    captures=value.get('captures',[])
    if not isinstance(captures,list):
        raise CliFailure('E_USAGE','Expected capture grant array.')
    grants=[]
    for entry in captures:
        object_value(entry,('alias','db_path','snapshot_id','supplier'),('alias','db_path','snapshot_id','supplier'))
        if any(not isinstance(entry[k],str) or not entry[k] for k in ('alias','db_path','supplier')):
            raise CliFailure('E_USAGE','Capture grant strings must be nonempty.')
        numeric(entry['snapshot_id'],1,2**63-1,integer=True)
        grants.append(CaptureGrant(**entry))
    allowed=strings(value.get('allowed_tools',list(TOOL_NAMES)))
    if any(name not in TOOL_NAMES for name in allowed) or len(set(allowed))!=len(allowed):
        raise CliFailure('E_USAGE','Unknown or duplicate tool names.')
    origins=strings(value.get('allowed_origins',[]))
    from .tools.security import normalized
    try:
        if any(normalized(origin)[0].rstrip('/')!=normalized(origin)[1] for origin in origins):
            raise ValueError()
    except Exception:
        raise CliFailure('E_USAGE','Operator allowlist entries must be valid public source origins.') from None
    limit_values=Limits(**limits)
    if len(grants)>limit_values.terminal_jobs or len({g.alias for g in grants})!=len(grants):
        raise CliFailure('E_USAGE','Duplicate or excessive capture grants.')
    return ToolConfig(origins,allowed,tuple(grants),limit_values)


def load_profiles(path):
    if path is None:return {}
    from .maintenance.profiles import CategoryProfile, FieldRule
    value=object_value(read_json_file(path),('schema_version','profiles'),('schema_version','profiles'))
    if type(value['schema_version']) is not int or value['schema_version']!=1 or not isinstance(value['profiles'],dict):
        raise CliFailure('E_USAGE','Profiles require integer schema_version 1 and a profiles object.')
    result={}
    for name,records in value['profiles'].items():
        if not isinstance(records,dict):raise CliFailure('E_USAGE','Invalid profile fields.')
        rules={}
        for field,record in records.items():
            object_value(record,('kind','role','normalization'),('kind','role'))
            rules[field]=FieldRule(**record)
        result[name]=CategoryProfile(name,rules)
    return result


def load_goal(path):
    from .maintenance import Goal,Budgets
    value=object_value(read_json_file(path),(f.name for f in fields(Goal)),
                       ('schema_version','baseline','supplier_origin','product_urls','deadline'))
    value=dict(value)
    if value['schema_version']!='1.0':raise CliFailure('E_USAGE','Goal requires schema_version string 1.0.')
    budgets=object_value(value.get('budgets',{}),(f.name for f in fields(Budgets)))
    value['budgets']=Budgets(**budgets)
    if not isinstance(value['baseline'],list):raise CliFailure('E_USAGE','Goal baseline must be an array.')
    value['product_urls']=strings(value['product_urls'])
    if 'fields' in value:value['fields']=strings(value['fields'])
    return Goal(**value)


async def total_deadline(awaitable,seconds):
    """Observe deadline independently of a native task swallowing cancellation."""
    task=asyncio.ensure_future(awaitable)
    try:
        done,_=await asyncio.wait({task},timeout=seconds)
        if not done:
            task.cancel()
            try:await task
            except (asyncio.CancelledError,Exception):pass
            raise CliFailure('E_TIMEOUT','Operation timed out; native cleanup completed.')
        return await task
    finally:
        if not task.done():
            task.cancel()
            try:await task
            except (asyncio.CancelledError,Exception):pass


def bounded_output(data,*,partial=False):
    failure=CliFailure('E_PARTIAL','Bounded operation retained incomplete results.') if partial else None
    response=make_response(data,failure=failure)
    if len(json.dumps(response,ensure_ascii=False,allow_nan=False).encode())+1>MAX_BYTES:
        raise CliFailure('E_OPERATION','Result exceeds 1 MiB CLI response limit; request a smaller report or page.')
    emit_response(response)
    if partial:raise SystemExit(3)


def maintenance_operation(command,scope,job=None,**params):
    from .maintenance import MaintenanceStore,MaintenanceEngine,MaintenanceError
    from .tools import ToolConfig
    store=None
    try:
        if not scope['db']:raise CliFailure('E_USAGE','Explicit --db maintenance scope is required.')
        profiles=load_profiles(scope['profiles'])
        category=None
        if scope['category_config']:
            from ._cli_categories import runtime_file
            category=runtime_file(scope['category_config'])
        config=load_operator(scope['operator_config']) if scope['operator_config'] else ToolConfig(allowed_origins=scope['allow_origin'])
        if scope['operator_config'] and scope['allow_origin']:
            raise CliFailure('E_USAGE','Select operator-config or allow-origin, not both.')
        if scope['allow_origin']:
            from .tools.security import normalized
            if any(normalized(origin)[0].rstrip('/')!=normalized(origin)[1] for origin in scope['allow_origin']):
                raise CliFailure('E_USAGE','Allowlist entries must be origins.')
        goal=load_goal(params['goal']) if command=='create' else None
        # A read of a missing durable scope must never initialize it.
        if command!='create' and not Path(scope['db']).expanduser().is_file():
            raise CliFailure('E_USAGE','An existing maintenance database is required.')
        store=MaintenanceStore(scope['db'],custom_profiles=profiles,category_config=category)
        if command=='create':return {'job_id':store.create(goal)}
        if command in {'show','status'}:return store.status(job)
        if command=='list':return {'jobs':store.list_jobs(offset=params['offset'],limit=params['limit'])}
        if command=='report':return store.report(job,offset=params['offset'],limit=params['limit'])
        if command=='evidence':return store.evidence(job,params['evidence_id'])
        # Validate ID before engine creates any runtime or acquires ownership.
        store.status(job)
        async def execute():
            engine=MaintenanceEngine(store,tool_config=config,category_config=category)
            try:
                operation=engine.retry_unknown(job,params['step']) if command=='retry' else getattr(engine,command)(job)
                return await total_deadline(operation,params.get('timeout',30))
            finally:await engine.close()
        return asyncio.run(execute())
    except CliFailure:raise
    except MaintenanceError as error:
        raise CliFailure('E_USAGE' if command=='create' else 'E_OPERATION','Maintenance operation rejected: '+error.code+'.') from None
    except (ValueError,TypeError,KeyError):
        raise CliFailure('E_USAGE','Invalid maintenance configuration; consult packaged schemas.') from None
    except (OSError,sqlite3.Error):
        raise CliFailure('E_OPERATION','Cannot access selected maintenance database or configuration.') from None
    finally:
        if store is not None:store.close()


_REF=re.compile(r'^([A-Za-z][A-Za-z0-9_-]{0,63})#((?:/(?:[^~]|~[01])*)*)$')


def references(value,prior,*,resolve=False):
    if isinstance(value,dict):
        if '$ref' in value:
            if set(value)!={'$ref'} or not isinstance(value['$ref'],str):raise CliFailure('E_USAGE','Invalid session reference.')
            match=_REF.fullmatch(value['$ref'])
            if match is None or match[1] not in prior:raise CliFailure('E_USAGE','References must target an earlier step and a valid JSON pointer.')
            if not resolve:return value
            result=prior[match[1]]
            try:
                for part in match[2].split('/')[1:]:
                    key=part.replace('~1','/').replace('~0','~')
                    if isinstance(result,list):
                        if not re.fullmatch('0|[1-9][0-9]*',key):raise ValueError()
                        result=result[int(key)]
                    else:result=result[key]
                return copy.deepcopy(result)
            except (KeyError,IndexError,TypeError,ValueError):
                raise CliFailure('E_USAGE','Session reference target is unavailable.') from None
        return {key:references(item,prior,resolve=resolve) for key,item in value.items()}
    if isinstance(value,list):return [references(item,prior,resolve=resolve) for item in value]
    return value


def preflight_arguments(name,args,limits=None):
    """Reject literal shape/type/budget errors in every step before runtime creation."""
    from .tools.contracts import FIELDS,validate,ToolError
    from .tools.runtime import Limits
    limits=limits or Limits()
    def is_ref(value):return isinstance(value,dict) and set(value)=={'$ref'}
    def literal(value):
        if isinstance(value,dict) and set(value)=={'$ref'}:return 'reference'
        return value
    resolved={key:literal(value) for key,value in args.items()}
    try:
        if name=='bootstrap':object_value(args,())
        elif name=='poll':
            object_value(args,('job_id','interval_seconds'),('job_id',))
            validate('job_status',{'schema_version':'1.0','job_id':resolved['job_id']},limits)
            if 'interval_seconds' in args and not is_ref(args['interval_seconds']):numeric(args['interval_seconds'],.01,1)
        elif name=='pages':
            object_value(args,('job_id','collection','page_size','cursor','max_pages'),('job_id','collection'))
            if 'max_pages' in args and not is_ref(args['max_pages']):numeric(args['max_pages'],1,10,integer=True)
            native={'schema_version':'1.0',**{key:value for key,value in resolved.items() if key!='max_pages'}}
            for key in ('page_size',):
                if is_ref(args.get(key)):native[key]=1
            validate('job_result',native,limits)
        else:
            for key in ('max_items','page_size','timeout_seconds'):
                if is_ref(args.get(key)):resolved[key]=1
            validate(name,resolved,limits)
    except ToolError:
        raise CliFailure('E_USAGE','Invalid native session arguments; consult schema show tool:NAME.') from None


def load_session(path,limits=None):
    from .tools.runtime import TOOL_NAMES
    value=object_value(read_json_file(path),('schema_version','steps'),('schema_version','steps'))
    if value['schema_version']!='1.0' or not isinstance(value['steps'],list) or not 1<=len(value['steps'])<=32:
        raise CliFailure('E_USAGE','Session requires version1.0 and 1..32 steps.')
    prior={}
    for step in value['steps']:
        object_value(step,('id','tool','arguments'),('id','tool','arguments'))
        if (not isinstance(step['id'],str) or not re.fullmatch('[A-Za-z][A-Za-z0-9_-]{0,63}',step['id'])
                or step['id'] in prior or step['tool'] not in (*TOOL_NAMES,'bootstrap','poll','pages')
                or not isinstance(step['arguments'],dict)):
            raise CliFailure('E_USAGE','Invalid session step id, tool or arguments.')
        references(step['arguments'],prior)
        preflight_arguments(step['tool'],step['arguments'],limits)
        prior[step['id']]=None
    return value


def native_error(result):
    if not result['ok']:
        raise CliFailure('E_OPERATION','Native tool rejected operation: '+result['error']['code']+'.')
    return result


async def run_session(config,request,seconds):
    from .tools import ToolRuntime
    from .tools.contracts import ToolError,validate
    runtime=ToolRuntime(config)
    async def call(name,args):return native_error(await runtime.call(name,args))
    async def poll(job,interval=.05):
        while True:
            status=await call('job_status',{'schema_version':'1.0','job_id':job})
            state=status['data']['state']
            if state=='succeeded':return status
            if state not in {'queued','running'}:raise CliFailure('E_OPERATION','Native tool job terminated: '+state+'.')
            await asyncio.sleep(interval)
    async def execute():
        prior={};rows=[];partial=False
        for step in request['steps']:
            args=references(step['arguments'],prior,resolve=True);name=step['tool']
            if name=='bootstrap':
                object_value(args,())
                result=await runtime.bootstrap()
            elif name=='poll':
                object_value(args,('job_id','interval_seconds'),('job_id',))
                validate('job_status',{'schema_version':'1.0','job_id':args['job_id']},config.limits)
                result=await poll(args['job_id'],numeric(args.get('interval_seconds',.05),.01,1))
            elif name=='pages':
                object_value(args,('job_id','collection','page_size','cursor','max_pages'),('job_id','collection'))
                maximum=numeric(args.pop('max_pages',10),1,10,integer=True)
                native={'schema_version':'1.0',**args};validate('job_result',native,config.limits)
                await poll(args['job_id']);pages=[];cursor=None;complete=True
                for _ in range(maximum):
                    page=await call('job_result',native);pages.append(page)
                    data=page['data'];cursor=data['next_cursor'];complete &= data['completeness']=='complete'
                    # Bound while collecting, not only after all pages have accumulated.
                    if len(json.dumps(pages,ensure_ascii=False).encode())>MAX_BYTES:
                        raise CliFailure('E_OPERATION','Session pages exceed CLI response limit; request fewer/smaller pages.')
                    if cursor is None:break
                    native['cursor']=cursor
                complete &= cursor is None
                result={'pages':pages,'next_cursor':cursor,'complete':complete};partial |= not complete
            else:
                validate(name,args,config.limits)
                result=await call(name,args)
            prior[step['id']]=result;rows.append({'id':step['id'],'tool':name,'result':result})
            if len(json.dumps(rows,ensure_ascii=False).encode())>MAX_BYTES:
                raise CliFailure('E_OPERATION','Session result exceeds CLI response limit; use a smaller session.')
        return {'session_only':True,'steps':rows,'completeness':'partial' if partial else 'complete'}
    try:
        return await total_deadline(execute(),seconds)
    except ToolError as error:
        raise CliFailure('E_USAGE' if error.code in {'invalid_argument','unsupported_version'} else 'E_OPERATION',
                         'Native tool rejected operation: '+error.code+'.') from None
    finally:await runtime.aclose()


def register(main):
    @main.group('maintenance')
    @click.option('--db',type=click.Path(dir_okay=False),help='Required explicit durable maintenance SQLite scope for operations.')
    @click.option('--profiles',type=click.Path(dir_okay=False),help='Versioned trusted custom profile definitions.')
    @click.option('--category-config',type=click.Path(dir_okay=False),help='Native category runtime record.')
    @click.option('--operator-config',type=click.Path(dir_okay=False),help='Trusted native tool policy and limits.')
    @click.option('--allow-origin',multiple=True,help='Trusted public supplier origin; repeatable.')
    @click.pass_context
    def maintenance(ctx,**scope):
        """Durable local read-only supplier maintenance; no merchant writes."""
        ctx.obj=scope
    maintenance.command_class=CoreCommand
    def finish(command,scope,job=None,**params):
        data=maintenance_operation(command,scope,job,**params)
        bounded_output(data,partial=command in {'run','resume','retry'} and data.get('state') in {'partial','paused','failed'})
    @maintenance.command('create')
    @click.argument('goal',type=click.Path(dir_okay=False))
    @click.pass_obj
    def create(scope,goal):finish('create',scope,goal=goal)
    for name in ('status','show','cancel','run','resume'):
        def build(command):
            @click.argument('job')
            @click.pass_obj
            def action(scope,job,**params):finish(command,scope,job,**params)
            if command in {'run','resume'}:action=click.option('--timeout',default=30.,show_default=True,type=click.FloatRange(1,120))(action)
            maintenance.command(command)(action)
        build(name)
    for name in ('list','report'):
        def build(command):
            @click.option('--offset',type=click.IntRange(0),default=0,show_default=True)
            @click.option('--limit',type=click.IntRange(1,1000),default=100,show_default=True)
            @click.pass_obj
            def action(scope,**params):finish(command,scope,**params)
            if command=='report':action=click.argument('job')(action)
            maintenance.command(command)(action)
        build(name)
    @maintenance.command('evidence')
    @click.argument('job')
    @click.argument('evidence_id')
    @click.pass_obj
    def evidence(scope,job,evidence_id):finish('evidence',scope,job,evidence_id=evidence_id)
    @maintenance.command('retry')
    @click.argument('job')
    @click.argument('step')
    @click.option('--timeout',default=30.,type=click.FloatRange(1,120),show_default=True)
    @click.pass_obj
    def retry(scope,job,step,timeout):finish('retry',scope,job,step=step,timeout=timeout)
    @main.group('tools')
    def tools():
        """Restricted read-only native tool schemas, bounded sessions and MCP stdio."""
    tools.command_class=CoreCommand
    @tools.command('schemas')
    def schemas():
        from .tools.contracts import schema
        from .tools.runtime import TOOL_NAMES
        bounded_output({'native_schema_version':'1.0','tools':[schema(name) for name in TOOL_NAMES]})
    @tools.command('call')
    @click.option('--config','config_path',required=True,type=click.Path(dir_okay=False),help='Trusted native operator config (not root CLI settings).')
    @click.option('--request',required=True,type=click.Path(dir_okay=False),help='Versioned session steps JSON; - for stdin.')
    @click.option('--timeout',default=30.,type=click.FloatRange(1,120),show_default=True)
    def tool_call(config_path,request,timeout):
        # Full topology is validated before any runtime exists.
        config=load_operator(config_path);spec=load_session(request,config.limits)
        data=asyncio.run(run_session(config,spec,timeout))
        bounded_output(data,partial=data['completeness']=='partial')
    @tools.command('serve')
    @click.option('--config','config_path',required=True,type=click.Path(dir_okay=False),help='Trusted native operator config; stdout is MCP JSON-RPC only.')
    def serve(config_path):
        try:
            import mcp
        except ImportError:
            raise CliFailure('E_DEPENDENCY','Install shopextract[mcp] to run the MCP server.') from None
        try:config=load_operator(config_path)
        except CliFailure:
            raise CliFailure('E_CONFIG','Invalid or unavailable operator config; consult schema show tool-operator.') from None
        from .tools import ToolRuntime
        from .tools.mcp_server import serve as native_serve
        asyncio.run(native_serve(ToolRuntime(config)))
