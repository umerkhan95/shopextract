"""One approved all-category attempt with an independent bounded parent watchdog.

No automatic resume: exclusive attempt marker rejects stale or repeated starts.
Child progress is durable evidence bound to source/code/catalog and exact IDs.
"""
import hashlib,json,os,signal,subprocess,sys,threading,time,uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/shopify-taxonomy'
SECONDS=540
RSS_BYTES=512*1024*1024
BATCH_SECONDS=15


def atomic_json(path,value):
    temporary=path.with_suffix(path.suffix+'.partial')
    with temporary.open('w') as stream:
        json.dump(value,stream,separators=(',',':'));stream.flush();os.fsync(stream.fileno())
    temporary.replace(path)
    descriptor=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(descriptor)
    finally:os.close(descriptor)


def code_identity(root=ROOT):
    paths=sorted((root/'src/shopextract').rglob('*.py'))+[root/'tests/shopify_taxonomy_sweep.py',root/'src/shopextract/taxonomies/shopify/pin.json']
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def group_rss(pid):
    # Darwin and Linux ps expose resident KiB. Include auxiliary descendants in
    # this process session/group; the parent never loads the application catalog.
    values=subprocess.check_output(['ps','-ax','-o','pgid=,rss='],text=True,timeout=2)
    return sum(int(rss)*1024 for group,rss in (line.split() for line in values.splitlines()) if int(group)==pid)


