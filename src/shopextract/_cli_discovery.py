"""Static packaged contracts and actual Click grammar for noninteractive clients."""
from __future__ import annotations
import json
from importlib import resources
import click
from ._cli_core import CliFailure, CoreCommand


def command_inventory(root):
    rows=[]
    def walk(command,path):
        params=[]
        for p in command.params:
            item={'name':p.name,'kind':'option' if isinstance(p,click.Option) else 'argument',
                  'required':p.required,'nargs':p.nargs,'multiple':getattr(p,'multiple',False),
                  'type':p.type.name,'default':p.default if isinstance(p.default,(str,int,float,bool,list,tuple,dict,type(None))) else None}
            if isinstance(p,click.Option):item.update(options=p.opts,secondary_options=p.secondary_opts,is_flag=p.is_flag,help=p.help)
            if isinstance(p.type,click.Choice):item['choices']=list(p.type.choices)
            if isinstance(p.type,(click.IntRange,click.FloatRange)):
                item.update(min=p.type.min,max=p.type.max)
            params.append(item)
        group=isinstance(command,click.Group)
        output='json-envelope-or-artifact-stdout' if path==['export'] else 'protocol-stdio' if path==['tools','serve'] else 'jsonl' if path==['watch'] else 'legacy-or-json' if len(path)==1 and path[0] in {'detect','discover','extract','compare','analyze','validate','snapshot','changes','history'} else 'json-envelope'
        row={'path':path,'group':group,'help':command.help or '',
                     'parameters':params,'output_contract':output,'help_option':'--help'}
        if path==['export']:
            row['output_modes']=[{'when':{'--output':'-'},'contract':'artifact-stdout','format_option':'--format'},
                                 {'when':'otherwise','contract':'json-envelope'}]
        rows.append(row)
        if group:
            for name,child in sorted(command.commands.items()):walk(child,[*path,name])
    walk(root,[])
    return rows


def packaged_schema(name):
    if name.startswith('tool:'):
        from .tools.contracts import FIELDS,schema
        if name[5:] in FIELDS:return schema(name[5:])
    if not name or any(v not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for v in name):
        raise CliFailure('E_USAGE','Unknown schema; use schema list.')
    try:return json.loads(resources.files('shopextract').joinpath('schemas',name+'.schema.json').read_text())
    except (FileNotFoundError,ValueError):raise CliFailure('E_USAGE','Unknown schema; use schema list.') from None


def register(main):
    from ._cli_operations import bounded_output
    @main.command('capabilities')
    def capabilities():
        """Versioned installed command grammar; does not initialize extraction or tools."""
        bounded_output({'schema_version':'1.0','response_schema_version':'1.0',
                        'commands':command_inventory(main),
                        'root_options_before_command':True,
                        'limits':{'input_bytes':1048576,'depth':64,'records':1000,'json_nodes':100000},
                        'schema_discovery':['schema','list'],
                        'session_handles':'one tools call invocation','maintenance_ids':'durable within explicit --db'})
    @main.group('schema')
    def schema_group():
        """Packaged versioned file contracts and native tool input/output schemas."""
    schema_group.command_class=CoreCommand
    @schema_group.command('list')
    def list_schemas():
        from .tools.runtime import TOOL_NAMES
        values=json.loads(resources.files('shopextract').joinpath('schemas','index.json').read_text())
        bounded_output({'schema_version':'1.0','schemas':values+[{'name':'tool:'+name,'version':'1.0','kind':'native-tool'} for name in TOOL_NAMES]})
    @schema_group.command('show')
    @click.argument('name')
    def show_schema(name):bounded_output({'name':name,'schema':packaged_schema(name)})
