"""Monitoring and evidence CLI adapters; native services own all algorithms."""
from __future__ import annotations

import asyncio
import json
import os
import sqlite3
import tempfile
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

import click

from ._cli_core import CliFailure, CoreCommand
from ._cli_analysis import output, number
from ._cli_data import read_json_file, load_products, atomic_json, MAX_BYTES
from ._cli_extract import validate_url, validate_max, validate_timeout, run_operation, execution_options, policy_options
from ._evidence import encode_value
from ._execution import ExecutionPolicy, execution_policy
from ._portable import product_to_record

DEFAULT_DB = '~/.shopextract/snapshots.db'


def time_value(value):
    try:
        parsed = datetime.fromisoformat(value.replace('Z','+00:00'))
        if parsed.utcoffset() is None:
            raise ValueError()
        return parsed.astimezone(timezone.utc)
    except (ValueError,AttributeError,OverflowError):
        raise CliFailure('E_USAGE','Expected timezone-aware ISO timestamp.') from None


def existing_db(path, ids=(), domain=None, *, reliable=False):
    from .monitor.changes import _open_read_db
    from .identity import supplier_scope
    try:
        with closing(_open_read_db(path)) as conn:
            conn.execute('SELECT id,domain,products_json,created_at FROM snapshots LIMIT 0')
            rows=[]
            for sid in ids:
                row=conn.execute('SELECT id,domain,created_at FROM snapshots WHERE id=?',(sid,)).fetchone()
                if row is None or domain is not None and row[1] != supplier_scope(domain):
                    raise CliFailure('E_USAGE','Snapshot ID does not exist in the requested supplier scope.')
                rows.append(row)
            if reliable:
                scopes=[conn.execute('SELECT observation_scope FROM snapshots WHERE id=?',(row[0],)).fetchone()[0] for row in rows]
                if any((a[2],a[0]) >= (b[2],b[0]) for a,b in zip(rows,rows[1:])):
                    raise CliFailure('E_USAGE','Snapshot ordering must be previous, current, recheck.')
                if len({s for s in scopes if s})>1 or len(rows)>2 and (not all(scopes) or len(set(scopes))!=1):
                    raise CliFailure('E_USAGE','Reliable comparison requires matching selected snapshot scopes.')
        return str(Path(path).expanduser())
    except CliFailure:
        raise
    except FileNotFoundError:
        raise CliFailure('E_USAGE','Existing snapshot database is required.') from None
    except sqlite3.Error:
        raise CliFailure('E_OPERATION','Invalid snapshot schema; explicit migration or supported database required.') from None


def native(operation, *, stored=False):
    from .monitor.evidence import PreviewLimitError
    try:
        return operation()
    except CliFailure:
        raise
    except PreviewLimitError as exc:
        message = ('Read-only prune preview exceeds 64 MiB logical database limit; use a smaller retained database.'
                   if exc.reason == 'size' else 'Read-only prune preview exceeded 5 seconds copying; release database contention and retry.')
        raise CliFailure('E_OPERATION',message) from None
    except (ValueError,KeyError) as exc:
        if 'migration required' in str(exc):
            raise CliFailure('E_OPERATION','Identity migration required; run identity migrate --db DB --apply.') from None
        raise CliFailure('E_OPERATION' if stored else 'E_USAGE','Stored data integrity validation failed.' if stored else 'Native input validation failed; check identifiers, scope, schema and artifact correspondence.') from None
    except (OSError,sqlite3.Error,TypeError,AttributeError):
        raise CliFailure('E_OPERATION','Cannot complete local storage or artifact operation; check schema and permissions.') from None


def change_record(change):
    fields={'PriceChange':('title','old_price','new_price','currency'),
            'NewProduct':('title','price','currency'),
            'RemovedProduct':('title','last_price','currency')}
    name=type(change).__name__
    return dict(type=name,**{key:encode_value(getattr(change,key)) for key in fields[name]})


