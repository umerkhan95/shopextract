"""Local read-only maintenance CLI; origins and profiles are operator configuration."""
import argparse
import asyncio
import json
from pathlib import Path

from . import Budgets, Goal, MaintenanceEngine, MaintenanceError, MaintenanceStore
from .profiles import CategoryProfile, FieldRule
from ..tools import ToolConfig


def load_profiles(path):
    if path is None:
        return {}
    values=json.loads(Path(path).read_text())
    return {name:CategoryProfile(name,{key:FieldRule(**value) for key,value in fields.items()})
            for name,fields in values.items()}


async def execute(args):
    store=MaintenanceStore(args.db,custom_profiles=load_profiles(args.profiles))
    try:
        if args.command=='create':
            data=json.loads(Path(args.goal).read_text())
            data['budgets']=Budgets(**data.get('budgets',{}))
            for key in ('baseline','product_urls','fields'):
                if key in data:data[key]=tuple(data[key])
            return {'job_id':store.create(Goal(**data))}
        if args.command=='status':return store.status(args.job)
        if args.command=='report':return store.report(args.job,offset=args.offset,limit=args.limit,include_profile_coverage=args.coverage)
        if args.command=='evidence':return store.evidence(args.job,args.evidence_id)
        engine=MaintenanceEngine(store,tool_config=ToolConfig(allowed_origins=tuple(args.allow_origin)))
        try:
            if args.command=='retry':return await engine.retry_unknown(args.job,args.step)
            return await getattr(engine,args.command)(args.job)
        finally:await engine.close()
    finally:store.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',required=True,help='Local SQLite state file')
    parser.add_argument('--profiles',help='Trusted JSON custom profile definitions')
    parser.add_argument('--allow-origin',action='append',default=[],help='Explicit trusted source origin; repeatable')
    commands=parser.add_subparsers(dest='command',required=True)
    create=commands.add_parser('create');create.add_argument('goal',help='Versioned goal JSON')
    for name in ('run','resume','status','cancel'):
        command=commands.add_parser(name);command.add_argument('job')
    report=commands.add_parser('report');report.add_argument('job');report.add_argument('--offset',type=int,default=0);report.add_argument('--limit',type=int,default=100);report.add_argument('--coverage',action='store_true')
    evidence=commands.add_parser('evidence');evidence.add_argument('job');evidence.add_argument('evidence_id')
    retry=commands.add_parser('retry');retry.add_argument('job');retry.add_argument('step')
    try:
        args=parser.parse_args()
        result=asyncio.run(execute(args))
        if args.command=='report' and args.coverage:
            from .reporting import encode_coverage_response
            encoded=encode_coverage_response({'ok':True,'data':result})
            print(encoded.decode('utf-8'),end='')
            return
    except (MaintenanceError,ValueError,TypeError,OSError) as error:
        print(json.dumps({'ok':False,'error':getattr(error,'code','invalid_argument'),'message':str(error)}))
        raise SystemExit(2)
    print(json.dumps({'ok':True,'data':result},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