def cleanup(process):
    try:os.killpg(process.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    process.wait(timeout=2)
    # Adopted descendants can be reaped on Linux; on macOS launchd owns orphans.
    while True:
        try:
            child,_=os.waitpid(-process.pid,os.WNOHANG)
            if child==0:break
        except ChildProcessError:break


def validate_progress(value,binding,previous):
    if not isinstance(value,dict) or value.get('binding')!=binding:raise ValueError('stale_progress_binding')
    ids=value.get('processed_ids')
    if (not isinstance(ids,list) or any(not isinstance(v,str) for v in ids) or len(ids)!=len(set(ids))
        or ids[:len(previous)]!=previous or len(ids)>14606 or value.get('categories')!=len(ids)):
        raise ValueError('invalid_processed_ids')
    return ids


def monitor(command,directory,binding,*,seconds=SECONDS,rss_bytes=RSS_BYTES,batch_seconds=BATCH_SECONDS):
    """Parent only: independent deadline/RSS checks; no application imports."""
    progress=directory/'progress.json';status=directory/'status.json';log=directory/'run.log'
    if progress.exists() or status.exists():raise ValueError('existing_attempt_state; automatic resume forbidden')
    started=time.monotonic();changed=started;ids=[];peak=0;reason=None;last_mtime=None
    process=None;watchdog=None;expired=threading.Event()
    try:
        with log.open('wb') as output:
            process=subprocess.Popen(command,stdout=output,stderr=output,start_new_session=True)
            def hard_stop():
                expired.set()
                try:os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError:pass
            watchdog=threading.Timer(max(0,seconds-(time.monotonic()-started)),hard_stop)
            watchdog.daemon=True;watchdog.start()
            while True:
                now=time.monotonic()
                if expired.is_set() or now-started>=seconds:reason='aggregate_timeout';break
                if now-changed>=batch_seconds:reason='batch_timeout';break
                resident=group_rss(process.pid);peak=max(peak,resident)
                if resident>rss_bytes:reason='rss_limit';break
                if log.stat().st_size>65536:reason='log_limit';break
                if progress.exists() and progress.stat().st_mtime_ns!=last_mtime:
                    value=json.loads(progress.read_text());new=validate_progress(value,binding,ids)
                    if len(new)>len(ids):changed=now
                    ids=new;last_mtime=progress.stat().st_mtime_ns
                    if value.get('peak_rss_bytes',0)>rss_bytes:reason='rss_limit';break
                exitcode=process.poll()
                if exitcode is not None:
                    if expired.is_set():reason='aggregate_timeout';break
                    if exitcode!=0:reason='child_failure'
                    elif not progress.exists() or value.get('state')!='passed' or len(ids)!=14606 or value.get('context_links')!=93007:
                        reason='incomplete_coverage'
                    break
                time.sleep(.05)
    except (ValueError,OSError,subprocess.SubprocessError) as error:reason=str(error)[:160]
    finally:
        if watchdog is not None:watchdog.cancel();watchdog.join(timeout=2)
        if process is not None:cleanup(process)
    record={'state':'failed' if reason else 'passed','reason':reason,'seconds':round(time.monotonic()-started,3),
        'processed_count':len(ids),'peak_sampled_group_rss_bytes':peak,'binding':binding,
        'limits':{'seconds':seconds,'rss_bytes':rss_bytes,'batch_seconds':batch_seconds},
        'coverage':'each ID real capture/normalize/map/bind/schema strict encode; representative decoding separately',
        'http_requests':0,'merchant_assignments_observed':False}
    atomic_json(status,record)
    if log.stat().st_size>65536:
        with log.open('r+b') as output:output.truncate(65536)
    return record


def child(directory,binding):
    import resource
    # Explicit socket denial makes accidental network use fail this attempt.
    import socket
    socket.socket.connect=lambda *a,**k:(_ for _ in ()).throw(AssertionError('offline sweep'))
    from shopextract.taxonomies.shopify import load_shopify_taxonomy,normalize_with_shopify_taxonomy
    from shopextract._capture import capture
    from shopextract._models import Platform
    started=time.monotonic()
    resource_path=ROOT/'build/shopify-taxonomy/catalogs/2026-08'/binding['fingerprint']/'catalog.json.gz'
    assert hashlib.sha256(resource_path.read_bytes()).hexdigest()==binding['resource_sha256']
    catalog=load_shopify_taxonomy(catalog_root=ROOT/'build/shopify-taxonomy/catalogs',fingerprint=binding['fingerprint'])
    assert dict(catalog.manifest.source_hashes)==dict(binding['source_hashes'])
    assert code_identity()==binding['code_hashes']
    processed=[];links=0
    def save(state):
        peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if sys.platform!='darwin':peak*=1024
        atomic_json(directory/'progress.json',{'state':state,'categories':len(processed),'processed_ids':processed,
            'context_links':links,'seconds':round(time.monotonic()-started,3),'peak_rss_bytes':peak,'binding':binding})
    for node in catalog.iter_categories():
        raw=capture({'id':101,'title':'Controlled taxonomy item','handle':'controlled','variants':[],
            'category':{'id':node.id,'name':node.name}},'https://merchant.test/products/controlled','synthetic_fixture',observed_at='2026-10-18T00:00:00+00:00')
        value=normalize_with_shopify_taxonomy(raw,platform=Platform.SHOPIFY,shop_url='https://merchant.test',taxonomy=catalog,allow_unknown_source_version=True)
        schema=catalog.schema_for(value)
        assert len(schema.resolved)==1 and schema.resolved[0].category==node
        assert schema.resolved[0].attributes==catalog.attributes_for(node.id)
        mapped=[m for m in value.mappings if m.status=='mapped']
        assert len(mapped)==1 and mapped[0].target_ids==(node.short_id,) and mapped[0].target_version==catalog.registry_version
        assert mapped[0].term.native_id==node.id and mapped[0].term.taxonomy_version is None
        assert mapped[0].source_pointers==('/category/id',)
        links+=len(schema.resolved[0].attributes);processed.append(node.id)
        if len(processed)%100==0:save('running')
    assert processed==[n.id for n in catalog.iter_categories()] and len(processed)==14606 and links==93007
    assert code_identity()==binding['code_hashes']
    save('passed')


def main():
    directory=OUT/'approved-sweep'
    directory.mkdir(parents=True,exist_ok=True)
    marker=directory/'attempt.json'
    pin=json.loads((ROOT/'src/shopextract/taxonomies/shopify/pin.json').read_text())
    binding={'attempt_id':str(uuid.uuid4()),'fingerprint':pin['fingerprint'],'source_hashes':pin['source_hashes'],
        'resource_sha256':pin['resource_sha256'],'code_hashes':code_identity(),'python':sys.version}
    # Exclusive lifetime reservation: never silently reuse old IDs or restart.
    with marker.open('x') as output:
        json.dump(binding,output);output.flush();os.fsync(output.fileno())
    result=monitor([sys.executable,str(Path(__file__).resolve()),'--child',str(directory)],directory,binding)
    print(json.dumps({k:v for k,v in result.items() if k!='binding'}))
    return 0 if result['state']=='passed' else 1


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--child':
        directory=Path(sys.argv[2]);child(directory,json.loads((directory/'attempt.json').read_text()))
    else:sys.exit(main())