def snapshot_command(url, db, maximum, timeout, options=None):
    from .monitor.snapshot import snapshot
    validate_url(url); validate_max(maximum)
    policy, deadline = policy_options(dict(options or {}, timeout=timeout))
    try:
        count,_=run_operation(lambda:snapshot(url,db_path=db,max_urls=maximum,retain_limit=maximum),policy,deadline)
    except (ValueError,OSError,sqlite3.Error):
        raise CliFailure('E_OPERATION','Snapshot source or persistence failed; no usable baseline established.') from None
    output({'stored_products':count})


def changes_command(domain, db, reliable, previous, current, recheck):
    from .monitor.changes import changes
    from .monitor.reliable import reliable_changes
    if reliable:
        if previous is None or current is None:
            raise CliFailure('E_USAGE','Reliable changes requires --previous and --current.')
        ids=(previous,current)+((recheck,) if recheck is not None else ())
        path=existing_db(db,ids,domain,reliable=True)
        output(native(lambda:reliable_changes(domain,previous_snapshot_id=previous,current_snapshot_id=current,recheck_snapshot_id=recheck,db_path=path),stored=True))
    else:
        if any(v is not None for v in (previous,current,recheck)):
            raise CliFailure('E_USAGE','Snapshot selectors require --reliable.')
        path=existing_db(db)
        output({'changes':[change_record(c) for c in native(lambda:changes(domain,db_path=path,read_only=True))]})


def history_command(domain, product, db, canonical_id):
    from .monitor.changes import price_history
    path=existing_db(db)
    entries=native(lambda:price_history(domain,product,db_path=path,canonical_product_id=canonical_id,exact=True,read_only=True))
    output({'entries':[dict(timestamp=t.isoformat(),price=encode_value(p)) for t,p in entries]})


def metadata_file(path):
    if path is None:
        return None
    data=read_json_file(path)
    if not isinstance(data,dict) or set(data)!={'schema_version','metadata'} or type(data['schema_version']) is not int or data['schema_version']!=1 or not isinstance(data['metadata'],dict):
        raise CliFailure('E_USAGE','Expected version1 metadata envelope.')
    meta=data['metadata']
    if set(meta)-{'observation_scope','catalog_complete','incompleteness_reasons','max_urls'}:
        raise CliFailure('E_USAGE','Unknown snapshot metadata key.')
    if meta.get('max_urls') is not None and (type(meta['max_urls']) is not int or not 1<=meta['max_urls']<=1000):
        raise CliFailure('E_USAGE','Metadata max_urls must be integer1..1000 or null.')
    # Native preparation validates the other closed types before DB initialization.
    return meta


def policy_file(path):
    from ._resolution import ResolutionPolicy
    if path is None:
        return ResolutionPolicy()
    value=read_json_file(path)
    keys={'offer_max_age_seconds','specification_max_age_seconds'}
    if not isinstance(value,dict) or set(value)-keys-{'schema_version'} or type(value.get('schema_version')) is not int or value['schema_version']!=1:
        raise CliFailure('E_USAGE','Expected closed version1 resolution policy.')
    kwargs={}
    for key in keys & value.keys():
        seconds=value[key]
        if type(seconds) is not int or not 1<=seconds<=31536000:
            raise CliFailure('E_USAGE','Policy ages must be integer seconds1..31536000.')
        kwargs[key.removesuffix('_seconds')]=timedelta(seconds=seconds)
    return ResolutionPolicy(**kwargs)


def payload_bytes(path):
    try:
        if path=='-':
            raw=click.get_binary_stream('stdin').read(MAX_BYTES+1)
        else:
            with open(path,'rb') as stream:
                raw=stream.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:
            raise CliFailure('E_USAGE','Projection exceeds1MiB.')
        return raw
    except OSError:
        raise CliFailure('E_USAGE','Cannot read projection file.') from None


def check_destination(destination, *inputs):
    if not destination:
        return
    target=Path(destination).expanduser()
    for source in inputs:
        if source is None or source=='-':
            continue
        candidate=Path(source).expanduser()
        if target.resolve()==candidate.resolve() or target.exists() and candidate.exists() and target.samefile(candidate):
            raise CliFailure('E_USAGE','Output must differ from every input artifact and projection.')


def bound_artifact(value):
    if len(json.dumps(value,ensure_ascii=False,allow_nan=False).encode('utf-8'))>MAX_BYTES:
        raise CliFailure('E_USAGE','Artifact exceeds CLI1MiB output limit; reduce the input catalog.')


def artifact(value, path):
    bound_artifact(value)
    if path:
        atomic_json(path,value)
        output({'output':str(path)})
    else:
        output(value)


def portable_output(records, destination):
    if destination:
        artifact(records,destination)
    else:
        output({'products':records})


def inspect_value(value):
    from ._models import Variant
    if isinstance(value,Variant):
        names=('variant_id','title','price','sku','in_stock','canonical_variant_id','attributes','gtin')
        return {name:inspect_value(getattr(value,name)) for name in names}
    if isinstance(value,dict):
        return {key:inspect_value(item) for key,item in value.items()}
    if isinstance(value,list):
        return [inspect_value(item) for item in value]
    return encode_value(value)


def register(main):
    @main.command('snapshot-save',cls=CoreCommand)
    @click.argument('file')
    @click.option('--domain',required=True)
    @click.option('--db',default=DEFAULT_DB)
    @click.option('--metadata',type=click.Path())
    def snapshot_save(file,domain,db,metadata):
        from .monitor.evidence import save_snapshot
        from .identity import supplier_scope
        if not supplier_scope(domain).strip() or len(domain)>2048:
            raise CliFailure('E_USAGE','Nonempty supplier domain required.')
        if file==metadata=='-':
            raise CliFailure('E_USAGE','Only one input may read stdin.')
        products=load_products(file); meta=metadata_file(metadata)
        output({'snapshot_id':native(lambda:save_snapshot(products,domain,db_path=db,metadata=meta))})

    @main.command('snapshot-load',cls=CoreCommand)
    @click.argument('snapshot_id',type=click.IntRange(1))
    @click.option('--db',default=DEFAULT_DB)
    def snapshot_load(snapshot_id,db):
        from .monitor.evidence import load_snapshot
        path=existing_db(db,(snapshot_id,))
        output({'products':[product_to_record(p) for p in native(lambda:load_snapshot(snapshot_id,db_path=path,read_only=True),stored=True)]})

    @main.command('resolve',cls=CoreCommand)
    @click.argument('file')
    @click.option('--as-of',required=True)
    @click.option('--policy',type=click.Path())
    def resolve(file,as_of,policy):
        from ._resolution import resolve_fields,resolution_references
        if file==policy=='-':
            raise CliFailure('E_USAGE','Only one input may read stdin.')
        when=time_value(as_of); rules=policy_file(policy); products=load_products(file); refs=[]
        for product in products:
            owner_refs=[]
            for owner in [product,*product.variants]:
                graph=getattr(owner,'evidence_contract',None)
                if graph is None:
                    owner_refs.append(None)
                else:
                    graph=native(lambda:resolve_fields(graph,as_of=when,policy=rules))
                    owner.evidence_contract=graph
                    owner_refs.append(resolution_references(graph))
            refs.append(dict(product=owner_refs[0],variants=owner_refs[1:]))
        output({'products':[product_to_record(p) for p in products],'references':refs})

    @main.command('watch',cls=CoreCommand)
    @click.argument('url')
    @click.option('--interval',type=float,required=True)
    @click.option('--max-events',type=click.IntRange(1,1000),required=True)
    @execution_options(timeout_required=True)
    @click.option('--max','maximum',type=click.IntRange(1,1000),default=20)
    @click.option('--db',default=DEFAULT_DB)
    def watch(url,interval,max_events,timeout,maximum,db,**options):
        from .monitor.watch import watch as native_watch
        validate_url(url); number(interval,low=0,high=3600,strict=True,name='interval')
        if timeout is None:
            raise CliFailure('E_USAGE','Watch requires an explicit --timeout.')
        policy, deadline=policy_options(dict(options,timeout=timeout))
        state={'events':0,'initialized':False}
        async def consume():
            with execution_policy(policy,deadline):
                generator=native_watch(url,interval=interval,db_path=db,max_urls=maximum,retain_limit=maximum,on_initialized=lambda:state.update(initialized=True))
                try:
                    async for change in generator:
                        output({'event':change_record(change),'verification':'unverified_scalar_comparison'})
                        state['events']+=1
                        if state['events']>=max_events:
                            break
                finally:
                    await generator.aclose()
        async def bounded():
            await asyncio.wait_for(consume(),deadline)
        try:
            asyncio.run(bounded())
        except asyncio.TimeoutError:
            output({'events':state['events'],'reason':'timeout','initialized':state['initialized']},partial=True)
        except (ValueError,OSError,sqlite3.Error):
            raise CliFailure('E_OPERATION','Watch source or persistence failed; monitoring did not complete.') from None
        output({'events':state['events'],'reason':'max_events','initialized':state['initialized']})

    @main.group('evidence',cls=click.Group)
    def evidence():
        """Inspect captured support and explicitly manage local retention/artifacts."""

    @evidence.command('inspect',cls=CoreCommand)
    @click.argument('file')
    @click.option('--view',type=click.Choice(['trust','paths']),default='trust')
    def inspect(file,view):
        from ._evidence import factual_paths
        rows=[]
        for product in load_products(file):
            values=[owner.trust_view() if view=='trust' else factual_paths(owner) for owner in [product,*product.variants]]
            rows.append({'product':inspect_value(values[0]),'variants':inspect_value(values[1:])})
        output({'views':rows})

    @evidence.command('get',cls=CoreCommand)
    @click.argument('evidence_id')
    @click.option('--snapshot','snapshot_id',type=click.IntRange(1),required=True)
    @click.option('--record-key',required=True)
    @click.option('--db',default=DEFAULT_DB)
    def get(evidence_id,snapshot_id,record_key,db):
        from .monitor.evidence import get_evidence
        path=existing_db(db,(snapshot_id,))
        lookup=native(lambda:get_evidence(evidence_id,snapshot_id=snapshot_id,record_key=record_key,db_path=path,read_only=True),stored=True)
        fields=('evidence_id','source_url','observed_at','method','excerpt','retained_data','pointer','source_role','truncated')
        capture=None if lookup.evidence is None else {key:encode_value(getattr(lookup.evidence,key)) for key in fields}
        output(dict(status=lookup.status,evidence_id=lookup.evidence_id,reason=lookup.reason,evidence=capture,snapshot_id=lookup.snapshot_id,record_key=lookup.record_key,expired_at=encode_value(lookup.expired_at)))

    @evidence.command('prune',cls=CoreCommand)
    @click.option('--before',required=True)
    @click.option('--db',required=True)
    @click.option('--apply',is_flag=True)
    @click.option('--unprotect-references',is_flag=True)
    @click.option('--batch-size',type=click.IntRange(1,1000),default=100)
    def prune(before,db,apply,unprotect_references,batch_size):
        from .monitor.evidence import prune_evidence
        when=time_value(before); path=existing_db(db)
        report=native(lambda:prune_evidence(db_path=path,before=when,protect_references=not unprotect_references,dry_run=not apply,batch_size=batch_size,read_only_preview=not apply),stored=True)
        output({name:getattr(report,name) for name in ('examined','protected','expired','payloads_deleted','dry_run','has_more')})

    @evidence.group('bundle',cls=click.Group)
    def bundle():
        """Native portable evidence bundle lifecycle."""

    @bundle.command('create',cls=CoreCommand)
    @click.argument('file')
    @click.option('-o','--output','destination',type=click.Path())
    def bundle_create(file,destination):
        from .export._bundle import create_evidence_bundle,write_evidence_bundle,read_evidence_bundle
        check_destination(destination,file)
        products=load_products(file)
        value=native(lambda:create_evidence_bundle(products)); bound_artifact(value)
        if not destination:
            output(native(lambda:create_evidence_bundle(products))); return
        temporary=None
        try:
            target=Path(destination)
            with tempfile.NamedTemporaryFile(dir=target.parent,prefix=f'.{target.name}.',delete=False) as stream:
                temporary=stream.name
            native(lambda:write_evidence_bundle(products,temporary))
            native(lambda:read_evidence_bundle(temporary))
            os.replace(temporary,target)
        except OSError:
            raise CliFailure('E_OPERATION','Cannot publish evidence bundle; existing output preserved.') from None
        finally:
            if temporary and os.path.exists(temporary):os.unlink(temporary)
        output({'output':destination})

    @bundle.command('load',cls=CoreCommand)
    @click.argument('file')
    @click.option('-o','--output','destination',type=click.Path())
    def bundle_load(file,destination):
        from .export._bundle import load_evidence_bundle
        check_destination(destination,file)
        value=read_json_file(file)
        products=native(lambda:load_evidence_bundle(value))
        if len(products)>1000:raise CliFailure('E_USAGE','Bundle exceeds CLI1000product limit.')
        records=[product_to_record(p) for p in products]
        portable_output(records,destination)

    @evidence.group('sidecar',cls=click.Group)
    def sidecar():
        """Digest-bound exported projection lifecycle."""

    @sidecar.command('create',cls=CoreCommand)
    @click.argument('file')
    @click.option('--payload',required=True)
    @click.option('--format','fmt',type=click.Choice(['csv','google_shopping','idealo']),required=True)
    @click.option('-o','--output','destination',type=click.Path())
    def sidecar_create(file,payload,fmt,destination):
        from .export._bundle import create_evidence_sidecar
        if file==payload=='-':raise CliFailure('E_USAGE','Only one input may read stdin.')
        check_destination(destination,file,payload)
        products=load_products(file); raw=payload_bytes(payload)
        artifact(native(lambda:create_evidence_sidecar(products,raw,format=fmt)),destination)

    @sidecar.command('load',cls=CoreCommand)
    @click.argument('file')
    @click.option('--payload',required=True)
    @click.option('-o','--output','destination',type=click.Path())
    def sidecar_load(file,payload,destination):
        from .export._bundle import load_evidence_sidecar
        if file==payload=='-':raise CliFailure('E_USAGE','Only one input may read stdin.')
        check_destination(destination,file,payload)
        value=read_json_file(file); raw=payload_bytes(payload)
        products=native(lambda:load_evidence_sidecar(value,raw))
        if len(products)>1000:raise CliFailure('E_USAGE','Sidecar exceeds CLI1000product limit.')
        portable_output([product_to_record(p) for p in products],destination)

    @main.commands['identity'].command('migrate',cls=CoreCommand)
    @click.option('--db',required=True)
    @click.option('--apply',is_flag=True)
    def migrate(db,apply):
        from .identity import migrate_snapshot_identities
        from .monitor.snapshot import _ensure_snapshot_metadata
        if not apply:raise CliFailure('E_USAGE','Identity migration requires explicit --apply; preview is unsupported.')
        path=existing_db(db)
        def operation():
            with closing(sqlite3.connect(path,timeout=5)) as conn:
                with conn:
                    conn.execute('BEGIN IMMEDIATE')
                    _ensure_snapshot_metadata(conn)
                    return migrate_snapshot_identities(conn)
        output({'applied':True,'updated':native(operation)})
